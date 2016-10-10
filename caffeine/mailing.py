#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import hashlib
import mailbox
import base64
import email.message


def json_default(obj):
    try:
        return list(obj)
    except:
        return repr(obj)


def content_type_is_binary(content_type):
    return (
        'image' in content_type or
        'video' in content_type or
        'octet-stream' in content_type
    )


def checksum(item):
    return hashlib.sha1(item.encode('utf-8')).hexdigest()


class InBox(object):
    def __init__(self, path):
        self.path = path
        self.box = mailbox.mbox(self.path)

    def get_all_emails(self):
        return map(EmailMessage, self.box.items())


class EmailMessage(object):
    def __init__(self, id_and_msg):
        self.id, self.msg = id_and_msg

    def extract_relevant_metadata(self, metadata):
        data = {}
        data[b'id'] = checksum(self.msg.as_string())
        data[b'to'] = metadata.pop('To')
        data[b'from'] = metadata.pop('Return-Path')
        data[b'received'] = metadata.pop('Received')
        data[b'subject'] = metadata.pop('Subject')
        data[b'content-type'] = metadata.pop('Content-Type')
        data[b'meta'] = metadata
        return data

    def extract_message(self, message):
        if isinstance(message, basestring):
            return {
                'id': checksum(message),
                'body': message
            }

        all_params = message.get_params()
        ((content_type, _), (_, charset)) = all_params
        body = message.get_payload(decode=True)

        if isinstance(body, email.message.Message):
            return self.extract_message(body)

        if message.is_multipart():
            parts = [self.extract_message(m) for m in message.get_payload()]
        else:
            parts = []

        if 'text' in content_type:
            body = body.decode(charset)

        elif content_type_is_binary(content_type):
            body = base64.b64encode('base64')

        return {
            'is_multipart': self.msg.is_multipart(),
            'content_type': content_type,
            'parts': parts,
            'encoding': charset,
            'body': body,
            'id': checksum(message.as_string())
        }

    def to_dict(self):
        metadata = dict(self.msg.items())

        data = self.extract_relevant_metadata(metadata)
        data[b'original'] = self.msg.as_string()
        data[b'messages'] = [self.extract_message(msg) for msg in self.msg.get_payload()]
        return data

    def to_json(self, indent=2):
        return json.dumps(self.to_dict(), indent=indent, default=json_default)


def main():
    inbox = InBox('inbox/webmaster')
    for message in inbox.get_all_emails():
        print message.to_json()


if __name__ == '__main__':
    main()

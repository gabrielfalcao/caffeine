# -*- coding: utf-8 -*-
#

from __future__ import unicode_literals

import sys
import logging
import argparse
import warnings
import coloredlogs
import multiprocessing

from plant import Node
from caffeine import settings
from caffeine.models import Track, User
from caffeine.workers import get_worker_class_by_label
from caffeine.application import server
from caffeine.util import generate_encryption_key
from caffeine.util import get_upload_node


LOGO = '''
\033[1;30m _______                    \033[1;34m _______               __
\033[1;30m|_     _|.--.--.-----.-----.\033[1;34m|_     _|.---.-.-----.|  |--.
\033[1;30m  |   |  |  |  |     |  -__|\033[1;34m  |   |  |  _  |     ||    <
\033[1;30m  |___|  |_____|__|__|_____|\033[1;34m  |___|  |___._|__|__||__|__|

{0}\033[0m'''


def args_include_debug_or_info():
    return len(sys.argv) > 1 and sys.argv[1] in ['--debug', '--info']


def get_remaining_sys_argv():
    if args_include_debug_or_info():
        argv = sys.argv[3:]
    else:
        argv = sys.argv[2:]

    return argv


def caffeine_scan():
    parser = argparse.ArgumentParser(
        prog='caffeine scan',
        description='scans a given folder for music files and import them')

    parser.add_argument('path', help='the label of the worker')

    args = parser.parse_args(get_remaining_sys_argv())
    node = Node(args.path)
    if not node.exists:
        logging.critical('path does not exist: {0}'.format(args.path))
        raise SystemExit(1)

    upload_node = get_upload_node()
    bot = User.get_bot_user()
    for music_node in node.find_with_regex('.[Mm][Pp]3'):
        existing_track = Track.find_one_by(download_path__contains=music_node.basename)
        if existing_track:
            logging.info('{0} already imported'.format(existing_track))
            continue

        final_path = upload_node.join(music_node.basename)
        with open(final_path, 'wb') as fd:
            fd.write(open(music_node.path, 'rb').read())

        track = Track.create(
            user_id=bot.id,
            download_path=final_path
        )
        logging.info('successfully imported track {0}'.format(track))


def caffeine_run_workers():
    parser = argparse.ArgumentParser(
        prog='caffeine workers',
        description='execute background workers')

    parser.add_argument('name', help='the label of the worker')
    parser.add_argument('--concurrency', default=multiprocessing.cpu_count(), type=int, help='how many coroutines')
    parser.add_argument('--pull-bind-address', required=True, help='the zmq address of the pull bind')

    args = parser.parse_args(get_remaining_sys_argv())

    WorkerClass = get_worker_class_by_label(args.name)

    worker = WorkerClass(args.concurrency, args.pull_bind_address)
    print LOGO.format('\033[1;30mWorkers: \033[1;32m{0}'.format(worker))
    worker.run()


def caffeine_run_web():
    parser = argparse.ArgumentParser(
        prog='caffeine web',
        description='execute web instance for local development')

    parser.add_argument('--host', default=settings.HOST, help='the http hostname')
    parser.add_argument('--port', default=settings.PORT, type=int, help='the http port')

    args = parser.parse_args(get_remaining_sys_argv())

    print LOGO.format('\033[1;30mWeb: \033[1;32m{0}'.format('http://{0}:{1}'.format(args.host, args.port)))
    server.run(
        host=args.host,
        port=args.port,
        debug=True
    )


def caffeine_generate_key():
    parser = argparse.ArgumentParser(
        prog='caffeine generate-key',
        description='generates a fernet key for token encryption')

    parser.parse_args(get_remaining_sys_argv())

    print generate_encryption_key()


def main():
    HANDLERS = {
        'workers': caffeine_run_workers,
        'web': caffeine_run_web,
        'generate-key': caffeine_generate_key,
        'scan': caffeine_scan,
    }

    parser = argparse.ArgumentParser(prog='caffeine')

    parser.add_argument('command', help='Available commands:\n\n{0}\n'.format("|".join(HANDLERS.keys())))
    parser.add_argument('--debug', help='debug mode, prints debug logs to stderr', action='store_true', default=False)
    parser.add_argument('--info', help='info mode, prints info logs to stderr', action='store_true', default=False)

    if args_include_debug_or_info():
        argv = sys.argv[1:3]
    else:
        argv = sys.argv[1:2]

    args = parser.parse_args(argv)

    if args.info:
        LOG_LEVEL_NAME = 'INFO'

    elif args.debug:
        LOG_LEVEL_NAME = 'DEBUG'

    else:
        LOG_LEVEL_NAME = 'INFO'

    LOG_LEVEL = getattr(logging, LOG_LEVEL_NAME)

    for logger in [None, 'caffeine', 'caffeine.worker', 'werkzeug']:
        logger = logging.getLogger()
        logger.setLevel(LOG_LEVEL)

    coloredlogs.install(level=LOG_LEVEL)

    if args.command not in HANDLERS:
        parser.print_help()
        raise SystemExit(1)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            HANDLERS[args.command]()
        except Exception:
            logging.exception("Failed to execute %s", args.command)
            raise SystemExit(1)


if __name__ == '__main__':
    main()

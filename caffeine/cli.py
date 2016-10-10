# -*- coding: utf-8 -*-
#

from __future__ import unicode_literals

import sys
import logging
import argparse
import warnings
import coloredlogs

from caffeine import settings
from caffeine.application import server


LOGO = '''
 ______         ___   ___         __
|      |.---.-.'  _|.'  _|.-----.|__|.-----.-----.
|   ---||  _  |   _||   _||  -__||  ||     |  -__|
|______||___._|__|  |__|  |_____||__||__|__|_____|
'''


def args_include_debug_or_info():
    return len(sys.argv) > 1 and sys.argv[1] in ['--debug', '--info']


def get_remaining_sys_argv():
    if args_include_debug_or_info():
        argv = sys.argv[3:]
    else:
        argv = sys.argv[2:]

    return argv


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


def main():
    HANDLERS = {
        'web': caffeine_run_web,
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

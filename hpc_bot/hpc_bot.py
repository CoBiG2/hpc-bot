#!/usr/bin/env python3
# coding: utf-8

# Copyright 2020 Pedro HC David (Kronopt), https://github.com/Kronopt
# This file is part of hpc-bot.
# hpc-bot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# hpc-bot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with hpc-bot. If not, see <http://www.gnu.org/licenses/>.

"""
hpc-bot - CoBiG² Discord server bot

to run:
$ python hpc_bot.py <bot_token>
"""


__author__ = 'Pedro HC David, https://github.com/Kronopt'
__credits__ = ['Pedro HC David', 'Francisco Pina Martins']
__copyright__ = 'Copyright Pedro HC David & Francisco Pina Martins 2020'
__license__ = 'GPLv3'
__version__ = '0.1.0a1'
__url__ = 'https://github.com/CoBiG2/hpc-bot'
__description__ = 'A discord bot to relay HPC information.'


import argparse
import copy
import hashlib
import json
import logging
import os
import socket
import sys

try:
    import cogs
except ImportError:
    import hpc_bot.cogs as cogs


def config_parser(cli, cli_parsed):
    """
    Parses the config file and modifies options accordingly

    cli holds all the arguments metadata
    cli_parsed holds the parsed arguments
    """
    with open(os.path.abspath(cli_parsed.config)) as config_data:
        configs = json.load(config_data)

    if 'token' in configs and cli_parsed.token == cli.get_default('token'):
        cli_parsed.token = configs['token']
    if 'nickname' in configs and cli_parsed.nickname == cli.get_default('nickname'):
        cli_parsed.nickname = configs['nickname']
    if 'avatar' in configs and cli_parsed.avatar == cli.get_default('avatar'):
        cli_parsed.avatar = configs['avatar']
    if 'bot_text_channel' in configs and cli_parsed.bot_text_channel == cli.get_default(
            'bot_text_channel'):
        cli_parsed.bot_text_channel = configs['bot_text_channel']
    if 'log' in configs and cli_parsed.log == cli.get_default('log'):
        cli_parsed.log = os.path.abspath(os.path.expanduser(configs['log']))
        # logging handles files directly
        if os.path.exists(cli_parsed.log) and os.path.isdir(cli_parsed.log):
            cli_parsed.log = os.path.join(cli_parsed.log, 'bot.log')  # append file to log path

    return cli_parsed


def arguments_handler():
    """
    Handles argument parsing

    Arguments precedence: commandline > config > defaults
    """
    cli = argparse.ArgumentParser(description='Run hpc-bot discord Bot')
    cli.add_argument('-t',
                     dest='token',
                     help='Bot token. REQUIRED. Get one here: \
                           https://discordapp.com/developers/applications/me',
                     default='')
    cli.add_argument('-n',
                     dest='nickname',
                     help='Bot nickname. Default is computer host name (in this case: '
                          f'"{socket.gethostname()}")',
                     default=socket.gethostname())
    cli.add_argument('-a',
                     dest='avatar',
                     help="Bot avatar image path (only .jpeg or .png). Sets bot avatar. "
                          "Ignoring this argument will leave your bot's avatar unchanged",
                     default='')
    cli.add_argument('-tc',
                     dest='bot_text_channel',
                     help='Text channel where bot will send its messages. Default is "hpc-bots"',
                     default='hpc-bots')
    cli.add_argument('-l',
                     dest='log',
                     help='Log file path. If file exists, logs will be appended to it. '
                          'Default is "./bot.log"',
                     default='bot.log')
    cli.add_argument('-c',
                     dest='config',
                     help='Config file path. Bot parameters will be loaded from config file. '
                          'Command line arguments take precedence over config parameters.',
                     default='')
    cli_parsed = cli.parse_args()

    if cli_parsed.config:
        cli_parsed = config_parser(cli, cli_parsed)

    # token is required
    if not cli_parsed.token:
        cli.error('Bot token is required for bot to run (-t TOKEN)')

    return cli_parsed


def main():
    """
    Handles logging and bot initialization
    """
    # command line interface stuff
    cli = arguments_handler()

    # logging stuff
    log_stderr_handler = logging.StreamHandler(sys.stderr)
    log_file_handler = logging.FileHandler(filename=cli.log, encoding='utf-8', mode='a')
    log_file_handler.setFormatter(logging.Formatter(
        '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logging.basicConfig(level=logging.INFO, handlers=[log_stderr_handler, log_file_handler])
    logger = logging.getLogger('hpc-bot.main')

    # log arguments
    args = copy.deepcopy(vars(cli))
    hashed_token = hashlib.sha256(args['token'].encode()).hexdigest()  # keep token private in log
    args['token'] = f'sha256({hashed_token})'
    for arg, value in args.items():
        logger.info(f'Parameter:{arg}={value}')
    del args

    # start bot
    logger.info('Starting bot')
    bot = cogs.Bot(
        nickname=cli.nickname,
        avatar_path=cli.avatar,
        bot_text_channel_name=cli.bot_text_channel,
    )
    bot.run(cli.token)
    logger.info('Shutting down bot complete')


if __name__ == '__main__':
    main()

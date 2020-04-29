#!python3
# coding: utf-8

"""
hpc-bot - CoBiG² Discord server bot

to run:
$ python hpc_bot.py <bot_token>
"""

import argparse
import json
import logging
import os
import socket
import discord
import requests
from io import BytesIO
from discord.ext import commands
from PIL import Image

try:
    import cogs
except ImportError:
    import hpc_bot.cogs as cogs


def config_parser(cli):
    """
    Parses the config file and modifies options accordingly
    """
    with open(os.path.abspath(cli.config)) as config_data:
        configs = json.load(config_data)

    if cli.token is None:
        cli.token = configs['token']
    if cli.log_file is None:
        cli.log_file = os.path.abspath(os.path.expanduser(configs['log']))
    if os.path.isdir(os.path.dirname(cli.log_file)) is False:
        os.makedirs(os.path.dirname(cli.log_file))
    if cli.bot_text_channel is None:
        cli.bot_text_channel = configs['bot_text_channel']

    return cli


def arguments_handler():
    """
    Handles argument parsing
    """
    cli = argparse.ArgumentParser(description='Run hpc-bot discord Bot')
    cli.add_argument('-t',
                     dest='token',
                     help='Bot token. Get one here: \
                           https://discordapp.com/developers/applications/me')
    cli.add_argument('-c',
                     dest='config',
                     help='Config file location',
                     default=None)
    cli.add_argument('-l',
                     dest='log_file',
                     help='Log file location. Default is "./bot.log"',
                     default='bot.log')
    cli.add_argument('-tc',
                     dest='bot_text_channel',
                     help='Text channel to join in discord',
                     default='hpc-bots')
    cli = cli.parse_args()

    if cli.config is not None:
        cli = config_parser(cli)

    return cli


def main():
    """
    Main bot function. Just ported from imperative code
    """
    # command line interface stuff
    cli = arguments_handler()

    # logging stuff
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('discord')
    handler = logging.FileHandler(filename=cli.log_file, encoding='utf-8', mode='a')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

    # bot setup
    bot = commands.Bot(command_prefix=commands.when_mentioned)  # bot only reacts when mentioned: @<bot_name> <command>
    bot.add_cog(cogs.Commands(bot))
    bot.help_command = commands.MinimalHelpCommand()
    bot.server_name = socket.gethostname()

    # bot server color
    image_request = requests.get(f'https://raw.githubusercontent.com/CoBiG2/hpc-bot/{bot.server_name}/img.png')
    if image_request.status_code == 200:
        server_image = Image.open(BytesIO(image_request.content))
    else:  # default image if request from github fails
        server_image = Image.open('hpc_bot/img/img.png')
    image_color = server_image.resize((1, 1)).getpixel((0, 0))[:-1]  # average pixel color
    bot.color = discord.Color.from_rgb(*image_color)

    # do some stuff when bot is ready
    @bot.event
    async def on_ready():
        await bot.change_presence(activity=discord.Game(f'Type @{bot.user.name} help'))
        logger.info('Logged in as: %s, (id: %s)' % (bot.user.name, bot.user.id))

        # check how many servers this bot is connected to (should only be one)
        if len(bot.guilds) > 1:
            logger.error('Bot can only be active on a single server')
            await bot.logout()

        # check if bot-specific text channel exists
        else:
            bot.bot_text_channel = ''
            for text_channel in bot.guilds[0].text_channels:
                if text_channel.name == cli.bot_text_channel:
                    bot.bot_text_channel = text_channel
                    break
            if not bot.bot_text_channel:
                logger.error(f'No text channel named "{cli.bot_text_channel}" exists on the server')
                await bot.logout()
            else:
                logger.info('Bot is ready')

    # start bot
    logger.info('Starting bot')
    bot.run(cli.token)
    logger.info('bot shutdown complete')


if __name__ == '__main__':
    main()

# TODO help command (based on commands.MinimalHelpCommand)
# TODO what to do on bot crash
# TODO what to do on machine restart (auto-run)
# TODO builtin alternative to requests to fetch bot image?

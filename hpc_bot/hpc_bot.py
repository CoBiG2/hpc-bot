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

import argparse
import json
import logging
import os
import socket
import discord
from io import BytesIO
from discord.ext import commands
from PIL import Image

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
    if 'name' in configs and cli_parsed.name == cli.get_default('name'):
        cli_parsed.name = configs['name']
    if 'avatar' in configs and cli_parsed.avatar == cli.get_default('avatar'):
        cli_parsed.avatar = configs['avatar']
    if 'bot_text_channel' in configs and cli_parsed.bot_text_channel == cli.get_default('bot_text_channel'):
        cli_parsed.bot_text_channel = configs['bot_text_channel']
    if 'log' in configs and cli_parsed.log == cli.get_default('log'):
        cli_parsed.log = os.path.abspath(os.path.expanduser(configs['log']))
        if os.path.exists(cli_parsed.log) and os.path.isdir(cli_parsed.log):  # logging handles files directly
            cli_parsed.log = os.path.join(cli_parsed.log, 'bot.log')  # append file to log path

    return cli_parsed


def arguments_handler():
    """
    Handles argument parsing
    """
    cli = argparse.ArgumentParser(description='Run hpc-bot discord Bot')
    cli.add_argument('-t',
                     dest='token',
                     help='Bot token. REQUIRED. Get one here: \
                           https://discordapp.com/developers/applications/me',
                     default='')
    cli.add_argument('-c',
                     dest='config',
                     help='Config file location',
                     default='')
    cli.add_argument('-n',
                     dest='name',
                     help="Bot name. Default is computer host name (in this case: "
                          f"'{socket.gethostname()}')",
                     default=socket.gethostname())
    cli.add_argument('-a',
                     dest='avatar',
                     help="Bot avatar image location (only .jpeg or .png). Sets bot avatar. "
                          "Ignoring this argument will leave your bot's avatar unchanged",
                     default='')
    cli.add_argument('-tc',
                     dest='bot_text_channel',
                     help='Text channel where bot will send its messages. Default is "hpc-bots"',
                     default='hpc-bots')
    cli.add_argument('-l',
                     dest='log',
                     help='Log file location. If file exists, logs will be appended to it. '
                          'Default is "./bot.log"',
                     default='bot.log')
    cli_parsed = cli.parse_args()

    if cli_parsed.config != '':
        cli_parsed = config_parser(cli, cli_parsed)

    # token is required
    if not cli_parsed.token:
        cli.error('Bot token is required for bot to run')

    return cli_parsed


def update_bot_color(image):
    """
    Generates a new bot color

    image is a filename (string), pathlib.Path object or a file object
    """
    image_read = Image.open(image)
    image_color = image_read.resize((1, 1)).getpixel((0, 0))[:-1]  # average pixel color
    return discord.Color.from_rgb(*image_color)


def main():
    """
    Main bot function
    Handles logging and bot initialization
    """
    # command line interface stuff
    cli = arguments_handler()

    # logging stuff
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('discord')
    handler = logging.FileHandler(filename=cli.log, encoding='utf-8', mode='a')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

    # bot setup
    bot = commands.Bot(command_prefix=commands.when_mentioned)  # bot only reacts when mentioned: @<bot_name> <command>
    bot.add_cog(cogs.Commands(bot))
    bot.help_command = commands.MinimalHelpCommand()
    bot.server_name = cli.name
    bot.bot_text_channel = cli.bot_text_channel

    # do some stuff when bot connects to discord (but is not ready yet)
    @bot.event
    async def on_connect():
        # check how many servers this bot is connected to (should only be one)
        if len(bot.guilds) > 1:
            logger.error('Bot can only be active on a single discord server')
            await bot.logout()

        # check if bot-specific text channel exists
        elif len(bot.guilds) == 1:
            for text_channel in bot.guilds[0].text_channels:
                if text_channel.name == bot.bot_text_channel:
                    bot.bot_text_channel = text_channel  # TextChannel object
                    break
            if isinstance(bot.bot_text_channel, str):
                logger.warning(f'No text channel named "{bot.bot_text_channel}" exists on the server.'
                               f'No messages will be sent by the bot until this channel exists')
        logger.info('Bot is ready')

        if cli.avatar:
            # set bot avatar if image path was defined
            with open(cli.avatar, 'rb') as avatar_image:
                await bot.user.edit(avatar_image.read())
        else:
            # fetch avatar image if there is no local image
            cli.avatar = await bot.user.avatar_url_as(format='png').read()
            cli.avatar = BytesIO(cli.avatar)

        # bot server color (based on avatar color)
        bot.color = update_bot_color(cli.avatar)

    # when bot joins a new discord server checks how many it is connected to (it shouldn't be on more than one)
    @bot.event
    async def on_guild_join(guild):
        if len(bot.guilds) > 1:
            logger.error('Bot cannot join additional discord servers')
            logger.warning(f'Leaving guild {guild.name}...')
            await guild.leave()

    # updates bot color on bot avatar change
    @bot.event
    async def on_user_update(user_before, user_after):
        if user_before == bot.user and user_before.avatar != user_after.avatar:
            avatar = await bot.user.avatar_url_as(format='png').read()
            avatar = BytesIO(avatar)
            bot.color = update_bot_color(avatar)

    # do some stuff when bot is ready
    @bot.event
    async def on_ready():
        await bot.change_presence(activity=discord.Game(f'Type @{bot.user.name} help'))
        logger.info('Logged in as: %s, (id: %s)' % (bot.user.name, bot.user.id))

    # start bot
    logger.info('Starting bot')
    bot.run(cli.token)
    logger.info('bot shutdown complete')


if __name__ == '__main__':
    main()

# TODO help command (based on commands.MinimalHelpCommand)
# TODO what to do on bot crash
# TODO what to do on machine restart (auto-run)

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
import json
import logging
import os
import socket
import traceback
import types
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
    with open(os.path.abspath("hpc_bot/config/config")) as config_data:
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
    cli.add_argument('-n',
                     dest='name',
                     help='Bot name. Default is computer host name (in this case: '
                          f'"{socket.gethostname()}")',
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
    cli.add_argument('--config',
                     dest='config',
                     help='Use config file (located at hpc_bot/config/)',
                     action='store_true')
    cli_parsed = cli.parse_args()

    if cli_parsed.config:
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
    image_color = image_read.resize((1, 1)).getpixel((0, 0))  # average pixel color
    image_color = image_color[:-1] if len(image_color) > 3 else image_color  # may contain alpha value
    return discord.Color.from_rgb(*image_color)


def retrieve_bot_text_channel(guild, bot_text_channel_name):
    """
    Finds a text channel with the defined bot text channel name
    """
    for text_channel in guild.text_channels:
        if text_channel.name == bot_text_channel_name:
            return text_channel


async def change_bot_presence(bot, guild):
    """
    Changes bot "presence" message
    """
    await bot.change_presence(activity=discord.Game(f'Type @{guild.me.nick} help'))


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
    bot.add_cog(cogs.Commands(bot, cli.log))
    bot.help_command = commands.MinimalHelpCommand()
    bot.bot_text_channel_name = cli.bot_text_channel
    bot.bot_text_channel = None

    async def send_message(self, ctx, *args, **kwargs):
        """
        Sends message to bot_text_channel or to the private channel where the command was called from
        """
        if isinstance(ctx.channel, (discord.DMChannel, discord.GroupChannel)):
            channel = ctx.channel
        else:
            channel = self.bot_text_channel
        message = await channel.send(*args, **kwargs)
        return message
    bot.send_message = types.MethodType(send_message, bot)

    def bot_guild(self):
        """
        return this bot discord server
        None if bot is still on no discord servers or on more than one
        """
        return self.guilds[0] if len(self.guilds) == 1 else None
    bot.bot_guild = types.MethodType(bot_guild, bot)

    def bot_name(self, ctx):
        """
        return bot nickname if on text channel, bot name if private channel
        """
        guild = ctx.guild
        return guild.me.nick if guild is not None else self.user.name
    bot.bot_name = types.MethodType(bot_name, bot)

    async def get_color(self):
        """
        if avatar didn't change, returns the already set color,
        else generate a new color based on the new avatar, sets bot.color and returns color
        """
        # avatar changed
        if self.avatar_hash != self.user.avatar:
            logger.info('Avatar changed. Generating new bot color')
            # fetch avatar image
            new_avatar = await self.user.avatar_url_as(format='png').read()
            new_avatar = BytesIO(new_avatar)
            self.avatar_hash = self.user.avatar
            self.color = update_bot_color(new_avatar)
        return self.color
    bot.get_color = types.MethodType(get_color, bot)

    #
    # events
    #

    @bot.event
    async def on_command_error(ctx, exception):
        # ignore non-existent commands
        if isinstance(exception, commands.CommandNotFound):
            return
        logger.error(f'Error:\n{traceback.format_exc()}')

    @bot.event
    async def on_guild_join(guild):
        logger.info(f'Joining guild: {guild.name}')
        # leave additional discord servers (1 max)
        if len(bot.guilds) > 1:
            logger.error('Bot cannot join additional discord servers')
            logger.warning(f'Leaving guild: {guild.name}')
            await guild.leave()

        else:
            # set nickname when joining guild
            logger.info(f'Setting nickname to: {cli.name}')
            await guild.me.edit(nick=cli.name, reason='Setting up bot nickname')

            # presence 'Type help'
            await change_bot_presence(bot, guild)

            # check if bot-specific text channel exists
            bot.bot_text_channel = retrieve_bot_text_channel(guild, bot.bot_text_channel_name)
            if not bot.bot_text_channel:
                logger.warning(f'No text channel named "{bot.bot_text_channel_name}" exists on the "{guild}" '
                               f'discord server. No messages will be sent by the bot until this channel exists')

    @bot.event
    async def on_guild_channel_delete(channel):
        # if bot text channel is deleted
        if channel == bot.bot_text_channel:
            logger.warning(f'Bot text channel "{bot.bot_text_channel}" '
                           f'(id: {bot.bot_text_channel.id}) was deleted.')

            # check if there is another text channel with the defined bot text channel name
            bot.bot_text_channel = retrieve_bot_text_channel(channel.guild, bot.bot_text_channel_name)

            # there is
            if bot.bot_text_channel:
                logger.info('Found another text channel that matches bot text channel definition: '
                            f'"{bot.bot_text_channel}" (id: {bot.bot_text_channel.id})')
            # there isn't
            else:
                logger.warning(f'No messages will be sent by the bot until this channel exists again')

    @bot.event
    async def on_guild_channel_create(channel):
        # if bot text channel doesn't exist yet
        if not bot.bot_text_channel \
                and isinstance(channel, discord.TextChannel) \
                and channel.name == bot.bot_text_channel_name:
            logger.info(f'Newly created text channel matches bot text channel definition.')
            bot.bot_text_channel = channel

    @bot.event
    async def on_ready():
        # check how many discord servers this bot is connected to (1 max)
        if len(bot.guilds) > 1:
            logger.error('Bot can only be active on a single discord server')
            await bot.close()

        # 0 or 1 discord server
        else:
            if len(bot.guilds) == 1:
                guild = bot.bot_guild()

                # set nickname
                if guild.me.nick != cli.name:
                    logger.info(f'Setting nickname from "{guild.me.nick}" to "{cli.name}"')
                    await guild.me.edit(nick=cli.name, reason='Setting up bot nickname')

                # check if bot-specific text channel exists
                bot.bot_text_channel = retrieve_bot_text_channel(guild, bot.bot_text_channel_name)
                if not bot.bot_text_channel:
                    logger.warning(f'No text channel named "{bot.bot_text_channel_name}" exists on the "{guild}" '
                                   f'discord server. No messages will be sent by the bot until this channel exists')

                # presence 'Type help'
                await change_bot_presence(bot, guild)

            # bot avatar
            if cli.avatar:
                # set bot avatar if image path was defined
                with open(cli.avatar, 'rb') as avatar_image:
                    await bot.user.edit(avatar_image.read())
            else:
                # fetch avatar image if no local image was defined
                cli.avatar = await bot.user.avatar_url_as(format='png').read()
                cli.avatar = BytesIO(cli.avatar)

            # bot color (based on avatar color)
            bot.avatar_hash = bot.user.avatar
            bot.color = update_bot_color(cli.avatar)

            logger.info(f'Guild: {bot.bot_guild()}')
            logger.info(f'Text channel: {bot.bot_text_channel}')
            logger.info(f'Logged in as: {bot.user.name}, id: {bot.user.id}')
            logger.info('Bot is ready')

    # start bot
    logger.info('Starting bot')
    bot.run(cli.token)
    logger.info('Shutting down bot complete')


if __name__ == '__main__':
    main()

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
Bot Cog - bot class
"""

import logging
import sys
import discord
from io import BytesIO
from discord.ext import commands
from PIL import Image

try:
    import cogs
except ImportError:
    import hpc_bot.cogs as cogs


class Bot(commands.Bot):

    def __init__(self, nickname, avatar_path, bot_text_channel_name, logfile_handler, *args, **kwargs):
        super().__init__(command_prefix=commands.when_mentioned, *args, **kwargs)

        # logger
        self.logger = logging.getLogger('hpc-bot.Bot')
        self.logger.addHandler(logfile_handler)

        # cogs/commands
        self.add_cog(cogs.Commands(self, logfile_handler))
        self.help_command = cogs.Help()
        self.help_command.cog = self.cogs['Commands']

        # bot variables
        self.nickname = nickname
        self.avatar_path = avatar_path
        self.bot_text_channel_name = bot_text_channel_name
        self.bot_text_channel = None
        self.avatar_hash = None
        self.color = None

    ########
    # EVENTS
    ########

    async def on_ready(self):
        # check how many discord servers this bot is connected to (1 max)
        if len(self.guilds) > 1:
            self.logger.error('Bot can only be active on a single discord server')
            await self.close()

        # 0 or 1 discord server
        else:
            if len(self.guilds) == 1:
                guild = self.bot_guild

                # set nickname
                if guild.me.nick != self.nickname:
                    self.logger.info(f'Setting nickname from "{guild.me.nick}" to "{self.nickname}"')
                    await guild.me.edit(nick=self.nickname, reason='Setting up bot nickname')

                # check if bot-specific text channel exists
                self.bot_text_channel = self.retrieve_bot_text_channel(guild)
                if not self.bot_text_channel:
                    self.logger.warning(f'No text channel named "{self.bot_text_channel_name}" exists '
                                        f'on the "{guild}" discord server. No messages will be sent by '
                                        f'the bot until this channel exists')

                # presence 'Type help'
                self.logger.info(f'Setting bot presence')
                await self.change_bot_presence(guild)

            # bot avatar
            if self.avatar_path:
                # if image path was defined
                with open(self.avatar_path, 'rb') as avatar_image:
                    self.logger.info(f'Setting avatar to "{self.avatar_path}"')
                    await self.user.edit(avatar=avatar_image.read())
                avatar = self.avatar_path
            else:
                # fetch avatar image if no local image path was defined
                avatar = await self.user.avatar_url_as(format='png').read()
                avatar = BytesIO(avatar)

            # bot color (based on avatar color)
            self.logger.info(f'Setting bot color')
            self.color = self.update_color(avatar)
            self.avatar_hash = self.user.avatar

            self.logger.info(f'Guild: {self.bot_guild}')
            self.logger.info(f'Text channel: {self.bot_text_channel}')
            self.logger.info(f'Logged in as: {self.user.name}, id: {self.user.id}')
            self.logger.info('Bot is ready')

    async def on_guild_join(self, guild):
        self.logger.info(f'Joining guild: {guild.name}')
        # leave additional discord servers (1 max)
        if len(self.guilds) > 1:
            self.logger.error('Bot cannot join additional discord servers')
            self.logger.warning(f'Leaving guild: {guild.name}')
            await guild.leave()

        else:
            # set nickname when joining guild
            self.logger.info(f'Setting nickname to: {self.nickname}')
            await guild.me.edit(nick=self.nickname, reason='Setting up bot nickname')

            # presence 'Type help'
            await self.change_bot_presence(guild)

            # check if bot-specific text channel exists
            self.bot_text_channel = self.retrieve_bot_text_channel(guild)
            if not self.bot_text_channel:
                self.logger.warning(f'No text channel named "{self.bot_text_channel_name}" exists on the "{guild}" '
                                    f'discord server. No messages will be sent by the bot until this channel exists')

    async def on_guild_channel_delete(self, channel):
        # if bot text channel is deleted
        if channel == self.bot_text_channel:
            self.logger.warning(f'Bot text channel "{self.bot_text_channel}" '
                                f'(id: {self.bot_text_channel.id}) was deleted.')

            # check if there is another text channel with the defined bot text channel name
            self.bot_text_channel = self.retrieve_bot_text_channel(channel.guild)

            # there is
            if self.bot_text_channel:
                self.logger.info('Found another text channel that matches bot text channel definition: '
                                 f'"{self.bot_text_channel}" (id: {self.bot_text_channel.id})')
            # there isn't
            else:
                self.logger.warning(f'No messages will be sent by the bot until this channel exists again')

    async def on_guild_channel_create(self, channel):
        # if bot text channel doesn't exist yet
        if not self.bot_text_channel \
                and isinstance(channel, discord.TextChannel) \
                and channel.name == self.bot_text_channel_name:
            self.logger.info(f'Newly created text channel matches bot text channel definition.')
            self.bot_text_channel = channel

    async def on_error(self, event, *args, **kwargs):
        # all uncaught/unhandled exceptions come through here
        self.logger.exception(f'When handling event: {event}, with arguments: {args}\n{sys.exc_info()[2]}')

    async def on_command_error(self, ctx, exception):
        # ignore non-existent commands
        if isinstance(exception, commands.CommandNotFound):
            return

    #########
    # METHODS
    #########

    @staticmethod
    def update_color(image):
        """
        Generates a new bot color
        image is a filename (string), pathlib.Path object or a file object
        """
        image_read = Image.open(image)
        image_color = image_read.resize((1, 1)).getpixel((0, 0))  # average pixel color
        image_color = image_color[:-1] if len(image_color) > 3 else image_color  # may contain alpha value
        return discord.Color.from_rgb(*image_color)

    @property
    def bot_guild(self):
        """
        return this bot discord server
        None if bot is still on no discord servers or on more than one
        """
        return self.guilds[0] if len(self.guilds) == 1 else None

    def bot_name(self, ctx):
        """
        return bot nickname if on text channel, bot name if private channel
        """
        guild = ctx.guild
        return guild.me.nick if guild is not None else self.user.name

    def retrieve_bot_text_channel(self, guild):
        """
        Finds a text channel with the defined bot text channel name
        """
        for text_channel in guild.text_channels:
            if text_channel.name == self.bot_text_channel_name:
                return text_channel

    async def change_bot_presence(self, guild):
        """
        Changes bot "presence" message
        """
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,
                                                             name=f'for @{guild.me.nick} help'))

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

    async def get_color(self):
        """
        if avatar didn't change, returns the already set color,
        else generate a new color based on the new avatar, sets bot.color and returns color
        """
        # avatar changed
        if self.avatar_hash != self.user.avatar:
            self.logger.info('Avatar changed. Generating new bot color')
            # fetch avatar image
            new_avatar = await self.user.avatar_url_as(format='png').read()
            new_avatar = BytesIO(new_avatar)
            self.avatar_hash = self.user.avatar
            self.color = self.update_color(new_avatar)
        return self.color

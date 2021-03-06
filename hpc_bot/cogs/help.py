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
Help command
"""

import discord
from discord.ext import commands

try:
    import checks
except ImportError:
    import hpc_bot.checks as checks


class Help(commands.MinimalHelpCommand):
    """
    Help Command
    """
    def __init__(self, **options):
        # don't check checks, send help as private message
        super().__init__(verify_checks=False, dm_help=True, **options)

    def get_opening_note(self):
        """
        Defines the message at the top of help command when called without parameters
        """
        if self.cog.bot.bot_text_channel:
            bot_text_channel = self.cog.bot.bot_text_channel.mention
        else:
            bot_text_channel = None
        prefix = self.cog.bot.prefix

        if prefix:
            prefix_help = 'If there are more hpc bots on the server you can call the same command' \
                          f' simultaneously on all of them\nby using the prefix `{prefix}`, ' \
                          f'like so:  `{prefix}<command>`\n\n'
        else:
            prefix_help = ''

        return 'This bot provides some commands that can retrieve information from the hpc ' \
               'server it is associated with.\nMost commands output to the defined ' \
               f'bot text channel ({bot_text_channel}).\n\nCommands can be called by typing:  ' \
               f'`{self.clean_prefix}<command>`\nTo get help on a certain command:   ' \
               f'`{self.clean_prefix}{self.invoked_with} <command>`\n\n{prefix_help}' \
               'You can also send commands to the bot as private messages, in which case the ' \
               'output of the command will be sent directly to you.'

    def add_bot_commands_formatting(self, commands_, heading):
        """
        Formats how each command looks when calling help without parameters
        """
        if commands_:
            joined = '\u2002'.join(c.name for c in commands_)
            self.paginator.add_line('__**%s**__:' % heading)
            self.paginator.add_line('```')
            self.paginator.add_line(joined)
            self.paginator.add_line('```')

    def get_command_signature(self, command):
        """
        Formats how to call the help command
        """
        return f'`{self.clean_prefix}{command.qualified_name} {command.signature}`'

    def command_not_found(self, command_name):
        """
        When command is not found
        """
        return f'No command called `{command_name}` found'

    def subcommand_not_found(self, command_, command_name):
        """
        When subcommand is not found
        """
        if isinstance(command_, commands.Group) and len(command_.all_commands) > 0:
            return f'Command `{command_.qualified_name}` has no subcommand named {command_name}'
        return f'Command `{command_.qualified_name}` has no subcommands.'

    async def command_callback(self, ctx, *, command=None):
        """
        Sends feedback message when sending help message, if channel is not private
        """
        value = await super().command_callback(ctx, command=command)

        # don't send feedback message if private channel
        if not isinstance(ctx.channel, (discord.DMChannel, discord.GroupChannel)):

            # can send feedback message to channel where command originated?
            bot = ctx.guild.me if ctx.guild is not None else ctx.bot.user
            can_write_to_origin_channel = checks.can_write_to_origin_channel(bot)
            if await can_write_to_origin_channel(ctx):

                # send feedback message
                await self.cog.command_finished_ok(
                    ctx, msg=f'{ctx.author.mention}, help was sent as a private message')
        return value

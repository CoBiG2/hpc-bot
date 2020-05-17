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
Command checks
"""

import discord


##################
# HELPER FUNCTIONS
##################


async def info_message(ctx, user, channel, what):
    """
    Sends info message to channel where command originated if bot has permission to do it
    """
    if await can_write_to_origin_channel(user)(ctx):

        # send info message
        if what == 'no_channel':
            await ctx.send(f"Error: Channel `{channel.name}` doesn't exist. Please create it.")
        elif what == 'no_permission':
            await ctx.send("Error: Can't send messages to channel "
                           f'`{channel.name}`. Check bot permissions.')


########
# CHECKS
########


def can_write_to_origin_channel(user):
    """
    Checks if user has write permissions on channel where command originated
    """
    async def predicate(ctx):
        permissions = ctx.channel.permissions_for(user)
        if getattr(permissions, 'send_messages'):
            return True
        return False

    return predicate


def can_write_to_bot_text_channel():
    """
    Adapted and built from discord.ext.commands.bot_has_permissions
    Checks if channel exists and if bot has write permissions
    """
    async def predicate(ctx):
        # if private channel, ok
        if isinstance(ctx.channel, (discord.DMChannel, discord.GroupChannel)):
            return True

        channel = ctx.bot.bot_text_channel  # discord.TextChannel or None
        guild = ctx.guild
        me = guild.me if guild is not None else ctx.bot.user

        # Bot doesn't recognize the bot text channel (deleted or didn't ever exist)
        if not channel:
            await info_message(ctx, me, channel, 'no_channel')
            return False

        # if, for some reason, the bot couldn't find out for himself that the bot channel
        # doesn't exist or was deleted, this is a redundant check
        channel_found = discord.utils.get(guild.text_channels, name=channel.name)
        if not channel_found:
            await info_message(ctx, me, channel, 'no_channel')
            return False

        permissions = channel.permissions_for(me)
        permission = getattr(permissions, 'send_messages')
        if not permission:
            await info_message(ctx, me, channel, 'no_permission')
            return False

        return True

    return predicate

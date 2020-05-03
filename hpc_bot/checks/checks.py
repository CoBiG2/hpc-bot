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


async def no_channel_info_message(ctx, channel):
    await ctx.send(f"Error: Channel `{channel.name}` doesn't exist. Please create it.")


def can_write_to_bot_text_channel():
    """
    Similar to discord.ext.commands.bot_has_permissions
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
            await no_channel_info_message(ctx, channel)
            return False

        # if, for some reason, the bot couldn't find out for himself that the bot channel
        # doesn't exist or was deleted, this is a redundant check
        channel_found = discord.utils.get(guild.text_channels, name=channel.name)  # does channel exist
        if not channel_found:
            await no_channel_info_message(ctx, channel)
            return False

        permissions = channel.permissions_for(me)
        permission = getattr(permissions, 'send_messages')
        if not permission:
            await ctx.send(f"Error: Can't send messages to channel `{channel.name}`. Check bot permissions.")
            return False

        return True

    return predicate

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


def can_write_to_bot_text_channel():
    """
    Similar to discord.ext.commands.bot_has_permissions
    Checks if channel exists and if bot has write permissions
    """
    async def predicate(ctx):
        channel_name = ctx.bot.bot_text_channel  # discord.TextChannel or str (if didn't exist when bot initialized)
        guild = ctx.guild
        me = guild.me if guild is not None else ctx.bot.user

        if isinstance(channel_name, discord.TextChannel):
            channel_name = channel_name.name

        channel = discord.utils.get(guild.text_channels, name=channel_name)  # does channel exist
        if channel is None:
            await ctx.send(f"Error: Channel `{channel_name}` doesn't exist. Please create it.")
            return False
        ctx.bot.bot_text_channel = channel  # set channel on bot (if it wasn't already set)

        permissions = channel.permissions_for(me)
        permission = getattr(permissions, 'send_messages')
        if not permission:
            await ctx.send(f"Error: Can't send messages to channel `{channel.name}`. Check bot permissions.")
            return False
        return True

    return predicate

#!python3
# coding: utf-8

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

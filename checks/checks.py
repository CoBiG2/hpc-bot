#!python3
# coding: utf-8

"""
Command checks
"""


def can_write_to_bot_text_channel():
    """
    Check similar to discord.ext.commands.bot_has_permissions
    except it checks for write permissions to the specific bot text channel
    """
    async def predicate(ctx):
        channel = ctx.bot.bot_text_channel

        guild = ctx.guild
        me = guild.me if guild is not None else ctx.bot.user
        permissions = channel.permissions_for(me)

        permission = getattr(permissions, 'send_messages')
        if not permission:
            await ctx.send(
                "Error: Can't send messages to channel `{}` (check bot permissions)".format(channel.name))
            return False
        return True

    return predicate

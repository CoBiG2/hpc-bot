#!python3
# coding: utf-8

"""
hpc-bot - CoBiG² Discord server bot

to run:
$ python hpc_bot.py <bot_token>
"""

import argparse
import logging
import discord
from discord.ext import commands
import cogs


if __name__ == '__main__':
    # command line interface stuff
    cli = argparse.ArgumentParser(description='Run hpc-bot discord Bot')
    cli.add_argument('token', help='Bot token. Get one here: https://discordapp.com/developers/applications/me')
    cli = cli.parse_args()

    # logging stuff
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('discord')
    handler = logging.FileHandler(filename='bot.log', encoding='utf-8', mode='a')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

    # bot setup
    bot = commands.Bot(command_prefix=commands.when_mentioned)  # bot only reacts when mentioned: @<bot_name> <command>
    bot.add_cog(cogs.Commands())
    bot.help_command = commands.MinimalHelpCommand()

    # do some stuff when bot is ready
    @bot.event
    async def on_ready():
        await bot.change_presence(activity=discord.Game("Type @{} help".format(bot.user.name)))
        logger.info('Logged in as: %s, (id: %s)' % (bot.user.name, bot.user.id))
        logger.info('Bot is ready')

    # start bot
    logger.info('Starting bot')
    bot.run(cli.token)
    logger.info('bot shutdown complete')

    # TODO help command (based on commands.MinimalHelpCommand)

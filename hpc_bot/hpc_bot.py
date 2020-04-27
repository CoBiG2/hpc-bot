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

try:
    import cogs
except ImportError:
    import hpc_bot.cogs


# TODO config file (bot text channel, server name, logfile)
BOT_TEXT_CHANNEL = 'bot-test'
LOG_FILE = 'bot.log'

def main():
    """
    Main bot function. Just ported from imperative code.
    """
    # command line interface stuff
    cli = argparse.ArgumentParser(description='Run hpc-bot discord Bot')
    cli.add_argument('token',
                     help='Bot token. Get one here: \
                           https://discordapp.com/developers/applications/me')
    cli = cli.parse_args()

    # logging stuff
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('discord')
    handler = logging.FileHandler(filename=LOG_FILE, encoding='utf-8', mode='a')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

    # bot setup
    bot = commands.Bot(command_prefix=commands.when_mentioned)  # bot only reacts when mentioned: @<bot_name> <command>
    bot.add_cog(cogs.Commands(bot))
    bot.help_command = commands.MinimalHelpCommand()

    # do some stuff when bot is ready
    @bot.event
    async def on_ready():
        await bot.change_presence(activity=discord.Game('Type @{} help'.format(bot.user.name)))
        logger.info('Logged in as: %s, (id: %s)' % (bot.user.name, bot.user.id))

        # check how many servers this bot is connected to (should only be one)
        if len(bot.guilds) > 1:
            logger.error('Bot can only be active on a single server')
            await bot.logout()

        # check if bot-specific text channel exists
        else:
            bot.bot_text_channel = ''
            for text_channel in bot.guilds[0].text_channels:
                if text_channel.name == BOT_TEXT_CHANNEL:
                    bot.bot_text_channel = text_channel
                    break
            if not bot.bot_text_channel:
                logger.error('No text channel named "{}" exists on the server'.format(BOT_TEXT_CHANNEL))
                await bot.logout()
            else:
                logger.info('Bot is ready')

    # start bot
    logger.info('Starting bot')
    bot.run(cli.token)
    logger.info('bot shutdown complete')


if __name__ == '__main__':
    main()

# TODO help command (based on commands.MinimalHelpCommand)
# TODO what to do on bot crash
# TODO what to do on machine restart (auto-run)

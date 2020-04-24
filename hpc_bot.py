#!/usr/bin/python3
# coding: utf-8

"""
hpc-bot - CoBiG² Discord server bot

to run:
$ python3 hpc_bot.py <bot_token>
"""

import argparse
import logging
import discord
from discord.ext import commands


logging.basicConfig(level=logging.INFO)
bot = commands.Bot(command_prefix=commands.when_mentioned)  # bot only reacts when mentioned: @<bot_name> <command>
bot.remove_command('help')  # remove default 'help' command

# TODO add cogs
# TODO get server name (machine where bot is running)


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game("Type @{} help".format(bot.user.name)))
    logging.info('Logged in as: %s, (id: %s)' % (bot.user.name, bot.user.id))
    logging.info('Bot is ready')


@bot.command()
async def test(ctx):
    await ctx.send('tested')

if __name__ == '__main__':
    cli = argparse.ArgumentParser(description='Run hpc-bot discord Bot')
    cli.add_argument('token', help='Bot token. Get one here: https://discordapp.com/developers/applications/me')
    cli = cli.parse_args()

    bot.run(cli.token)


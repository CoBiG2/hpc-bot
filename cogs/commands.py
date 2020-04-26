#!python3
# coding: utf-8

"""
Commands Cog - bot commands
"""

import asyncio
import logging
import socket
from discord.ext import commands


class Commands(commands.Cog):

    def __init__(self):
        super().__init__()
        self.server_name = socket.gethostname()
        self.logger = logging.getLogger(__name__)

    @commands.command()
    async def test(self, ctx):
        """
        This is a testing command
        Some test text
        another line of test
        """
        await ctx.send('tested')

    @commands.command()
    async def name(self, ctx):
        """
        Server name
        Name of the server where the bot is running
        """
        await ctx.send(f'server name: {self.server_name}')

    @commands.command()
    async def status(self, ctx):
        """
        Server status
        CPU, RAM and total disk usage
        """
        pass
        # TODO uptime + cpu ($ uptime)
        # TODO ram + swap usage ($ free -gh)

    @commands.command()
    async def home(self, ctx):
        """
        Space usage of home folders
        Total space occupied by each user's home folder
        """
        command = 'sudo du -sh /home/*'
        process = await asyncio.create_subprocess_shell(
            command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

        while not process.stdout.at_eof():  # if command isn't done outputting to stdout
            line_read = await process.stdout.readline()
            line = line_read.decode('utf-8').rstrip()
            if line:
                await ctx.send(line)

        while not process.stderr.at_eof():  # if command isn't done outputting to stderr
            line_read = await process.stderr.readline()
            line = line_read.decode('utf-8').rstrip()
            if line:
                await ctx.send(line)

        # TODO embed
        # TODO:
        #   - see if there's a "home" message from this server (if not create one)
        #   - edit that message with the output of the command as it is being read

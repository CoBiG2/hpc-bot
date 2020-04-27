#!python3
# coding: utf-8

"""
Commands Cog - bot commands
"""

import asyncio
import logging
import signal
import socket
import discord
from functools import partial
from discord.ext import commands
import checks


class Commands(commands.Cog):

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.server_name = socket.gethostname()
        self.logger = logging.getLogger(__name__)

    async def cog_before_invoke(self, ctx):
        """Called before each command invocation"""
        user = ctx.author.nick if isinstance(ctx.author, discord.Member) else ctx.author.name
        self.logger.info("calling command: {}, by user: {}, from channel: {}".format(
            ctx.command.name, user, ctx.channel))

    async def cog_command_error(self, ctx, error):
        """Called when an error is raised inside this cog"""
        self.logger.error(error)

    @commands.command()
    async def name(self, ctx):
        """
        Server name
        Name of the server where the bot is running
        """
        await ctx.send(f'server name: {self.server_name}')

    @commands.command()
    @commands.check(checks.can_write_to_bot_text_channel())
    async def status(self, ctx):
        """
        Server status
        CPU, RAM and total disk usage
        """
        command_cpu_and_uptime = 'uptime'
        command_ram_and_swap = 'free -gh'
        command_disk_usage = 'df -h --total | tail -n 1'
        await self.run_shell_cmd(ctx, command_cpu_and_uptime, partial(self.handle_status, cmd_output='cpu_and_time'))
        await self.run_shell_cmd(ctx, command_ram_and_swap, partial(self.handle_status, cmd_output='ram_and_swap'))
        await self.run_shell_cmd(ctx, command_disk_usage, partial(self.handle_status, cmd_output='disk_usage'))

    async def handle_status(self, ctx, line, cmd_output=''):
        """
        Handles status command output

        Parameters
        ----------
        ctx: Context
            context
        line: str
            line of command output
        cmd_output: str
            what command output to expect
        """
        if cmd_output == 'cpu_and_time':
            uptime = line[line.find('up ')+3:line.find('user')].rsplit(',', maxsplit=1)[0]
            cpu_usage = line[line.rfind('load average: ')+14:]  # 1, 5 and 15 minutes average
            await self.bot.bot_text_channel.send(f'uptime: {uptime}\ncpu usage: {cpu_usage}')

        elif cmd_output == 'ram_and_swap':
            line_contents = line.split()
            # ignores first line, which only contains column headers
            if line_contents[0] == 'Mem:':
                _, ram_total, ram_used, ram_free, _, _, ram_available = line_contents
                await self.bot.bot_text_channel.send(
                    f'ram:\ntotal {ram_total}\nused {ram_used}\nfree {ram_free}\navailable {ram_available}')
            elif line_contents[0] == 'Swap:':
                _, swap_total, swap_used, swap_free = line_contents
                await self.bot.bot_text_channel.send(f'swap:\ntotal {swap_total}\nused {swap_used}\nfree {swap_free}')

        elif cmd_output == 'disk_usage':
            _, disk_size, disk_used, disk_available, disk_use_percentage, _ = line.split()
            await self.bot.bot_text_channel.send(
                f'disk:\nsize {disk_size}\nused {disk_used}\navailable {disk_available}\n'
                f'used percentage {disk_use_percentage}')

        # TODO embed
        # TODO:
        #   - see if there's a "status" message from this server/machine (if not create one)
        #   - edit that message with the output of the command as it is being read

    @commands.command()
    @commands.check(checks.can_write_to_bot_text_channel())
    async def home(self, ctx):
        """
        Space usage of home folders
        Total space occupied by each user's home folder on each server
        """
        command = 'sudo du -sh /home/*'
        await self.run_shell_cmd(ctx, command, self.handle_home)

    async def handle_home(self, ctx, line):
        """
        Handles home command output

        Parameters
        ----------
        ctx: Context
            context
        line: str
            line of command output
        """
        await self.bot.bot_text_channel.send(line)

        # TODO embed
        # TODO:
        #   - see if there's a "home" message from this server/machine (if not create one)
        #   - edit that message with the output of the command as it is being read

    async def run_shell_cmd(self, ctx, cmd, handle_output_line):
        """
        Runs shell command 'cmd' on the local machine

        Parameters
        ----------
        ctx: Context
            context
        cmd: str
            command to be executed
        handle_output_line: function
            function to handle each line of output produced by the command
        """
        async with ctx.channel.typing():
            process = await asyncio.create_subprocess_shell(
                cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

            # read each line of stdout
            while not process.stdout.at_eof():  # if command isn't done outputting to stdout
                line_read = await process.stdout.readline()
                line = line_read.decode('utf-8').rstrip()
                if line:
                    await handle_output_line(ctx, line)

            # no error while running the command
            if process.returncode == 0:
                await ctx.send("Command `{}` finished running successfully".format(ctx.command.name))
                # TODO every server will send this message...

            # errors
            else:
                _, stderr = await process.communicate()  # wait for command to terminate and finish reading stderr

                # signal terminated
                if process.returncode < 0:
                    signal_code = abs(process.returncode)
                    await ctx.send("Error: command `{}` terminated by signal `{} ({})`".format(
                        ctx.command.name,
                        signal_code,
                        signal.Signals(signal_code).name))
                    # TODO every server will send this message...

                # error return code
                else:
                    await ctx.send("Error: command `{}` terminated with error code `{}`".format(
                        ctx.command.name,
                        process.returncode))
                    # TODO every server will send this message...
                    # TODO find a way to get return code name with python...

                self.logger.error(stderr.decode('utf-8').rstrip())

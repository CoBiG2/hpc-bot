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
Commands Cog - bot commands
"""

import asyncio
import logging
import signal
import traceback
from functools import partial
import discord
from discord.ext import commands

try:
    import checks
except ImportError:
    import hpc_bot.checks as checks


class Commands(commands.Cog):
    """
    Main Cog. Contains all bot commands
    """
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.logger = logging.getLogger('hpc-bot.Commands')

    async def cog_before_invoke(self, ctx):
        """
        Called before each command invocation
        """
        user = ctx.author
        self.logger.info(f'Calling command: {ctx.command}, '
                         f'by user: {user}, nickname: {user.display_name}, '
                         f'from channel: {ctx.channel}')

    async def cog_command_error(self, ctx, error):
        """
        Called when an error is raised inside this cog
        """
        if isinstance(error, (commands.MaxConcurrencyReached, commands.CheckFailure)):
            self.logger.warning(f'When calling command {ctx.command.name}: {error}')
        else:
            self.logger.error(
                f'Error calling command {ctx.command.name}:\n{traceback.format_exc()}')

    async def command_finished_ok(self, ctx, msg=None):
        """
        Commands can call this when finished
        """
        # can send feedback message to channel where command originated?
        me = ctx.guild.me if ctx.guild is not None else ctx.bot.user
        can_write_to_origin_channel = checks.can_write_to_origin_channel(me)
        if await can_write_to_origin_channel(ctx):

            # feedback message
            if not msg:  # default feedback message for commands
                message = f'Command `{ctx.command.name}` finished'
                # for private messages don't mention bot_text_channel
                if not isinstance(ctx.channel, (discord.DMChannel, discord.GroupChannel)):
                    message += f'. Check output at {self.bot.bot_text_channel.mention}'
            else:
                message = msg
            message_ok = await ctx.send(message)
            await message_ok.delete(delay=30)

    async def handle_command_runtime(self, cmd_runtime, **kwargs):
        """
        Adds command runtime to sent message
        """
        embed = kwargs.get('embed')
        embed.description = f'ran in {cmd_runtime}s'
        await kwargs.get('message_sent').edit(embed=embed)

    @commands.command()
    @commands.check(checks.can_write_to_bot_text_channel())
    async def test(self, ctx):
        """
        Test command
        """
        bot_color = await self.bot.get_color()
        embed = discord.Embed(
            title="🔧 test command",
            color=bot_color
        ).set_footer(
            text=f'🖥️ {ctx.command.name}'
        )
        await self.bot.send_message(ctx,
                                    f'this is a test message from bot "{self.bot.bot_name(ctx)}"',
                                    embed=embed)
        await self.command_finished_ok(ctx)

    @commands.command()
    @commands.max_concurrency(1)
    @commands.check(checks.can_write_to_bot_text_channel())
    async def status(self, ctx):
        """
        Shows server status: CPU, RAM and total disk usage
        """
        cmds = {
            'cpu_and_time': 'uptime',
            'ram_and_swap': 'free -gh',
            'disk_usage':   'df -h --total | tail -n 1'
        }
        status_embed = await self.new_status_embed(ctx)
        status_message_sent = await self.bot.send_message(ctx, embed=status_embed)

        for cmd_name, cmd in cmds.items():
            ok = await self.run_shell_cmd(
                ctx, cmd,
                partial(self.handle_status, cmd_output=cmd_name),
                self.handle_command_runtime,
                embed=status_embed,
                message_sent=status_message_sent)
            if not ok:
                return
        await self.command_finished_ok(ctx)

    async def handle_status(self, ctx, line, cmd_output='', **kwargs):
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
            cpu = line[line.rfind('load average: ')+14:].split(', ')  # 1, 5 and 15 minutes average
            await kwargs.get('message_sent').edit(
                embed=kwargs.get('embed').add_field(
                    name='🕒 UP time',
                    value=uptime,
                    inline=True
                ).add_field(
                    name='🎛️ CPU',
                    value=f'1min : {cpu[0]}\n'
                          f'5min : {cpu[1]}\n'
                          f'15min : {cpu[2]}',
                    inline=True))

        elif cmd_output == 'ram_and_swap':
            line_contents = line.split()
            # ignores first line, which only contains column headers
            if line_contents[0] == 'Mem:':
                _, ram_total, ram_used, ram_free, _, ram_cache, ram_available = line_contents
                await kwargs.get('message_sent').edit(
                    embed=kwargs.get('embed').add_field(
                        name='🧠 RAM',
                        value=f'total : {ram_total}\n'
                              f'used : {ram_used}\n'
                              f'free : {ram_free}\n'
                              f'cache : {ram_cache}\n'
                              f'available : {ram_available}',
                        inline=True))
            elif line_contents[0] == 'Swap:':
                _, swap_total, swap_used, swap_free = line_contents
                await kwargs.get('message_sent').edit(
                    embed=kwargs.get('embed').add_field(
                        name='📼 SWAP',
                        value=f'total : {swap_total}\n'
                              f'used : {swap_used}\n'
                              f'free : {swap_free}',
                        inline=True))

        elif cmd_output == 'disk_usage':
            _, disk_size, disk_used, disk_available, disk_use_percentage, _ = line.split()
            await kwargs.get('message_sent').edit(
                embed=kwargs.get('embed').add_field(
                    name='🖴 STORAGE',
                    value=f'size : {disk_size}\n'
                          f'available : {disk_available}\n'
                          f'used : {disk_used} ({disk_use_percentage})',
                    inline=True))

    async def new_status_embed(self, ctx):
        """
        Generates a new default embed for the status command
        """
        bot_color = await self.bot.get_color()
        return discord.Embed(
            title="🎚️ server status",
            color=bot_color,
        ).set_footer(
            text=f'🖥️ {ctx.command.name}'
        )

    @commands.command()
    @commands.max_concurrency(1)
    @commands.check(checks.can_write_to_bot_text_channel())
    async def home(self, ctx):
        """
        Disk usage of each user's /home folder on the server
        """
        command = 'sudo du -sh /home/*'
        home_embed = await self.new_home_embed(ctx)
        home_message_sent = await self.bot.send_message(ctx, embed=home_embed)
        ok = await self.run_shell_cmd(ctx, command,
                                      self.handle_home,
                                      self.handle_command_runtime,
                                      embed=home_embed,
                                      message_sent=home_message_sent)
        if ok:
            await self.command_finished_ok(ctx)

    async def handle_home(self, ctx, line, **kwargs):
        """
        Handles home command output

        Parameters
        ----------
        ctx: Context
            context
        line: str
            line of command output
        """
        line_contents = line.split('/')
        usage = line_contents[0].rstrip()
        user = line_contents[-1]

        await kwargs.get('message_sent').edit(
            embed=kwargs.get('embed').add_field(
                name=user, value=usage, inline=True))

    async def new_home_embed(self, ctx):
        """
        Generates a new default embed for the home command
        """
        bot_color = await self.bot.get_color()
        return discord.Embed(
            title="🏠 size of each home folder",
            color=bot_color,
        ).set_footer(
            text=f'🖥️ {ctx.command.name}'
        )

    async def run_shell_cmd(self, ctx, cmd, handle_output_line, handle_cmd_runtime, **kwargs):
        """
        Runs shell command 'cmd' on the local machine
        Sends error message to origin channel on command error

        Parameters
        ----------
        ctx: Context
            context
        cmd: str
            command to be executed
        handle_output_line: function
            function to handle each line of output produced by the command
        handle_cmd_runtime: function
            function to handle the single line of command runtime
        kwargs:
            should include 'embed' and 'message_sent'

        Returns
        -------
        bool
            True if command ran to conclusion, False if an error occurred.
        """
        async with self.bot.bot_text_channel.typing():
            # wrap command in GNU time (outputs "real" command runtime to stderr)
            cmd = f'/usr/bin/time -f "%e" bash -c "{cmd}"'

            process = await asyncio.create_subprocess_shell(
                cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

            # read each line of stdout and pass it to handling function
            while not process.stdout.at_eof():  # if command isn't done outputting to stdout
                line_read = await process.stdout.readline()
                line = line_read.decode('utf-8').rstrip()
                if line:
                    await handle_output_line(ctx, line, **kwargs)

            # no error while running the command
            if process.returncode == 0:
                # read command runtime from stderr and pass it to runtime handling function
                cmd_runtime = await process.stderr.readline()
                cmd_runtime = cmd_runtime.decode('utf-8').rstrip()
                await handle_cmd_runtime(cmd_runtime, **kwargs)
                return True

            # errors
            _, stderr = await process.communicate()  # wait for command to finish and read stderr
            stderr = stderr.decode("utf-8").rstrip().rsplit("\n", 1)[0]  # remove runtime from end

            # signal terminated
            if process.returncode < 0:
                signal_code = abs(process.returncode)
                await ctx.send(f'Error: command `{ctx.command.name}` '
                               f'terminated by signal `{signal_code}` '
                               f'({signal.Signals(signal_code).name})')

            # error return code
            else:
                await ctx.send(f'Error: command `{ctx.command.name}` '
                               f'terminated with an error code `{process.returncode}`')
                # TODO find a way to get return code name with python...

            # delete message that was being updated, if any
            message_sent = kwargs.get('message_sent')
            if message_sent:
                await message_sent.delete()

            self.logger.error(
                f'Error code {process.returncode} while running command: '
                f'{ctx.command.name} ({cmd})\n{stderr}')
            return False

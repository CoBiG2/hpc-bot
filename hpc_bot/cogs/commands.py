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
import discord
from functools import partial
from discord.ext import commands

try:
    import checks
except ImportError:
    import hpc_bot.checks as checks


class Commands(commands.Cog):

    def __init__(self, bot, logfile):
        super().__init__()
        self.bot = bot

        self.logger = logging.getLogger(__name__)
        handler = logging.FileHandler(filename=logfile, encoding='utf-8', mode='a')
        handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
        self.logger.addHandler(handler)

    async def cog_before_invoke(self, ctx):
        """Called before each command invocation"""
        user = ctx.author
        self.logger.info(f'Calling command: {ctx.command}, '
                         f'by user: {user}, nickname: {user.display_name}, '
                         f'from channel: {ctx.channel}')

    async def cog_command_error(self, ctx, error):
        """Called when an error is raised inside this cog"""
        if not isinstance(error, commands.MaxConcurrencyReached):
            self.logger.error(f'Error calling command {ctx.command.name}:\n{traceback.format_exc()}')

    @commands.command()
    @commands.check(checks.can_write_to_bot_text_channel())
    async def test(self, ctx):
        bot_color = await self.bot.get_color()
        embed = discord.Embed(
            title="test embed",
            color=bot_color
        ).set_footer(
            text=f'command name: {"test"} 🔧'
        ).set_author(
            name=self.bot.bot_name(ctx),
            icon_url=f"https://raw.githubusercontent.com/CoBiG2/hpc-bot/extras/img/loki.png")
        await self.bot.send_message(ctx, f'test message from bot "{self.bot.bot_name(ctx)}"', embed=embed)

    @commands.command()
    @commands.max_concurrency(1)
    @commands.check(checks.can_write_to_bot_text_channel())
    async def status(self, ctx):
        """
        Server status
        CPU, RAM and total disk usage of the server(s)
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
            await self.bot.send_message(ctx, f'uptime: {uptime}\ncpu usage: {cpu_usage}')

        elif cmd_output == 'ram_and_swap':
            line_contents = line.split()
            # ignores first line, which only contains column headers
            if line_contents[0] == 'Mem:':
                _, ram_total, ram_used, ram_free, _, _, ram_available = line_contents
                await self.bot.send_message(
                    ctx,
                    f'ram:\ntotal {ram_total}\nused {ram_used}\nfree {ram_free}\navailable {ram_available}')
            elif line_contents[0] == 'Swap:':
                _, swap_total, swap_used, swap_free = line_contents
                await self.bot.send_message(ctx, f'swap:\ntotal {swap_total}\nused {swap_used}\nfree {swap_free}')

        elif cmd_output == 'disk_usage':
            _, disk_size, disk_used, disk_available, disk_use_percentage, _ = line.split()
            await self.bot.send_message(
                ctx,
                f'disk:\nsize {disk_size}\nused {disk_used}\navailable {disk_available}\n'
                f'used percentage {disk_use_percentage}')

        # TODO embed
        # TODO:
        #   - see if there's a "status" message from this server/machine (if not create one)
        #   - edit that message with the output of the command as it is being read

    @commands.command()
    @commands.max_concurrency(1)
    @commands.check(checks.can_write_to_bot_text_channel())
    async def home(self, ctx):
        """
        Home folders disk space usage
        Total space occupied by each user's home folder on the server(s)
        """
        command = 'sudo du -sh /home/*'
        home_embed = await self.new_home_embed(ctx, "home")
        home_message_sent = await self.bot.send_message(ctx, embed=home_embed)
        await self.run_shell_cmd(ctx, command, self.handle_home,
                                 embed=home_embed, message_sent=home_message_sent)

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

    async def new_home_embed(self, ctx, command_name):
        """Generates a new default embed for the home command"""
        bot_name = self.bot.bot_name(ctx)
        bot_color = await self.bot.get_color()
        return discord.Embed(
            title="size of all __home__ folders:",
            color=bot_color,
        ).set_footer(
            text=f'{command_name} 🏠'
        ).set_author(
            name=bot_name,
            icon_url=f"https://raw.githubusercontent.com/CoBiG2/hpc-bot/extras/img/{bot_name.lower()}.png"
        )

    async def run_shell_cmd(self, ctx, cmd, handle_output_line, **kwargs):
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
        async with self.bot.bot_text_channel.typing():
            process = await asyncio.create_subprocess_shell(
                cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

            # read each line of stdout
            while not process.stdout.at_eof():  # if command isn't done outputting to stdout
                line_read = await process.stdout.readline()
                line = line_read.decode('utf-8').rstrip()
                if line:
                    await handle_output_line(ctx, line, **kwargs)

            # no error while running the command
            if process.returncode == 0:
                await ctx.send(f'Command `{ctx.command.name}` finished running successfully')

            # errors
            else:
                _, stderr = await process.communicate()  # wait for command to terminate and finish reading stderr

                # signal terminated
                if process.returncode < 0:
                    signal_code = abs(process.returncode)
                    await ctx.send(f'Error: command `{ctx.command.name}` '
                                   f'terminated by signal `{signal_code}` '
                                   f'({signal.Signals(signal_code).name})')

                # error return code
                else:
                    await ctx.send(f'Error: command `{ctx.command.name}` '
                                   f'terminated with error code `{process.returncode}`')
                    # TODO find a way to get return code name with python...

                # delete message that was being updated, if any
                message_sent = kwargs.get('message_sent')
                if message_sent:
                    await message_sent.delete()

                self.logger.error(stderr.decode('utf-8').rstrip())

#!python3
# coding: utf-8

"""
Commands Cog - bot commands
"""

import asyncio
import logging
import random
import signal
import discord
from functools import partial
from discord.ext import commands

try:
    import checks
except ImportError:
    import hpc_bot.checks as checks


class Commands(commands.Cog):

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.home_embed = None
        self.home_message_sent = None

    async def cog_before_invoke(self, ctx):
        """Called before each command invocation"""
        user = ctx.author.nick if isinstance(ctx.author, discord.Member) else ctx.author.name
        self.logger.info("calling command: {}, by user: {}, from channel: {}".format(
            ctx.command.name, user, ctx.channel))

    async def cog_command_error(self, ctx, error):
        """Called when an error is raised inside this cog"""
        if not isinstance(error, commands.MaxConcurrencyReached):
            self.logger.error(error)

    @commands.command()
    async def servers(self, ctx):
        """
        Server(s) name(s)
        Name of the server(s) where the bot is running
        """
        await ctx.send(self.bot.server_name)

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
    @commands.max_concurrency(1)
    @commands.check(checks.can_write_to_bot_text_channel())
    async def home(self, ctx):
        """
        Home folders disk space usage
        Total space occupied by each user's home folder on the server(s)
        """
        command = 'sudo du -sh /home/*'

        # because only one instance of this command can run at a time, saving these attributes
        # and editing them is ok, because there's no risk of them being accessed from another place
        self.home_embed = self.new_home_embed("home")
        self.home_message_sent = await self.bot.bot_text_channel.send(embed=self.home_embed)

        await self.run_shell_cmd(ctx, command, self.handle_home)

        # reset variables
        self.home_embed = None
        self.home_message_sent = None

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
        line_contents = line.split('/')
        usage = line_contents[0].rstrip()
        user = line_contents[-1]

        await self.home_message_sent.edit(embed=self.home_embed.add_field(
            name=user, value=usage, inline=True))

    def new_home_embed(self, command_name):
        """Generates a new default embed for the home command"""
        return discord.Embed(
            title="size of all __home__ folders:",
            color=self.bot.color,
        ).set_footer(
            text=f'{command_name} 🏠'
        ).set_author(
            name=self.bot.server_name,
            icon_url=f"https://github.com/CoBiG2/hpc-bot/raw/{self.bot.server_name}/img.png"  # TODO config this
        )

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
        async with ctx.channel.typing(), self.bot.bot_text_channel.typing():
            process = await asyncio.create_subprocess_shell(
                cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

            # read each line of stdout
            while not process.stdout.at_eof():  # if command isn't done outputting to stdout
                line_read = await process.stdout.readline()
                line = line_read.decode('utf-8').rstrip()
                if line:
                    await asyncio.sleep(random.random() + 3)  # handles rate limit when using multiple servers
                    await handle_output_line(ctx, line)

            # no error while running the command
            if process.returncode == 0:
                await ctx.send(f'Command `{ctx.command.name}` '
                               f'finished running successfully on `{self.bot.server_name}`')

            # errors
            else:
                _, stderr = await process.communicate()  # wait for command to terminate and finish reading stderr

                # signal terminated
                if process.returncode < 0:
                    signal_code = abs(process.returncode)
                    await ctx.send(f"Error: command `{ctx.command.name}` "
                                   f"terminated by signal `{signal_code}` "
                                   f"({signal.Signals(signal_code).name}) `"
                                   f"on `{self.bot.server_name}`")

                # error return code
                else:
                    await ctx.send(f"Error: command `{ctx.command.name}` "
                                   f"terminated with error code `{process.returncode}` "
                                   f"on `{self.bot.server_name}`")
                    # TODO find a way to get return code name with python...

                self.logger.error(stderr.decode('utf-8').rstrip())

# hpc-bot
A repository to host code to build a discord bot

## Instructions
1.  Clone repository
    ```shell script
    git clone https://github.com/CoBiG2/hpc-bot.git
    ```

2.  Install python 3.8
    *   Downloads [here](https://www.python.org/downloads/), installation instructions [here](https://docs.python.org/3.8/using/unix.html)
    *   Alternatively, install to user space (on `Linux`) with [conda](https://docs.conda.io/projects/conda/en/latest/):
        ```shell script
        make install-conda
        make install-python
        ```

3.  Install dependencies
    ```shell script
    make upgrade-pip
    make install-dependencies
    ```
4.  Run, through the command line

    Pass command line arguments as needed, `TOKEN` being the only one required (all others have defaults).
    Alternatively, define a config file and use the `--config` argument to load it (`TOKEN` can be defined in the config file as well)

    ```
    usage: hpc_bot.py [-h] [-t TOKEN] [-n NICKNAME] [-a AVATAR] [-tc BOT_TEXT_CHANNEL] [-p COMMAND_PREFIX] [-l LOG] [-c CONFIG]

    Run hpc-bot discord Bot

    optional arguments:
      -h, --help            show this help message and exit
      -t TOKEN              Bot token. REQUIRED. Get one here: https://discordapp.com/developers/applications/me
      -n NICKNAME           Bot nickname. Default is computer host name (in this case: "My Computer")
      -a AVATAR             Bot avatar image path (only .jpeg or .png). Sets bot avatar. Ignoring this argument will leave your bot's avatar unchanged
      -tc BOT_TEXT_CHANNEL  Text channel where bot will send its messages. Default is "hpc-bots"
      -p COMMAND_PREFIX     Prefix string that indicates if a message sent by a user is a command. If omitted, only bot mentions will trigger command calls
      -l LOG                Log file path. If file exists, logs will be appended to it. Default is "./bot.log"
      -c CONFIG             Config file path. Bot parameters will be loaded from config file. Command line arguments take precedence over config parameters.
    ```

    `config` file structure (every parameter is optional):
    ```json
    {
      "token": "<BOT-TOKEN> (see https://discordapp.com/developers/applications/me')",
      "nickname": "<SERVER-NICKNAME>",
      "avatar": "<BOT-AVATAR-IMAGE-PATH>",
      "bot_text_channel": "<BOT-TEXT-CHANNEL>",
      "command_prefix": "<COMMAND_PREFIX>",
      "log": "<LOG-FILE-PATH>"
    }
    ```

5.  Run, using `systemd`

    `hpc-bot` has a `systemd` service file. You can use it to manage starting and stopping the bot.
    In order to use it you must first install `hpc-bot` as a module:

    ```shell script
    pip install --user .
    ```
  
    then create a config file like the one mentioned in `4.` under `~/.local/etc/hpc_bot/config`.
    You can then use `systemctl` to control how your bot starts:
    
    ```shell script
    systemctl --user start hpc-bot.service    # Starts the bot
    systemctl --user stop hpc-bot.service     # Stops the bot
    systemctl --user status hpc-bot.service   # Gets a short status summary of the bot
    systemctl --user enable hpc-bot.service   # Makes the bot startup whenever your user logs in
    ```
    
    In order to make the bot start whenever the system boots, you must enable `user-linger`:
    
    ```shell script
    loginctl enable-linger <username>
    ```
    
    This command must be run as `root`, and you have to replace `username` with the name of the user for whom the bot is installed.

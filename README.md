# hpc-bot
A repository to host code to build a discord bot

## Instructions
1. Clone repository
    ```shell script
    git clone https://github.com/CoBiG2/hpc-bot.git
    ```
   
2. Install python 3.8
    * Downloads [here](https://www.python.org/downloads/), installation instructions [here](https://docs.python.org/3.8/using/unix.html)
    * Alternatively, install to user space (on `Linux`) with [conda](https://docs.conda.io/projects/conda/en/latest/):
        ```shell script
        make install-conda
        make install-python
        ```

3. Install dependencies
    ```shell script
    make upgrade-pip
    make install-dependencies
    ```
3. Run

    Pass command line arguments as needed, `TOKEN` being the only one required (all others have defaults).
    Alternatively, define a config file inside the `config` folder and use the `--config` argument to load it (`TOKEN` can be defined in the config file as well)
    
    ```
    usage: hpc_bot.py [-h] [-t TOKEN] [-n NAME] [-a AVATAR] [-tc BOT_TEXT_CHANNEL] [-l LOG] [--config]

    Run hpc-bot discord Bot
    
    optional arguments:
      -h, --help            show this help message and exit
      -t TOKEN              Bot token. REQUIRED. Get one here: https://discordapp.com/developers/applications/me
      -n NAME               Bot name. Default is computer host name (in this case: "My Computer")
      -a AVATAR             Bot avatar image location (only .jpeg or .png). Sets bot avatar. Ignoring this argument will leave your bot's avatar unchanged
      -tc BOT_TEXT_CHANNEL  Text channel where bot will send its messages. Default is "hpc-bots"
      -l LOG                Log file location. If file exists, logs will be appended to it. Default is "./bot.log"
      --config              Use config file (located at hpc_bot/config/)
    ```
   
   `config` file structure (every parameter is optional):
   ```json
   {
      "token": "<BOT-TOKEN> (see https://discordapp.com/developers/applications/me')",
      "name": "<SERVER-NAME>",
      "avatar": "<BOT-AVATAR-IMAGE-PATH>",
      "bot_text_channel": "<BOT-TEXT-CHANNEL>",
      "log": "<LOG-FILE-PATH>"
   }
   ```

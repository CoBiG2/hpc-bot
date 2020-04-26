# hpc-bot
A repository to host code to build a discord bot

## Instructions
1. Clone repository
    ```shell script
    git clone https://github.com/CoBiG2/hpc-bot.git
    ```
   
2. Install python 3.8
    * Downloads [here](https://www.python.org/downloads/), installation instructions [here](https://docs.python.org/3.8/using/unix.html)
    * Alternatively, install to user space (on `Linux`) with:
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
    ```shell script
    python hpc_bot.py <bot_token>
    ```

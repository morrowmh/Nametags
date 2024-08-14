# Nametags
A Discord bot written in Python for managing user introductions
## Installation
For this installation example we'll assume we're using [Ubuntu 20.04.6 LTS](https://www.releases.ubuntu.com/focal/).

First of all, make sure you have [Python 3.12](https://linuxcapable.com/install-python-3-12-on-ubuntu-linux/) as well as [pip](https://stackoverflow.com/questions/6587507/how-to-install-pip-with-python-3).

Then make a new virtual environment using [venv](https://docs.python.org/3/library/venv.html):

```bash
python3.12 -m venv Nametags_Python3.12_Env
```

Now we can `cd` into our virtual environment, activate the environment and clone the repository:
```bash
cd Nametags_Python3.12_Env
source bin/activate
git clone https://github.com/morrowmh/Nametags
```

Now `cd` into the repository and install the required modules with `pip`:
```bash
cd Nametags
pip install -r requirements.txt
```

Finally, add your bot token to the `.env` file:
```bash
echo TOKEN=(your bot token) > .env
```

We are now ready to run our bot:
```bash
python bot.py
```

## Documentation

### User Commands
`/nametags help`: Display the list of commands and their purposes to the user.

`/nametags create`: Create a new nametag. Spawns a modal dialog for user input.

`/nametags update`: Update your existing nametag. Fails if no nametag exists. Spawns a modal dialog for user input and autofills fields with previous user data.

`/nametags view`: View a user's nametag. Has optional argument `user` which specifies the user whose nametag is to be viewed. If `user` is left blank, then `user` defaults to the user who ran this command.

`/nametags delete`: Delete your nametag if it exists.

## Admin Commands
`/nametags setup`: Setup the bot for your server. You must specify the `nametags_channel_id` for the channel in which nametags will be posted. You may also specify a `commands_channel_id` if you want to restrict bot commands to a certain channel. Leaving this option blank will result in "global" behavior, meaning bot commands can be ran from any channel. There are also optional arguments `require_age` and `require_location` which are booleans that determine whether age or location should be required when making a nametag.

`/nametags showconfig`: Display the current configuration for the server.
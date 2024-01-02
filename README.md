# memebot
Commands can be found [here](https://github.com/goeo-/memebot-2.0/wiki).

## Setting up
This bot runs on python3.8. An example of config.ini is as follows:
```
[irc]
host = irc.ppy.sh
nick = ilyt
password = CHANGEME
channels = osu, turkish
port = 6667

[bot]
prefix = !

[osu]
api_url = https://osu.ppy.sh/api/
api_key = CHANGEME
beatmap_url = https://osu.ppy.sh/b/

[sql]
db = memebot
host = 127.0.0.1
port = 3306
user = memebot
password = CHANGEME

[oppai]
map_dir = ./.memebot/maps
```

Make sure the directory for maps exists already.

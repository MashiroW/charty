# Charty - From the Marketing Dpt.
Charty is a statistics bot for your discord channel.
Give it a channel to watch and will upload to the chosen channel your daily statistics.
Charty also does the same for weekly statistics.

## Installation

### 1 - Clone the repository

```bash
git clone https://github.com/MashiroW/charty
```

### 2 - Install the python dependencies

You will need the package manager [pip](https://pip.pypa.io/en/stable/) to install the dependencies.

```bash
pip install -r requirements.txt
```

You can also choose do it manually 

```bash
pip install pandas
pip install numpy
pip install matplotlib
pip install datetime
pip install discord_webhook
```

### 3 - DiscordChatExporter

Some guy on Github named [Tyrrrz](https://github.com/Tyrrrz) did a very efficient script to retrieve the chats from a specific channel or server and we will need it here.
For that you will have to download the lastest [DiscordChatExporter.CLI.zip"](https://github.com/Tyrrrz/DiscordChatExporter/releases) and extract it inside the "./DiscordChatExtractor/" folder

### 4 - settings.json file

Create a file or fill the one already created with your informations and respect the following way:
```
{
    "token": "",                    
    "channel_ID": "",
    "webhook_url": "",
                                    
    "users_to_watch"  : [],         (you either specify a list of users to include in the stats using "users_to_watch"...)
    "users_to_ignore" : [],         (...or a list to exclude using "users_to_ignore" but DO NOT do both)

    "daily"  : true,                (set to 'false' if you don't want daily   plots)
    "weekly" : true,                (set to 'false' if you don't want weekly  plots)
    "monthly": true,                (set to 'false' if you don't want monthly plots)
    "yearly" : true,                (set to 'false' if you don't want yearly  plots)

    "textual_pie_chart" : true
}
```
([Where do I find the three first values ?](https://github.com/Tyrrrz/DiscordChatExporter/wiki/Obtaining-Token-and-Channel-IDs))

* ##### Q: How to I get someone's userID ?
* ##### A: Go to User Settings > Advanced > Enable Developer Mode. You will then be able to right click an user and click "Copy ID"

### 5 How this whole thing looks like once finished

```bash
.
├── dataset.csv                                             (will be created by the script)
├── DiscordChatExporter/
│   ├── CliFx.dll
│   ├── DiscordChatExporter.Cli.deps.json
│   ├── DiscordChatExporter.Cli.dll
│   ├── DiscordChatExporter.Cli.exe
│   ├── DiscordChatExporter.Cli.pdb
│   ├── DiscordChatExporter.Cli.runtimeconfig.json
│   ├── DiscordChatExporter.Core.dll
│   ├── DiscordChatExporter.Core.pdb
│   ├── Gress.dll
│   ├── JsonExtensions.dll
│   ├── MiniRazor.Runtime.dll
│   ├── Polly.dll
│   ├── Spectre.Console.dll
│   └── Superpower.dll
├── discord_stats_bot.py                                    (this is the script you should run)
├── logs.txt                                                (will be created by the script)
├── plots/                                                  (will be created by the script, same for what's inside)
│   ├── daily/                                                        
│   │   ├── 2022-02-28_day.png
│   │   ├── 2022-03-01_day.png
│   │   └── 2022-03-02_day.png
│   └── weekly/
│       └── 2022-02-22_week.png
├── README.md
├── requirements.txt                                        
└── settings.json                                           (where your user informations and settings for the script should be)

4 directories, 24 files
```

### 6 Preview 

[INSERT A PICTURE HERE IM TOO LAZY TO INSERT]


# About
Charty was coded in python (v3.7.3)


## License
[MIT](https://choosealicense.com/licenses/mit/)

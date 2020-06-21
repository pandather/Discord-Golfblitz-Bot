import os, sys
import json
import csv
import discord
global_bot = discord.Client()
bot_config = False
golfblitz_bot_details = {"userId": False}
safe_split_str = "SAFE_SPLIT"
configuration_path = os.path.join(sys.path[0], "configuration")
resources_path = os.path.join(sys.path[0], "resources")
extra_assets_path = os.path.join(resources_path, "extra_assets")
assets_path = os.path.join(resources_path, "assets")
if not os.path.exists(extra_assets_path):
    os.makedirs(extra_assets_path)
curr_season = -1
extraResponseCount = {"get_current_challenge": 1}
pending_requests = {}
group_configs_path = os.path.join(configuration_path, "group_configs.json")
group_configs = json.load(open(group_configs_path, 'r')) if os.path.isfile(group_configs_path) else {}
user_configs = {}
user_configs_path = os.path.join(configuration_path, "user_configs.json")
user_configs_file_content = open(user_configs_path, 'r').read() if os.path.isfile(user_configs_path) else ""
if user_configs_file_content:
    user_configs = json.loads(user_configs_file_content)
friendly_matches = {}
error_messages = {"insufficient_permissions":"Error: Insufficient Permissions\nYou do not have sufficient permissions to perform this operation.","no_associated_player_id": "Error: No Associated Player Id:\nThe command failed because there is no golf blitz player associated with this account!", "page_not_found": "Error: Page Not Found\nThe page you are requesting does not exist"}
command_data_path = os.path.join(sys.path[0], "command_data.json")
command_data = json.load(open(command_data_path, 'r')) if os.path.isfile(command_data_path) else {}
command_short_descriptions = {"getchallenge": "[-event <event_name>]", "help": "[-command <command name>]", "leaderboard": "[-count <number (max is 1000)>] [-country <country accronym>] [-offset <number>] [-season <number>] [-team]", "leaderboardstats": "same syntax as leaderboard", "listchallenges": "", "playerinfo": "[-code <friend code>] or [-id <player uuid>] or [-rank <number>] [-country <country>]", "setprefix": "-prefix <prefix str>", "teaminfo": "[-id <team id>] or [-name <team name>]", "verifyaccount": "-id <id of other client>"}
default_help_msg_head = "Golf Blitz Bot Help Page"
default_help_msg = '''Global Arguments:
* -disable_code_format (only has an effect on discord)
* -json (only works on discord)
* -pages <number or start_page-end_page or all>,<page_elem>,...

Commands:
'''
command_help_page = {
"getchallenge": ("getchallenge help page", '''Get 1v1 challenge event details for the current event or for a past event.
Usage: getchallenge [-event <event name>]
Arguments:
* event (optional) - the event name from listchallenges
'''),
"info": ("info help page", '''Display information about the bot.
Usage: info
Arguments: none
'''),
"help": ("help help page", '''Get detailed information about how to use a command.
Usage: help [-command <command>]
Arguments:
* command (optional) - the command that you want to get more detailed information about
'''),
"leaderboard": ("leaderboard help page", '''Get a leaderboard of teams or individuals that has up to 1000 entries.
Usage: leaderboard": "[-count <number (max is 1000)>] [-country <country accronym>] [-offset <number>] [-season <number>] [-team]
Command Aliases:
* ranks
Arguments (all are optional):
* count - the number of entries in the leaderboard
* country - get the leaderboard for a specified country using its two letter accronym
* offset - start the leaderboard entries after the given rank offset value
* season - which season this leaderboard applies to
* team - show the leaderboard for teams instead of the leaderboard for individual players
'''),
"leaderboardstats": ("leaderboardstats help page", '''Get the statistics for a given leaderboard selection.
See the leaderboard help page for usage specifications.
'''),
"listchallenges": ("listchallenges help page", '''Show the history of golf blitz 1v1 challenges that are stored on the bot sorted by time (newest at the top, oldest at the bottom).
Usage: listchallenges
Arguments: none
'''),
"ping": ("ping help page", '''Get a sense of the network latency for the golf blitz and discord parts of the bot
Usage: ping
Arguments: none
'''),
"playerinfo": ("playerinfo help page", '''Get very detailed information about a player
Usage: playerinfo [-code <friend code>] or [-id <player uuid>] or [-rank <number>] [-country <country>]
Arguments (you must specify the code, id, or rank):
* code - the player's friend code
* id - the player's uuid (should be 24 characters long)
* rank - the player's ranking in the leaderboard
* country - changes the leaderboard to the local leaderboard of the country specified (only works with the rank argument)
'''),
"setprefix": ("setprefix help page", '''Set the bot's command prefix for your group (you must have enough permissions to do so)
Usage: setprefix": "-prefix <prefix str>
Arguments:
* prefix - the string of the prefix
'''),
"teaminfo": ("teaminfo help page", '''Get detailed information about a team
Usage: teaminfo [-id <team id>] or [-name <team name>]
Arguments:
* id - the team's uuid (should be 24 characters long)
* name - the team's name
'''),
"verifyaccount": ("verifyaccount help page", '''Link up your golf blitz and discord accounts
Usage: verifyaccount -id <id of other client>
Arguments:
* id - if you are on discord, this is your golf blitz uuid.  if you are on golf blitz, this is your discord id.
''')
}
command_help_page["ranks"] = command_help_page["leaderboard"]
info_msg_head = "Golfblitz Bot Information Page"
info_msg = '''This bot was created by lighthouse64#5760.
prefix: {prefix}
Add this bot to your server by using this link: https://discord.com/api/oauth2/authorize?client_id=720685363026198532&permissions=67488832&scope=bot
You can also add the bot as a friend and send commands to it in a friendly lobby.  Its friend code is g33ykw.
The bot testing server is at https://discord.gg/eaddU2c
If you have any comments or concerns, contact me on discord.
'''
for command in command_short_descriptions:
    default_help_msg += "* " + command + " " + command_short_descriptions[command] + "\n"
strings = {}
hats = {}
golfers = {}
emotes = {}
powerups = {}
cardpacks = {}
def update_hats_and_golfers():
    global strings, hats, golfers, emotes, cardpacks
    string_paths = [os.path.join(assets_path, "strings.csv"), os.path.join(extra_assets_path, "emote_strings.csv"), os.path.join(extra_assets_path, "golfer_strings.csv"), os.path.join(extra_assets_path, "hat_strings.csv")]
    for path in string_paths:
        reader = csv.reader(open(path, 'r', encoding="utf-8"), delimiter=",")
        head = next(reader)
        for row in reader:
            strings[row[0]] = {}
            for i in range(1, len(row)):
                strings[row[0]][head[i]] = row[i]
    cardpacks = {1: strings["UI_PACK_TYPE_ONE"]["en"], 2: strings["UI_PACK_TYPE_TWO"]["en"], 3: strings["UI_PACK_TYPE_THREE"]["en"], 4: strings["UI_PACK_TYPE_FOUR"]["en"], 5: strings["UI_PACK_TYPE_FIVE"]["en"], 6: strings["UI_PACK_TYPE_SIX"]["en"], 7: strings["UI_PACK_TYPE_SEVEN"]["en"]} #pack type 6 is a star pack and 7 is a free pack
    base_paths = [os.path.join(assets_path, "emotesdata.json"), os.path.join(assets_path, "golfers.json"), os.path.join(assets_path, "hats.json"), os.path.join(assets_path, "cards.json"), os.path.join(extra_assets_path, "emotesdata.json"), os.path.join(extra_assets_path, "golfers.json"), os.path.join(extra_assets_path, "hats.json")]
    for path in base_paths:
        if os.path.isfile(path):
            partial = json.loads(open(path, 'r').read())
        outputDict = golfers
        if "hats" in path:
            outputDict = hats
        elif "emotes" in path:
            outputDict = emotes
            partial = partial["emotes"]
        elif "cards" in path:
            outputDict = powerups
        for id in partial:
            elem = partial[id]
            for key in elem:
                if type(elem[key]) is dict:
                    continue
                if elem[key] in strings:
                    elem[key] = strings[elem[key]]
            outputDict[id] = elem.copy()

if os.path.isdir(assets_path):
  update_hats_and_golfers()

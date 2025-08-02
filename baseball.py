from datetime import date, timedelta
import discord
import logging
from dotenv import load_dotenv
import os
import requests
from pymongo import MongoClient
import pandas as pd

load_dotenv()

token = os.getenv('DISCORD_TOKEN')
handler = logging.FileHandler(filename = 'discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = discord.Bot()
client = MongoClient("mongodb://localhost:27017/")
db = client["baseballbot"]
users = db["users"]

today = date.today().strftime('%Y-%m-%d')
yesterday = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
resp = requests.get(f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={today}")
schedule = resp.json()
games = True
if schedule['totalGames'] == 0:
    games = False

# url = f"https://statsapi.mlb.com/api/v1/game/{game_id}/linescore"
# response = requests.get(url)
# linescore = response.json()

# innings = linescore['innings']
# away_1st = innings[0]['away']['runs']
# home_1st = innings[0]['home']['runs']
# url = f"https://statsapi.mlb.com/api/v1/game/{game_id}/boxscore"
# response = requests.get(url)
# data = response.json()
# away_team = data['teams']['away']['team']['name']
# home_team = data['teams']['home']['team']['name']

# print(f"Away Team: {away_team}")
# print(f"Home Team: {home_team}")

# print(f"Away team runs in 1st inning: {away_1st}")
# print(f"Home team runs in 1st inning: {home_1st}")
# print(f"Total runs in 1st inning: {away_1st + home_1st}")

#################HELPERS#####################

def update_user(user_id, roster):
    users.update_one(
        {"_id": user_id}, 
        {"$setOnInsert": 
            {"roster": {
                "active": [
                    {"slot": 1, "player_id": None, "position": None},
                    {"slot": 2, "player_id": None, "position": None},
                    {"slot": 3, "player_id": None, "position": None},
                    {"slot": 4, "player_id": None, "position": None},
                    {"slot": 5, "player_id": None, "position": None},
                    {"slot": 6, "player_id": None, "position": None},
                    {"slot": 7, "player_id": None, "position": None},
                    {"slot": 8, "player_id": None, "position": None},
                    {"slot": 9, "player_id": None, "position": None}
                ],
                "inactive": [
                ]
                }
            }
        }, 
        upsert=True
    )
    for doc in users.find():
        print(doc)
    return True

def harvest_players():
    team_url = "https://statsapi.mlb.com/api/v1/teams?sportId=1"
    team_data = requests.get(team_url).json()
    team_data = pd.DataFrame(team_data)
    for team in team_data["teams"]:
        team_id = team["id"]
        roster_url = f"https://statsapi.mlb.com/api/v1/teams/{team_id}/roster/40Man"
        roster_data = requests.get(roster_url).json()
        if team["name"] == "New York Yankees":
            for x in roster_data.get("roster", []):
                print(x["person"]["id"])
    pass

##################COMMANDS###################

@bot.event
async def on_ready():
    print(f"I'm {bot.user.name}")

@bot.slash_command(name = "live-games", description="Show me what games are on right now.")
async def live_games(ctx: discord.ApplicationContext):
    msg = ''
    if not games:
        await ctx.respond('There are no games today.')
    else:
        for x in schedule['dates'][0]['games']:
            game_id = x['gamePk']
            url = f"https://statsapi.mlb.com/api/v1/game/{game_id}/boxscore"
            response = requests.get(url)
            data = response.json()
            away_team = data['teams']['away']['team']['name']
            home_team = data['teams']['home']['team']['name']
            msg += (f"{away_team} at {home_team}\n")
        await ctx.respond(msg)

@bot.slash_command(name = "add-user", description="Add me as a player.")
async def add_user(ctx: discord.ApplicationContext):
    if update_user(ctx.author.id, True):
        await ctx.respond(f"Successfully added {ctx.author.mention} as a player")

@bot.slash_command(name = "lineup", description="Show player's active batting order.")
async def lineup(ctx: discord.ApplicationContext, player: discord.User = None):
    if player is None:
        player = ctx.author.id
        curr = users.find_one({"_id": player})
        for x in curr["roster"]["active"]:
            print(x["player_id"])
    else:
        pass

@bot.slash_command(name = "test", description="Test command to check bot functionality.")
async def test(ctx: discord.ApplicationContext):
    harvest_players()
          


harvest_players()

bot.run(token)

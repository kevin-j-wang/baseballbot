from datetime import date, timedelta
import discord
import logging
from dotenv import load_dotenv
import os
import requests
from pymongo import MongoClient

load_dotenv()

token = os.getenv('DISCORD_TOKEN')
handler = logging.FileHandler(filename = 'discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = discord.Bot()
client = MongoClient("mongodb://localhost:27017/")
db = client["user_data"]
users = db["users"]

today = date.today().strftime('%Y-%m-%d')
yesterday = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
curr_date = '2025-07-01'
resp = requests.get(f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={today}")
schedule = resp.json()
game_id = schedule['dates'][0]['games'][0]['gamePk']

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

def update_user(user_id, roster):
    users.update_one({"_id": user_id}, {"$set": {"1": "Shohei Ohtani"}}, upsert=True)
    for doc in users.find():
        print(doc)

@bot.event
async def on_ready():
    print(f"I'm {bot.user.name}")

@bot.slash_command(name = "live-games", description="Show me what games are on right now.")
async def live_games(ctx: discord.ApplicationContext):
    print(ctx.author)
    print(ctx.author.id)
    update_user(ctx.author.id, True)
    for x in schedule['dates'][0]['games']:
            game_id = x['gamePk']
            url = f"https://statsapi.mlb.com/api/v1/game/{game_id}/boxscore"
            response = requests.get(url)
            data = response.json()
            away_team = data['teams']['away']['team']['name']
            home_team = data['teams']['home']['team']['name']
            await ctx.message(f"{away_team} at {home_team}")

@bot.slash_command(name = "add-user", description="Add me as a player.")
async def add_user(ctx: discord.ApplicationContext):
    print(ctx.author)
    print(ctx.author.id)

bot.run(token)

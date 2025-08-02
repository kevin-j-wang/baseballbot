from datetime import date, timedelta
import os
import requests
from pymongo import MongoClient
import pandas as pd

base_url = "https://statsapi.mlb.com/"

today = date.today().strftime('%Y-%m-%d')
yesterday = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
resp = requests.get(f"{base_url}api/v1/schedule?sportId=1&date={today}")
schedule = resp.json()
games = True
if schedule['totalGames'] == 0:
    games = False

team_url = f"{base_url}api/v1/teams?sportId=1"
team_data = requests.get(team_url).json()
team_data = pd.DataFrame(team_data)
# for team in team_data["teams"]:
#     team_id = team["id"]
#     roster_url = f"https://statsapi.mlb.com/api/v1/teams/{team_id}/roster/40Man"
#     roster_data = requests.get(roster_url).json()
#     if team["name"] == "New York Yankees":
#         for x in roster_data.get("roster", []):
#             print(x["person"]["id"])

team_id = 147  #New York Yankees

games_url = f"{base_url}api/v1/schedule?teamId={team_id}&season=2024&sportId=1"
games_data = requests.get(games_url).json()
games_data = pd.json_normalize(games_data['dates'])
games_data['date'] = pd.to_datetime(games_data['date'])
cutoff_date = pd.to_datetime("2024-03-28")

df = (games_data[games_data['date'] > cutoff_date]['games'])
df = df.apply(pd.json_normalize)
df = pd.concat(df.tolist(), ignore_index=True)

df = df[['link', 'teams.home.team.name', 'teams.away.team.name']]
df = df.rename(columns={
    'teams.home.team.name': 'home_team',
    'teams.away.team.name': 'away_team'
})
for url_tail in df['link']:
    url = f'{base_url}{url_tail}'
    response = requests.get(url)
    away_data = (response.json()['liveData']['boxscore']['teams']['away'])
    print(pd.json_normalize(away_data['info'][0]['fieldList']))
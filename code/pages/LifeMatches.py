import streamlit as st
import pandas as pd
from numpy import nan
import requests
import json
import os

key = '3A65F973BAF1C8130DCD77B739C74EC9'

with open(os.path.abspath("data/teams_dict.txt"), 'r', encoding='utf-8') as file:
    teams_dict = eval(file.read())

with open(os.path.abspath("data/teamid_stats.txt"), 'r', encoding='utf-8') as file:
    teamid_stats = eval(file.read())

teams_list = list(teams_dict.keys())

r_steam = requests.get(f'https://api.steampowered.com/IDOTA2Match_570/GetLiveLeagueGames/v1/?key={key}')
live_games = json.loads(r_steam.text)

life_df = pd.json_normalize(live_games['result']['games'])

life_df = life_df[['match_id', 'radiant_team.team_name', 'radiant_team.team_id', 'dire_team.team_id'
                    , 'dire_team.team_name']]
life_df = life_df[['radiant_team.team_id', 'dire_team.team_id']].apply(int)

st.dataframe(life_df)

cool_teams = [int(t) for t in life_df['dire_team.team_id'].tolist() if t in teams_list]

st.dataframe(life_df[life_df['dire_team.team_id'].isin(cool_teams)])
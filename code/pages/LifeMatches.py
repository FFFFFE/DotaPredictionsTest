import streamlit as st
import pandas as pd
from numpy import nan
import requests
import json
import os


def make_predict_upd(rad_team, dire_team):
    rad_team_id, dire_team_id = teams_dict[rad_team], teams_dict[dire_team]

    teams_rating_ratio = teamid_stats[rad_team_id][0] / teamid_stats[dire_team_id][0]
    wr_ratio = teamid_stats[rad_team_id][2] - teamid_stats[dire_team_id][2]
    new_match = [teams_rating_ratio, wr_ratio]

    # 1 - radiant_win, 0 - dire_win
    predict = clf.predict(new_match)
    probability = clf.predict(new_match, prediction_type='Probability')
    return predict, probability


steam_key = st.secrets['steam_key']

with open(os.path.abspath("data/teams_dict.txt"), 'r', encoding='utf-8') as file:
    teams_dict = eval(file.read())

with open(os.path.abspath("data/teamid_stats.txt"), 'r', encoding='utf-8') as file:
    teamid_stats = eval(file.read())

teams_id_list = list(teamid_stats.keys())

r_steam = requests.get(f'https://api.steampowered.com/IDOTA2Match_570/GetLiveLeagueGames/v1/?key={steam_key}')
live_games = json.loads(r_steam.text)

life_df = pd.json_normalize(live_games['result']['games'])
life_df = life_df[['match_id', 'radiant_team.team_name', 'radiant_team.team_id', 'dire_team.team_name', 'dire_team.team_id']]
life_df = life_df.rename(columns={'radiant_team.team_name': 'radiant_team', 'dire_team.team_name': 'dire_team',
                        'radiant_team.team_id': 'rad_team_id', 'dire_team.team_id': 'dire_team_id'})
life_df.dropna(inplace=True)

life_df[['rad_team_id', 'dire_team_id']] = life_df[['rad_team_id', 'dire_team_id']].astype('int64')
life_df.reset_index(drop=True, inplace=True)


cool_teams_1 = [t for t in life_df['rad_team_id'].tolist() if t in teams_id_list]
cool_teams_2 = [t for t in life_df['dire_team_id'].tolist() if t in teams_id_list]
cool_teams = set(cool_teams_1).union(set(cool_teams_2))

st.dataframe(life_df[(life_df['rad_team_id'].isin(cool_teams)) &
             (life_df['dire_team_id'].isin(cool_teams))][['match_id', 'radiant_team', 'dire_team']])
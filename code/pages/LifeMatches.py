import streamlit as st
import pandas as pd
from numpy import nan
from catboost import CatBoostClassifier
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


from_file = CatBoostClassifier()
clf = from_file.load_model(os.path.abspath("data/model_eval.cbm"))

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

filtered_df = life_df[(life_df['rad_team_id'].isin(teams_id_list)) & (life_df['dire_team_id'].isin(teams_id_list))]
filtered_df.reset_index(drop=True, inplace=True)

filtered_df[['winner_predict', 'probability']] = filtered_df.apply(lambda x: make_predict_upd(x['radiant_team'],
                                                                                      x['dire_team']), axis=1).tolist()
filtered_df['winner_predict'] = filtered_df['winner_predict'].apply(lambda x: ["dire_team", "radiant_team"][x])
filtered_df['probability'] = filtered_df['probability'].apply(lambda x: round(max(x), 4))

filtered_df['test_column'] = filtered_df.apply(lambda x: x["dire_team")

st.markdown('## Матчи, идущие в настоящий момент')
st.dataframe(filtered_df[['match_id', 'radiant_team', 'dire_team', 'winner_predict', 'probability']])

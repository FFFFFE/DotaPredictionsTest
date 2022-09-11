import pandas as pd
import numpy as np
import joblib
from catboost import CatBoostClassifier
import os
from numpy import nan

teams_scaller = joblib.load(os.path.abspath("data/teams_scaller.save"))

from_file = CatBoostClassifier()
clf = from_file.load_model(os.path.abspath("data/domi_last_patch"), format='cbm')

with open(os.path.abspath("data/heroes_dict.txt"), 'r') as file:
    heroes_dict = eval(file.read())

with open(os.path.abspath("data/teams_dict.txt"), 'r', encoding='utf-8') as file:
     teams_dict = eval(file.read())

with open(os.path.abspath("data/teamid_stats.txt"), 'r', encoding='utf-8') as file:
    teamid_stats = eval(file.read())


def make_predict(rad_pick, dire_pick, rad_team, dire_team, patch=51):
     picks_lst = [heroes_dict[i] for i in rad_pick] + [heroes_dict[i] for i in dire_pick]

     rad_team_id, dire_team_id = teams_dict[rad_team], teams_dict[dire_team]

     team_stats = teams_scaller.transform([list(teamid_stats[rad_team_id][:2] + teamid_stats[dire_team_id][:2])])[0]

     cols = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'rad_team_id', 'dire_team_id', 'rad_rating',
             'rad_matches_cnt',	'dire_rating',	'dire_matches_cnt',	'patch']
     int_cols = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'rad_team_id', 'dire_team_id', 'patch']

     new_match = pd.DataFrame(np.array([picks_lst + [rad_team_id] + [dire_team_id] + list(team_stats) + [patch]])
                              , columns=cols)
     new_match[int_cols] = new_match[int_cols].apply(int)

     # 1 - radiant_win, 0 - dire_win
     predict = clf.predict(new_match)[0]
     probability = clf.predict(new_match, prediction_type='Probability')[0]

     return predict, probability
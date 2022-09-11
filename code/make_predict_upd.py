import pandas as pd
import numpy as np
import joblib
from catboost import CatBoostClassifier
import os
from numpy import nan

teams_scaller = joblib.load(os.path.abspath("data/teams_scaller.save"))

from_file = CatBoostClassifier()
clf = from_file.load_model(os.path.abspath("data/domi_last_patch"), format='cbm')


with open(os.path.abspath("data/teams_dict.txt"), 'r', encoding='utf-8') as file:
     teams_dict = eval(file.read())

with open(os.path.abspath("data/teamid_stats.txt"), 'r', encoding='utf-8') as file:
    teamid_stats = eval(file.read())


def make_predict(rad_team, dire_team):
     team_stats = teams_scaller.transform([list(teamid_stats[rad_team_id] + teamid_stats[dire_team_id])])[0]
     new_match = pd.DataFrame(list(team_stats))

     # 1 - radiant_win, 0 - dire_win
     predict = clf.predict(new_match)[0]
     probability = clf.predict(new_match, prediction_type='Probability')[0]

     return predict, probability


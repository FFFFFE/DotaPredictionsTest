import pandas as pd
import numpy as np
import joblib
from catboost import CatBoostClassifier
import os
from numpy import nan

from_file = CatBoostClassifier()
clf = from_file.load_model(os.path.abspath("data/model_eval.cbm"))


with open(os.path.abspath("data/teams_dict.txt"), 'r', encoding='utf-8') as file:
     teams_dict = eval(file.read())

with open(os.path.abspath("data/teamid_stats.txt"), 'r', encoding='utf-8') as file:
    teamid_stats = eval(file.read())


def make_predict_upd(rad_team, dire_team):
     rad_team_id, dire_team_id = teams_dict[rad_team], teams_dict[dire_team]
     new_match = [teamid_stats[rad_team_id][2]] + [teamid_stats[dire_team_id][2]]

     # 1 - radiant_win, 0 - dire_win
     predict = clf.predict(new_match)
     probability = clf.predict(new_match, prediction_type='Probability')[0]

     return predict, probability
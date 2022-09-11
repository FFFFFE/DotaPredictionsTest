import streamlit as st
from numpy import nan
from catboost import CatBoostClassifier
import os

with open(os.path.abspath("data/teams_dict.txt"), 'r', encoding='utf-8') as file:
    teams_dict = eval(file.read())

with open(os.path.abspath("data/teamid_stats.txt"), 'r', encoding='utf-8') as file:
    teamid_stats = eval(file.read())

from_file = CatBoostClassifier()
clf = from_file.load_model(os.path.abspath("data/model_eval.cbm"))

def make_predict_upd(rad_team, dire_team):
    rad_team_id, dire_team_id = teams_dict[rad_team], teams_dict[dire_team]

    new_match = [teamid_stats[rad_team_id][2]] + [teamid_stats[dire_team_id][2]]

    # 1 - radiant_win, 0 - dire_win
    predict = clf.predict(new_match)
    probability = clf.predict(new_match, prediction_type='Probability')[0]
    return predict, probability


teams_list = list(teams_dict.keys())

with st.container():
    st.write("---")
    left_column, right_column = st.columns(2)
    with left_column:
        rad_team = st.selectbox("Команда Radiant: ", teams_list[0:2:-1] + teams_list[2:])

    with right_column:
        dire_team = st.selectbox("Команда Dire: ", teams_list)

    if (st.button("Сделать предсказание")):
        is_rad_win, probability = make_predict_upd(rad_team, dire_team)
        probability = round(max(probability) * 100)
        winner = [f'Победит команда {dire_team} ({probability}%)',
                       f'Победит команда {rad_team} ({probability}%)'][is_rad_win]
         st.success(winner)

import streamlit as st
from numpy import nan
from catboost import CatBoostClassifier
from streamlit_lottie import st_lottie
import requests
import os


def make_predict_upd(rad_team, dire_team):
    rad_team_id, dire_team_id = teams_dict[rad_team], teams_dict[dire_team]

    new_match = [teamid_stats[rad_team_id][2]] + [teamid_stats[dire_team_id][2]]

    # 1 - radiant_win, 0 - dire_win
    predict = clf.predict(new_match)
    probability = clf.predict(new_match, prediction_type='Probability')
    return predict, probability


def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


lottie_coding = load_lottieurl("https://assets2.lottiefiles.com/packages/lf20_7gxfokzr.json")

with open(os.path.abspath("data/teams_dict.txt"), 'r', encoding='utf-8') as file:
    teams_dict = eval(file.read())

with open(os.path.abspath("data/teamid_stats.txt"), 'r', encoding='utf-8') as file:
    teamid_stats = eval(file.read())

from_file = CatBoostClassifier()
clf = from_file.load_model(os.path.abspath("data/model_eval.cbm"))

teams_list = list(teams_dict.keys())


with st.container():
    left_column, right_column = st.columns(2)
    with left_column:
        st.write('##')
        st.markdown("## Предсказание матчей Dota 2 🎮")
        st.write("Выберите команды, чтобы получить прогноз")
    with right_column:
        st_lottie(lottie_coding, height=250, key="coding")

with st.container():
    # st.write("---")
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

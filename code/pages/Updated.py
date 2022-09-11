import streamlit as st
from numpy import nan
import os
import make_predict_upd

with open(os.path.abspath("data/heroes_dict.txt"), 'r') as file:
    heroes_dict = eval(file.read())

with open(os.path.abspath("data/teams_dict.txt"), 'r', encoding='utf-8') as file:
    teams_dict = eval(file.read())

with open(os.path.abspath("data/teamid_stats.txt"), 'r', encoding='utf-8') as file:
    teamid_stats = eval(file.read())

teams_list = list(teams_dict.keys())

with st.container():
    st.write("---")
    left_column, right_column = st.columns(2)
    with left_column:
        rad_team = st.selectbox("Команда Radiant: ", teams_list[0:2:-1] + teams_list[2:])

    with right_column:
        dire_team = st.selectbox("Команда Dire: ", teams_list)

    if (st.button("Сделать предсказание")):
        st.write(str(make_predict_upd.make_predict_upd(rad_team, dire_team)))

        # is_rad_win, probability = make_predict_upd.make_predict_upd(rad_team, dire_team)
        # probability = round(max(probability) * 100)
        # winner = [f'Победит команда {dire_team} ({probability}%)',
        #               f'Победит команда {rad_team} ({probability}%)'][is_rad_win]
        # st.success(winner)

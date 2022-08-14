import streamlit as st
import requests
from streamlit_lottie import st_lottie
import make_predict
from numpy import nan

#streamlit run streamlit.py

def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_coding = load_lottieurl("https://assets9.lottiefiles.com/packages/lf20_iv4dsx3q.json")

with open(r".\data\heroes_dict.txt", 'r') as file:
    heroes_dict = eval(file.read())

with open(r".\data\teams_dict.txt", 'r', encoding='utf-8') as file:
     teams_dict = eval(file.read())

with open(r".\data\teamid_stats.txt", 'r', encoding='utf-8') as file:
    teamid_stats = eval(file.read())

heroes_list = list(heroes_dict.keys())
teams_list = list(teams_dict.keys())
tundra_list = teams_list.copy()

teams_list.remove('OG')
tundra_list.remove('Tundra Esports')
teams_list = ['OG'] + teams_list
tundra_list = ['Tundra Esports'] + tundra_list


with st.container():
    left_column, right_column = st.columns(2)
    with left_column:
        st.markdown("# Предсказание матчей Dota 2")
        st.write("В форме ниже введите информормацию по матчу, чтобы получить прогноз")
    with right_column:
        st_lottie(lottie_coding, height=250, key="coding")

with st.container():
    st.write("---")
    left_column, right_column = st.columns(2)
    with left_column:
        rad_team = st.selectbox("Radiant team name: ", teams_list)
        rad_pick = st.multiselect("Choose 5 heroes for Radiant team: ", heroes_list,
                       ['Void Spirit', 'Jakiro', 'Batrider', 'Weaver', 'Enigma'])

    with right_column:
        dire_team = st.selectbox("Dire team name: ", tundra_list)
        dire_pick = st.multiselect("Choose 5 heroes for Dire team: ", heroes_list,
                                   ['Io', 'Razor', 'Zeus', 'Lycan', 'Doom'])

    is_rad_win = make_predict.make_predict(rad_pick, dire_pick, rad_team, dire_team)
    winner = [f'Победит команда {dire_team}', f'Победит команда {rad_team}'][is_rad_win]

    if(st.button("Сделать предсказание")):
        st.success(winner)


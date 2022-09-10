import streamlit as st

with open(os.path.abspath("data/heroes_dict.txt"), 'r') as file:
    heroes_dict = eval(file.read())

with open(os.path.abspath("data/teams_dict.txt"), 'r', encoding='utf-8') as file:
     teams_dict = eval(file.read())

with open(os.path.abspath("data/teamid_stats.txt"), 'r', encoding='utf-8') as file:
    teamid_stats = eval(file.read())

teams_list = list(teams_dict.keys())
tundra_list = teams_list.copy()


teams_list.remove('OG')
tundra_list.remove('Tundra Esports')
teams_list = ['OG'] + teams_list
tundra_list = ['Tundra Esports'] + tundra_list

with st.container():
    st.write("---")
    left_column, right_column = st.columns(2)
    with left_column:
        rad_team = st.selectbox("Команда Radiant: ", teams_list)

    with right_column:
        dire_team = st.selectbox("Команда Dire: ", tundra_list)

    if (st.button("Сделать предсказание")):
        st.write('Ещё не 17:19')


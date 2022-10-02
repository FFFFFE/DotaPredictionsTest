import streamlit as st
import pandas as pd
from numpy import nan
from catboost import CatBoostClassifier
from streamlit_lottie import st_lottie
import requests
import json
import os


def make_predict_upd(rad_team, dire_team):
    rad_team_id, dire_team_id = teams_dict[rad_team], teams_dict[dire_team]

    teams_rating_ratio = teamid_stats[rad_team_id][0] / teamid_stats[dire_team_id][0]
    wr_ratio = teamid_stats[rad_team_id][2] - teamid_stats[dire_team_id][2]
    new_match = [teams_rating_ratio, wr_ratio]
    # 1 - radiant_win, 0 - dire_win
    probability = round(max(clf.predict(new_match, prediction_type='Probability')), 4)
    return clf.predict(new_match), probability

def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


lottie_error = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_bhw1ul4g.json")


from_file = CatBoostClassifier()
clf = from_file.load_model(os.path.abspath("data/model_eval.cbm"))

steam_key = st.secrets['steam_key']

with open(os.path.abspath("data/teams_dict.txt"), 'r', encoding='utf-8') as file:
    teams_dict = eval(file.read())

with open(os.path.abspath("data/teamid_stats.txt"), 'r', encoding='utf-8') as file:
    teamid_stats = eval(file.read())

teams_id_list = list(teamid_stats.keys())

r_steam = requests.get(f'https://api.steampowered.com/IDOTA2Match_570/GetLiveLeagueGames/v1/?key={steam_key}')

if r_steam.status_code != 200:
    st.error(f'Ошибка {r_steam.status_code}. Попробуйте перезагрузить страницу')
else:
    live_games = json.loads(r_steam.text)
    live_df = pd.json_normalize(live_games['result']['games'])
    important_cols = ['match_id', 'radiant_team.team_name', 'radiant_team.team_id', 'dire_team.team_name',
                      'dire_team.team_id']

    if len(set(important_cols) - set(live_df.columns)) != 0:
        st.error('Перезагрузите страницу')
        st_lottie(lottie_error, height=250, key="coding")
    else:
        st.markdown('## Матчи, идущие в настоящий момент')
        st_lottie(lottie_error, height=250, key="coding")

        live_df = live_df[important_cols]
        live_df = live_df.rename(columns={'radiant_team.team_name': 'radiant_team', 'dire_team.team_name': 'dire_team',
                                    'radiant_team.team_id': 'rad_team_id', 'dire_team.team_id': 'dire_team_id'})
        live_df.dropna(inplace=True)
        live_df[['rad_team_id', 'dire_team_id']] = live_df[['rad_team_id', 'dire_team_id']].astype('int64')

        filtered_df = live_df[(live_df['rad_team_id'].isin(teams_id_list)) & (live_df['dire_team_id'].isin(teams_id_list))]
        filtered_df.reset_index(drop=True, inplace=True)
        if len(filtered_df) == 0:
            st.info('Сейчас нет онлайн профессиональных матчей')
        else:
            filtered_df[['winner_side', 'probability']] = filtered_df.apply(lambda x: make_predict_upd(x['radiant_team'],
                                                                                        x['dire_team']), axis=1).tolist()
            filtered_df['winner_side'] = filtered_df['winner_side'].apply(lambda x: ["dire_team", "radiant_team"][int(x)])

            filtered_df['winner_predict'] = filtered_df.apply(lambda x: ([x['radiant_team'], x['dire_team']]
                                                                    [x['winner_side'] == 'dire_team']), axis=1).tolist()

            st.dataframe(filtered_df[['match_id', 'radiant_team', 'dire_team', 'winner_predict', 'probability']])

        st.write('##')
        st.markdown('### Что здесь происходит?')
        st.markdown('- Получаю из Steam API онлайн идущие матчи')
        st.markdown('- Делаю для них предсказание победителя с помощью предобученой модели')
        st.markdown('- Публикую прогноз в телеграм канал')
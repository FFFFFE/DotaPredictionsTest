#!/usr/bin/env python
# coding: utf-8

# In[196]:


import requests
import json
import os
import pandas as pd
from catboost import CatBoostClassifier
from numpy import nan
import numpy as np


# In[197]:


pd.options.mode.chained_assignment = None  # default='warn'


# # 1. Импорт и обработка данных

# ## 1.1. Датафрейм

# In[198]:


key = '3A65F973BAF1C8130DCD77B739C74EC9'


# In[199]:


r_steam = requests.get(f'https://api.steampowered.com/IDOTA2Match_570/GetLiveLeagueGames/v1/?key={key}')
live_games = json.loads(r_steam.text)


# In[200]:


life_df = pd.json_normalize(live_games['result']['games'])


# In[201]:


life_df['map_cnt'] = life_df['radiant_series_wins'] + life_df['dire_series_wins'] + 1


# In[202]:


important_cols = ['match_id', 'radiant_team.team_name', 'radiant_team.team_id', 'dire_team.team_name', 
                  'dire_team.team_id', 'map_cnt']


# In[203]:


# Есть так же инфа по героям
life_df = life_df[important_cols]


# In[204]:


# Переименуем столбцы
life_df = life_df.rename(columns={'radiant_team.team_name': 'radiant_team', 'dire_team.team_name': 'dire_team',
                                    'radiant_team.team_id': 'rad_team_id', 'dire_team.team_id': 'dire_team_id'})


# In[205]:


# Избавимся от пропусков и приведем столбцы к нужному типу
life_df.dropna(inplace=True)
life_df[['rad_team_id', 'dire_team_id']] = life_df[['rad_team_id', 'dire_team_id']].astype('int64')
life_df.reset_index(drop=True, inplace=True)


# In[206]:


life_df


# ## 1.2. Справочники и модель

# In[207]:


from_file = CatBoostClassifier()
clf = from_file.load_model(os.path.abspath(r"C:\Users\Admin\PycharmProjects\DotaWinnerPrediction\data\model_eval.cbm"))


# In[208]:


def make_predict_upd(rad_team, dire_team):
    rad_team_id, dire_team_id = teams_dict[rad_team], teams_dict[dire_team]

    teams_rating_ratio = teamid_stats[rad_team_id][0] / teamid_stats[dire_team_id][0]
    wr_ratio = teamid_stats[rad_team_id][2] - teamid_stats[dire_team_id][2]
    new_match = [teams_rating_ratio, wr_ratio]
    # 1 - radiant_win, 0 - dire_win
    probability = round(max(clf.predict(new_match, prediction_type='Probability')), 4)
    return clf.predict(new_match), probability


# In[209]:


with open(os.path.abspath(r"C:\Users\Admin\PycharmProjects\DotaWinnerPrediction\data\teamid_stats.txt"),
          'r', encoding='utf-8') as file:
    teamid_stats = eval(file.read())


# In[210]:


with open(os.path.abspath(r"C:\Users\Admin\PycharmProjects\DotaWinnerPrediction\data\teams_dict.txt"),
          'r', encoding='utf-8') as file:
    teams_dict = eval(file.read())


# In[211]:


teams_id_list = list(teamid_stats.keys())


# # 2. Предикт

# ## 2.1 Филтруем матчи

# In[212]:


filtered_df = life_df[(life_df['rad_team_id'].isin(teams_id_list)) & (life_df['dire_team_id'].isin(teams_id_list))]
filtered_df.reset_index(drop=True, inplace=True)


# In[213]:


if len(filtered_df) == 0:
    print('Сейчас нет онлайн профессиональных матчей')
else:
    filtered_df[['winner_side', 'probability']] = filtered_df.apply(lambda x: make_predict_upd(x['radiant_team'],
                                                                                        x['dire_team']), axis=1).tolist()
    filtered_df.loc[:, 'winner_side'] = filtered_df['winner_side'].apply(lambda x: ["dire_team", "radiant_team"][int(x)])
    filtered_df.loc[:, 'winner_predict'] = filtered_df.apply(lambda x: ([x['radiant_team'], x['dire_team']]
                                                                    [x['winner_side'] == 'dire_team']), axis=1).tolist()


# Создадим для будущего результата матча
filtered_df['fact_result'] = 'noresult'

# Импортируем archive.csv
archive = pd.read_csv(r"C:\Users\Admin\PycharmProjects\DotaWinnerPrediction\data\archive.csv")


# Для загрузки в архив выберем только те матчи, которых нет в archive.csv
new_matches = filtered_df[~filtered_df['match_id'].isin(archive['match_id'].tolist())]



# Объединим новое со старым
merged = pd.concat([archive, new_matches]).reset_index(drop=True)


# ## 2.2 Обновим результаты матчей


def define_winner(match_id):
    response = requests.get('https://api.opendota.com/api/matches/' + str(match_id))
    data = response.json()
    if 'radiant_win' not in data.keys():
        return 'noresult'
    winner = ['dire_team', 'radiant_team'][int(data['radiant_win'])]
    return winner


merged['fact_result'] = merged[['match_id', 'fact_result']].apply((lambda x: define_winner(x['match_id']) 
                                                            if x['fact_result'] == 'noresult' else x['fact_result']), axis=1)


# Перезапишем archive.csv
merged.to_csv(r"C:\Users\Admin\PycharmProjects\DotaWinnerPrediction\data\archive.csv", index=False)


# # 3. Публикация в телеграм


def send_telegram(text: str):
    token = "5447729429:AAF9yxTlohAx75qvtd5gv3mknhRS8xuQ-ts"
    url = "https://api.telegram.org/bot"
    channel_id = "@betsrenaissance"
    url += token
    method = url + "/sendMessage"

    r = requests.post(method, data={
         "chat_id": channel_id,
         "text": text,
         "parse_mode": 'Markdown'
          })

    if r.status_code != 200:
        raise Exception("post_text error")



# Список уже опубликованных матчей
with open(r"C:\Users\Admin\PycharmProjects\DotaWinnerPrediction\data\published.txt", 'r') as file:
    published = eval(file.read())


# In[224]:


# Незавершившиеся матчи
noresult = merged[merged['fact_result'] == 'noresult']


# In[225]:


# Неопубликованные незавершившиеся матчи
not_posted = noresult[~noresult['match_id'].isin(published)]

# Фильтр команд которых нет в бк
not_in_bk = ['celestials', 'ninfaw', 'eye-gaming', 'others', 'deep ravage', 'rakuzan', 'shinigami gaming']

for i in not_posted.index:
    if not_posted.loc[i, 'radiant_team'].lower() and not_posted.loc[i, 'dire_team'].lower() not in not_in_bk:
        new_message = f"""*{not_posted.loc[i, 'radiant_team']} - {not_posted.loc[i, 'dire_team']}*
`ID матча: {not_posted.loc[i, 'match_id']}
Карта: {not_posted.loc[i, 'map_cnt']}`
`Прогноз:` *{not_posted.loc[i, 'winner_predict']}*"""
        send_telegram(new_message)
        published.append(not_posted.loc[i, 'match_id'])



with open(r"C:\Users\Admin\PycharmProjects\DotaWinnerPrediction\data\published.txt", 'w') as file:
    file.write(str(published))


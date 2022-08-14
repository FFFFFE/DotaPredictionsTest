import pandas as pd

df = pd.read_csv("/data/generaldf2.csv")

teams_to_id = dict(zip(df['rad_team_name'].tolist(), df['rad_team_id'].tolist()))
teams_to_id.update(dict(zip(df['dire_team_name'].tolist(), df['dire_team_id'].tolist())))

teamid_to_stats = dict(zip(df['rad_team_id'].tolist(),
                           list(df[['rad_rating', 'rad_matches_cnt']].itertuples(index=False, name=None))))
teamid_to_stats.update(dict(zip(df['dire_team_id'].tolist(),
                           list(df[['dire_rating', 'dire_matches_cnt']].itertuples(index=False, name=None)))))


with open("/data/teams_dict.txt", 'w', encoding='utf-8') as file:
    file.write(str(teams_to_id))

with open("/data/teamid_stats.txt", 'w', encoding='utf-8') as file:
    file.write(str(teamid_to_stats))
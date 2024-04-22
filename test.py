
from nba_api.stats.endpoints import leagueleaders
import pandas as pd
import config
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_rows', None)

def get_top_players_current_season(top_n):
    # 使用 leagueleaders endpoint 获取当前赛季的联盟领袖数据
    leaders = leagueleaders.LeagueLeaders(proxy=config.proxy)
    leaders_data = leaders.get_data_frames()[0]

    # 返回前top_n名球员的数据
    return leaders_data.head(top_n)


# 指定要获取的前10名球员
top_n = 10

# 获取当前赛季各项数据总和前10的球员
top_players_current_season = get_top_players_current_season(top_n)
print(top_players_current_season.columns)
print(top_players_current_season)

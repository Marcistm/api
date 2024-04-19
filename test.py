from nba_api.stats.endpoints import commonplayerinfo, playergamelog

from config import proxy


def get_player_game_logs(player_id, season):
    # 使用 playergamelog endpoint 获取球员比赛数据
    gamelog = playergamelog.PlayerGameLog(player_id=player_id, season=season,proxy=proxy)
    gamelog_data = gamelog.get_data_frames()[0]

    # 返回球员比赛数据
    return gamelog_data


# 指定要查询的球员ID和赛季
player_id = 201939  # 以史蒂芬·库里为例
season = '2023-24'  # 示例赛季，你需要根据实际情况修改

# 获取球员在指定赛季的比赛数据
player_game_logs = get_player_game_logs(player_id, season)
print(player_game_logs.columns)

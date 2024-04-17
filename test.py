from datetime import datetime
from nba_api.stats.endpoints import ScoreboardV2

from config import proxy


def get_game_schedule(date):
    formatted_date = datetime.strftime(date, "%m/%d/%Y")
    data = []
    scoreboard = ScoreboardV2(game_date=formatted_date,proxy=proxy)
    games = scoreboard.get_dict()['resultSets'][1]['rowSet']
    for i in range(0,len(games),2):
        dic = {
            'gameId': games[i][2],
            'awayTeam': games[i+1][6],
            'homeTeam': games[i][6],
            'awayTeamScore': games[i+1][18] if games[i+1][18] is not None else '',
            'homeTeamScore': games[i][18] if games[i][18] is not None else '',
            'gameTimeLTZ': games[i][0]
        }
        data.append(dic)
    return data


# 指定要查询的日期
date_to_query = datetime(2024, 4, 17)  # 示例日期，你需要替换为你要查询的日期

# 获取指定日期的比赛赛程
schedule = get_game_schedule(date_to_query)
print(schedule)

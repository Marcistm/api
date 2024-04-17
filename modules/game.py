import parser
from time import timezone
from datetime import datetime, timezone
from dateutil import parser
from flask import Blueprint, request, jsonify
from nba_api.live.nba.endpoints import scoreboard, boxscore
from nba_api.stats.endpoints import ScoreboardV2

from config import proxy, headers
from lib.db import UseMySQL

game = Blueprint('game', __name__)


def get_game_schedule(date):
    date_obj = datetime.strptime(date, '%Y-%m-%d')
    formatted_date = date_obj.strftime('%m/%d/%Y')
    data = []
    scoreboard = ScoreboardV2(game_date=formatted_date, proxy=proxy)
    resultSets = scoreboard.get_dict()['resultSets']
    game_header = resultSets[0]['rowSet']
    games = resultSets[1]['rowSet']
    for i in range(0, len(games), 2):
        dic = {
            'gameId': games[i][2],
            'awayTeam': games[i][6],
            'homeTeam': games[i+1][6],
            'awayTeamScore': games[i][22] if games[i + 1][22] is not None else '',
            'homeTeamScore': games[i+1][22] if games[i][22] is not None else '',
            'gameTimeLTZ': games[i][0][:10]+' '+game_header[int(i/2)][4]
        }
        data.append(dic)
    return data


@game.route('/search1', methods=['get'])
def search1():
    board = scoreboard.ScoreBoard(proxy=proxy)
    games = board.games.get_dict()
    data = []
    for game in games:
        gameTimeLTZ = parser.parse(game["gameTimeUTC"]).replace(tzinfo=timezone.utc).astimezone(tz=None)
        dic = {
            'gameId': game['gameId'],
            'awayTeam': game['awayTeam']['teamName'],
            'homeTeam': game['homeTeam']['teamName'],
            'awayTeamScore': game['awayTeam']['score'],
            'homeTeamScore': game['homeTeam']['score'],
            'gameTimeLTZ': gameTimeLTZ
        }
        data.append(dic)
    print(data)
    return jsonify(code=200, msg='success', data=data)


@game.route('/search', methods=['get'])
def search():
    date = request.args.get('date')
    data = get_game_schedule(date)
    return jsonify(code=200, msg='success', data=data)


@game.route('/detail', methods=['get'])
def detail():
    data = []
    gameId = request.args.get('gameId')
    type = request.args.get('type')
    box = boxscore.BoxScore(game_id=gameId, proxy=proxy)
    players = box.home_team_player_stats.get_dict() if type == 'home' else box.away_team_player_stats.get_dict()
    con = UseMySQL()
    for player in players:
        row = player['statistics']
        row['name'] = player['name']
        row['gameId'] = gameId
        name = row['name'].replace('\'', '\'\'')
        sql = f"select avg(rate) res from evaluate where gameId='{gameId}' and name='{name}'"
        df = con.get_mssql_data(sql).fillna(0)
        row['rate'] = str(df.iloc[0]['res'])
        data.append(row)
    return jsonify(code=200, msg='success', data=data)

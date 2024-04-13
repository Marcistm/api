import parser
from time import timezone
from datetime import datetime, timezone
from dateutil import parser
from flask import Blueprint, request, jsonify
from nba_api.live.nba.endpoints import scoreboard, boxscore

from lib.db import UseMySQL

game = Blueprint('game', __name__)


@game.route('/search', methods=['get'])
def search():
    board = scoreboard.ScoreBoard()
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
    return jsonify(code=200, msg='success', data=data)


@game.route('/detail', methods=['get'])
def detail():
    data = []
    gameId = request.args.get('gameId')
    type = request.args.get('type')
    box = boxscore.BoxScore(gameId)
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

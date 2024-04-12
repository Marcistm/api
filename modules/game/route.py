import parser
from time import timezone
from datetime import datetime, timezone
from dateutil import parser
from flask import Blueprint, request, jsonify
from nba_api.live.nba.endpoints import scoreboard

game = Blueprint('game', __name__)


@game.route('/search', methods=['get'])
def search():
    board = scoreboard.ScoreBoard()
    games = board.games.get_dict()
    data = []
    for game in games:
        gameTimeLTZ = parser.parse(game["gameTimeUTC"]).replace(tzinfo=timezone.utc).astimezone(tz=None)
        dic = {
            'awayTeam':game['awayTeam']['teamName'],
            'homeTeam':game['homeTeam']['teamName'],
            'awayTeamScore': game['awayTeam']['score'],
            'homeTeamScore': game['homeTeam']['score'],
            'gameTimeLTZ':gameTimeLTZ
        }
        data.append(dic)
    print(data)
    return jsonify(code=200, msg='success',data=data)


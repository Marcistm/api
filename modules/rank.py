import requests
from flask import Blueprint, request, jsonify
from nba_api.stats.endpoints import LeagueStandings

from config import proxy

rank = Blueprint('rank', __name__)


@rank.route('/search', methods=['get'])
def search():
    region = request.args.get('region')
    standings = LeagueStandings(proxy=proxy)
    data = []
    teams = standings.get_dict()['resultSets'][0]['rowSet']
    for team in teams:
        if team[5] == region:
            dic = {
                'team': team[4],
                'W': team[12],
                'L': team[13],
                'rate':team[14]
            }
            data.append(dic)
    return jsonify(code=200, msg='success', data=data)

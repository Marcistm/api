import requests
from flask import Blueprint, request, jsonify
from nba_api.stats.endpoints import LeagueStandings, CommonTeamRoster
from nba_api.stats.static import players, teams

from config import proxy

player = Blueprint('player', __name__)


def get_players_by_team_id(team_id):
    team_roster = CommonTeamRoster(team_id=team_id, proxy=proxy).get_data_frames()[0]
    return team_roster


@player.route('/search/by/team', methods=['get'])
def search_by_team():
    team_id = request.args.get('team_id')
    data = get_players_by_team_id(team_id)
    print(data.columns)
    return jsonify(code=200, msg='success', data=data.fillna('').to_dict('records'))


@player.route('/search',methods=['get'])
def search():
    team_roster = CommonTeamRoster( proxy=proxy).get_data_frames()[0]
    return jsonify(code=200, msg='success', data=team_roster.fillna('').to_dict('records'))

import requests
from flask import Blueprint, request, jsonify
from nba_api.stats.endpoints import LeagueStandings
from nba_api.stats.static import teams

from config import proxy

team = Blueprint('team', __name__)


def get_all_team_names():
    # 获取所有NBA球队信息
    nba_teams = teams.get_teams()
    # 获取所有球队的名称
    team_names = [{'full_name': team['full_name'], 'id': team['id']} for team in nba_teams]
    # 返回所有球队的名称列表
    return team_names


@team.route('/get', methods=['get'])
def get():
    data = get_all_team_names()
    return jsonify(code=200, msg='success', data=data)

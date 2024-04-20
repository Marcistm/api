import json

import requests
from flask import Blueprint, request, jsonify
from nba_api.stats.endpoints import LeagueStandings, teamgamelog
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


def get_team_season_average_stats(team_id):
    # 使用 teamgamelog endpoint 获取球队比赛数据
    team_gamelog = teamgamelog.TeamGameLog(team_id=team_id,proxy=proxy)
    team_gamelog_data = team_gamelog.get_data_frames()[0]
    # 计算平均数据，并保留1位小数
    season_average_stats = team_gamelog_data.mean().round(1).to_dict()
    dict = {
        'REB':season_average_stats['REB'],
        'BLK': season_average_stats['BLK'],
        'PTS': season_average_stats['PTS'],
        'STL': season_average_stats['STL'],
        'AST': season_average_stats['AST'],
    }
    return dict

@team.route('/get', methods=['get'])
def get():
    data = get_all_team_names()
    return jsonify(code=200, msg='success', data=data)


@team.route('/season/avg', methods=['post'])
def season_avg():
    val = json.loads(request.get_data())
    teams = val['teams']
    data = []
    for i in teams:
        player = get_team_season_average_stats(i)
        data.append(player)
    return jsonify(code=200, msg='success', data=data)
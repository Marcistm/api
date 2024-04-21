import json

import pandas as pd
import requests
from flask import Blueprint, request, jsonify
from nba_api.stats.endpoints import LeagueStandings, CommonTeamRoster, playergamelog
from nba_api.stats.static import players, teams

from config import proxy

player = Blueprint('player', __name__)


def get_players_by_team_id(team_id):
    team_roster = CommonTeamRoster(team_id=team_id, proxy=proxy).get_data_frames()[0]
    return team_roster


def get_player_season_average_stats(player_id):
    gamelog = playergamelog.PlayerGameLog(player_id=player_id, proxy=proxy)
    gamelog_data = gamelog.get_data_frames()[0]
    season_average_stats = gamelog_data.mean().round(1).to_dict()
    dict = {
        'REB': season_average_stats['REB'],
        'BLK': season_average_stats['BLK'],
        'PTS': season_average_stats['PTS'],
        'STL': season_average_stats['STL'],
        'AST': season_average_stats['AST'],
    }
    return dict


def get_top10_player_season_average():
    gamelog = playergamelog.PlayerGameLog(proxy=proxy)
    gamelog_data = gamelog.get_data_frames()[0]
    # 根据球员分组，计算各项数据总和
    grouped_data = gamelog_data.groupby('PLAYER_ID').mean().round(1).reset_index()
    top_players = grouped_data.sort_values(by='PTS', ascending=False).head(10)
    return top_players


@player.route('/search/by/team', methods=['get'])
def search_by_team():
    team_id = request.args.get('team_id')
    data = get_players_by_team_id(team_id)
    return jsonify(code=200, msg='success', data=data.fillna('').to_dict('records'))


@player.route('/search', methods=['get'])
def search():
    team_roster = CommonTeamRoster(proxy=proxy).get_data_frames()[0]
    return jsonify(code=200, msg='success', data=team_roster.fillna('').to_dict('records'))


@player.route('/season/avg', methods=['post'])
def season_avg():
    val = json.loads(request.get_data())
    players = val['players']
    data = []
    for i in players:
        player = get_player_season_average_stats(i)
        data.append(player)
    return jsonify(code=200, msg='success', data=data)


@player.route('/top/10', methods=['get'])
def top_10():
    category = request.args.get('category')
    top_10 = get_top10_player_season_average()
    print(top_10)
    return jsonify(code=200, msg='success')

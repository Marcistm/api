import json

import pandas as pd
import requests
from flask import Blueprint, request, jsonify
from nba_api.stats.endpoints import LeagueStandings, CommonTeamRoster, playergamelog, leagueleaders
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


@player.route('/top', methods=['get'])
def top():
    category = request.args.get('category')
    num = request.args.get('num')
    leaders = leagueleaders.LeagueLeaders(proxy=proxy, stat_category_abbreviation=category)
    leaders_data = leaders.get_data_frames()[0]
    leaders_data = leaders_data.head(int(num))
    return jsonify(code=200, msg='success', data=leaders_data.to_dict('records'))

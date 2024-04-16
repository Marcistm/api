from nba_api.live.nba.endpoints import boxscore
from nba_api.stats.endpoints import ScoreboardV2, LeagueGameFinder
from datetime import datetime

# Function to retrieve schedule for a specific date
from config import proxy


def get_schedule(date):
    scoreboard = ScoreboardV2(game_date=date,proxy=proxy)
    print(scoreboard.get_dict())
    games = scoreboard.get_normalized_dict()["GameHeader"]
    schedule = []
    print(games)
    game_finder = LeagueGameFinder(proxy=proxy)
    game_finder.get_json()
    gamess = game_finder.get_data_frames()[0]
    for game in games:
        game_details = gamess[gamess['GAME_ID'] == game['GAME_ID']]
        print(game_details)
        print(game_details['MATCHUP'].values[0].split(' vs ')[1])
    return schedule

# Example usage
date = datetime(2024, 4, 14)
schedule = get_schedule(date)

# Display schedule
print("Schedule for", date.strftime("%Y-%m-%d"))


import requests

url = 'https://cdn.nba.com/static/json/staticData/scheduleLeagueV2.json'
r = requests.get(url)
schedule = r.json()
schedule = schedule['leagueSchedule']['gameDates']
games = []
for l in schedule:
    game = l['games']
    for l in game:
        print(l)

from flask import Flask, render_template
import numpy as np
import pandas as pd
import urllib.request
import json
import seaborn as sns
import matplotlib.pyplot as plt
import googlemaps
import folium
import time

app = Flask('app')

@app.route("/")
def index():
  # getting all teams data
  all_teams_url = "https://www.balldontlie.io/api/v1/teams"
  r1 = urllib.request.urlopen(all_teams_url)
  all_teams_data = json.loads(r1.read())

  # getting all players data
  all_players_data = []
  for i in range(1, 25):
    all_players_url = f"https://www.balldontlie.io/api/v1/players?page={i}"
    r2 = urllib.request.urlopen(all_players_url)
    temp = json.loads(r2.read())
    all_players_data.append(temp)

  # getting all games data
  all_games_data = []
  for i in range(1, 8):
    all_games_url = f"https://www.balldontlie.io/api/v1/games?team_ids[]=2&seasons[]=2017&seasons[]=2018&seasons[]=2019&page={i}"
    r3 = urllib.request.urlopen(all_games_url)
    temp2 = json.loads(r3.read())
    all_games_data.append(temp2)
    # This is to done to tackle respnse code 409 receciving from server
    time.sleep(5)
  
  #### 1st GRAPH #####
  # creating an empty map
  m = folium.Map(location=[37.0902, -95.7129], tiles="OpenStreetMap", zoom_start=4)
  # creating a list of cities
  city_list = [all_teams_data["data"][x]["city"] for x in range(30)]
  # converting the list of cities to set to retain only unique values
  city_set = set(city_list)
  # calling the googlemaps api to fetch coordinates
  gmaps = googlemaps.Client(key='INSERT KEY')
  # creating empty lists to store lat and long values
  lon = []
  lat = []
  cities = []
  for item in city_set:
    # getting the lat and long of cities
    geocode_result = gmaps.geocode(item)
    if geocode_result != []:
      lon.append(geocode_result[0]['geometry']['location']['lng'])
      lat.append(geocode_result[0]['geometry']['location']['lat'])
      cities.append(item)
  # creating a df
  city_df = pd.DataFrame({
    'lon': lon,
    'lat': lat,
    'city': cities},
    dtype=str)
  # plotting the marker of cities on the empty map created above
  for i in range(0, len(city_df)):
    folium.Marker(
        location=[city_df.iloc[i]['lat'], city_df.iloc[i]['lon']],
        popup=city_df.iloc[i]['city'],
        radius=float(10) * 20000,
        color='crimson',
        fill=True,
        fill_color='crimson'
    ).add_to(m)
  m.save('templates/map.html')
  
  #### 2nd GRAPH #####
  # creating a list of positions
  position_list = [all_players_data[x]["data"][y]["position"] for x in range(24) for y in range(len(all_players_data[x]["data"]))]
  # creating a dict of frequencies of positions
  position_list_frq = {}
  for item in position_list:
    if item != '':
      if item in position_list_frq:
        position_list_frq[item] += 1
      else:
        position_list_frq[item] = 1
  # creating a df of dict
  position_df = pd.DataFrame({'positions': list(position_list_frq.keys()),'number of players':list(position_list_frq.values())})
  # plotting the graph
  plt.figure(figsize=(10, 7))
  sns.set(style="darkgrid")
  ax = sns.barplot(data=position_df,x='positions', y='number of players')
  ax.set(xlabel="Different type of positions of players in a basketball game", ylabel="Number of players")
  ax.set_xticklabels(['Center', 'Guard', 'Forward', 'Center-Forward', 'Forward-Center', 'Guard-Forward'])
  plt.tight_layout()
  # saving the graph
  plt.savefig('static/images/pst.png')

  #### 3rd GRAPH #####
  # creating a list of cities
  players_city_list = [all_players_data[x]["data"][y]["team"]["city"] for x in range(24) for y in
                   range(len(all_players_data[x]["data"]))]
  # creating a dict of freq of cities
  players_city_list_frq = {}
  for item in players_city_list:
    if item != '':
      if item in players_city_list_frq:
        players_city_list_frq[item] += 1
      else:
        players_city_list_frq[item] = 1
  # creating a df of dict
  players_city_df = pd.DataFrame({'cities': list(players_city_list_frq.keys()), 'number of players': list(players_city_list_frq.values())})
  # plotting the graph
  plt.figure(figsize=(10, 7))
  sns.set(style="darkgrid")
  ax = sns.barplot(data=players_city_df, x='number of players', y='cities')
  ax.set(xlabel="Number of players", ylabel="Cities in USA")
  plt.tight_layout()
  # saving the graph
  plt.savefig('static/images/city_of_players.png')

  #### 4th GRAPH #####
  # creating a list of weight of players
  players_weight_list = [all_players_data[x]["data"][y]["weight_pounds"] for x in range(24) for y in
                       range(len(all_players_data[x]["data"]))]
  # creating a list of teams
  players_team_list = [all_players_data[x]["data"][y]["team"]["name"] for x in range(24) for y in
                       range(len(all_players_data[x]["data"]))]
  # creating a df
  players_wt_df = pd.DataFrame({
    'weight of players': players_weight_list,
    'team name': players_team_list})
  # plotting the graph
  plt.figure(figsize=(10, 7))
  sns.set(style="darkgrid")
  ax = sns.barplot(data=players_wt_df, x='weight of players', y='team name', estimator=np.mean)
  ax.set(xlabel="Avg weight of players (in Pounds)", ylabel="Name of teams")
  plt.tight_layout()
  # saving the graph
  plt.savefig('static/images/wt_of_players.png')

  #### 5th GRAPH #####
  # creating a list of seasons
  season_list = [all_games_data[x]["data"][y]["season"] for x in range(7) for y in
                 range(len(all_games_data[x]["data"]))]
  # creating a list of scores
  score_list = [all_games_data[x]["data"][y]["visitor_team_score"] for x in range(7) for y in
                range(len(all_games_data[x]["data"]))]
  # creating a df
  games_df = pd.DataFrame({
      'season': season_list,
      'score': score_list})
  games_df['season'] = games_df['season'].astype(int)
  games_df['season'] = games_df['season'].round()
  games_df['season'] = games_df['season'].astype(str)
  # creating the graph
  plt.figure(figsize=(10, 7))
  sns.set(style="darkgrid")
  ax = sns.lineplot(x='season', y='score', data=games_df, estimator=np.mean, sort= False)
  ax.set(xlabel="Seasons", ylabel="Avg team score")
  plt.tight_layout()
  # saving the chart
  plt.savefig('static/images/avgscores.png')

  return render_template("main.html")

@app.route("/map")
def map():
  return render_template("map.html")

app.run(host='0.0.0.0', port=8080)
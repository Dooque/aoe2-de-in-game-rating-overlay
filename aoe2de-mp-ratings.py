# -*- coding: utf-8 -*-
#!/usr/bin/python3

#
# python -m pysimplegui-exemaker.pysimplegui-exemaker
#

import os
import requests
import sys
import threading
import time

import PySimpleGUI as sg

player_info_template = [
    '{name} ({tgelo}) [{elo}] P{numer}',
    'P{numer} [{elo}] ({tgelo})  {name}'   
]

title = 'Age of Empires II DE - Multyplayer Ratings'

t1p1_info = sg.Text('.' * 128, pad=((0,0),(0,0)), background_color='#000000', justification='right', font=('Arial', 12))
t1p2_info = sg.Text('.' * 128, pad=((0,0),(0,0)), background_color='#000000', justification='right', font=('Arial', 12))
t1p3_info = sg.Text('.' * 128, pad=((0,0),(0,0)), background_color='#000000', justification='right', font=('Arial', 12))
t1p4_info = sg.Text('.' * 128, pad=((0,0),(0,0)), background_color='#000000', justification='right', font=('Arial', 12))
t2p1_info = sg.Text('.' * 128, pad=((0,0),(0,0)), background_color='#000000', justification='left', font=('Arial', 12))
t2p2_info = sg.Text('.' * 128, pad=((0,0),(0,0)), background_color='#000000', justification='left', font=('Arial', 12))
t2p3_info = sg.Text('.' * 128, pad=((0,0),(0,0)), background_color='#000000', justification='left', font=('Arial', 12))
t2p4_info = sg.Text('.' * 128, pad=((0,0),(0,0)), background_color='#000000', justification='left', font=('Arial', 12))

team_players_info = [
    [
        t1p1_info,
        t1p2_info,
        t1p3_info,
        t1p4_info,
    ],
    [
        t2p1_info,
        t2p2_info,
        t2p3_info,
        t2p4_info,
    ],
]

team1_column = [
    [t1p1_info],
    [t1p2_info],
    [t1p3_info],
    [t1p4_info],
]

separator_column = []

team2_column = [
    [t2p1_info],
    [t2p2_info],
    [t2p3_info],
    [t2p4_info],
]

layout = [
    [
        sg.Column(team1_column, background_color='#000000', vertical_alignment='top', element_justification='right'),
        sg.VSeparator(),
        sg.Column(team2_column, background_color='#000000', vertical_alignment='top', element_justification='left'),
    ]
]

def fetch_data():

    r = requests.get('https://aoe2.net/api/strings?game=aoe2de&language=en')
    strings = r.json()

    match_uuid = ''
    while True:
        f = open('./AOE2NET_PROFILE_ID.txt', 'r')
        AOE2NET_PROFILE_ID = int(f.read())
        f.close()

        # Get Last/Current match.
        r = requests.get('https://aoe2.net/api/player/lastmatch?game=aoe2de&profile_id={}'.format(AOE2NET_PROFILE_ID))
        match = r.json()

        if match_uuid != match['last_match']['match_uuid']:
            match_uuid = match['last_match']['match_uuid']
            game_type_id = match['last_match']['game_type']
            game_type_string = [x['string'] for x in strings['game_type'] if x['id'] == game_type_id].pop()
            map_type_id = match['last_match']['map_type']
            map_type_string = [x['string'] for x in strings['map_type'] if x['id'] == map_type_id].pop()
            
            players_team1 = [player for player in match['last_match']['players'] if player['team'] == 1]
            players_team2 = [player for player in match['last_match']['players'] if player['team'] == 2]

            t1p1_info.Update(value='')
            t1p2_info.Update(value='')
            t1p3_info.Update(value='')
            t1p4_info.Update(value='')
            t2p1_info.Update(value='')
            t2p2_info.Update(value='')
            t2p3_info.Update(value='')
            t2p4_info.Update(value='')

            team_number = 0
            for team in (players_team1, players_team2):
                player_numer = 0
                for player in team:
                    profile_id = player['profile_id']
                    rating_1v1 = requests.get('https://aoe2.net/api/player/ratinghistory?game=aoe2de&leaderboard_id=3&count=1&profile_id={}'.format(profile_id))
                    rating_tg = requests.get('https://aoe2.net/api/player/ratinghistory?game=aoe2de&leaderboard_id=4&count=1&profile_id={}'.format(profile_id))

                    civ = [ x['string'] for x in strings['civ'] if x['id'] == player['civ']]
                    if civ:
                        civ = civ.pop()
                    else:
                        civ = 'N/A'

                    rating_1v1 = rating_1v1.json()
                    if (len(rating_1v1) == 0):
                        games_1v1 = 'N/A  '
                        rating_1v1 = {'rating':'N/A', 'num_wins':'N/A', 'num_losses':'N/A', 'streak':'N/A'}
                    else:
                        rating_1v1 = rating_1v1.pop()
                        games_1v1 = str(rating_1v1['num_wins'] + rating_1v1['num_losses'])
                        games_1v1 = games_1v1 + " " * (4 - len(games_1v1))
                        rating_1v1['rating'] = str(rating_1v1['rating'])
                        rating_1v1['rating'] = rating_1v1['rating'] + " " * (4 - len(rating_1v1['rating']))
                        rating_1v1['num_wins'] = str(rating_1v1['num_wins'])
                        rating_1v1['num_wins'] = rating_1v1['num_wins'] + " " * (4 - len(rating_1v1['num_wins']))
                        rating_1v1['num_losses'] = str(rating_1v1['num_losses'])
                        rating_1v1['num_losses'] = rating_1v1['num_losses'] + " " * (4 - len(rating_1v1['num_losses']))
                        rating_1v1['streak'] = str(rating_1v1['streak'])
                        rating_1v1['streak'] = rating_1v1['streak'] + " " * (4 - len(rating_1v1['streak']))

                    rating_tg = rating_tg.json()
                    if (len(rating_tg) == 0):
                        games_tg = 'N/A  '
                        rating_tg = {'rating':'N/A', 'num_wins':'N/A', 'num_losses':'N/A', 'streak':'N/A'}
                    else:
                        rating_tg = rating_tg.pop()
                        games_tg = str(rating_tg['num_wins'] + rating_tg['num_losses'])
                        games_tg = games_tg + " " * (4 - len(games_tg))
                        rating_tg['rating'] = str(rating_tg['rating'])
                        rating_tg['rating'] = rating_tg['rating'] + " "*(4 - len(rating_tg['rating']))
                        rating_tg['num_wins'] = str(rating_tg['num_wins'])
                        rating_tg['num_wins'] = rating_tg['num_wins'] + " "*(4 - len(rating_tg['num_wins']))
                        rating_tg['num_losses'] = str(rating_tg['num_losses'])
                        rating_tg['num_losses'] = rating_tg['num_losses'] + " "*(4 - len(rating_tg['num_losses']))
                        rating_tg['streak'] = str(rating_tg['streak'])
                        rating_tg['streak'] = rating_tg['streak'] + " "*(4 - len(rating_tg['streak']))

                    text = player_info_template[team_number].format(
                        numer=player['color'],
                        name=player['name'],
                        tgelo=rating_tg['rating'],
                        elo=rating_1v1['rating'],
                    )

                    team_players_info[team_number][player_numer].Update(value=text)

                    player_numer += 1
                team_number += 1
        time.sleep(10)

if __name__ == '__main__':

    window = sg.Window( title,
                        layout,
                        no_titlebar=True,
                        keep_on_top=True,
                        grab_anywhere=True,
                        background_color='black',
                        transparent_color='black',
                        alpha_channel=1)

    threading.Thread(target=fetch_data, daemon=True).start()

    while True:
       event, values = window.read()
       if event in (sg.WIN_CLOSED, 'Exit'):
            break

    window.close()

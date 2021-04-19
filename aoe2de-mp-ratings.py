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

COLORS = {
    1: '#7A7AFC', # blue
    2: '#FD3434', # red
    3: '#00ff00', # green
    4: '#ffff00', # yellow
    5: '#00fafa', # teal
    6: '#ff00ff', # purple
    7: '#bababa', # gary
    8: '#ffA500', # orange
}

player_info_template = [
    '{name} ({tgelo}) [{elo}] P{numer}',
    'P{numer} [{elo}] ({tgelo})  {name}'
]

title = 'Age of Empires II DE - Multyplayer Ratings'

t1p1_info = sg.Text(' ' * 100, pad=((0,0),(0,0)), background_color='#101010', justification='right', font=('Britannic Bold', 11))
t1p2_info = sg.Text(' ' * 100, pad=((0,0),(0,0)), background_color='#101010', justification='right', font=('Britannic Bold', 11))
t1p3_info = sg.Text(' ' * 100, pad=((0,0),(0,0)), background_color='#101010', justification='right', font=('Britannic Bold', 11))
t1p4_info = sg.Text(' ' * 100, pad=((0,0),(0,0)), background_color='#101010', justification='right', font=('Britannic Bold', 11))
t2p1_info = sg.Text(' ' * 100, pad=((0,0),(0,0)), background_color='#101010', justification='left', font=('Britannic Bold', 11))
t2p2_info = sg.Text(' ' * 100, pad=((0,0),(0,0)), background_color='#101010', justification='left', font=('Britannic Bold', 11))
t2p3_info = sg.Text(' ' * 100, pad=((0,0),(0,0)), background_color='#101010', justification='left', font=('Britannic Bold', 11))
t2p4_info = sg.Text(' ' * 100, pad=((0,0),(0,0)), background_color='#101010', justification='left', font=('Britannic Bold', 11))

team_players_text = [
    [
        None,
        None,
        None,
        None,
    ],
    [
        None,
        None,
        None,
        None,
    ],
]

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

event = threading.Event()
location_file_lock = threading.Lock()
window_location_lock = threading.Lock()

def fetch_data(window):

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
            window_location_lock.acquire()
            window.disappear()
            window.refresh()

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

            team_players_text = [[None, None, None, None], [None, None, None, None]]

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
                        civ = 'None'

                    rating_1v1 = rating_1v1.json()
                    if (len(rating_1v1) == 0):
                        games_1v1 = 'None  '
                        rating_1v1 = {'rating':'None', 'num_wins':'None', 'num_losses':'None', 'streak':'None'}
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
                        games_tg = 'None  '
                        rating_tg = {'rating':'None', 'num_wins':'None', 'num_losses':'None', 'streak':'None'}
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

                    team_players_text[team_number][player_numer] = (text, COLORS[player['color']])

                    player_numer += 1
                team_number += 1

            for team_number in [0, 1]:
                for player_numer in [0, 1, 2, 3]:
                    if team_players_text[team_number][player_numer] is not None:
                        text = team_players_text[team_number][player_numer][0]
                        color = team_players_text[team_number][player_numer][1]
                        team_players_info[team_number][player_numer].Update(value=text, text_color=color)
            window.refresh()
            c, y = get_last_window_location()
            sx, sy = window.size
            window.move(int(c - sx/2), y)
            window.refresh()
            window.reappear()

            window_location_lock.release()

        event.set()
        time.sleep(10)

def get_last_window_location():
    location_file_lock.acquire()
    try:
        location_file_path = '{}\\aoe2de-mp-ratings_window-location.txt'.format(os.getenv('USERPROFILE'))
        location_file = open(location_file_path, 'r')
        try:
            location = eval(location_file.read())
        except SyntaxError:
            location = (0, 0)
    except FileNotFoundError:
        location = (0, 0)
    location_file_lock.release()

    return location

def save_window_location(window):
    event.wait()
    last_location = get_last_window_location()
    while True:
        window_location_lock.acquire()
        x, y = window.CurrentLocation()
        sx, sy = window.size
        window_location_lock.release()
        current_location = (x + sx/2, y)
        if current_location != last_location:
            last_location = current_location
            location_file_path = '{}\\aoe2de-mp-ratings_window-location.txt'.format(os.getenv('USERPROFILE'))
            location_file_lock.acquire()
            location_file = open(location_file_path, 'w')
            location_file.write(str(current_location))
            location_file.close()
            location_file_lock.release()
        time.sleep(2)

if __name__ == '__main__':

    c, y = get_last_window_location()

    window = sg.Window( title,
                        layout,
                        no_titlebar=True,
                        keep_on_top=True,
                        grab_anywhere=True,
                        background_color='#000000',
                        transparent_color='#000000',
                        alpha_channel=1 )
    window.finalize()
    window.disappear()

    threading.Thread(target=fetch_data, daemon=True, args=(window,)).start()
    threading.Thread(target=save_window_location, daemon=True, args=(window,)).start()

    while True:
       event, values = window.read()
       if event in (sg.WIN_CLOSED, 'Exit'):
            break

    window.close()

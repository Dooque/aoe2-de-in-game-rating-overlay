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

FONT_TYPE = 'Liberation Mono Bold'
FONT_SIZE = 9

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
    'P{numer} [{elo}] ({tgelo}) {name}'
]

title = 'Age of Empires II DE - Multyplayer Ratings'

t1p1_info = sg.Text(' ' * 100, pad=((0,0),(0,0)), background_color='#000000', justification='right', font=(FONT_TYPE, FONT_SIZE))
t1p2_info = sg.Text(' ' * 100, pad=((0,0),(0,0)), background_color='#000000', justification='right', font=(FONT_TYPE, FONT_SIZE))
t1p3_info = sg.Text(' ' * 100, pad=((0,0),(0,0)), background_color='#000000', justification='right', font=(FONT_TYPE, FONT_SIZE))
t1p4_info = sg.Text(' ' * 100, pad=((0,0),(0,0)), background_color='#000000', justification='right', font=(FONT_TYPE, FONT_SIZE))
t2p1_info = sg.Text(' ' * 100, pad=((0,0),(0,0)), background_color='#000000', justification='left', font=(FONT_TYPE, FONT_SIZE))
t2p2_info = sg.Text(' ' * 100, pad=((0,0),(0,0)), background_color='#000000', justification='left', font=(FONT_TYPE, FONT_SIZE))
t2p3_info = sg.Text(' ' * 100, pad=((0,0),(0,0)), background_color='#000000', justification='left', font=(FONT_TYPE, FONT_SIZE))
t2p4_info = sg.Text(' ' * 100, pad=((0,0),(0,0)), background_color='#000000', justification='left', font=(FONT_TYPE, FONT_SIZE))

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

layout_data = [
    [
        sg.Column(team1_column, pad=((0,0),(0,0)), background_color='#010101', vertical_alignment='top', element_justification='right'),
        sg.VSeparator(),
        sg.Column(team2_column, pad=((0,0),(0,0)), background_color='#010101', vertical_alignment='top', element_justification='left'),
    ],
    [
        sg.Text(u'\u00A9' + ' Dooque', pad=((0,0),(0,0)), background_color='#000000', justification='center', font=('Arial', 7))
    ]
]

layout_loading = [
    [
        sg.Text('Loading game information...', pad=((0,0),(0,0)), background_color='#000000', justification='center', font=(FONT_TYPE, 14))
    ],
    [
        sg.Text(u'\u00A9' + ' Dooque', pad=((0,0),(0,0)), background_color='#000000', justification='center', font=('Arial', 7))
    ]
]

event = threading.Event()
location_file_lock = threading.Lock()
window_location_lock = threading.Lock()

def fetch_data(window_data, window_loading):

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
            window_data.disappear()
            window_data.refresh()
            window_loading.reappear()
            window_loading.refresh()

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
            max_text_size = 0

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
                    max_text_size = max_text_size if max_text_size > len(text) else len(text)

                    player_numer += 1
                team_number += 1

            for team_number in [0, 1]:
                for player_numer in [0, 1, 2, 3]:
                    if team_players_text[team_number][player_numer] is not None:
                        text = team_players_text[team_number][player_numer][0]
                        color = team_players_text[team_number][player_numer][1]
                        if team_number == 0:
                            text = ' ' * (max_text_size - len(text)) + text
                        else:
                            text = text + ' ' * (max_text_size - len(text))
                        team_players_info[team_number][player_numer].Update(value=text, text_color=color)

            window_data.refresh()
            last_location = get_last_window_location()
            if last_location != (None, None):
                c, y = last_location
                sx, sy = window_data.size
                window_data.move(int(c - sx/2), y)
            window_loading.disappear()
            window_loading.refresh()
            window_data.reappear()
            window_data.refresh()

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
            location = (None, None)
    except FileNotFoundError:
        location = (None, None)
    location_file_lock.release()

    return location

def save_window_location(window_data):
    event.wait()
    last_location = get_last_window_location()
    while True:
        window_location_lock.acquire()
        x, y = window_data.CurrentLocation()
        sx, sy = window_data.size
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

    window_loading = sg.Window( title,
                                layout_loading,
                                no_titlebar=True,
                                keep_on_top=True,
                                grab_anywhere=True,
                                background_color='#010101',
                                transparent_color='#010101',
                                alpha_channel=1,
                                element_justification='center',
                                location = (None, None),)
    window_loading.finalize()
    last_location = get_last_window_location()
    if last_location != (None, None):
        c, y = last_location
        sx, sy = window_loading.size
        window_loading.move(int(c - sx/2), y)
        window_loading.refresh()

    window_data = sg.Window(    title,
                                layout_data,
                                no_titlebar=True,
                                keep_on_top=True,
                                grab_anywhere=True,
                                background_color='#010101',
                                transparent_color='#010101',
                                alpha_channel=1,
                                element_justification='center' )
    window_data.finalize()
    window_data.disappear()
    window_data.refresh()

    threading.Thread(target=fetch_data, daemon=True, args=(window_data, window_loading)).start()
    threading.Thread(target=save_window_location, daemon=True, args=(window_data,)).start()

    while True:
       event_data, values_data = window_data.read(500)
       event_loading, values_loadinga = window_loading.read(500)
       if event_data in (sg.WIN_CLOSED, 'Exit') or event_loading in (sg.WIN_CLOSED, 'Exit'):
            break

    window_data.close()
    window_loading.close()

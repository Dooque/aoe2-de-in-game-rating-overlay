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

LEFT = 0
RIGHT = 1

class PlayerInformationPrinter():


    @staticmethod
    def print(number, name, elo, tgelo, text_position):
        if text_position == LEFT:
            return '{name} ({tgelo}) [{elo}] P{number}'.format(name=name, tgelo=tgelo, elo=elo, number=number)
        elif text_position == RIGHT:
            return 'P{number} [{elo}] ({tgelo}) {name}'.format(number=number, elo=elo, tgelo=tgelo, name=name)
        else:
            raise Exception('Invalid text_position value: {}'.format(text_position))

class InGameRatingOverlay():

    TITLE = 'Age of Empires II DE - Multyplayer Ratings'

    FONT_TYPE = 'Liberation Mono Bold'
    FONT_SIZE = 10

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

    NO_PADDING = ((0,0),(0,0))
    TEXT_BG_COLOR = '#000000'
    BG_COLOR_INVISIBLE = '#010101'
    COPYRIGHT_FONT = ('Arial', 8)
    COPYRIGHT_TEXT = u'\u00A9' + ' Dooque'

    AOE2NET_URL = 'https://aoe2.net/api/'

    def __init__(self):
        self._players_text_string = [ None ] * 8

        self._loading_information_text = sg.Text('Loading game information...', pad=NO_PADDING, background_color=TEXT_BG_COLOR, justification='center', font=(FONT_TYPE, 14))
        self._copyright_text = sg.Text(COPYRIGHT_TEXT, pad=NO_PADDING, background_color=TEXT_BG_COLOR, justification='center', font=COPYRIGHT_FONT)

        self._main_window_columns = [[], []]

        self._main_window_layout = None

        self._loading_information_window_layout = [
            [
                self._loading_information_text
            ],
            [
                self._copyright_text
            ]
        ]

        self._event_is_safe_to_record_window_location = threading.Event()
        self._event_refresh_game_information = threading.Event()
        self._location_file_lock = threading.Lock()
        self._main_window_location_lock = threading.Lock()

        def update_main_window_layout(self):
            self._main_window_layout = [
                [
                    sg.Column(self._main_window_columns[LEFT], pad=NO_PADDING, background_color=BG_COLOR_INVISIBLE, vertical_alignment='top', element_justification='right'),
                    sg.VSeparator(),
                    sg.Column(self._main_window_columns[RIGHT], pad=NO_PADDING, background_color=BG_COLOR_INVISIBLE, vertical_alignment='top', element_justification='left'),
                ],
                [
                    self._copyright_text
                ]
            ]

    def update_game_information(window_data, window_loading):

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
                self._main_window_location_lock.acquire()
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

                self._players_text_string = [[None, None, None, None], [None, None, None, None]]
                max_text_size = 0

                team_number = 0
                for team in (players_team1, players_team2):
                    player_number = 0
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

                        text = PlayerInformationPrinter.print(
                            player['color'],
                            player['name'],
                            rating_1v1['rating'],
                            rating_tg['rating'],
                            team_number % 2
                        )

                        self._players_text_string[team_number][player_number] = (text, COLORS[player['color']])
                        max_text_size = max_text_size if max_text_size > len(text) else len(text)

                        player_number += 1
                    team_number += 1

                for team_number in [0, 1]:
                    for player_number in [0, 1, 2, 3]:
                        if self._players_text_string[team_number][player_number] is not None:
                            text = self._players_text_string[team_number][player_number][0]
                            color = self._players_text_string[team_number][player_number][1]
                            if team_number == 0:
                                text = ' ' * (max_text_size - len(text)) + text
                            else:
                                text = text + ' ' * (max_text_size - len(text))
                            team_players_info[team_number][player_number].Update(value=text, text_color=color)

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

                self._main_window_location_lock.release()

            self._event_is_safe_to_record_window_location.set()
            self._event_refresh_game_information.wait(10)

def get_last_window_location():
    self._location_file_lock.acquire()
    try:
        location_file_path = '{}\\aoe2de-mp-ratings_window-location.txt'.format(os.getenv('USERPROFILE'))
        location_file = open(location_file_path, 'r')
        try:
            location = eval(location_file.read())
        except SyntaxError:
            location = (None, None)
    except FileNotFoundError:
        location = (None, None)
    self._location_file_lock.release()

    return location

def save_window_location(window_data):
    self._event_is_safe_to_record_window_location.wait()
    last_location = get_last_window_location()
    while True:
        self._main_window_location_lock.acquire()
        x, y = window_data.CurrentLocation()
        sx, sy = window_data.size
        self._main_window_location_lock.release()
        current_location = (x + sx/2, y)
        if current_location != last_location:
            last_location = current_location
            location_file_path = '{}\\aoe2de-mp-ratings_window-location.txt'.format(os.getenv('USERPROFILE'))
            self._location_file_lock.acquire()
            location_file = open(location_file_path, 'w')
            location_file.write(str(current_location))
            location_file.close()
            self._location_file_lock.release()
        time.sleep(2)


if __name__ == '__main__':

    window_loading = sg.Window( TITLE,
                                layout_loading,
                                no_titlebar=True,
                                keep_on_top=True,
                                grab_anywhere=True,
                                background_color=BG_COLOR_INVISIBLE,
                                transparent_color=BG_COLOR_INVISIBLE,
                                alpha_channel=1,
                                element_justification='center',
                                right_click_menu=['menu', ['Exit',]],
                                location = (None, None),)
    window_loading.finalize()
    last_location = get_last_window_location()
    if last_location != (None, None):
        c, y = last_location
        sx, sy = window_loading.size
        window_loading.move(int(c - sx/2), y)
        window_loading.refresh()

    window_data = sg.Window(    TITLE,
                                layout_data,
                                no_titlebar=True,
                                keep_on_top=True,
                                grab_anywhere=True,
                                background_color=BG_COLOR_INVISIBLE,
                                transparent_color=BG_COLOR_INVISIBLE,
                                alpha_channel=1,
                                element_justification='center',
                                right_click_menu=['menu', ['Refresh now...', 'Exit',]], )
    window_data.finalize()
    window_data.disappear()
    window_data.refresh()

    threading.Thread(target=self.update_game_information, daemon=True, args=(window_data, window_loading)).start()
    threading.Thread(target=save_window_location, daemon=True, args=(window_data,)).start()

    while True:
        event_data, values_data = window_data.read(500)
        event_loading, values_loadinga = window_loading.read(500)
        if event_data in (sg.WIN_CLOSED, 'Exit') or event_loading in (sg.WIN_CLOSED, 'Exit'):
            break
        if event_data == 'Refresh now...':
            self._event_refresh_game_information.set()

    window_data.close()
    window_loading.close()

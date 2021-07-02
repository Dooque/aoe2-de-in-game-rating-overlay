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

AOE2NET_URL = 'https://aoe2.net/api/'

CONFIGURATION_FILE = './AOE2NET_PROFILE_ID.txt'

FONT_TYPE = 'Liberation Mono Bold'

FONT_SIZE = 10

NO_PADDING = ((0,0),(0,0))

TEXT_BG_COLOR = '#000000'

BG_COLOR_INVISIBLE = '#010101'

COPYRIGHT_FONT = ('Arial', 8)

COPYRIGHT_TEXT = u'\u00A9' + ' Dooque'

REFRESH_TIMEOUT = 10 # Seconds

NO_DATA_STRING = '-----'

MAX_NUMBER_OF_PLAYERS = 8

COLOR_CODES = {
    1: '#7A7AFC', # blue
    2: '#FD3434', # red
    3: '#00ff00', # green
    4: '#ffff00', # yellow
    5: '#00fafa', # teal
    6: '#ff00ff', # purple
    7: '#bababa', # gary
    8: '#ffA500', # orange
}

COLOR_STRINGS = {
    1: 'blue',
    2: 'red',
    3: 'green',
    4: 'yellow',
    5: 'teal',
    6: 'purple',
    7: 'gary',
    8: 'orange',
}


class Rating():

    def __init__(self, rating):
        self.rating = rating["rating"]
        self.num_wins = rating["num_wins"]
        self.num_losses = rating["num_losses"]
        self.streak = rating["streak"]
        self.games = self.num_wins + self.num_losses
        self.win_ratio = self.num_wins / self.games
        self.losses_ratio = self.num_losses / self.games


class Player():

    def __init__(self, player, strngs):
        self.profile_id = player['profile_id']
        self.steam_id = player['steam_id']
        self.name = player['name']
        self.number = player['color']
        self.color_number = player['color']
        self.color_string = COLOR_STRINGS[player['color']]
        self.color_code = COLOR_CODES[player['color']]
        self.team = player['team']
        civ = [ x['string'] for x in strings['civ'] if x['id'] == player['civ'] ]
        self.civ = civ.pop() if civ else NO_DATA_STRING

        rating_1v1 = requests.get(AOE2NET_URL + 'player/ratinghistory?game=aoe2de&leaderboard_id=3&count=1&profile_id={}'.format(self.profile_id)).json()
        self.rating_1v1 = Rating(rating_1v1)

        rating_tg = requests.get(AOE2NET_URL + 'player/ratinghistory?game=aoe2de&leaderboard_id=4&count=1&profile_id={}'.format(self.profile_id)).json()
        self.rating_tg = Rating(rating_tg)


class Match():

    def __init__(self, match, strings):
        last_match = match['last_match']

        self.match_id = last_match['match_uuid']
        self.game_type = [x['string'] for x in strings['game_type'] if x['id'] == last_match['game_type']].pop()
        self.map_type = [x['string'] for x in strings['map_type'] if x['id'] == last_match['map_type']].pop()
        self.number_of_players = last_match['num_players']

        self.players = [ Player(player, strings) for player in last_match['players'] ]


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

    def __init__(self):
        self._players_text_string = [ None ] * MAX_NUMBER_OF_PLAYERS

        self._copyright_text = sg.Text(COPYRIGHT_TEXT, pad=NO_PADDING, background_color=TEXT_BG_COLOR, justification='center', font=COPYRIGHT_FONT)

        self._loading_information_text = sg.Text('Loading game information...', pad=NO_PADDING, background_color=TEXT_BG_COLOR, justification='center', font=(FONT_TYPE, 14))
        self._loading_information_window_layout = [
            [
                self._loading_information_text
            ],
            [
                self._copyright_text
            ]
        ]
        self._loading_information_window_menu = ['menu', ['Exit',]]

        self._main_window_location = (None, None)
        self._main_window_columns = [[], []]
        self._main_window_layout = None
        self._main_window_menu = ['menu', ['Refresh now...', 'Exit']]

        self._event_is_safe_to_record_window_location = threading.Event()
        self._event_refresh_game_information = threading.Event()
        self._location_file_lock = threading.Lock()
        self._main_window_lock = threading.Lock()

        self._strings = requests.get(AOE2NET_URL + 'strings?game=aoe2de&language=en').json()
        self._current_match_id = ''

    def run(self):
        self._loading_information_window = sg.Window(
            '',
            self._loading_information_window_layout,
            no_titlebar=True,
            keep_on_top=True,
            grab_anywhere=True,
            background_color=BG_COLOR_INVISIBLE,
            transparent_color=BG_COLOR_INVISIBLE,
            alpha_channel=1,
            element_justification='center',
            right_click_menu=self._loading_information_window_menu,
            location = (None, None),
        )

        self._loading_information_window.finalize()
        last_location = get_last_window_location()
        if last_location != (None, None):
            c, y = last_location
            sx, sy = self._loading_information_window.size
            self._loading_information_window.move(int(c - sx/2), y)
            self._loading_information_window.refresh()

        self._main_window = sg.Window(
            '',
            layout_data,
            no_titlebar=True,
            keep_on_top=True,
            grab_anywhere=True,
            background_color=BG_COLOR_INVISIBLE,
            transparent_color=BG_COLOR_INVISIBLE,
            alpha_channel=1,
            element_justification='center',
            right_click_menu=self._main_window_menu
        )
        self._main_window.finalize()
        self._main_window.disappear()
        self._main_window.refresh()

        threading.Thread(target=self.update_game_information, daemon=True, args=(self._main_window, self._loading_information_window)).start()
        threading.Thread(target=save_window_location, daemon=True, args=(self._main_window,)).start()

        while True:
            event_data, values_data = self._main_window.read(500)
            event_loading, values_loadinga = self._loading_information_window.read(500)
            if event_data in (sg.WIN_CLOSED, 'Exit') or event_loading in (sg.WIN_CLOSED, 'Exit'):
                break
            if event_data == 'Refresh now...':
                self._event_refresh_game_information.set()

        self._main_window.close()
        self._loading_information_window.close()

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

    def update_game_information(self):
        while True:
            # Read AoE2.net profile ID from configuration file.
            configuration_file = open(CONFIGURATION_FILE, 'r')
            AOE2NET_PROFILE_ID = int(configuration_file.read())
            configuration_file.close()

            # Get Last/Current match.
            match = requests.get(AOE2NET_URL + 'player/lastmatch?game=aoe2de&profile_id={}'.format(AOE2NET_PROFILE_ID)).json()
            self._match = Match(match, self._strings)

            if self._current_match_id != match.match_id:
                self._main_window_lock.acquire()

                self._main_window.disappear()
                self._main_window.refresh()
                self._loading_information_window.reappear()
                self._loading_information_window.refresh()

                self._current_match_id = match.match_id




                text = PlayerInformationPrinter.print(
                    player['color'],
                    player['name'],
                    rating_1v1['rating'],
                    rating_tg['rating'],
                    team_number % 2
                )

                self._players_text_string[team_number][player_number] = (text, COLORS[player['color']])
                max_text_size = max_text_size if max_text_size > len(text) else len(text)

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

                self._main_window.refresh()
                last_location = get_last_window_location()
                if last_location != (None, None):
                    c, y = last_location
                    sx, sy = self._main_window.size
                    self._main_window.move(int(c - sx/2), y)
                self._loading_information_window.disappear()
                self._loading_information_window.refresh()
                self._main_window.reappear()
                self._main_window.refresh()

                self._main_window_lock.release()

            self._event_is_safe_to_record_window_location.set()
            self._event_refresh_game_information.wait(REFRESH_TIMEOUT)

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

    def save_window_location(self._main_window):
        self._event_is_safe_to_record_window_location.wait()
        last_location = get_last_window_location()
        while True:
            self._main_window_lock.acquire()
            x, y = self._main_window.CurrentLocation()
            sx, sy = self._main_window.size
            self._main_window_lock.release()
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
    overlay = InGameRatingOverlay()
    overlay.run()

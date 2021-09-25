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

NO_DATA_STRING = '----'

MAX_NUMBER_OF_PLAYERS = 8

MAX_PLAYER_NAME_STRING_SIZE = 15

MAX_PLAYER_ROW_STRING_SIZE = 32

SAVE_WINDOW_LOCATION_INTERVAL = 1 # Seconds.

WINDOW_LOCATION_FILE = '{}\\aoe2de_in_game_rating_overlay-window_location.txt'

TOOLTIP_FORMAT_STR = """{name}
Civ: {civ} - [{rating1v1}] - ({ratingtg})
1v1: G={games1v1}, S={streak1v1}, W={wins1v1}, L={losses1v1}, {ratio1v1}%
TG : G={gamestg}, S={streaktg}, W={winstg}, L={lossestg}, {ratiotg}%"""

# This is not an error!!!
JUSTIFICATION = {
    LEFT: 'right',
    RIGHT: 'left'
}

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


loading_progress = {'steps':1, 'current':0}

sg.set_options(tooltip_font=('"{}" {}'.format(FONT_TYPE, FONT_SIZE)))


class Rating():

    def __init__(self, rating=None):
        if rating is not None:
            self.rating = rating["rating"]
            self.num_wins = rating["num_wins"]
            self.num_losses = rating["num_losses"]
            self.streak = rating["streak"]
            self.games = self.num_wins + self.num_losses
            self.win_ratio = int(self.num_wins / self.games * 100)
        else:
            self.rating = 0
            self.num_wins = 0
            self.num_losses = 0
            self.streak = 0
            self.games = 0
            self.win_ratio = 0


class Player():

    def __init__(self, player, strings):
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

        if self.name is None:
            self.name = 'IA ' + self.civ

    def fetch_rating_information(self):
        print('[Thread-1] Fetching 1v1 rating information for player {}'.format(self.name))
        if self.profile_id is not None:
            url = AOE2NET_URL + 'player/ratinghistory?game=aoe2de&leaderboard_id=3&count=1&profile_id={}'.format(self.profile_id)
            print('[Thread-1] Fetching from:', url)
            rating_1v1 = requests.get(url).json()
            if rating_1v1:
                self.rating_1v1 = Rating(rating_1v1[0])
            else:
                self.rating_1v1 = Rating()
        else:
            self.rating_1v1 = Rating()
        loading_progress['current'] += 1

        print('[Thread-1] Fetching TG rating information for player {}'.format(self.name))
        if self.profile_id is not None:
            url = AOE2NET_URL + 'player/ratinghistory?game=aoe2de&leaderboard_id=4&count=1&profile_id={}'.format(self.profile_id)
            print('[Thread-1] Fetching from:', url)
            rating_tg = requests.get(url).json()
            if rating_tg:
                self.rating_tg = Rating(rating_tg[0])
            else:
                self.rating_tg = Rating()
        else:
            self.rating_tg = Rating()
        loading_progress['current'] += 1


class Match():

    def __init__(self, match, strings):
        last_match = match['last_match']

        self.match_id = last_match['match_uuid']
        self.game_type = [x['string'] for x in strings['game_type'] if x['id'] == last_match['game_type']].pop()
        self.map_type = [x['string'] for x in strings['map_type'] if x['id'] == last_match['map_type']].pop()
        self.number_of_players = last_match['num_players']

        self.players = [ Player(player, strings) for player in last_match['players'] ]

    def fetch_rating_information(self):
        for player in self.players:
            player.fetch_rating_information()

class PlayerInformationPrinter():

    def print(self, number, name, elo, tgelo, text_position):
        name = name[:MAX_PLAYER_NAME_STRING_SIZE]
        if text_position == LEFT:
            text = '{name} ({tgelo}) [{elo}] P{number}'.format(name=name, tgelo=tgelo, elo=elo, number=number)
            return (' ' * (MAX_PLAYER_ROW_STRING_SIZE - len(text))) + text
        elif text_position == RIGHT:
            text = 'P{number} [{elo}] ({tgelo}) {name}'.format(number=number, elo=elo, tgelo=tgelo, name=name)
            return text + (' ' * (MAX_PLAYER_ROW_STRING_SIZE - len(text)))
        else:
            raise Exception('Invalid text_position value: {}'.format(text_position))


class InGameRatingOverlay():

    def __init__(self):
        self._strings = None
        self._is_server_ok = False
        self._event_refresh_game_information = threading.Event()
        self._player_info_printer = PlayerInformationPrinter()
        self._current_match_lock = threading.Lock()
        self._fetching_data = False
        self._current_match = None
        self._finish = False

        self._loading_information_window_text = sg.Text('Loading game information:   0%', pad=NO_PADDING, background_color=TEXT_BG_COLOR, justification='center', font=(FONT_TYPE, 14))
        self._loading_information_window_location = (None, None)
        self._loading_information_window_layout = [
            [
                self._loading_information_window_text
            ],
            [
                self._get_copyright_text()
            ]
        ]
        self._loading_information_window_menu = ['menu', ['Exit',]]
        self._loading_information_window = None

        self._main_window_last_location = self._get_last_windows_location()['main_window']
        self._main_window_columns = [[], []]
        self._main_window_layout = None
        self._main_window_menu = ['menu', ['Refresh', 'Minimize', '---', 'Exit']]
        self._main_window = None
        self._update_main_window = False

        self._minimized_window = None
        self._minimized_window_last_location = self._get_last_windows_location()['minimized_window']
        self._minimized_window_menu = ['menu', ['Maximize', '---', 'Exit']]
        self._minimized_window_layout = [
            [
                sg.Text('Ratings', pad=NO_PADDING, background_color=TEXT_BG_COLOR, justification='center', font=(FONT_TYPE, 14))
            ],
            [
                self._get_copyright_text()
            ]
        ]

    def run(self):
        self._create_loading_information_window()
        self._create_minimized_window()

        print('[Thread-0] Starting "update_game_information" thread.')
        self._update_game_information_thread = threading.Thread(target=self._update_game_information)
        self._update_game_information_thread.start()

        print('[Thread-0] Entering main loop...')

        number_of_retries = 0

        while not self._finish:
            if self._strings is None:
                url = AOE2NET_URL + 'strings?game=aoe2de&language=en'
                print('[Thread-0] Fetching from:', url)
                try:
                    if number_of_retries != 0:
                        time.sleep(5)
                        print('[Thread-0] Number of retries:', number_of_retries)    
                    self._strings = requests.get(url).json()
                    self._is_server_ok = True
                except Exception as error:
                    print('[Thread-0] request timeout... retrying...:', error)
                    self._is_server_ok = False
                    number_of_retries += 1

            if self._is_server_ok:
                percentage = int(loading_progress['current'] / loading_progress['steps'] * 100)
                self._loading_information_window_text.update(value='Loading game information: {}%'.format(percentage))
                self._loading_information_window.refresh()
            else:
                self._loading_information_window_text.update(value='Waiting for server...')
                self._loading_information_window.refresh()

            if self._main_window is not None:
                e1, v1 = self._main_window.read(50)
            else:
                e1, v1 = ('no-event', [])

            e2, v2 = self._loading_information_window.read(50)
            e3, v3 = self._minimized_window.read(50)

            if any(True for x in (e1, e2, e3) if x in (sg.WIN_CLOSED, 'Exit')):
                print('[Thread-0] finish = True')
                self._finish = True
                self._event_refresh_game_information.set()

            if e1 == 'Refresh':
                print('[Thread-0] Evenet: "Refresh now" generated.')
                self._current_match = None
                self._event_refresh_game_information.set()

            if e1 == 'Minimize':
                self._main_window.disappear()
                self._main_window.refresh()
                x, y = self._minimized_window_last_location
                if (x, y) != (None, None):
                    self._minimized_window.move(int(x), int(y))
                else:
                    self._minimized_window.move(x, y)
                self._minimized_window.reappear()
                self._minimized_window.refresh()

            if e3 == 'Maximize':
                self._minimized_window.disappear()
                self._minimized_window.refresh()
                if self._main_window_last_location != (None, None):
                    c, y = self._main_window_last_location
                    sx, sy = self._main_window.size
                    self._main_window.move(int(c - sx/2.0), int(y))
                self._main_window.reappear()
                self._main_window.refresh()

            self._save_windows_location()

            if self._fetching_data or not self._is_server_ok:
                if self._fetching_data:
                    print('[Thread-0] Fetching new data')
                elif not self._is_server_ok:
                    print('[Thread-0] Server if offline')
                if self._main_window is not None:
                    self._main_window.close()
                    self._main_window = None
                if self._main_window_last_location != (None, None):
                    c, y = self._main_window_last_location
                    sx, sy = self._loading_information_window.size
                    self._loading_information_window.move(int(c - sx/2), int(y))
                self._loading_information_window.reappear()
                self._loading_information_window.refresh()
                self._fetching_data = False

            if self._update_main_window:
                print('[Thread-0] Updating main window.')
                self._current_match_lock.acquire()
                if self._main_window is not None:
                    self._main_window.close()
                    self._main_window = None
                self._create_main_window()
                self._update_main_window = False
                self._loading_information_window.disappear()
                self._loading_information_window.refresh()
                self._current_match_lock.release()

        print('[Thread-0] Main loop terminated!')

        if self._main_window is not None:
            self._main_window.close()
            self._main_window = None
        if self._loading_information_window is not None:
            self._loading_information_window.close()
            self._loading_information_window = None

        print('[Thread-0] Waiting for update_game_information thread to terminate...')
        self._update_game_information_thread.join()
        print('[Thread-0] update_game_information thread terminated!')

    def _get_copyright_text(self):
        return sg.Text(COPYRIGHT_TEXT, pad=NO_PADDING, background_color=TEXT_BG_COLOR, justification='center', font=COPYRIGHT_FONT)

    def _create_loading_information_window(self):
        print('[Thread-0] Creating loading_information_window...')
        self._loading_information_window = sg.Window(
            None,
            self._loading_information_window_layout,
            no_titlebar=True,
            keep_on_top=True,
            grab_anywhere=True,
            background_color=BG_COLOR_INVISIBLE,
            transparent_color=BG_COLOR_INVISIBLE,
            alpha_channel=1,
            element_justification='center',
            right_click_menu=self._loading_information_window_menu
        )

        # We show this window in the same location than the main window.
        self._loading_information_window.finalize()
        if self._main_window_last_location != (None, None):
            c, y = self._main_window_last_location
            sx, sy = self._loading_information_window.size
            self._loading_information_window.move(int(c - sx/2.0), int(y))
            self._loading_information_window.refresh()
        print('[Thread-0] loading_information_window created!')

    def _create_main_window(self):
        print('[Thread-0] Creating main window...')
        self._update_main_window_layout()
        self._main_window = sg.Window(
            None,
            self._main_window_layout,
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
        if self._main_window_last_location != (None, None):
            c, y = self._main_window_last_location
            sx, sy = self._main_window.size
            self._main_window.move(int(c - sx/2.0), int(y))
        self._main_window.refresh()
        print('[Thread-0] Main window created!')

    def _create_minimized_window(self):
        print('[Thread-0] Creating minimized window...')
        self._minimized_window = sg.Window(
            None,
            self._minimized_window_layout,
            no_titlebar=True,
            keep_on_top=True,
            grab_anywhere=True,
            background_color=BG_COLOR_INVISIBLE,
            transparent_color=BG_COLOR_INVISIBLE,
            alpha_channel=1,
            element_justification='center',
            right_click_menu=self._minimized_window_menu
        )
        self._minimized_window.finalize()
        x, y = self._minimized_window_last_location
        if (x, y) != (None, None):
            self._minimized_window.move(int(x), int(y))
        else:
            self._minimized_window.move(x, y)
        self._minimized_window.refresh()
        self._minimized_window.disappear()
        print('[Thread-0] Minimized window created!')

    def _update_main_window_layout(self):
        print('[Thread-0] Updating main window layout...')
        self._main_window_layout = [
            [
                sg.Column(self._main_window_columns[LEFT], pad=NO_PADDING, background_color=BG_COLOR_INVISIBLE, vertical_alignment='top', element_justification='right'),
                sg.VSeparator(),
                sg.Column(self._main_window_columns[RIGHT], pad=NO_PADDING, background_color=BG_COLOR_INVISIBLE, vertical_alignment='top', element_justification='left'),
            ],
            [
                self._get_copyright_text()
            ]
        ]

    def _get_last_windows_location(self):
        try:
            location_file_path = WINDOW_LOCATION_FILE.format(os.getenv('USERPROFILE'))
            location_file = open(location_file_path, 'r')
            try:
                main_window_location = tuple(map(float, location_file.readline().split(',')))
                minimized_window_location = tuple(map(float, location_file.readline().split(',')))
                location = {'main_window':main_window_location, 'minimized_window':minimized_window_location}
            except:
                location = {'main_window':(None, None), 'minimized_window':(None, None)}
        except FileNotFoundError:
            location = {'main_window':(None, None), 'minimized_window':(None, None)}

        print('[Thread-0] Getting last windows location:', location)

        return location

    def _save_windows_location(self):
        if self._main_window is not None:
            x, y = self._main_window.CurrentLocation()
            sx, sy = self._main_window.size
        else:
            x, y = self._loading_information_window.CurrentLocation()
            sx, sy = self._loading_information_window.size
        main_current_location = (x + sx/2.0, y)
        minimized_current_location = self._minimized_window.CurrentLocation()
        if (main_current_location != self._main_window_last_location) or (minimized_current_location != self._minimized_window_last_location):
            print('[Thread-0] Saving main window location:', main_current_location)
            print('[Thread-0] Saving minimized window location:', minimized_current_location)
            self._main_window_last_location = main_current_location
            self._minimized_window_last_location = minimized_current_location
            location_file_path = WINDOW_LOCATION_FILE.format(os.getenv('USERPROFILE'))
            location_file = open(location_file_path, 'w')
            location_file.write(str(main_current_location[0]) + ',' + str(main_current_location[1]) + '\n')
            location_file.write(str(minimized_current_location[0]) + ',' + str(minimized_current_location[1]))
            location_file.close()

    def _update_game_information(self):
        while not self._finish:
            print('[Thread-1] update_game_information thread loop...')

            if self._strings is None:
                print('[Thread-1] Server connection has not been established. Waiting for 1 second.')
                time.sleep(1)
                continue

            # Read AoE2.net profile ID from configuration file.
            configuration_file = open(CONFIGURATION_FILE, 'r')
            AOE2NET_PROFILE_ID = int(configuration_file.read())
            configuration_file.close()
            print('[Thread-1] AOE2NET_PROFILE_ID:', AOE2NET_PROFILE_ID)

            # Get Last/Current match.
            print('[Thread-1] Fetching game data...')
            try:
                url = AOE2NET_URL + 'player/lastmatch?game=aoe2de&profile_id={}'.format(AOE2NET_PROFILE_ID)
                print('[Thread-1] Fetching from:', url)
                match_data = requests.get(url).json()
                self._is_server_ok = True
            except Exception as error:
                print('[Thread-1] request timeout... retrying...:', error)
                self._is_server_ok = False
                self._event_refresh_game_information.wait(REFRESH_TIMEOUT)
                self._event_refresh_game_information.clear()
                continue
            new_match = Match(match_data, self._strings)
            print('[Thread-1] Fetching game data done!')

            if (self._current_match is None):
                print('[Thread-1] New match id: {}'.format(new_match.match_id))            
            else:
                print('[Thread-1] Current match id: {} - New match id: {}'.format(self._current_match.match_id, new_match.match_id))

            if (self._current_match is None) or (self._current_match.match_id != new_match.match_id):
                self._fetching_data = True

                loading_progress['current'] = 0
                loading_progress['steps'] = new_match.number_of_players * 2

                print('[Thread-1] Fetching rating information...')
                try:
                    new_match.fetch_rating_information()
                    self._is_server_ok = True
                except Exception as error:
                    print('[Thread-1] request timeout... retrying...:', error)
                    self._is_server_ok = False
                    self._event_refresh_game_information.wait(REFRESH_TIMEOUT)
                    self._event_refresh_game_information.clear()
                    continue
                print('[Thread-1] Fetching rating information done!')

                self._current_match_lock.acquire()
                self._current_match = new_match

                self._main_window_columns = [[], []]

                print('[Thread-1] Generating players rating information...')
                max_text_size = 0
                for player in self._current_match.players:
                    player.text = self._player_info_printer.print(
                        player.number,
                        player.name,
                        player.rating_1v1.rating,
                        player.rating_tg.rating,
                        player.team % 2
                    )
                    max_text_size = max_text_size if max_text_size > len(player.text) else len(player.text)

                auxiliar_counter = 0
                number_of_players = self._current_match.number_of_players
                for player in self._current_match.players:
                    if ((number_of_players == 2) or (number_of_players == 4)) and any(p.team == -1 for p in self._current_match.players):
                        column = auxiliar_counter
                        auxiliar_counter += 1
                    else:
                        column = player.team % 2

                    if column == LEFT:
                        player.text = ' ' * (max_text_size - len(player.text)) + player.text
                    else: # column == RIGH:
                        player.text = player.text + ' ' * (max_text_size - len(player.text))

                    tooltip = TOOLTIP_FORMAT_STR.format(
                        name=player.name,
                        civ=player.civ, rating1v1=player.rating_1v1.rating, ratingtg=player.rating_tg.rating,
                        games1v1=player.rating_1v1.games, gamestg=player.rating_tg.games,
                        streak1v1=player.rating_1v1.streak, streaktg=player.rating_tg.streak,
                        wins1v1=player.rating_1v1.num_wins, winstg=player.rating_tg.num_wins,
                        losses1v1=player.rating_1v1.num_losses, lossestg=player.rating_tg.num_losses,
                        ratio1v1=player.rating_1v1.win_ratio, ratiotg=player.rating_tg.win_ratio
                    )

                    text = sg.Text(
                        player.text,
                        pad=NO_PADDING,
                        background_color=TEXT_BG_COLOR,
                        justification=JUSTIFICATION[column],
                        font=(FONT_TYPE, FONT_SIZE),
                        text_color=COLOR_CODES[player.color_number],
                        tooltip=tooltip
                    )

                    self._main_window_columns[column].append([text])
                print('[Thread-1] Generating players rating information done!')

                if not self._finish:
                    print('[Thread-1] update_main_window = True')
                    self._update_main_window = True
                self._current_match_lock.release()

            if not self._finish:
                print('[Thread-1] Waiting for {} seconds to next update or for "Refresh now" event.'.format(REFRESH_TIMEOUT))
                self._event_refresh_game_information.wait(REFRESH_TIMEOUT)
                self._event_refresh_game_information.clear()


def previouse_version_cleanup():
    USERPROFILE = os.getenv('USERPROFILE')
    old_file = '{}\\aoe2de-mp-ratings_window-location.txt'.format(USERPROFILE)
    new_file = WINDOW_LOCATION_FILE.format(USERPROFILE)
    if os.path.exists(old_file):
        os.rename(old_file, new_file)


if __name__ == '__main__':
    previouse_version_cleanup()
    overlay = InGameRatingOverlay()
    overlay.run()

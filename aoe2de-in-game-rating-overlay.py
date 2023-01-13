# -*- coding: utf-8 -*-
#!/usr/bin/python3

#
# python -m pysimplegui-exemaker.pysimplegui-exemaker
#

from datetime import datetime
import aoe2netapi
import json
import os
import PySimpleGUI as sg
import requests
import shutil
import sys
import threading
import time
import traceback

# If executable name ends with .py extension is because we're running it from source code.
DEBUG = sys.argv[0].endswith('.py')
DEBUG_FILE = 'aoe2de-igro.log'
def DebugMsg(msg, enabled):
    if enabled:
        if DEBUG:
            print(msg)
        else:
            with open(DEBUG_FILE, 'a') as file:
                file.write(msg + '\n')

DebugMsg('¡Starting AoE2 DE In Game Rating Overlay!', True)

CURRENT_VERSION = 'v1.0.1'

LEFT = 0

RIGHT = 1

VERSION_FILE_URL = 'https://raw.github.com/Dooque/aoe2-de-in-game-rating-overlay/main/VERSION'

AOE2NET_URL = 'https://aoe2.net/api/'

CONFIGURATION_FILE = './configuration.txt'

NO_PADDING = ((0,0),(0,0))

TEXT_BG_COLOR = '#000000'

BG_COLOR_INVISIBLE = '#010101'

COPYRIGHT_FONT = ('Arial', 8)

COPYRIGHT_TEXT = u'\u00A9' + ' Dooque'

NO_DATA_STRING = '----'

MAX_NUMBER_OF_PLAYERS = 8

MAX_PLAYER_NAME_STRING_SIZE = 15

MAX_PLAYER_ROW_STRING_SIZE = 32

WINDOW_LOCATION_FILE = '{}\\aoe2de_in_game_rating_overlay-window_location.txt'

TOOLTIP_FORMAT_STR = """{name}
Civ: {civ} - [{rating1v1}] - ({ratingtg})
1v1: G={games1v1}, S={streak1v1}, W={wins1v1}, L={losses1v1}, {ratio1v1}%
TG : G={gamestg}, S={streaktg}, W={winstg}, L={lossestg}, {ratiotg}%"""

ABOUT_STRING = """Age of Empires II DE
In Game Rating Overlay
Version {version}
{copyright}

https://github.com/Dooque/aoe2-de-in-game-rating-overlay
https://discord.gg/5Ke9Fa5G5x
"""

# This is not an error!!!
JUSTIFICATION = {
    LEFT: 'right',
    RIGHT: 'left'
}

COLOR_CODES = {
    0: '#FFFFFF', # white
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
    0: 'white',
    1: 'blue',
    2: 'red',
    3: 'green',
    4: 'yellow',
    5: 'teal',
    6: 'purple',
    7: 'gary',
    8: 'orange',
}

# Ranked Game Types
DEATHMATCH = 0
RANDOMMAP = 1
EMPIREWARS = 2

GAME_TYPE_STR = {
    0: "Random Map",
    1: "Regicide",
    2: "Death Match",
    3: "Scenario",
    6: "King of the Hill",
    7: "Wonder Race",
    8: "Defend the Wonder",
    9: "Turbo Random Map",
    10: "Capture the Relic",
    11: "Sudden Death",
    12: "Battle Royale",
    13: "Empire Wars",
    15: "Co-Op Campaign",
}

GAME_TYPE_TO_LADER_BOARD_MAP = {
    0:  RANDOMMAP, # Random Map
    1:  RANDOMMAP, # Regicide
    2:  DEATHMATCH, # Death Match
    3:  RANDOMMAP, # Scenario
    6:  RANDOMMAP, # King of the Hill
    7:  RANDOMMAP, # Wonder Race
    8:  RANDOMMAP, # Defend the Wonder
    9:  RANDOMMAP, # Turbo Random Map
    10: RANDOMMAP, # Capture the Relic
    11: DEATHMATCH, # Sudden Death
    12: RANDOMMAP, # Battle Royale
    13: EMPIREWARS, # Empire Wars
    15: RANDOMMAP, # Co-Op Campaign
}

LEADERBOARD_ID = {
    DEATHMATCH: {'1v1':1 , 'tg':2},
    RANDOMMAP: {'1v1':3 , 'tg':4},
    EMPIREWARS: {'1v1':13 , 'tg':14},
}


aoe2api = aoe2netapi.API()

loading_progress = {'steps':1, 'current':0}


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

    def __init__(self, player, strings, debug):
        self._debug = debug
        self.profile_id = player['profile_id']
        self.name = player['name']
        self.number = player['color'] if player['color'] > 0 else player['slot'] 
        self.color_number = player['color'] 
        self.color_string = COLOR_STRINGS[self.color_number]
        self.color_code = COLOR_CODES[self.color_number]
        self.team = player['team']
        self.slot = player['slot']
        civ = [ x['string'] for x in strings['civ'] if x['id'] == player['civ'] ]
        self.civ = civ.pop() if civ else NO_DATA_STRING

        if self.name is None:
            self.name = 'IA ' + self.civ

    def fetch_rating_information(self, leaderboard_id):
        DebugMsg('[Thread-1] Fetching 1vs1 rating information for player "{}"'.format(self.name), self._debug)
        if self.profile_id is not None:
            rating_1v1 = aoe2api.get_rating_history(leaderboard_id=LEADERBOARD_ID[leaderboard_id]['1v1'], count=1, profile_id=self.profile_id)
            if rating_1v1:
                self.rating_1v1 = Rating(rating_1v1[0])
            else:
                self.rating_1v1 = Rating()
        else:
            self.rating_1v1 = Rating()
        loading_progress['current'] += 1

        DebugMsg('[Thread-1] Fetching TeamGame rating information for player "{}"'.format(self.name), self._debug)
        if self.profile_id is not None:
            rating_tg = aoe2api.get_rating_history(leaderboard_id=LEADERBOARD_ID[leaderboard_id]['tg'], count=1, profile_id=self.profile_id)
            if rating_tg:
                self.rating_tg = Rating(rating_tg[0])
            else:
                self.rating_tg = Rating()
        else:
            self.rating_tg = Rating()
        loading_progress['current'] += 1


class Match():

    def __init__(self, match, strings, debug):
        self._debug = debug

        self.match_id = match['match_uuid']
        self.game_type = match['game_type']
        self.game_type_str = GAME_TYPE_STR[self.game_type]
        self.map_type = [x['string'] for x in strings['map_type'] if x['id'] == match['map_type']].pop()
        self.number_of_players = match['num_players']

        self.players = [ Player(player, strings, self._debug) for player in match['players'] ]

    def fetch_rating_information(self):
        for player in self.players:
            player.fetch_rating_information(GAME_TYPE_TO_LADER_BOARD_MAP[self.game_type])


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
        self._load_configuration()
        self._check_for_new_version()
        self._load_users_information()

        self._strings = None
        self._is_server_ok = False
        self._event_refresh_game_information = threading.Event()
        self._player_info_printer = PlayerInformationPrinter()
        self._current_match_lock = threading.Lock()
        self._fetching_data = False
        self._current_match = None
        self._finish = False

        self._loading_information_window_text = sg.Text('Loading game information:   0%', expand_x=True, pad=NO_PADDING, background_color=TEXT_BG_COLOR, justification='center', font=(self._font_type, self._font_size))
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
        self._main_window_menu = ['menu', ['Minimize', 'Refresh', '---', 'Users', [user['name'] for user in self._users], '---', 'About', 'Exit']]
        self._main_window = None
        self._update_main_window = False

        self._minimized_window = None
        self._minimized_window_last_location = self._get_last_windows_location()['minimized_window']
        self._minimized_window_menu = ['menu', ['Maximize', '---', 'Exit']]
        self._minimized_window_layout = [
            [
                sg.Text('Ratings', expand_x=True, pad=NO_PADDING, background_color=TEXT_BG_COLOR, justification='center', font=(self._font_type, self._font_size))
            ],
            [
                self._get_copyright_text()
            ]
        ]

    def run(self):
        self._create_loading_information_window()
        self._create_minimized_window()

        DebugMsg('[Thread-0] Starting "update_game_information" thread.', self._debug)
        self._update_game_information_thread = threading.Thread(target=self._update_game_information)
        self._update_game_information_thread.start()

        DebugMsg('[Thread-0] Entering main loop...', self._debug)

        number_of_retries = 0

        while not self._finish:
            if self._strings is None:
                DebugMsg('[Thread-0] Fetching game string.', self._debug)
                try:
                    if number_of_retries != 0:
                        time.sleep(5)
                        DebugMsg('[Thread-0] Number of retries: {}'.format(number_of_retries))   , self._debug 
                    self._strings = aoe2api.get_strings()
                    self._is_server_ok = True
                except Exception as error:
                    DebugMsg('[Thread-0] request timeout... retrying...: {}'.format(error), self._debug)
                    self._is_server_ok = False
                    number_of_retries += 1

            if self._is_server_ok:
                percentage = int(loading_progress['current'] / loading_progress['steps'] * 100)
                self._loading_information_window_text.update(value='Loading game information: {}%'.format(percentage))
                self._loading_information_window.refresh()
            else:
                self._loading_information_window_text.update(value='Server not availableN...')
                self._loading_information_window.refresh()

            if self._main_window is not None:
                e1, v1 = self._main_window.read(50)
            else:
                e1, v1 = ('no-event', [])

            e2, v2 = self._loading_information_window.read(50)
            e3, v3 = self._minimized_window.read(50)

            if any(True for x in (e1, e2, e3) if x in (sg.WIN_CLOSED, 'Exit')):
                DebugMsg('[Thread-0] finish = True', self._debug)
                self._finish = True
                self._event_refresh_game_information.set()

            if e1 in [user['name'] for user in self._users]:
                for user in self._users:
                    if e1 == user['name']:
                        user['current'] = 1
                    else:
                        user['current'] = 0
                e1 = 'Refresh'

            if e1 == 'Refresh':
                DebugMsg('[Thread-0] Evenet: "Refresh now" generated.', self._debug)
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

            if e1 == 'About':
                about_window = sg.Window(
                    'About!',
                    [[sg.Text(ABOUT_STRING.format(version=CURRENT_VERSION, copyright=COPYRIGHT_TEXT), expand_x=True, background_color='#000000', justification='center', font=('Arial', 10))],],
                    keep_on_top=True,
                    background_color='#000000',
                    alpha_channel=1.0,
                    element_justification='center',
                    icon='./res/813780_icon.ico'
                )
                about_window.finalize()

            self._save_windows_location()

            if self._fetching_data or not self._is_server_ok:
                if self._fetching_data:
                    DebugMsg('[Thread-0] Fetching new data', self._debug)
                elif not self._is_server_ok:
                    DebugMsg('[Thread-0] Server is offline', self._debug)
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
                DebugMsg('[Thread-0] Updating main window.', self._debug)
                self._current_match_lock.acquire()
                if self._main_window is not None:
                    self._main_window.close()
                    self._main_window = None
                self._create_main_window()
                self._update_main_window = False
                self._loading_information_window.disappear()
                self._loading_information_window.refresh()
                self._current_match_lock.release()

        DebugMsg('[Thread-0] Main loop terminated!', self._debug)

        if self._main_window is not None:
            self._main_window.close()
            self._main_window = None
        if self._loading_information_window is not None:
            self._loading_information_window.close()
            self._loading_information_window = None

        DebugMsg('[Thread-0] Waiting for update_game_information thread to terminate...', self._debug)
        self._update_game_information_thread.join()
        DebugMsg('[Thread-0] update_game_information thread terminated!', self._debug)

    def _load_users_information(self):
        DebugMsg('[Thread-0] Loading users...', True)
        #DebugMsg('[Thread-0] Time: {}'.format(), True)
        self._users = []
        current = True
        steam_ids = self._get_local_steam_ids()
        for steam_id in steam_ids:
            last_match = aoe2api.get_last_match(steam_id=steam_id)
            for player in last_match['last_match']['players']:
                if (player['steam_id'] is not None) and (int(player['steam_id']) == steam_id):
                    self._users.append({'name':player['name'], 'ID':steam_id, 'current':current})
                    current = False
                    break

    def _get_local_steam_ids(self):
        """By https://github.com/didierrenardub."""
        steam_ids = []
        aoe_path = os.path.join(os.environ['USERPROFILE'], 'Games', 'Age of Empires 2 DE')

        for dir in os.listdir(aoe_path):
            steam_id = None
            try:
                steam_id = int(dir)
            except ValueError:
                pass
            if steam_id is not None and steam_id > 0:
                steam_ids.append(steam_id)

        return steam_ids

    def _check_for_new_version(self):
        now = datetime.now()
        DebugMsg('[Thread-0] Time: {}'.format(now.strftime("%m/%d/%Y-%H:%M:%S")), True)
        DebugMsg('[Thread-0] Running version {}.'.format(CURRENT_VERSION), True)

        DebugMsg('[Thread-0] Checking for new version at: {}'.format(VERSION_FILE_URL), self._debug)
        try:
            new_version = requests.get(VERSION_FILE_URL).text
            if new_version[0] != 'v':
                new_version = CURRENT_VERSION
        except:
            new_version = CURRENT_VERSION
            DebugMsg('[Thread-0] Failed to fetch new version.', self._debug)

        if CURRENT_VERSION < new_version:
            DebugMsg('[Thread-0] There is a new version available!', self._debug)
            update_window = sg.Window(
                'Version {} is now available!'.format(new_version),
                [[sg.Text('The new version {} is now available for download at\nhttps://github.com/Dooque/aoe2-de-in-game-rating-overlay.'.format(new_version), expand_x=True, background_color='#000000', justification='center', font=('Arial', 10))],],
                keep_on_top=True,
                background_color='#000000',
                alpha_channel=1.0,
                element_justification='center',
                icon='./res/813780_icon.ico'
            )
            update_window.finalize()

    def _load_configuration(self):
        try:
            DebugMsg('[Thread-0] Loading configuration file at: {}'.format(CONFIGURATION_FILE), True)
            f = open(CONFIGURATION_FILE)
            conf = json.load(f)
            f.close()
            self._font_type = conf['font-type']
            self._font_size = conf['font-size']
            self._refresh_time = conf['refresh-time']
            self._debug = conf['debug']
            DebugMsg('[Thread-0] Configuration loaded successfully: {}'.format(conf), self._debug)
            sg.set_options(tooltip_font=('"{}" {}'.format(self._font_type, self._font_size)))
        except json.JSONDecodeError:
            DebugMsg('[Thread-0] Configuration loading failed!', self._debug)
            error_window = sg.Window(
                'ERROR',
                [[sg.Text('There is a syntax error in the configuration file.', expand_x=True, background_color='#ff0000', justification='center', font=('Arial', 14))],],
                keep_on_top=True,
                background_color='#ff0000',
                alpha_channel=1.0,
                element_justification='center',
                icon='./res/813780_icon.ico'
            )
            error_window.finalize()

            while True:
                e1, v1 = error_window.read()
                if e1 in (sg.WIN_CLOSED, 'Exit'):
                    sys.exit(0)

    def _get_copyright_text(self):
        return sg.Text(COPYRIGHT_TEXT, expand_x=True, pad=NO_PADDING, background_color=TEXT_BG_COLOR, justification='center', font=COPYRIGHT_FONT)

    def _create_loading_information_window(self):
        DebugMsg('[Thread-0] Creating loading_information_window...', self._debug)
        self._loading_information_window = sg.Window(
            None,
            self._loading_information_window_layout,
            no_titlebar=True,
            keep_on_top=True,
            #grab_anywhere=False,
            background_color=BG_COLOR_INVISIBLE,
            transparent_color=BG_COLOR_INVISIBLE,
            alpha_channel=1.0,
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
        DebugMsg('[Thread-0] loading_information_window created!', self._debug)

    def _create_main_window(self):
        DebugMsg('[Thread-0] Creating main window...', self._debug)
        self._update_main_window_layout()
        self._main_window = sg.Window(
            None,
            self._main_window_layout,
            no_titlebar=True,
            keep_on_top=True,
            #grab_anywhere=True,
            grab_anywhere_using_control=True,
            background_color=BG_COLOR_INVISIBLE,
            transparent_color=BG_COLOR_INVISIBLE,
            alpha_channel=1.0,
            element_justification='center',
            right_click_menu=self._main_window_menu,
            icon='./res/813780_icon.ico'
        )
        self._main_window.finalize()
        if self._main_window_last_location != (None, None):
            c, y = self._main_window_last_location
            sx, sy = self._main_window.size
            self._main_window.move(int(c - sx/2.0), int(y))
        self._main_window.refresh()
        DebugMsg('[Thread-0] Main window created!', self._debug)
        import ipdb; ipdb.set_trace()

    def _create_minimized_window(self):
        DebugMsg('[Thread-0] Creating minimized window...', self._debug)
        self._minimized_window = sg.Window(
            None,
            self._minimized_window_layout,
            no_titlebar=True,
            keep_on_top=True,
            #grab_anywhere=True,
            background_color=BG_COLOR_INVISIBLE,
            transparent_color=BG_COLOR_INVISIBLE,
            alpha_channel=1.0,
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
        DebugMsg('[Thread-0] Minimized window created!', self._debug)

    def _update_main_window_layout(self):
        DebugMsg('[Thread-0] Updating main window layout...', self._debug)
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

        DebugMsg('[Thread-0] Getting last windows location: {}'.format(location), self._debug)

        return location

    def _save_windows_location(self):
        if self._main_window is not None:
            x, y = self._main_window.CurrentLocation()
            sx, sy = self._main_window.size
            main_current_location = (x + sx/2.0, y)
            minimized_current_location = self._minimized_window.CurrentLocation()
            if (main_current_location != self._main_window_last_location) or (minimized_current_location != self._minimized_window_last_location):
                DebugMsg('[Thread-0] Saving main window location: {}'.format(main_current_location), self._debug)
                DebugMsg('[Thread-0] Saving minimized window location: {}'.format(minimized_current_location), self._debug)
                self._main_window_last_location = main_current_location
                self._minimized_window_last_location = minimized_current_location
                location_file_path = WINDOW_LOCATION_FILE.format(os.getenv('USERPROFILE'))
                location_file = open(location_file_path, 'w')
                location_file.write(str(main_current_location[0]) + ',' + str(main_current_location[1]) + '\n')
                location_file.write(str(minimized_current_location[0]) + ',' + str(minimized_current_location[1]))
                location_file.close()

    def _update_game_information(self):
        while not self._finish:
            DebugMsg('[Thread-1] update_game_information thread loop...', self._debug)

            if self._strings is None:
                DebugMsg('[Thread-1] Server connection has not been established. Waiting for 1 second.', self._debug)
                time.sleep(1)
                continue

            # Read AoE2.net profile ID from configuration.
            for user in self._users:
                if user['current']:
                    profile_id = user['ID']
                    DebugMsg('[Thread-1] Current user: Name = {name} - Profile ID = {id}'.format(name=user['name'], id=profile_id), self._debug)

            # Get Last/Current match.
            DebugMsg('[Thread-1] Fetching last match information', self._debug)
            try:
                last_match = aoe2api.get_last_match(steam_id=profile_id)
                self._is_server_ok = True
            except Exception as error:
                DebugMsg('[Thread-1] request timeout... retrying...: {}'.format(error), self._debug)
                self._is_server_ok = False
                self._event_refresh_game_information.wait(self._refresh_time)
                self._event_refresh_game_information.clear()
                continue
            new_match = Match(last_match, self._strings, self._debug)
            DebugMsg('[Thread-1] Fetching last match data done!', self._debug)
            DebugMsg('[Thread-1] Game Type is "({}) {}".'.format(new_match.game_type, new_match.game_type_str), self._debug)

            if (self._current_match is None):
                DebugMsg('[Thread-1] New match id: {}'.format(new_match.match_id), self._debug)  
            else:
                DebugMsg('[Thread-1] Current match id: {} - New match id: {}'.format(self._current_match.match_id, new_match.match_id), self._debug)

            if (self._current_match is None) or (self._current_match.match_id != new_match.match_id):
                self._fetching_data = True

                loading_progress['current'] = 0
                loading_progress['steps'] = new_match.number_of_players * 2

                DebugMsg('[Thread-1] Fetching rating information...', self._debug)
                try:
                    new_match.fetch_rating_information()
                    self._is_server_ok = True
                except Exception as error:
                    DebugMsg('[Thread-1] request timeout... retrying...: {}'.format(error), self._debug)
                    self._is_server_ok = False
                    self._event_refresh_game_information.wait(self._refresh_time)
                    self._event_refresh_game_information.clear()
                    continue
                DebugMsg('[Thread-1] Fetching rating information done!', self._debug)

                self._current_match_lock.acquire()
                self._current_match = new_match

                self._main_window_columns = [[], []]

                use_slots = any(player.color_number <= 0 for player in self._current_match.players)
                use_team = all(player.team > 0 for player in self._current_match.players)
                DebugMsg('[Thread-1] use_slots = {}'.format(use_slots), self._debug)
                DebugMsg('[Thread-1] use_team = {}'.format(use_team), self._debug)

                DebugMsg('[Thread-1] Generating players rating information...', self._debug)
                max_text_size = 0
                for player in self._current_match.players:
                    player.text = self._player_info_printer.print(
                        player.number,
                        player.name,
                        player.rating_1v1.rating,
                        player.rating_tg.rating,
                        (player.team if use_team else (player.number if not use_slots else player.slot)) % 2
                    )
                    max_text_size = max_text_size if max_text_size > len(player.text) else len(player.text)

                number_of_players = self._current_match.number_of_players
                for player in self._current_match.players:
                    if ((number_of_players == 2) or (number_of_players == 4)) and any(p.team == -1 for p in self._current_match.players):
                        column = player.slot % 2
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
                        expand_x=True,
                        pad=NO_PADDING,
                        background_color=TEXT_BG_COLOR,
                        justification=JUSTIFICATION[column],
                        font=(self._font_type, self._font_size),
                        text_color=COLOR_CODES[player.color_number if not use_slots else player.slot],
                        tooltip=tooltip
                    )

                    self._main_window_columns[column].append([text])
                DebugMsg('[Thread-1] Generating players rating information done!', self._debug)

                if not self._finish:
                    DebugMsg('[Thread-1] update_main_window = True', self._debug)
                    self._update_main_window = True
                self._current_match_lock.release()

            if not self._finish:
                DebugMsg('[Thread-1] Waiting for {} seconds to next update or for "Refresh now" event.'.format(self._refresh_time), self._debug)
                self._event_refresh_game_information.wait(self._refresh_time)
                self._event_refresh_game_information.clear()


def previouse_version_cleanup():
    USERPROFILE = os.getenv('USERPROFILE')
    old_file = '{}\\aoe2de-mp-ratings_window-location.txt'.format(USERPROFILE)
    new_file = WINDOW_LOCATION_FILE.format(USERPROFILE)
    if os.path.exists(old_file):
        os.rename(old_file, new_file)


if __name__ == '__main__':
    try:
        overlay = InGameRatingOverlay()
        overlay.run()
    except:
        DebugMsg(str(print(traceback.format_exc())), True)

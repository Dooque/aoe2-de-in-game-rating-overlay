"""
A simple and basic Python 3 https://aoe2.net/ API wrapper for sending `GET requests`.

Available on GitHub (+ documentation): https://github.com/sixP-NaraKa/aoe2net-api-wrapper

Additional data manipulation/extraction from the provided data by this API wrapper has to be done by you, the user.

See https://aoe2.net/#api & https://aoe2.net/#nightbot.
"""


import requests
import json as jsn


# api base urls
API_BASE_URL = "https://aoe2.net/api"
NIGHTBOT_BASE_URL = API_BASE_URL + "/nightbot"  # "https://aoe2.net/api/nightbot"

# request api base urls (api endpoints)
STRINGS_URL = API_BASE_URL + "/strings"
LEADERBOARD_URL = API_BASE_URL + "/leaderboard"
LOBBIES_URL = API_BASE_URL + "/lobbies"
LAST_MATCH_URL = API_BASE_URL + "/player/lastmatch"
MATCH_HISTORY_URL = API_BASE_URL + "/player/matches"
RATING_HISTORY_URL = API_BASE_URL + "/player/ratinghistory"
MATCHES_URL = API_BASE_URL + "/matches"
MATCH_URL = API_BASE_URL + "/match"
NUMBERS_ONLINE_URL = API_BASE_URL + "/stats/players"

# request nightbot api base urls (api endpoints)
RANK_DETAILS_URL = NIGHTBOT_BASE_URL + "/rank?"
RECENT_OPPONENT_URL = NIGHTBOT_BASE_URL + "/opponent?"
CURRENT_MATCH_URL = NIGHTBOT_BASE_URL + "/match?"
CURRENT_CIVS_URL = NIGHTBOT_BASE_URL + "/civs?"
CURRENT_MAP_URL = NIGHTBOT_BASE_URL + "/map?"

# request headers
headers = {'content-type': 'application/json;charset=UTF-8'}


# simple base exception class, to raise errors with
class Aoe2NetException(Exception):
    """ AoE2.net API error. """


""" ----------------------------------------------- HELPER FUNCTIONS -----------------------------------------------"""


def _is_valid_kwarg(provided: dict, available: dict):
    """
    Helper function to check if a user provided dictionary has the correct arguments,
    compared to a dictionary with the actual available arguments.

    Updates, if no difference found, the dictionary 'available'.

    Parameters
    ----------
    provided : `dict`
        The user defined dictionary of optional additional arguments.
    available : `dict`
        The available optional additional arguments possible.

    :raises KeyError:
        invalid additional keyword argument supplied
    """

    diff = provided.keys() - available.keys()
    if diff:  # if there are differences
        msg = "invalid optional keyword argument passed: {}. Available arguments: {}".format(diff, list(available.keys()))
        raise KeyError(msg)
    available.update(provided)
    return available


def _get_request_response(url: str, params: dict = None, json: bool = True):
    """
    Helper function to request data.

    For the NIGHTBOT_API calls, the returned data is not JSON, but plain text.
    Each of those functions will return the response.text explicitly.

    Parameters
    ----------
    url : `str`
        The request to call the API with.
    params : `dict`
        A dictionary of parameters that will be used for a GET request.
    json : `bool`
        Specifies if the request response should be returned in JSON format. Defaults to True.

    :return:
        the request response

    :raises requests.exceptions.RequestException:
        if a exception happens during the request handling
    :raises Aoe2NetExecution:
        if status code of the response is not 200
    """

    try:
        response = requests.get(url, params=params, headers=headers)
    except requests.exceptions.RequestException as rer:
        raise requests.exceptions.RequestException(rer)
    if response.status_code != 200:
        msg = "Expected status code 200 - got {}.".format(response.status_code)
        raise Aoe2NetException(msg)
    if json:
        try:
            response = response.json()
        except jsn.JSONDecodeError as jde:
            raise Aoe2NetException(jde)
    return response


""" ------------------------------------------- API REQUESTS (class API) -------------------------------------------"""


class API:
    """
    The 'API' class encompasses the https://aoe2.net/#api API functions,
    which can return their requested data in JSON format.
    """

    def get_strings(self, game: str = "aoe2de", json: bool = True):
        """
        Requests a list of strings used by the API.

        Parameters
        ----------
        game : `str`
            The game for which to extract the list of strings. Defaults to "aoe2de" if omitted.

            Possible games:

            aoe2hd -> Age of Empires 2: HD Edition, aoe2de -> Age of Empires 2: Definitive Edition
        json : `bool`
            Specifies to the '_get_request_response()' function if the request response should be returned in JSON format.
            Defaults to True.

        :return:
            the data in json format (if set), otherwise the plain response object.
        """

        return _get_request_response(url=STRINGS_URL, params={"game": game}, json=json)

    def get_leaderboard(self, leaderboard_id: int = 3, start: int = 1, count: int = 10, json: bool = True, **kwargs):
        """
        Requests the data of the given leaderboard, specified by the 'leaderboard_id'.

        Parameters
        ----------
        leaderboard_id : `int`
            The leaderboard in which to extract data in. Defaults to ID 3 (1v1 RM).

            Possible IDs:

            0 -> Unranked, 1 -> 1v1 Deathmatch, 2 -> Team Deathmatch, 3 -> 1v1 Random Map, 4 -> Team Random Map
        start : `int`
            Specifies the start point for which to extract data at. Defaults to 1.

            Ignored if 'search', 'steam_id' or 'profile_id' are defined.
        count : `int`
            Specifies how many entries of the given leaderboard should be extracted,
            if able to find with the given criteria. Defaults to 10.
            Max. 10000.
        json : `bool`
            Specifies to the '_get_request_response()' function if the request response should be returned in JSON format.
            Defaults to True.
        **kwargs : `dict`
            Additional optional arguments.

            Possible arguments:

            search : `str`
                Specifies a player name to search for. All players found that match the given name will be returned.

            steam_id : `str`
                The steamID64 of a player. (ex: 76561199003184910)

                Takes precedence over both 'search' and 'profile_id'.

            profile_id : `str`
                The profile ID. (ex: 459658)

                Takes precedence over 'search'.

        :return:
            the data in json format (if set), otherwise the plain response object.

        :raises Aoe2NetException:
            'count' has to be 10000 or less.
        """

        if count > 10000:
            raise Aoe2NetException("'count' has to be 10000 or less.")

        optionals = {
                    "search": "",
                    "steam_id": "",
                    "profile_id": "",
                    }
        optionals = _is_valid_kwarg(kwargs, optionals)

        params = {"game": "aoe2de", "leaderboard_id": leaderboard_id, "start": start, "count": count}
        params.update(optionals)

        return _get_request_response(url=LEADERBOARD_URL, params=params, json=json)

    def get_open_lobbies(self, game: str = "aoe2de", json: bool = True):
        """
        Requests all open lobbies.

        Parameters
        ----------
        game : `str`
            The game for which to extract the lobby data. Defaults to "aoe2de" if omitted.

            Possible games:

            aoe2hd -> Age of Empires 2: HD Edition, aoe2de -> Age of Empires 2: Definitive Edition
        json : `bool`
            Specifies to the '_get_request_response()' function if the request response should be returned in JSON format.
            Defaults to True.

        :return:
            the data in json format (if set), otherwise the plain response object.
        """

        params = {"game": game}
        return _get_request_response(url=LOBBIES_URL, params=params, json=json)

    def get_last_match(self, steam_id: str = "", profile_id: str = "", json: bool = True):
        """
        Requests the last match a player started playing.
        This will be the current match if they still are in game.

        Either 'steam_id' or 'profile_id' required.

        Parameters
        ----------
        steam_id : `str`
            The steamID64 of a player. (ex: 76561199003184910)

            Takes precedence over 'profile_id'.
        profile_id : `str`
                The profile ID. (ex: 459658)

                Defaults to an empty string.
        json : `bool`
            Specifies to the '_get_request_response()' function if the request response should be returned in JSON format.
            Defaults to True.

        :return:
            the data in json format (if set), otherwise the plain response object.

        :raises Aoe2NetException:
            Either 'steam_id' or 'profile_id' required.
        """

        if not steam_id and not profile_id:
            raise Aoe2NetException("Either 'steam_id' or 'profile_id' required.")

        params = {"steam_id": steam_id, "profile_id": profile_id}
        return _get_request_response(url=LAST_MATCH_URL, params=params, json=json)

    def get_match_history(self, start: int = 0, count: int = 5, steam_id: str = "", profile_id: str = "", json: bool = True):
        """
        Requests the match history for a player.

        Either 'steam_id' or 'profile_id' required.

        Parameters
        ---------
        start : `int`
            Specifies the start point for which to extract data at. Defaults to 0 (most recent match).
        count : `int`
            Specifies how many entries of the given leaderboard should be extracted,
            if able to find with the given criteria. Defaults to 5.
            Max. 1000.
        steam_id : `str`
            The steamID64 of a player. (ex: 76561199003184910)

            Takes precedence over 'profile_id'.
        profile_id : `str`
            The profile ID. (ex: 459658)

            Defaults to an empty string.
        json : `bool`
            Specifies to the '_get_request_response()' function if the request response should be returned in JSON format.
            Defaults to True.

        :return:
            the data in json format (if set), otherwise the plain response object.

        :raises Aoe2NetException:
            'count' has to be 1000 or less. || Either 'steam_id' or 'profile_id' required.
        """

        if count > 1000:
            raise Aoe2NetException("'count' has to be 1000 or less.")

        if not steam_id and not profile_id:
            raise Aoe2NetException("Either 'steam_id' or 'profile_id' required.")

        params = {"start": start, "count": count, "steam_id": steam_id, "profile_id": profile_id}
        return _get_request_response(url=MATCH_HISTORY_URL, params=params, json=json)

    def get_rating_history(self, leaderboard_id: int = 3, start: int = 0, count: int = 100, steam_id: str = "", profile_id: str = "", json: bool = True):
        """
        Requests the rating history for a player.

        Either 'steam_id' or 'profile_id' required.

        Parameters
        ---------
        leaderboard_id : `int`
            The leaderboard in which to extract data in. Defaults to ID 3 (1v1 RM).

            Possible IDs:

            0 -> Unranked, 1 -> 1v1 Deathmatch, 2 -> Team Deathmatch, 3 -> 1v1 Random Map, 4 -> Team Random Map
        start : `int`
            Specifies the start point for which to extract data at. Defaults to 0 (most recent match).

            Ignored if 'steam_id' or 'profile_id' are defined.
        count : `int`
            Specifies how many entries of the given leaderboard should be extracted,
            if able to find with the given criteria. Defaults to 100.
            Max. 10000.
        steam_id : `str`
            The steamID64 of a player. (ex: 76561199003184910)

            Takes precedence over 'profile_id'.
        profile_id : `str`
            The profile ID. (ex: 459658)

            Defaults to an empty string.
        json : `bool`
            Specifies to the '_get_request_response()' function if the request response should be returned in JSON format.
            Defaults to True.

        :return:
            the data in json format (if set), otherwise the plain response object.

        :raises Aoe2NetException:
            'count' has to be 10000 or less. || Either 'steam_id' or 'profile_id' required.
        """

        if count > 10000:
            raise Aoe2NetException("'count' has to be 10000 or less.")

        if not steam_id and not profile_id:
            raise Aoe2NetException("Either 'steam_id' or 'profile_id' required.")

        params = {"leaderboard_id": leaderboard_id, "start": start, "count": count, "steam_id": steam_id, "profile_id": profile_id}
        return _get_request_response(url=RATING_HISTORY_URL, params=params, json=json)

    def get_matches(self, count: int = 5, json: bool = True, **kwargs):
        """
        Requests the match history in a optionally given time frame (globally).

        If 'since' is not set, only the X amount of current past matches (specified by 'count') will be returned.

        Parameters
        ---------
        count : `int`
            Specifies how many entries of the match history should be extracted. Defaults to 5.
            Max. 1000.
        json : `bool`
            Specifies to the '_get_request_response()' function if the request response should be returned in JSON format.
            Defaults to True.
        **kwargs : `dict`
            Additional optional arguments.

            Possible arguments:

            since : `str` | `int`
                Only shows matches after this timestamp. (ex: 1596775000)

        :return:
            the data in json format (if set), otherwise the plain response object.

        :raises Aoe2NetException:
            'count' has to be 1000 or less.
        """

        if count > 1000:
            raise Aoe2NetException("'count' has to be 1000 or less.")

        optionals = {"since": ""}
        optionals = _is_valid_kwarg(kwargs, optionals)

        params = {"count": count}
        params.update(optionals)
        return _get_request_response(url=MATCHES_URL, params=params, json=json)

    def get_match(self, uuid: str = "", match_id: str = "", json: bool = True):
        """
        Requests a single match (globally).

        Either 'uuid' or 'match_id' required.

        Parameters
        ---------
        uuid : `str`
            the Match UUID, viewable via a function such as 'ab_get_matches()'.

            Takes precedence over 'match_id'.
        match_id : `str`
            the Match ID, viewable via a function such as 'ab_get_matches()'.
        json : `bool`
            Specifies to the '_get_request_response()' function if the request response should be returned in JSON format.
            Defaults to True.

        :return:
            the data in json format (if set), otherwise the plain response object.

        :raises Aoe2NetException:
            Either 'uuid' or 'match_id' required.
        """

        if not uuid and not match_id:
            raise Aoe2NetException("Either 'uuid' or 'match_id' required.")

        params = {"uuid": uuid, "match_id": match_id}
        return _get_request_response(url=MATCH_URL, params=params, json=json)

    def get_num_online(self, game: str = "aoe2de", json: bool = True):
        """
        Requests the current player numbers of AoE2: DE.

        Parameters
        ---------
        game : `str`
            The game for which to extract the player numbers. Defaults to "aoe2de" if omitted.

            Possible games:

            aoe2hd -> Age of Empires 2: HD Edition, aoe2de -> Age of Empires 2: Definitive Edition
        json : `bool`
            Specifies to the '_get_request_response()' function if the request response should be returned in JSON format.
            Defaults to True.

        :return:
            the data in json format (if set), otherwise the plain response object.
        """

        params = {"game": game}
        return _get_request_response(url=NUMBERS_ONLINE_URL, params=params, json=json)


""" ------------------------------------ NIGHTBOT API REQUESTS (class Nightbot) ------------------------------------"""


class Nightbot:
    """
    The 'Nighbot' class encompasses the https://aoe2.net/#nightbot Nightbot API functions,
    which only return their requested data as plain text.
    """

    def get_rank_details(self, search: str = "", steam_id: str = "", profile_id: str = "", leaderboard_id: int = 3):
        """
        Requests the rank details of a player, specified by the 'leaderboard_id'.

        Either 'search', 'steam_id' or 'profile_id' required.

        The request response is only available as pure text.

        Returns "Player not found", if no player could be found with the given criteria.
        With some combinations of 'search', 'steam_id' and 'profile_id', if nothing could be found for example,
        the current rank #1 player of the given optional additional 'leaderboard_id' will be returned by the API.

        Parameters
        ----------
        search : `str`
            The name of the to be searched player. Returns the highest rated player found.
        steam_id : `str`
            The steamID64 of a player. (ex: 76561199003184910)

            Takes precedence over 'search' and 'profile_id'.
        profile_id : `str`
            The profile ID. (ex: 459658)

            Takes precedence over 'search'.

            Defaults to an empty string.
        leaderboard_id : `int`
            The leaderboard in which to extract data in. Defaults to ID 3 (1v1 RM).

            Possible IDs:

            0 -> Unranked, 1 -> 1v1 Deathmatch, 2 -> Team Deathmatch, 3 -> 1v1 Random Map, 4 -> Team Random Map

        :return:
            the response.text

        :raises Aoe2NetException:
            Either 'search', 'steam_id' or 'profile_id' required.
        """

        if not search and not steam_id and not profile_id:
            raise Aoe2NetException("Either 'search', 'steam_id' or 'profile_id' required.")

        params = {"flag": "false", "search": search, "steam_id": steam_id, "profile_id": profile_id, "leaderboard_id": leaderboard_id}

        return _get_request_response(url=RANK_DETAILS_URL, params=params, json=False).text

    def get_recent_opp(self, search: str = "", steam_id: str = "", profile_id: str = "", leaderboard_id: int = 3):
        """
        Requests the rank details of the most recent opponent of a player (1v1 only).

        Either 'steam_id' or 'profile_id' required.

        The request response is only available as pure text.

        Returns "Player not found", if no player could be found.

        Parameters
        ----------
        search : `str`
            The name of the to be searched player. Returns the highest rated player found.
        steam_id : `str`
            The steamID64 of a player. (ex: 76561199003184910)

            Takes precedence over 'search' and 'profile_id'.
        profile_id : `str`
            The profile ID. (ex: 459658)

            Takes precedence over 'search'.

            Defaults to an empty string.
        leaderboard_id : `int`
            The leaderboard in which to extract data in. Defaults to ID 3 (1v1 RM).

            Is used when 'search' is defined.

            Possible IDs:

            0 -> Unranked, 1 -> 1v1 Deathmatch, 2 -> Team Deathmatch, 3 -> 1v1 Random Map, 4 -> Team Random Map

        :return:
            the response.text

        :raises Aoe2NetException:
            Either 'search', 'steam_id' or 'profile_id' required.
        """

        if not search and not steam_id and not profile_id:
            raise Aoe2NetException("Either 'search', 'steam_id' or 'profile_id' required.")

        params = {"flag": "false", "search": search, "steam_id": steam_id, "profile_id": profile_id, "leaderboard_id": leaderboard_id}

        return _get_request_response(url=RECENT_OPPONENT_URL, params=params, json=False).text

    def get_current_match(self, search: str = "", steam_id: str = "", profile_id: str = "", leaderboard_id: int = 3, **kwargs):
        """
        Requests details about the last match, or current match if still in game, of a player.

        Either 'search', 'steam_id' or 'profile_id' required.

        The request response is only available as pure text.

        Returns "Player not found", if no player could be found.

        Parameters
        ----------
        search : `str`
            The name of the to be searched player. Returns the highest rated player found.
        steam_id : `str`
            The steamID64 of a player. (ex: 76561199003184910)

            Takes precedence over 'search' and 'profile_id'.
        profile_id : `str`
            The profile ID. (ex: 459658)

            Takes precedence over 'search'.

            Defaults to an empty string.
        leaderboard_id : `int`
            The leaderboard in which to extract data in. Defaults to ID 3 (1v1 RM).

            Is used when 'search' is defined.

            Possible IDs:

            0 -> Unranked, 1 -> 1v1 Deathmatch, 2 -> Team Deathmatch, 3 -> 1v1 Random Map, 4 -> Team Random Map
        **kwargs : `dict`
            Additional optional arguments.

            Possible arguments:

            color : `bool`
                The color the players picked in game to play as. Defaults to False.

        :return:
            the response.text

        :raises Aoe2NetException:
            Either 'search', 'steam_id' or 'profile_id' required.
        """

        if not search and not steam_id and not profile_id:
            raise Aoe2NetException("Either 'search', 'steam_id' or 'profile_id' required.")

        optionals = {
                    "color": False
                    }
        optionals = _is_valid_kwarg(kwargs, optionals)

        params = {"flag": "false", "search": search, "steam_id": steam_id, "profile_id": profile_id, "leaderboard_id": leaderboard_id}
        params.update(optionals)
        color = params.get("color").__str__().lower()
        params["color"] = color

        return _get_request_response(url=CURRENT_MATCH_URL, params=params, json=False).text

    def get_current_civs(self, search: str = "", steam_id: str = "", profile_id: str = "", leaderboard_id: int = 3):
        """
        Requests details about the civilisations from the current (if still in game) or last match.

        Either 'steam_id' or 'profile_id' required.

        The request response is only available as pure text.

        Returns "Player not found", if no player could be found.

        Parameters
        ----------
        search : `str`
            The name of the to be searched player. Returns the highest rated player found.
        steam_id : `str`
            The steamID64 of a player. (ex: 76561199003184910)

            Takes precedence over 'search' and 'profile_id'.
        profile_id : `str`
            The profile ID. (ex: 459658)

            Takes precedence over 'search'.

            Defaults to an empty string.
        leaderboard_id : `int`
            The leaderboard in which to extract data in. Defaults to ID 3 (1v1 RM).

            Is used when 'search' is defined.

            Possible IDs:

            0 -> Unranked, 1 -> 1v1 Deathmatch, 2 -> Team Deathmatch, 3 -> 1v1 Random Map, 4 -> Team Random Map

        :return:
            the response.text

        :raises Aoe2NetException:
            Either 'search', 'steam_id' or 'profile_id' required.
        """

        if not search and not steam_id and not profile_id:
            raise Aoe2NetException("Either 'search', 'steam_id' or 'profile_id' required.")

        params = {"search": search, "steam_id": steam_id, "profile_id": profile_id, "leaderboard_id": leaderboard_id}

        return _get_request_response(url=CURRENT_CIVS_URL, params=params, json=False).text

    def get_current_map(self, search: str = "", steam_id: str = "", profile_id: str = "", leaderboard_id: int = 3):
        """
        Requests the current map name of a player.

        Either 'search', 'steam_id' or 'profile_id' required.

        The request response is only available as pure text.

        Returns "Player not found", if no player could be found.

        Parameters
        ----------
        search : `str`
            The name of the to be searched player. Returns the highest rated player found.
        steam_id : `str`
            The steamID64 of a player. (ex: 76561199003184910)

            Takes precedence over 'search' and 'profile_id'.
        profile_id : `str`
            The profile ID. (ex: 459658)

            Takes precedence over 'search'.

            Defaults to an empty string.
        leaderboard_id : `int`
            The leaderboard in which to extract data in. Defaults to ID 3 (1v1 RM).

            Is used when 'search' is defined.

            Possible IDs:

            0 -> Unranked, 1 -> 1v1 Deathmatch, 2 -> Team Deathmatch, 3 -> 1v1 Random Map, 4 -> Team Random Map

        :return:
            the response.text

        :raises Aoe2NetException:
            Either 'search', 'steam_id' or 'profile_id' required.
        """

        if not search and not steam_id and not profile_id:
            raise Aoe2NetException("Either 'search', 'steam_id' or 'profile_id' required.")

        params = {"search": search, "steam_id": steam_id, "profile_id": profile_id, "leaderboard_id": leaderboard_id}

        return _get_request_response(url=CURRENT_MAP_URL, params=params, json=False).text

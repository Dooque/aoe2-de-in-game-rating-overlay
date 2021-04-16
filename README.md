# Age of Empires II DE - Multiplayer Ratings Overlay

## Download

You can download the latest release from [here](https://github.com/Dooque/aoe2-de-mp-ratings/archive/refs/tags/v0.0.1.zip).

## Introduction

This is an overlay which shows on top of the screen the RM 1v1 ELO and RM TG ELO for all players in a multiplayer game.

It currently works only for "Random Map" games.

You can drag the text anywhere in the in the screen.

The 1v1 ELO is shown between *[ ]* and the TG ELO is shown between *( )*.

![](./res/picture1.png)
![](./res/picture2.png)

## Installation & Configuration

The program requires no installation. Just extract the ZIP file and run the `aoe2de-mp-ratings.exe` file.

The only required configuration you need is to write your [AoE2.net](https://aoe2.net) profile ID into the `AOE2NET_PROFILE_ID.txt` file.

### How to close the program?

After have moved the text around the window and without click anywhere else press `Alt+F4`.

### How do I get my AoE2.net profile ID?

Go to https://aoe2.net/.

Click on "Leaderboards" and pick "Random Map":

![](./res/picture3.png)

On the search section enter your Steam profile name. Once you see yourself in the table click on your name:

> NOTE: If you don't appear in the list it is because you haven't play at least 10 ranked games. You need to play 10 ranked games to have an AoE2.net profile ID.

![](./res/picture4.png)

Click on the "Profile" button at the bottom right of the window:

![](./res/picture5.png)

Then you will see the profile ID in the URL section:

![](./res/picture6.png)

Copy and paste it into the `AOE2NET_PROFILE_ID.txt` file.

And that's it you can run the `aoe2de-mp-ratings.exe` file.

## What's next?

1. Be able to change the text color, font and size from a configuration file.
2. Be able to set a background with solid color from a configuration file.
3. Show the text with the current color of each player in the game.
4. Show the text with the "self (blue) / ally (yellow) / enemy (red)" color mode.
5. Show extended player information when the mouse goes over the player name.
6. Make configurable the refresh time.

## CHANGELOG

### v0.0.1

* Fetch the latest game of the AoE2.net profile ID saved in the `AOE2NET_PROFILE_ID.txt` file.
* Fetch all the players from the latest game.
* Fetch the following information from each player:
  * Random Map 1v1 Rating.
  * Random Map 1v1 number of wins.
  * Random Map 1v1 number of losses.
  * Random Map 1v1 streak.
  * Random Map Team Game Rating.
  * Random Map Team Game number of wins.
  * Random Map Team Game number of losses.
  * Random Map Team Game streak.
* Show some of the information in a transparent window of fixed text font (Arial), size (14) and color. (white).
* The program fetch for a new game every a fixed amount of time (10 seconds).

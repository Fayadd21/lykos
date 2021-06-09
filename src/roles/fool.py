import re
import random
import itertools
import math
from collections import defaultdict
from typing import Optional

from src.utilities import *
from src import channels, users, debuglog, errlog, plog
from src.functions import get_players, get_all_players, get_main_role, get_reveal_role, get_target
from src.decorators import command, event_listener
from src.containers import UserList, UserSet, UserDict, DefaultUserDict
from src.messages import messages
from src.status import try_misdirection, try_exchange

VOTED = None # type: Optional[users.User]

@event_listener("lynch")
def on_lynch(evt, var, votee, voters):
    global VOTED
    if votee in get_all_players(("fool",)):
        # ends game immediately, with fool as only winner
        # hardcode "fool" as the role since game is ending due to them being lynched,
        # so we want to show "fool" even if it's a template
        lmsg = messages["lynch_reveal"].format(votee, "fool")
        VOTED = votee
        channels.Main.send(lmsg)
        from src.wolfgame import chk_win
        chk_win(winner="fool")

        evt.prevent_default = True
        evt.stop_processing = True

@event_listener("chk_win", priority=0)
def on_chk_win(evt, var, rolemap, mainroles, lpl, lwolves, lrealwolves):
    if evt.data["winner"] == "fool":
        evt.data["message"] = messages["fool_win"]

@event_listener("team_win")
def on_team_win(evt, var, player, main_role, all_roles, winner):
    if winner == "fool" and player is VOTED:
        # giving voted fool a team win means that lover can win with them if they're voted
        evt.data["team_win"] = True

@event_listener("player_win")
def on_player_win(evt, var, player, main_role, all_roles, winner, team_win, survived):
    if winner == "fool" and player is VOTED:
        evt.data["individual_win"] = True

@event_listener("send_role")
def on_send_role(evt, var):
    for fool in get_all_players(("fool",)):
        fool.send(messages["fool_notify"])

@event_listener("reset")
def on_reset(evt, var):
    global VOTED
    VOTED = None

@event_listener("get_role_metadata")
def on_get_role_metadata(evt, var, kind):
    if kind == "role_categories":
        evt.data["fool"] = {"Neutral", "Win Stealer", "Innocent"}

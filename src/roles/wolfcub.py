import re
import random
from collections import defaultdict

from src.utilities import *
from src.functions import get_players
from src import debuglog, errlog, plog, users, channels
from src.decorators import command, event_listener
from src.containers import UserList, UserSet, UserDict, DefaultUserDict
from src.messages import messages
from src.status import try_misdirection, try_exchange
from src.cats import Wolf, Killer

from src.roles.helper.wolves import wolf_can_kill, register_wolf, is_known_wolf_ally

register_wolf("wolf cub")
ANGRY_WOLVES = False

@event_listener("wolf_numkills")
def on_wolf_numkills(evt, var, wolf):
    if ANGRY_WOLVES and is_known_wolf_ally(var, wolf, wolf):
        evt.data["numkills"] = max(evt.data["numkills"], 2)

@event_listener("del_player")
def on_del_player(evt, var, player, all_roles, death_triggers):
    if death_triggers and "wolf cub" in all_roles:
        global ANGRY_WOLVES
        ANGRY_WOLVES = True

@event_listener("new_role")
def on_new_role(evt, var, player, old_role):
    if ANGRY_WOLVES and evt.data["in_wolfchat"] and wolf_can_kill(var, player):
        evt.data["messages"].append(messages["angry_wolves"])

@event_listener("wolf_notify")
def on_wolf_notify(evt, var, role):
    if not ANGRY_WOLVES or role not in Wolf & Killer:
        return

    wolves = get_players((role,))
    if not wolves:
        return

    for wofl in wolves:
        if wolf_can_kill(var, wofl):
            wofl.queue_message(messages["angry_wolves"])

    users.User.send_messages()

@event_listener("chk_win", priority=1)
def on_chk_win(evt, var, rolemap, mainroles, lpl, lwolves, lrealwolves):
    did_something = False
    if lrealwolves == 0:
        for wc in list(rolemap["wolf cub"]):
            var.NIGHT_IDLE_EXEMPT.add(wc) # if they grow up during night, don't give them idle warnings
            rolemap["wolf"].add(wc)
            rolemap["wolf cub"].remove(wc)
            if mainroles[wc] == "wolf cub":
                mainroles[wc] = "wolf"
            did_something = True
            if var.PHASE in var.GAME_PHASES:
                # don't set cub's FINAL_ROLE to wolf, since we want them listed in endgame
                # stats as cub still.
                wc.send(messages["cub_grow_up"])
    if did_something:
        evt.prevent_default = True
        evt.stop_processing = True

@event_listener("reconfigure_stats")
def on_reconfigure_stats(evt, var, roleset, reason):
    # if we're making new wolves or there aren't cubs, nothing to do here
    if reason == "howl" or roleset["wolf cub"] == 0:
        return
    for role in Wolf & Killer:
        if roleset[role] > 0:
            break
    else:
        roleset["wolf"] = roleset["wolf cub"]
        roleset["wolf cub"] = 0

@event_listener("transition_day_resolve_end")
def on_transition_day_resolve_end(evt, var, victims):
    global ANGRY_WOLVES
    ANGRY_WOLVES = False

@event_listener("reset")
def on_reset(evt, var):
    global ANGRY_WOLVES
    ANGRY_WOLVES = False

@event_listener("get_role_metadata")
def on_get_role_metadata(evt, var, kind):
    if kind == "role_categories":
        evt.data["wolf cub"] = {"Wolf", "Wolfchat", "Wolfteam", "Wolf Objective"}

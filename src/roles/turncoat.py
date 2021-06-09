import re
import random
import itertools
import math
from collections import defaultdict
from typing import Tuple

from src import channels, users, debuglog, errlog, plog
from src.functions import get_players, get_all_players, match_role
from src.decorators import command, event_listener
from src.containers import UserList, UserSet, UserDict, DefaultUserDict
from src.messages import messages
from src.status import try_misdirection, try_exchange

TURNCOATS = UserDict() # type: UserDict[users.User, Tuple[str, int]]
PASSED = UserSet()

@command("side", chan=False, pm=True, playing=True, phases=("night",), roles=("turncoat",))
def change_sides(var, wrapper, message, sendmsg=True):
    if TURNCOATS[wrapper.source][1] == var.NIGHT_COUNT - 1:
        wrapper.pm(messages["turncoat_already_turned"])
        return

    team = re.split(" +", message)[0]
    team = match_role(var, team, scope=("villager", "wolf"))
    if not team:
        wrapper.pm(messages["turncoat_error"])
        return

    team = team.get().key

    wrapper.pm(messages["turncoat_success"].format(team))
    TURNCOATS[wrapper.source] = (team, var.NIGHT_COUNT)
    PASSED.discard(wrapper.source)
    debuglog("{0} (turncoat) SIDE {1}".format(wrapper.source, team))

@command("pass", chan=False, pm=True, playing=True, phases=("night",), roles=("turncoat",))
def pass_cmd(var, wrapper, message):
    """Decline to use your special power for that night."""
    if TURNCOATS[wrapper.source][1] == var.NIGHT_COUNT:
        # theoretically passing would revert them to how they were before, but
        # we aren't tracking that, so just tell them to change it back themselves.
        wrapper.pm(messages["turncoat_fail"])
        return

    wrapper.pm(messages["turncoat_pass"])
    if TURNCOATS[wrapper.source][1] == var.NIGHT_COUNT - 1:
        # don't add to PASSED since we aren't counting them anyway for nightdone
        # let them still use !pass though to make them feel better or something
        return
    PASSED.add(wrapper.source)

    debuglog("{0} (turncoat) PASS".format(wrapper.source))

@event_listener("send_role")
def on_send_role(evt, var):
    for turncoat in get_all_players(("turncoat",)):
        # they start out as unsided, but can change n1
        if turncoat not in TURNCOATS:
            TURNCOATS[turncoat] = ("none", -1)

        if TURNCOATS[turncoat][0] != "none":
            message = messages["turncoat_current_team"].format(TURNCOATS[turncoat][0])
        else:
            message = messages["turncoat_no_team"]

        if TURNCOATS[turncoat][1] < var.NIGHT_COUNT - 1 or var.NIGHT_COUNT == 0:
            # they can act tonight
            turncoat.send(messages["turncoat_notify"], message)
        else:
            turncoat.send(messages["turncoat_notify_no_act"], message)

@event_listener("chk_nightdone")
def on_chk_nightdone(evt, var):
    # add in turncoats who should be able to act or who passed
    # but if they can act they're in TURNCOATS where the second tuple item is the current night
    # (if said tuple item is the previous night, then they are not allowed to act tonight)
    pl = get_players()
    evt.data["acted"].extend(PASSED)
    for turncoat, (team, night) in TURNCOATS.items():
        if turncoat not in pl:
            continue
        if night == var.NIGHT_COUNT:
            evt.data["nightroles"].append(turncoat)
            evt.data["acted"].append(turncoat)
        elif night < var.NIGHT_COUNT - 1:
            evt.data["nightroles"].append(turncoat)

@event_listener("team_win")
def on_team_win(evt, var, player, main_role, all_roles, winner):
    if main_role == "turncoat" and player in TURNCOATS and TURNCOATS[player][0] != "none":
        team = "villagers" if TURNCOATS[player][0] == "villager" else "wolves"
        evt.data["team_win"] = (winner == team)

@event_listener("myrole")
def on_myrole(evt, var, user):
    if evt.data["role"] == "turncoat" and user in TURNCOATS:
        key = "turncoat_current_no_team"
        if TURNCOATS[user][0] != "none":
            key = "turncoat_current_team"
        evt.data["messages"].append(messages[key].format(TURNCOATS[user][0]))

@event_listener("revealroles_role")
def on_revealroles_role(evt, var, user, role):
    if role == "turncoat" and user in TURNCOATS:
        if TURNCOATS[user][0] == "none":
            evt.data["special_case"].append(messages["turncoat_revealroles_none"])
        else:
            evt.data["special_case"].append(messages["turncoat_revealroles"].format(TURNCOATS[user][0]))

@event_listener("new_role")
def on_new_role(evt, var, player, old_role):
    if old_role == "turncoat" and evt.data["role"] != "turncoat":
        del TURNCOATS[player]
    elif evt.data["role"] == "turncoat" and old_role != "turncoat":
        TURNCOATS[player] = ("none", -1)

@event_listener("swap_role_state")
def on_swap_role_state(evt, var, actor, target, role):
    if role == "turncoat":
        TURNCOATS[actor], TURNCOATS[target] = TURNCOATS.pop(target), TURNCOATS.pop(actor)
        for user, to_send in ((actor, "actor_messages"), (target, "target_messages")):
            key = "turncoat_current_no_team"
            if TURNCOATS[user][0] != "none":
                key = "turncoat_current_team"
            evt.data[to_send].append(messages[key].format(TURNCOATS[user][0]))

@event_listener("begin_day")
def on_begin_day(evt, var):
    PASSED.clear()

@event_listener("reset")
def on_reset(evt, var):
    PASSED.clear()
    TURNCOATS.clear()

@event_listener("get_role_metadata")
def on_get_role_metadata(evt, var, kind):
    if kind == "role_categories":
        evt.data["turncoat"] = {"Neutral", "Team Switcher"}

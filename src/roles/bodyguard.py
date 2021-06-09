from __future__ import annotations

import re
import random
import itertools
import math
from collections import defaultdict
from typing import Set

import src.settings as var
from src.utilities import *
from src import channels, debuglog, errlog, plog
from src.functions import get_players, get_all_players, get_target, get_main_role
from src.decorators import command, event_listener
from src.containers import UserList, UserSet, UserDict, DefaultUserDict
from src.messages import messages
from src.status import try_misdirection, try_exchange, add_protection, add_dying
from src.cats import Wolf
from src.users import User

GUARDED: UserDict[User, User] = UserDict()
PASSED = UserSet()
DYING = UserSet()

@command("guard", chan=False, pm=True, playing=True, silenced=True, phases=("night",), roles=("bodyguard",))
def guard(var, wrapper, message):
    """Guard a player, preventing them from being killed that night."""
    if wrapper.source in GUARDED:
        wrapper.pm(messages["already_protecting"])
        return

    target = get_target(var, wrapper, re.split(" +", message)[0], not_self_message="cannot_guard_self")
    if not target:
        return

    target = try_misdirection(var, wrapper.source, target)
    if try_exchange(var, wrapper.source, target):
        return

    add_protection(var, target, wrapper.source, "bodyguard")
    GUARDED[wrapper.source] = target

    wrapper.pm(messages["protecting_target"].format(target))
    target.send(messages["target_protected"])

    debuglog("{0} (bodyguard) GUARD: {1} ({2})".format(wrapper.source, target, get_main_role(target)))

@command("pass", chan=False, pm=True, playing=True, phases=("night",), roles=("bodyguard",))
def pass_cmd(var, wrapper, message):
    """Decline to use your special power for that night."""
    if wrapper.source in GUARDED:
        wrapper.pm(messages["already_protecting"])
        return
    PASSED.add(wrapper.source)
    wrapper.pm(messages["guardian_no_protect"])
    debuglog("{0} (bodyguard) PASS".format(wrapper.source))

@event_listener("del_player")
def on_del_player(evt, var, player, all_roles, death_triggers):
    if var.PHASE == "night" and player in GUARDED:
        GUARDED[player].send(messages["protector_disappeared"])
    for k,v in list(GUARDED.items()):
        if player in (k, v):
            del GUARDED[k]
    PASSED.discard(player)

@event_listener("new_role")
def on_new_role(evt, var, player, old_role):
    if old_role == "bodyguard" and evt.data["role"] != "bodyguard":
        if player in GUARDED:
            guarded = GUARDED.pop(player)
            guarded.send(messages["protector_disappeared"])

@event_listener("chk_nightdone")
def on_chk_nightdone(evt, var):
    evt.data["acted"].extend(GUARDED)
    evt.data["acted"].extend(PASSED)
    evt.data["nightroles"].extend(get_players(("bodyguard",)))

@event_listener("transition_day_resolve_end", priority=3)
def on_transition_day_resolve_end(evt, var, victims):
    for bodyguard in DYING:
        evt.data["message"][bodyguard].clear()
    DYING.clear()
    for bodyguard in get_all_players(("bodyguard",)):
        if GUARDED.get(bodyguard) in get_players(Wolf) and bodyguard not in evt.data["dead"]:
            r = random.random()
            if r < var.BODYGUARD_DIES_CHANCE:
                if var.ROLE_REVEAL == "on":
                    evt.data["message"][bodyguard].append(messages["bodyguard_protected_wolf"].format(bodyguard))
                else: # off and team
                    evt.data["message"][bodyguard].append(messages["bodyguard_protection"].format(bodyguard))
                evt.data["dead"].append(bodyguard)

@event_listener("transition_night_begin")
def on_transition_night_begin(evt, var):
    # needs to be here in order to allow bodyguard protections to work during the daytime
    # (right now they don't due to other reasons, but that may change)
    GUARDED.clear()

@event_listener("send_role")
def on_send_role(evt, var):
    ps = get_players()
    for bg in get_all_players(("bodyguard",)):
        pl = ps[:]
        random.shuffle(pl)
        pl.remove(bg)
        chance = math.floor(var.BODYGUARD_DIES_CHANCE * 100)

        bg.send(messages["bodyguard_notify"])
        if var.NIGHT_COUNT == 0:
            return
        if chance > 0:
            bg.send(messages["bodyguard_death_chance"].format(chance))
        bg.send(messages["players_list"].format(pl))

@event_listener("try_protection")
def on_try_protection(evt, var, target, attacker, attacker_role, reason):
    if len(evt.data["protections"]) <= 1: # We only care if there's 2+ protections
        return
    for (protector, protector_role, scope) in list(evt.data["protections"]):
        if protector_role == "bodyguard":
            evt.data["protections"].remove((protector, protector_role, scope))
            evt.data["protections"].append((protector, protector_role, scope))

@event_listener("player_protected")
def on_player_protected(evt, var, target, attacker, attacker_role, protector, protector_role, reason):
    if protector_role == "bodyguard":
        evt.data["messages"].append(messages[reason + "_bodyguard"].format(attacker, target, protector))
        add_dying(var, protector, killer_role=attacker_role, reason="bodyguard")
        if var.PHASE == "night" and var.GAMEPHASE == "day": # currently transitioning
            DYING.add(protector)

@event_listener("remove_protection")
def on_remove_protection(evt, var, target, attacker, attacker_role, protector, protector_role, reason):
    if attacker_role == "fallen angel" and protector_role == "bodyguard":
        evt.data["remove"] = True
        add_dying(var, protector, killer_role="fallen angel", reason=reason)
        protector.send(messages[reason + "_success"].format(target))
        target.send(messages[reason + "_deprotect"])

@event_listener("begin_day")
def on_begin_day(evt, var):
    PASSED.clear()

@event_listener("reset")
def on_reset(evt, var):
    GUARDED.clear()
    PASSED.clear()
    DYING.clear()

@event_listener("get_role_metadata")
def on_get_role_metadata(evt, var, kind):
    if kind == "role_categories":
        evt.data["bodyguard"] = {"Village", "Safe", "Nocturnal"}

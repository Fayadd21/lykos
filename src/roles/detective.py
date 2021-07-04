from __future__ import annotations

import math
import re
import random
import typing

from src.utilities import *
from src import users, channels, errlog, plog
from src.functions import get_players, get_all_players, get_main_role, get_target
from src.decorators import command, event_listener
from src.containers import UserList, UserSet, UserDict, DefaultUserDict
from src.messages import messages
from src.status import try_misdirection, try_exchange
from src.events import Event

from src.roles.helper.wolves import get_wolfchat_roles

if typing.TYPE_CHECKING:
    from src.dispatcher import MessageDispatcher

INVESTIGATED = UserSet()

@command("id", chan=False, pm=True, playing=True, silenced=True, phases=("day",), roles=("detective",))
def investigate(wrapper: MessageDispatcher, message: str):
    """Investigate a player to determine their exact role."""
    if wrapper.source in INVESTIGATED:
        wrapper.send(messages["already_investigated"])
        return

    var = wrapper.game_state

    target = get_target(wrapper, re.split(" +", message)[0], not_self_message="no_investigate_self")
    if target is None:
        return

    target = try_misdirection(var, wrapper.source, target)
    if try_exchange(var, wrapper.source, target):
        return

    targrole = get_main_role(var, target)

    evt = Event("investigate", {"role": targrole})
    evt.dispatch(var, wrapper.source, target)
    targrole = evt.data["role"]

    INVESTIGATED.add(wrapper.source)
    wrapper.send(messages["investigate_success"].format(target, targrole))

    if random.random() < var.DETECTIVE_REVEALED_CHANCE:  # a 2/5 chance (changeable in settings)
        # The detective's identity is compromised!
        wolves = get_all_players(var, get_wolfchat_roles(var))
        if wolves:
            for wolf in wolves:
                wolf.queue_message(messages["detective_reveal"].format(wrapper.source))
            wolf.send_messages()

@event_listener("del_player")
def on_del_player(evt, var, player, all_roles, death_triggers):
    INVESTIGATED.discard(player)

@event_listener("new_role")
def on_new_role(evt, var, user, old_role):
    if old_role == "detective" and evt.data["role"] != "detective":
        INVESTIGATED.discard(user)

@event_listener("send_role")
def on_send_role(evt, var):
    ps = get_players(var)
    for dttv in var.ROLES["detective"]:
        pl = ps[:]
        random.shuffle(pl)
        pl.remove(dttv)
        chance = math.floor(var.DETECTIVE_REVEALED_CHANCE * 100)

        dttv.send(messages["detective_notify"])
        if chance > 0:
            dttv.send(messages["detective_chance"].format(chance))
        dttv.send(messages["players_list"].format(pl))

@event_listener("transition_night_begin")
def on_transition_night_begin(evt, var):
    INVESTIGATED.clear()

@event_listener("reset")
def on_reset(evt, var):
    INVESTIGATED.clear()

@event_listener("get_role_metadata")
def on_get_role_metadata(evt, var, kind):
    if kind == "role_categories":
        evt.data["detective"] = {"Village", "Spy", "Safe"}

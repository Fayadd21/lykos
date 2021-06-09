import re
import random
import itertools
import math
from collections import defaultdict

from src.utilities import *
from src import channels, users, debuglog, errlog, plog
from src.functions import get_players, get_all_players, get_main_role, get_reveal_role, get_target, match_role
from src.decorators import command, event_listener
from src.containers import UserList, UserSet, UserDict, DefaultUserDict
from src.messages import messages
from src.status import try_misdirection, try_exchange

PRAYED = UserSet()


@command("pray", chan=False, pm=True, playing=True, silenced=True, phases=("night",), roles=("prophet",))
def pray(var, wrapper, message):
    """Receive divine visions of who has a role."""
    if wrapper.source in PRAYED:
        wrapper.pm(messages["already_prayed"])
        return

    if not message:
        wrapper.pm(messages["not_enough_parameters"])
        return

    # complete this as a match with other roles (so "cursed" can match "cursed villager" for instance)
    matches = match_role(var, message, allow_special=False)
    if len(matches) == 0:
        wrapper.pm(messages["no_such_role"].format(message))
        return
    elif len(matches) > 1:
        wrapper.pm(messages["ambiguous_role"].format([m.singular for m in matches]))
        return

    role = matches.get().key
    pl = get_players()
    PRAYED.add(wrapper.source)

    # this sees through amnesiac, so the amnesiac's final role counts as their role
    from src.roles.amnesiac import ROLES as amn_roles
    people = set(get_all_players((role,))) | {p for p, r in amn_roles.items() if p in pl and r == role}
    if len(people) == 0:
        # role is not in this game, this still counts as a successful activation of the power!
        wrapper.pm(messages["vision_none"].format(role))
        debuglog("{0} (prophet) PRAY {1} - NONE".format(wrapper.source, role))
        return

    target = random.choice(list(people))
    part = random.sample([p for p in pl if p is not wrapper.source], len(pl) // 3)
    if target not in part:
        part[0] = target
    random.shuffle(part)

    if len(part) == 1:
        wrapper.pm(messages["vision_role"].format(role, target))
    else:
        wrapper.pm(messages["vision_players"].format(role, part))
    debuglog("{0} (prophet) PRAY {1} ({2})".format(wrapper.source, role, target))


@event_listener("send_role")
def on_send_role(evt, var):
    for pht in get_all_players(("prophet",)):
        pht.send(messages["prophet_notify"])

@event_listener("chk_nightdone")
def on_chk_nightdone(evt, var):
    evt.data["nightroles"].extend(get_all_players(("prophet",)))
    evt.data["acted"].extend(PRAYED)

@event_listener("begin_day")
def on_begin_day(evt, var):
    PRAYED.clear()

@event_listener("reset")
def on_reset(evt, var):
    PRAYED.clear()

@event_listener("get_role_metadata")
def on_get_role_metadata(evt, var, kind):
    if kind == "role_categories":
        evt.data["prophet"] = {"Village", "Safe", "Nocturnal", "Spy"}

import re
import random
import itertools
import math
from collections import defaultdict

from src.utilities import *
from src import channels, users, debuglog, errlog, plog
from src.functions import get_players, get_all_players, get_main_role, get_reveal_role, get_target
from src.decorators import command, event_listener
from src.containers import UserList, UserSet, UserDict, DefaultUserDict
from src.messages import messages
from src.status import try_misdirection, try_exchange
from src.cats import Hidden

@event_listener("send_role")
def on_send_role(evt, var):
    if not var.ROLES_SENT or var.ALWAYS_PM_ROLE:
        cultroles = {"cultist"}
        if var.HIDDEN_ROLE == "cultist":
            cultroles |= Hidden
        cultists = get_players(cultroles)
        if cultists:
            for cultist in cultists:
                cultist.queue_message(messages["cultist_notify"])
            cultist.send_messages()

@event_listener("chk_win", priority=3)
def on_chk_win(evt, var, rolemap, mainroles, lpl, lwolves, lrealwolves):
    if evt.data["winner"] is not None:
        return
    if lwolves == lpl / 2:
        evt.data["winner"] = "wolves"
        evt.data["message"] = messages["wolf_win_equal"]
    elif lwolves > lpl / 2:
        evt.data["winner"] = "wolves"
        evt.data["message"] = messages["wolf_win_greater"]

@event_listener("get_role_metadata")
def on_get_role_metadata(evt, var, kind):
    if kind == "role_categories":
        evt.data["cultist"] = {"Wolfteam"}

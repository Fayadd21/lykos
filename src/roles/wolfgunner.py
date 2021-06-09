import math

from src.events import Event, find_listener
from src.functions import get_players, get_all_players
from src.decorators import event_listener
from src.messages import messages

from src.roles.helper.gunners import setup_variables
from src.roles.helper.wolves import register_wolf, is_known_wolf_ally

register_wolf("wolf gunner")
GUNNERS = setup_variables("wolf gunner")
# unregister the gunner night message and send the number of bullets a different way
find_listener("send_role", "gunners.<wolf gunner>.on_send_role").remove("send_role")
# wolf gunners don't shoot other wolves at night nor get their gun stolen
find_listener("transition_day_resolve_end", "gunners.<wolf gunner>.on_transition_day_resolve_end").remove("transition_day_resolve_end")

@event_listener("wolf_notify")
def on_wolf_notify(evt, var, role):
    if role != "wolf gunner":
        return
    gunners = get_all_players(("wolf gunner",))
    for gunner in gunners:
        if GUNNERS[gunner] or var.ALWAYS_PM_ROLE:
            gunner.send(messages["gunner_bullets"].format(GUNNERS[gunner]))

@event_listener("gun_shoot")
def on_gun_shoot(evt, var, player, target, role):
    if role == "wolf gunner" and is_known_wolf_ally(var, player, target):
        evt.data["hit"] = False

@event_listener("get_role_metadata")
def on_get_role_metadata(evt, var, kind):
    if kind == "role_categories":
        evt.data["wolf gunner"] = {"Wolf", "Wolfchat", "Wolfteam", "Killer", "Nocturnal", "Village Objective", "Wolf Objective"}

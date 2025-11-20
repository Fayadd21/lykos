from src.events import Event, event_listener
from src.functions import get_all_roles
from src.gamestate import GameState
from src.roles.helper.wolves import register_wolf
from src.users import User

register_wolf("werekitten")


@event_listener("gun_shoot")
def on_gun_shoot(evt: Event, var: GameState, user: User, target: User, role: str):
    if "werekitten" in get_all_roles(var, target):
        evt.data["hit"] = False
        evt.data["kill"] = False


@event_listener("get_role_metadata")
def on_get_role_metadata(evt: Event, var: GameState | None, kind: str):
    if kind == "role_categories":
        evt.data["werekitten"] = {
            "Wolf",
            "Wolfchat",
            "Wolfteam",
            "Innocent",
            "Killer",
            "Nocturnal",
            "Village Objective",
            "Wolf Objective",
            "Evil",
        }

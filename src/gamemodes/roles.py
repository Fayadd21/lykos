from collections import Counter
from src.gamemodes import game_mode, GameMode, InvalidModeException
from src.messages import messages
from src import events, channels, users, cats, config

@game_mode("roles", minp=4, maxp=35)
class ChangedRolesMode(GameMode):
    """Example: !fgame roles=wolf:1,seer:0,guardian angel:1"""

    def __init__(self, arg=""):
        super().__init__(arg)
        self.MAX_PLAYERS = 35
        self.ROLE_GUIDE = {1: []}
        self.SECONDARY_ROLES = {}
        arg = arg.replace("=", ":").replace(";", ",")

        pairs = [arg]
        while pairs:
            pair, *pairs = pairs[0].split(",", 1)
            change = pair.lower().replace(":", " ").strip().rsplit(None, 1)
            if len(change) != 2:
                raise InvalidModeException(messages["invalid_mode_roles"].format(arg))
            role, num = change
            try:
                if "/" in role:
                    choose = role.split("/")
                    for c in choose:
                        if c not in cats.ROLES:
                            raise InvalidModeException(messages["specific_invalid_role"].format(c))
                        elif c in config.Main.get("gameplay.disable.roles"):
                            raise InvalidModeException(messages["role_disabled"].format(c))
                    self.ROLE_SETS[role] = Counter(choose)
                    self.ROLE_GUIDE[1].extend((role,) * int(num))
                elif role == "default" and num in cats.ROLES:
                    self.DEFAULT_ROLE = num
                elif role == "hidden" and num in ("villager", "cultist"):
                    self.HIDDEN_ROLE = num
                elif role in ("role reveal", "stats", "abstain"):
                    # handled in parent constructor
                    pass
                else:
                    if role[0] == "$":
                        role = role[1:]
                        self.SECONDARY_ROLES[role] = cats.All
                    if role in config.Main.get("gameplay.disable.roles"):
                        raise InvalidModeException(messages["role_disabled"].format(role))
                    elif role in cats.ROLES:
                        self.ROLE_GUIDE[1].extend((role,) * int(num))
                    else:
                        raise InvalidModeException(messages["specific_invalid_role"].format(role))
            except ValueError:
                raise InvalidModeException(messages["bad_role_value"].format(role, num))

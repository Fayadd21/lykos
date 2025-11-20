# Enforce a strict import ordering to ensure things are properly defined when they need to be

# This "bootstraps" the bot in preparation for importing the bulk of the code. Some imports
# change behavior based on whether or not we're in debug mode, so that must be established before
# we continue on to import other files
from src import config, lineparse, locks, match, random

# Initialize config.Main
config.init()

# Initialize logging framework
from src import logger

logger.init()

# Files with dependencies only on things imported in previous lines, in order
# The top line must only depend on things imported above in our "no dependencies" block
# Import the user-defined roles, as well as builtins if custom roles don't exist or they want them
import roles as custom_roles  # type: ignore
from src import (
    cats,
    channels,
    containers,
    context,
    db,
    debug,
    decorators,
    dispatcher,
    events,
    functions,
    game_stats,
    gamecmds,
    gamejoin,
    gamemodes,
    gamestate,
    handler,
    hooks,
    locations,
    messages,
    pregame,
    reaper,
    relay,
    roles,
    status,
    trans,
    transport,
    users,
    votes,
    warnings,
    wolfgame,
)

if not getattr(custom_roles, "CUSTOM_ROLES_DEFINED", False):
    roles.import_builtin_roles()

# Import the user-defined modes, as well as builtins if custom modes don't exist or they want them
import gamemodes as custom_gamemodes  # type: ignore

if not getattr(custom_gamemodes, "CUSTOM_MODES_DEFINED", False):
    gamemodes.import_builtin_modes()

# Import user-defined hooks
import hooks as custom_hooks  # type: ignore

# Perform final initialization
events.Event("init", {}).dispatch()

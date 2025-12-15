#!/usr/bin/env python3
import os
import signal
import sys
import time
from pathlib import Path

# create status file to indicate bot is running
status_file = Path("logs/.bot_running")
status_file.parent.mkdir(exist_ok=True)


# cleanup on exit
def cleanup(signum=None, frame=None):
    if status_file.exists():
        status_file.unlink()
    sys.exit(0)


# register cleanup handlers
signal.signal(signal.SIGTERM, cleanup)
signal.signal(signal.SIGINT, cleanup)

try:
    # keep updating the status file to show bot is alive
    while True:
        # write current timestamp to status file
        status_file.write_text(str(time.time()))
        time.sleep(10)  # update every 10 seconds
except Exception:
    cleanup()

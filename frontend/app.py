import os
import time

from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index():
    # check if backend is running by looking for status file
    bot_status = "Stopped"
    current_time = time.time()

    # check both docker and local paths for status file
    status_paths = ["/app/logs/.bot_running", "../logs/.bot_running"]

    for status_path in status_paths:
        if os.path.exists(status_path):
            try:
                # read timestamp from status file
                with open(status_path) as f:
                    timestamp = float(f.read().strip())

                # if timestamp is recent (within 30 seconds), bot is running
                age = current_time - timestamp
                if age < 30:
                    bot_status = "Running"
                    break
            except Exception:
                pass

    return render_template("index.html", status=bot_status)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

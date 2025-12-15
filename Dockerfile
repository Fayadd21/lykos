FROM python:3.11-slim

WORKDIR /app

# install poetry
RUN pip install poetry

# copy the dependency files first
COPY pyproject.toml poetry.lock* ./

# install dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-root

# copy everything else
COPY . .

# create required directories
RUN mkdir -p logs data

# start heartbeat and bot, cleanup status file on exit
CMD ["bash", "-c", "trap 'rm -f logs/.bot_running' EXIT; python heartbeat.py & python wolfbot.py"]

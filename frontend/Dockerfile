FROM python:3.11-slim

WORKDIR /app

# install poetry
RUN pip install poetry

# copy dependency file
COPY pyproject.toml ./

# install flask and other dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-root

# copy the web app
COPY app.py .
COPY templates/ templates/

# create logs directory
RUN mkdir -p logs

# start the web server on port 8080
CMD ["python", "app.py"]

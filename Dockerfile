FROM debian:12-slim

ARG TZ=$TZ

RUN apt-get update && \
    apt-get install --no-install-suggests --no-install-recommends --yes \
    python3 \
    pipx \
    python-is-python3 \
    cron

ENV PATH="/root/.local/bin:${PATH}"

RUN pipx install poetry
RUN pipx inject poetry poetry-plugin-bundle

WORKDIR /src
COPY pyproject.toml poetry.lock crontab .
COPY planningpod_stats/ planningpod_stats/
RUN poetry bundle venv --python=/usr/bin/python3 --only=main /venv

RUN crontab crontab


CMD ["cron", "-f"]
#ENTRYPOINT ["/venv/bin/planningpod-stats"]
#ENTRYPOINT ["tail", "-f", "/dev/null"]

FROM python:3.7.3-alpine3.9

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=0.12.17

#System deps
RUN apk --no-cache add \
    zip \
    curl \
    tini \
 && curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python
ENV PATH="/root/.poetry/bin:$PATH"

# Copy only requirements to cache them in docker layer
WORKDIR /code
COPY poetry.lock pyproject.toml /code/

# Project initialization:
RUN poetry config settings.virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

COPY . /code

ENTRYPOINT ["/sbin/tini", "--"]
EXPOSE 8080
CMD ["python", "server.py"]
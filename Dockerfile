FROM python3.10

RUN mkdir ./app

COPY ./truck_counting ./app
COPY pyproject.toml ./app

WORKDIR /app
ENV PYTHONPATH=${PYTHONPATH}:${PWD}

RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

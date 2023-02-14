FROM python:3.10

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1

RUN apt-get update && apt-get install -y libpq-dev

WORKDIR /app

RUN pip install pipenv

COPY . .

RUN pipenv install --deploy

CMD ["/bin/bash", "-c", "make run"]

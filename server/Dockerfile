FROM python:3.10.12

ENV PYTHONUNBUFFERED 1

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENV APP_HOME /root
WORKDIR $APP_HOME
COPY /src $APP_HOME/src

EXPOSE 8000

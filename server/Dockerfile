FROM python:3.10.12
ENV INSTANCE_CONNECTION_NAME "chess-app-server:europe-west1:chess-app-db"
ENV DB_USER "postgres"
ENV DB_PASS "oBz{vzL7b(smjnp7"
ENV DB_NAME "chess_db"

ENV PYTHONUNBUFFERED True

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r  requirements.txt

ENV APP_HOME /root
WORKDIR $APP_HOME
COPY /src $APP_HOME/src

EXPOSE 8080
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]


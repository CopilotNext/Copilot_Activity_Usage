FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY static/*.png static/
COPY data/org.csv data/
COPY . .

CMD [ "python3", "app.py" ]
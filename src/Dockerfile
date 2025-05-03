FROM python:3.10.5 

RUN mkdir /usr/app
WORKDIR /usr/app

COPY . .

RUN pip install -r requirements.txt
RUN python3 seed.py

CMD python3 app.py
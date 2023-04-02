FROM python:3.9.10

EXPOSE 5000

EXPOSE 8081

Expose 8080

COPY . .

RUN cd Api && pip install -r requirements.txt

RUN cd ../SessionProcessor && pip install -r requirements.txt 
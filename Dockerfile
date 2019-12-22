FROM python:3.8

#RUN useradd -g root -u 61000 -m  www
#RUN mkdir /www; chown www:www /www; chown www:www /home/www
#USER www

WORKDIR /www
COPY . .
RUN pip install flask
RUN pip install -r requirements.txt

CMD ["python", "application.py"]


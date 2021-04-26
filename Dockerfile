FROM python:3.9

EXPOSE 80

RUN mkdir /data
VOLUME ["/data"]

COPY . /app
ADD templates /app/

RUN pip install -r /app/requirements.txt

WORKDIR /app

CMD ["python", "/app/main.py"]

FROM python:3.9

COPY * /app/
COPY data/ /

RUN pip install -r /app/requirements.txt

CMD ["python", "/app/main.py"]

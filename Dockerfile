FROM python:3.9-slim

RUN apt-get update && apt-get install -y git

COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY main.py /app/main.py

ENTRYPOINT ["python", "/app/main.py"]

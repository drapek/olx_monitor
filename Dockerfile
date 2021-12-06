FROM python:3.9-bullseye

WORKDIR /app

COPY . .
RUN pip install --no-cache-dir --no-deps -r requriements.txt

WORKDIR /app/src
CMD [ "python3", "main.py"]

FROM python:3

WORKDIR /usr/src/app

# Install curl
RUN apt-get update && apt-get install -y curl

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
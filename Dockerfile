FROM python:3.9
LABEL authors="humadi"

WORKDIR /docker_api

# Install system dependencies for OpenCV
RUN apt-get update && \
    apt-get install -y libgl1-mesa-glx && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
COPY ./src ./src
COPY ./samples ./samples

RUN pip install -r requirements.txt

CMD ["python", "./src/main.py"]

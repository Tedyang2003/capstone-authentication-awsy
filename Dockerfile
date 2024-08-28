FROM python:3.10-slim-bullseye

# All in one line for single layer instruction
RUN apt-get update \ 
    && apt-get upgrade \
    && apt-get install pkg-config -y \
    && apt-get install -y --no-install-recommends --no-install-suggests \
    build-essential default-libmysqlclient-dev \
    && pip install --no-cache-dir --upgrade pip

# Create /app, out requirements inside, install, add rest of app
# Seperare the pip to optimise cache and prevent reinstallation
WORKDIR /app
COPY ./requirements.txt /app
RUN pip install --no-cache-dir --requirement /app/requirements.txt
COPY . /app

# Just a documentation
EXPOSE 5000

# Run the command
CMD ["python3", "server.py"]
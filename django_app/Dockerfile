# pull official base image
FROM python:3.11.4-slim-buster

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update && apt-get install -y netcat && apt-get install -y cron supervisor dos2unix && rm -rf /var/lib/apt/lists/*

# Verify that cron is installed
RUN which cron && which crontab

# install dependencies
RUN pip install --upgrade pip
RUN pip install ruff==0.0.290
COPY . /usr/src/app/
RUN ruff check . --ignore E501
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# Add the cron job for the dev environment
COPY ./cronjob.dev /etc/cron.d/my-cron-job
RUN chmod 0644 /etc/cron.d/my-cron-job
RUN crontab /etc/cron.d/my-cron-job

# Copy the supervisor configuration file
COPY ./supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Run supervisor to start both the Telegram bot and Django app
CMD ["/usr/bin/supervisord"]

# copy entrypoint.sh
COPY ./entrypoint.sh .
# Convert line endings in case its from a Windows environment
RUN dos2unix /usr/src/app/entrypoint.sh
RUN sed -i 's/\r$//g' /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh

# copy project
COPY . .

# run entrypoint.sh
# ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
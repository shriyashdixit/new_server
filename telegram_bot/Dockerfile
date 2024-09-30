# Dockerfile for the Telegram bot
FROM python:3.9-slim

# Set the working directory
WORKDIR /usr/src/bot

# Copy project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the bot script
CMD ["python", "bot.py"]

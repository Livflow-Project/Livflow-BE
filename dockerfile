# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3-slim

EXPOSE 8000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install Poetry
RUN pip install poetry

# Set the working directory
WORKDIR /app

# Copy pyproject.toml and poetry.lock first to leverage Docker cache
COPY pyproject.toml poetry.lock /app/

# Install dependencies using Poetry, disabling the virtual environment
RUN poetry config virtualenvs.create false && poetry install

# Copy the rest of the application code
COPY . /app

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# Set the default command to run the application with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi"]

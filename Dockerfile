FROM python:latest

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
ENTRYPOINT "python manage.py runserver"


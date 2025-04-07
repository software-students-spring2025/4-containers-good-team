FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y python3 python3-venv python3-dev

COPY Pipfile Pipfile.lock ./
RUN pip install pipenv && pipenv install --system --deploy

COPY . .

EXPOSE 5001

CMD ["python", "main.py"]

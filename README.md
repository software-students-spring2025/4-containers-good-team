![Lint-free](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/lint.yml/badge.svg)
[![Machine Learning Client CI](https://github.com/software-students-spring2025/4-containers-good-team/actions/workflows/ml-client-ci.yml/badge.svg)](https://github.com/software-students-spring2025/4-containers-good-team/actions/workflows/ml-client-ci.yml)
[![Web App CI](https://github.com/software-students-spring2025/4-containers-good-team/actions/workflows/wep-app-ci.yml/badge.svg)](https://github.com/software-students-spring2025/4-containers-good-team/actions/workflows/wep-app-ci.yml)


# Microphone Translation App

This containerized application captures speech input through a web interface, transcribes it to text, and translates it into another language using a machine learning client. The system is split into modular services that communicate through a shared MongoDB database.



## Components

### Web App (Flask)
- Collects voice input from the user
- Submits raw text and language preferences to the database
- Displays original and translated results

### Machine Learning Client
- Monitors the database for untranslated entries
- Uses `googletrans` to translate text
- Updates the database with translated output

### MongoDB (via Docker)
- Stores all input and output text documents
- Serves as the message bus between services


## Features
- Voice input for language translation
- Real-time interaction between services
- MongoDB integration for asynchronous communication
- Fully containerized setup for consistent local and deployment environments

## Getting Started

### Requirements
- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Python](https://www.python.org/downloads/)

---

### Run with Docker

Clone the repository:
```shell
git clone https://github.com/software-students-spring2025/4-containers-good-team.git
```

Set up your .env:
```
cp .env.example .env
```

Replace the template URI with your MongoDB connection string

Run the command:
```shell
docker-compose up --build
```

This will start all three services:
- Machine Learning Client
- Flask web app
- MongoDB database

Access the web app at [http://localhost:5050](http://localhost:5050)


## Team Members

- [Isaac Vivar](https://github.com/isaacv3)
- [Ethan Yu](https://github.com/ethanyuu910)
- [Giulia Carvalho](https://github.com/giulia-carvalho)
- [Margarita Billi](https://github.com/pinkmaggs)



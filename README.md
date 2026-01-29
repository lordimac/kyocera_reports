# Kyocera Printer Reports Analyzer

A web application to analyze Kyocera printer XML logs fetched from POP3 emails, store data in a database, and provide statistical reports.

## Features

- Fetch XML logs from POP3 mailbox
- Parse and store job data without duplicates
- Identify printer based on email body
- Statistical analysis and reporting
- Dockerized setup

## Setup

1. Clone the repository
2. Copy `.env.example` to `.env` and configure POP3 settings
3. Run with Docker Compose: `docker-compose up --build`
4. Or run locally: `python app.py`

## Usage

Access the web interface at http://localhost:5000

## Manual Testing

Run `python test.py` to parse the included XML file and populate the database.
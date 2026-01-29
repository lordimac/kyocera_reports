# Kyocera Printer Reports Analyzer

A web application to analyze Kyocera printer XML logs fetched from POP3 emails, store data in a database, and provide statistical reports.

## Features

- Fetch XML logs from POP3 mailbox
- Parse and store job data without duplicates
- Identify printer based on email body
- Statistical analysis and reporting with filtering, sorting, and pagination
- Bulk deletion of jobs
- Dockerized setup with automated GitHub Actions builds

## Setup

### Docker Setup (Recommended)

1. Clone the repository
2. Create a `data` directory for persistent storage:
   ```bash
   mkdir data
   ```
3. Copy `.env.example` to `.env` and configure POP3 settings:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```
4. Pull and run the latest image from GitHub Container Registry:
   ```bash
   docker-compose pull
   docker-compose up
   ```

### Local Development Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and configure settings
5. Run the application:
   ```bash
   python app.py
   ```

## Usage

Access the web interface at http://localhost:5000

### Features:
- **Dashboard**: View all printers and their statistics
- **Job Statistics**: Filter by user and color mode, sort by any column
- **Pagination**: View 50, 100, 250, or 500 jobs per page
- **Bulk Actions**: Select multiple jobs and delete them at once
- **Email Fetch**: Manually trigger email fetching or wait for automatic 10-minute intervals

## Manual Testing

Run `python test.py` to parse the included XML file and populate the database.

## Docker Image

The Docker image is automatically built via GitHub Actions and available at:
```
ghcr.io/lordimac/kyocera_reports:latest
```

## Environment Variables

- `SQLALCHEMY_DATABASE_URI`: Database connection string (default: `sqlite:///data/kyocera_reports.db`)
- `POP3_SERVER`: POP3 server hostname
- `POP3_PORT`: POP3 server port (default: 995)
- `POP3_USERNAME`: POP3 username
- `POP3_PASSWORD`: POP3 password
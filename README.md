# Insta Engagement Analysis

## Overview
**Insta Engagement Analysis** is a Python-based project that scrapes Instagram profile data, fetches post details, and analyzes engagement metrics. The project stores data in a MySQL database and provides visualization tools to interpret user interactions.

## Features
- Fetch Instagram profile data (username, followers, bio, etc.).
- Retrieve posts along with likes, comments, and captions.
- Store and manage data in a structured MySQL database.
- Analyze engagement metrics (likes/comments per post, trends, etc.).
- Visualize engagement trends using charts and graphs.

## Project Structure
```
insta-engagement-analysis/
├── .dist/
|----notebook/
|     |---- fetch_comments.ipynb
├── scripts/
│   ├── fetch_profiles.py       # Script to fetch profile data
│   ├── run_analysis.py         # Runs engagement analysis
│   └── run_scraper.py          # Runs the scraping workflow
├── src/
│   ├── analysis/
│   │   ├── engagement.py       # Engagement metrics computation
│   │   └── visualization.py    # Charts and graphs for insights
│   ├── api/
│   │   ├── main.py             # API for fetching stored data
│   │   └── routes.py           # API routes
│   ├── config/
│   │   ├── db.py               # Database connection
│   │   └── settings.py         # Configuration settings
│   ├── database/
│   │   ├── models.py           # Database schema
│   │   └── queries.py          # SQL queries
│   ├── scraper/
│   │   ├── fetch_data.py       # Fetches profile/posts/comments
│   │   └── save_to_db.py       # Saves data to MySQL
│   └── utils/
│       ├── helpers.py          # Utility functions
│       └── logger.py           # Logging setup
├── tests/
│   ├── test_analysis.py        # Unit tests for analysis
│   ├── test_db.py              # Tests for database interactions
│   └── test_scraper.py         # Tests for scraping module
├── .env                        # Environment variables
├── .gitignore                  # Git ignore file
├── docker-compose.yml          # Docker setup
├── README.md                   # Documentation
└── requirements.txt            # Python dependencies
```

## Installation
### Prerequisites
- Python 3.8+
- MySQL Database
- RapidAPI account (for Instagram scraping API)
- Docker (optional, for containerized setup)

### Setup Instructions
```bash
# Clone the repository
git clone https://github.com/tamannakhare12/insta-engagement-analysis.git
cd insta-engagement-analysis

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
nano .env   # Add your API keys and DB credentials

# Initialize the database
python -m src.database.models

# Run the scraper to fetch data
python src/api/main.py

```

## Usage
### Fetch Instagram Profiles
```bash
python scripts/fetch_profiles.py
```


## API Endpoints
| Method | Endpoint               | Description                  |
|--------|------------------------|------------------------------|
| GET    | `/info/{username}` | Fetch profile data          |
| GET    | `/posts/{username}`    | Get posts and engagement    |
| GET    | `/comments/{post_id}`  | Fetch comments for a post   |



## License
MIT License © 2025 Your Name

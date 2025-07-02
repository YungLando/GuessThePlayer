"""Configuration settings for the application."""

# Football-Data.org API configuration
FOOTBALL_DATA_API_KEY = "74603af1ab63494ebcb60d7712039d5b"  # Add your API key here
FOOTBALL_DATA_BASE_URL = "https://api.football-data.org/v4"

# Database configuration
DATABASE = "players.db"

# Teams to fetch (currently Arsenal and Manchester City)
TEAM_IDS = {
    "Arsenal": 57,
    "Manchester City": 65
} 
# Guess The Player

A Wordle-like game for guessing soccer players, inspired by Poeltl (NBA version). Each day, there's a new player to guess, and you get feedback on various attributes like nationality, league, team, position, and age.

## Features

- Daily changing player
- Feedback on guesses with color coding:
  - 🟩 Green: Exact match
  - 🟨 Yellow: Partial match (for position groups)
  - 🟥 Red: No match
- Age hints with arrows indicating if the player is older (↑) or younger (↓)
- Simple and clean interface

## Setup

1. Make sure you have Python 3.7+ installed
2. Create and activate the virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install flask python-dotenv requests
   ```

## Running the Game

1. Make sure your virtual environment is activated
2. Run the Flask application:
   ```bash
   python app.py
   ```
3. Open your browser and go to `http://localhost:5000`

## Project Structure

- `app.py`: Main Flask application with game logic
- `templates/index.html`: Frontend interface
- `data/players.json`: Database of players
- `static/`: Static files (CSS, JavaScript, images)

## Adding More Players

To add more players, edit the `data/players.json` file. Each player should have the following attributes:
- id: Unique identifier
- name: Player's full name
- nation: Player's nationality
- league: Current league
- team: Current team
- position: Specific position (e.g., "Striker", "Right Wing")
- position_group: General position category (e.g., "Forward", "Midfielder")
- age: Player's current age

## Future Improvements

- Add player search autocomplete
- Include player images
- Add statistics tracking
- Implement a hint system
- Add more players to the database
- Add share results feature 
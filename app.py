from flask import Flask, render_template, request, jsonify
from datetime import datetime
import json
import random
import requests
from bs4 import BeautifulSoup
import time
import sqlite3
from contextlib import closing
import os

# List of user agents to rotate between
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
]

# Database setup
DATABASE = 'players.db'

def init_db():
    """Initialize the database with the players table"""
    with closing(sqlite3.connect(DATABASE)) as db:
        with open('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def setup_database():
    """Ensure database and tables exist"""
    if not os.path.exists(DATABASE):
        init_db()

# Initialize Flask app
app = Flask(__name__)
setup_database()  # Initialize database when app starts

def get_db():
    """Get database connection"""
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def fetch_players():
    """Fetch players from Premier League using Transfermarkt"""
    players_data = []
    
    # Premier League URL
    premier_league_url = 'https://www.transfermarkt.com/premier-league/startseite/wettbewerb/GB1'

    def get_headers():
        return {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }

    session = requests.Session()
    processed_teams = set()  # Keep track of processed teams
    
    def make_request(url, retry_count=0):
        """Make a request with retry logic and random delays"""
        if retry_count >= 3:
            print(f"Failed to fetch {url} after 3 retries")
            return None
            
        try:
            # Random delay between 5-15 seconds, increasing with each retry
            delay = random.uniform(5 + (retry_count * 5), 15 + (retry_count * 5))
            print(f"Waiting {delay:.1f} seconds before request...")
            time.sleep(delay)
            
            response = session.get(url, headers=get_headers())
            
            if response.status_code == 200:
                # Check if we got a valid HTML response
                if 'text/html' in response.headers.get('Content-Type', ''):
                    return response
                else:
                    print(f"Received non-HTML response from {url}")
                    return None
            elif response.status_code == 503 or response.status_code == 429:
                print(f"Rate limited on {url}, retrying after longer delay...")
                # Exponential backoff for rate limit (15-30 seconds * retry count)
                time.sleep(random.uniform(15 * (retry_count + 1), 30 * (retry_count + 1)))
                return make_request(url, retry_count + 1)
            else:
                print(f"Failed to fetch {url}. Status code: {response.status_code}")
                if retry_count < 2:
                    print("Retrying...")
                    return make_request(url, retry_count + 1)
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error making request to {url}: {e}")
            if retry_count < 2:
                print("Retrying...")
                return make_request(url, retry_count + 1)
            return None
    
    try:
        # Get Premier League page
        print("Fetching Premier League page...")
        response = make_request(premier_league_url)
        if not response:
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get all team links - only from the main competition table
        team_links = soup.select("div#yw1 table.items tbody tr td.hauptlink a[href*='/verein/']")
        print(f"Found {len(team_links)} teams")
        
        for team_link in team_links:
            team_url = f"https://www.transfermarkt.com{team_link['href']}"
            team_name = team_link.text.strip()
            
            # Skip if we've already processed this team
            if team_name in processed_teams:
                print(f"Skipping duplicate team: {team_name}")
                continue
                
            processed_teams.add(team_name)
            print(f"Fetching players from {team_name}...")
            
            team_response = make_request(team_url)
            if not team_response:
                continue
                
            team_soup = BeautifulSoup(team_response.text, 'html.parser')
            
            # Get players from the squad table
            player_rows = team_soup.select("table.items tbody tr:not(.table-header)")
            
            for row in player_rows:
                try:
                    name_cell = row.select_one("td.hauptlink a")
                    if not name_cell:
                        continue
                        
                    name = name_cell.text.strip()
                    
                    # Get position
                    position_cell = row.select_one("td:nth-child(2)")
                    position = position_cell.text.strip() if position_cell else "Unknown"
                    
                    # Get age
                    age_cell = row.select_one("td.zentriert")
                    try:
                        age = int(age_cell.text.strip()) if age_cell and age_cell.text.strip() != '-' else 0
                    except (ValueError, AttributeError):
                        age = 0
                    
                    # Get nationality
                    nation_cell = row.select_one("img.flaggenrahmen")
                    nation = nation_cell['title'] if nation_cell else "Unknown"
                    nation_code = nation_cell['src'].split('/')[-1].split('.')[0].upper() if nation_cell else ""
                    
                    # Get appearances - we need to find the correct column
                    appearances = 0
                    # First, try to find the header row to identify which column contains appearances
                    header_row = team_soup.select_one("table.items thead tr")
                    if header_row:
                        # Find which column contains appearances
                        columns = header_row.select("th")
                        print(f"Found {len(columns)} columns in header row")
                        appearance_col_index = None
                        for i, col in enumerate(columns):
                            print(f"Column {i}: {col.text.strip()}")
                            if any(term in col.text.lower() for term in ['games', 'appearances', 'played', 'apps', 'matches']):
                                appearance_col_index = i
                                print(f"Found appearances column at index {i}")
                                break
                        
                        if appearance_col_index is not None:
                            # Now get the cell at that same index for our player
                            cells = row.select("td")
                            if appearance_col_index < len(cells):
                                cell = cells[appearance_col_index]
                                app_text = cell.text.strip()
                                print(f"Found appearance text: '{app_text}'")
                                try:
                                    # The appearance data might be in different formats
                                    # Could be just a number or could be "23 (2)" format
                                    if '(' in app_text:
                                        appearances = int(app_text.split('(')[0].strip())
                                    # If it contains '/', take the first number (starts)
                                    elif '/' in app_text:
                                        appearances = int(app_text.split('/')[0].strip())
                                    # Otherwise try to convert directly
                                    else:
                                        appearances = int(app_text) if app_text.strip().isdigit() else 0
                                except (ValueError, IndexError) as e:
                                    print(f"Error parsing appearances: {e}")
                                    appearances = 0
                        else:
                            print("Could not find appearances column in header row")
                    else:
                        print("Could not find header row in team table")
                    
                    print(f"Processing {name} - Appearances: {appearances}")
                    
                    # Only add players with at least 5 appearances
                    if appearances >= 5:
                        players_data.append({
                            "name": name,
                            "nation": nation,
                            "nation_code": nation_code,
                            "league": "Premier League",
                            "team": team_name,
                            "position": position,
                            "position_group": get_position_group(position),
                            "age": age,
                            "appearances": appearances,
                            "last_updated": datetime.now().strftime('%Y-%m-%d')
                        })
                        print(f"Added {name} to database (Appearances: {appearances})")
                    else:
                        print(f"Skipped {name} (insufficient appearances: {appearances})")
                    
                except Exception as e:
                    print(f"Error processing player: {e}")
                    continue

        print(f"Successfully fetched {len(players_data)} Premier League players")
        
        if len(players_data) == 0:
            print("No players were added. This might indicate an issue with the scraping.")
            return []
            
        # Update database
        with closing(get_db()) as db:
            # Clear existing players
            db.execute('DELETE FROM players')
            
            # Insert new players
            db.executemany('''
                INSERT INTO players (name, nation, nation_code, league, team, position, position_group, age, appearances, last_updated)
                VALUES (:name, :nation, :nation_code, :league, :team, :position, :position_group, :age, :appearances, :last_updated)
            ''', players_data)
            
            db.commit()
            
        return players_data
    except Exception as e:
        print(f"Error fetching players: {e}")
        return []

def get_position_group(position):
    """Convert specific position to position group"""
    position = position.lower()
    
    forwards = ['striker', 'centre-forward', 'forward', 'left winger', 'right winger', 'attack']
    midfielders = ['midfield', 'attacking midfield', 'defensive midfield', 'central midfield']
    defenders = ['defence', 'centre-back', 'left-back', 'right-back', 'defender']
    goalkeepers = ['goalkeeper', 'keeper']
    
    if any(pos in position for pos in forwards):
        return "Forward"
    elif any(pos in position for pos in midfielders):
        return "Midfielder"
    elif any(pos in position for pos in defenders):
        return "Defender"
    elif any(pos in position for pos in goalkeepers):
        return "Goalkeeper"
    else:
        return "Unknown"

def load_players():
    """Load players from database"""
    with closing(get_db()) as db:
        players = db.execute('SELECT * FROM players').fetchall()
        return [dict(player) for player in players]

def get_daily_player():
    """Get the daily player using date as seed"""
    with closing(get_db()) as db:
        players = db.execute('SELECT * FROM players').fetchall()
        if not players:
            return None
            
        today = datetime.now().strftime('%Y-%m-%d')
        random.seed(today)
        player = random.choice(players)
        return dict(player)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/players/search')
def search_players():
    """Search players by name (for autocomplete)"""
    query = request.args.get('q', '').lower()
    
    with closing(get_db()) as db:
        players = db.execute('''
            SELECT id, name, team, league 
            FROM players 
            WHERE LOWER(name) LIKE ?
            LIMIT 10
        ''', [f'%{query}%']).fetchall()
        
        return jsonify([dict(player) for player in players])

@app.route('/api/guess', methods=['POST'])
def check_guess():
    data = request.get_json()
    guessed_player_id = data.get('guess', {}).get('id')
    
    with closing(get_db()) as db:
        guessed_player = db.execute('SELECT * FROM players WHERE id = ?', [guessed_player_id]).fetchone()
        if not guessed_player:
            return jsonify({"error": "Player not found"}), 404
            
        daily_player = get_daily_player()
        if not daily_player:
            return jsonify({"error": "No players in database"}), 500
        
        guessed_player = dict(guessed_player)
        
        feedback = {
            'nation': guessed_player['nation'] == daily_player['nation'],
            'league': guessed_player['league'] == daily_player['league'],
            'team': guessed_player['team'] == daily_player['team'],
            'position': {
                'exact': guessed_player['position'] == daily_player['position'],
                'similar': guessed_player['position_group'] == daily_player['position_group']
            },
            'age': {
                'correct': guessed_player['age'] == daily_player['age'],
                'higher': guessed_player['age'] < daily_player['age'],
                'lower': guessed_player['age'] > daily_player['age']
            },
            'correct': guessed_player['id'] == daily_player['id']
        }
        
        return jsonify(feedback)

@app.route('/api/update-players')
def update_players():
    """Admin route to update player database"""
    # Check if database needs updating (once per week)
    with closing(get_db()) as db:
        last_update = db.execute('SELECT last_updated FROM players LIMIT 1').fetchone()
        if last_update:
            last_update = datetime.strptime(last_update['last_updated'], '%Y-%m-%d')
            days_since_update = (datetime.now() - last_update).days
            
            if days_since_update < 7:
                return jsonify({
                    "message": f"Database was updated {days_since_update} days ago. Next update in {7 - days_since_update} days."
                })
    
    players = fetch_players()
    return jsonify({"message": f"Updated {len(players)} players"})

if __name__ == '__main__':
    # Make sure the data directory exists
    os.makedirs('data', exist_ok=True)
    # Run the Flask app on port 5002 instead of 5001
    app.run(debug=True, host='0.0.0.0', port=5002) 
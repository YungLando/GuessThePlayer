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
import re

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
    """Fetch players from Premier League using Transfermarkt's market value page"""
    players_data = []
    
    # Define the teams with their IDs
    teams = {
        '11': {'name': 'Arsenal', 'url': 'arsenal'},
        '281': {'name': 'Manchester City', 'url': 'manchester-city'},
        # Commented out for testing
        # '31': {'name': 'Liverpool', 'url': 'liverpool'},
        # '405': {'name': 'Aston Villa', 'url': 'aston-villa'},
        # '148': {'name': 'Tottenham', 'url': 'tottenham'},
        # '985': {'name': 'Manchester United', 'url': 'manchester-united'},
        # '762': {'name': 'Newcastle United', 'url': 'newcastle-united'},
        # '1237': {'name': 'Brighton', 'url': 'brighton'},
        # '379': {'name': 'West Ham', 'url': 'west-ham-united'},
        # '631': {'name': 'Chelsea', 'url': 'chelsea'},
        # '1148': {'name': 'Brentford', 'url': 'brentford'},
        # '543': {'name': 'Wolves', 'url': 'wolverhampton'},
        # '873': {'name': 'Crystal Palace', 'url': 'crystal-palace'},
        # '703': {'name': 'Nottingham Forest', 'url': 'nottingham'},
        # '931': {'name': 'Fulham', 'url': 'fulham'},
        # '29': {'name': 'Everton', 'url': 'everton'},
        # '1031': {'name': 'Luton', 'url': 'luton-town'},
        # '989': {'name': 'Bournemouth', 'url': 'bournemouth'},
        # '350': {'name': 'Sheffield United', 'url': 'sheffield-united'},
        # '1132': {'name': 'Burnley', 'url': 'burnley'}
    }
    
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
    processed_players = set()  # Track processed players to avoid duplicates
    
    def make_request(url, retry_count=0):
        """Make a request with retry logic and random delays"""
        if retry_count >= 3:
            print(f"Failed to fetch {url} after 3 retries")
            return None
            
        try:
            delay = random.uniform(5 + (retry_count * 5), 15 + (retry_count * 5))
            print(f"Waiting {delay:.1f} seconds before request...")
            time.sleep(delay)
            
            response = session.get(url, headers=get_headers())
            
            if response.status_code == 200:
                if 'text/html' in response.headers.get('Content-Type', ''):
                    return response
                else:
                    print(f"Received non-HTML response from {url}")
                    return None
            elif response.status_code == 503 or response.status_code == 429:
                print(f"Rate limited on {url}, retrying after longer delay...")
                time.sleep(random.uniform(15 * (retry_count + 1), 30 * (retry_count + 1)))
                return make_request(url, retry_count + 1)
            else:
                print(f"Failed to fetch {url}. Status code: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error making request to {url}: {e}")
            return None
    
    try:
        # Iterate through each team
        for team_id, team_info in teams.items():
            print(f"Fetching players from {team_info['name']}...")
            url = f'https://www.transfermarkt.com/{team_info["url"]}/startseite/verein/{team_id}'
            
            response = make_request(url)
            if not response:
                continue
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Get player rows from the squad table
            player_rows = soup.select("table.items tbody tr.odd, table.items tbody tr.even")
            print(f"Found {len(player_rows)} players for {team_info['name']}")
            
            for row in player_rows:
                try:
                    # Get player name
                    name_cell = row.select_one("td.hauptlink a")
                    if not name_cell:
                        continue
                    name = name_cell.text.strip()
                    
                    # Skip if we've already processed this player
                    if name.lower() in processed_players:
                        print(f"Skipping duplicate player: {name}")
                        continue
                    
                    # Debug: Print the row HTML to see structure
                    print(f"\nRow HTML for {name}:")
                    print(row.prettify())
                    
                    # Get squad number to filter for first team players
                    squad_number = None
                    number_cell = row.select_one("td.zentriert .rn_nummer")
                    if number_cell:
                        try:
                            number_text = number_cell.text.strip()
                            if number_text.isdigit():
                                squad_number = int(number_text)
                                print(f"Found squad number for {name}: {squad_number}")
                        except (ValueError, AttributeError) as e:
                            print(f"Error parsing squad number for {name}: {e}")
                    
                    # Get age from the date cell (3rd td which contains birth date and age in parentheses)
                    age = 0
                    date_cell = row.select_one("td:nth-child(3)")
                    if date_cell:
                        try:
                            # Look for number in parentheses, e.g., "(24)"
                            age_match = re.search(r'\((\d+)\)', date_cell.text.strip())
                            if age_match:
                                age = int(age_match.group(1))
                                print(f"Found age for {name}: {age}")
                        except (ValueError, AttributeError) as e:
                            print(f"Error parsing age for {name}: {e}")
                    
                    if age == 0:
                        print(f"Could not find age for {name}")
                    
                    # Get market value and format it
                    market_value = 0
                    value_cell = row.select_one("td.rechts.hauptlink a")
                    if value_cell:
                        try:
                            value_text = value_cell.text.strip()
                            # Convert value text (e.g., "€40.00m" or "€800Th.") to numeric
                            if 'm' in value_text.lower():
                                # Value in millions
                                value_num = float(value_text.replace('€', '').replace('m', '').strip())
                                market_value = value_num * 1000000
                            elif 'th.' in value_text.lower():
                                # Value in thousands
                                value_num = float(value_text.replace('€', '').replace('Th.', '').strip())
                                market_value = value_num * 1000
                        except (ValueError, AttributeError) as e:
                            print(f"Error parsing market value for {name}: {e}")
                    
                    # Get player ID from their profile URL
                    player_id = None
                    player_link = row.select_one("td.hauptlink a[href*='/profil/spieler/']")
                    if player_link:
                        try:
                            player_id = player_link['href'].split('/spieler/')[1].split('/')[0]
                            print(f"Found player ID for {name}: {player_id}")
                        except (IndexError, KeyError) as e:
                            print(f"Error getting player ID for {name}: {e}")
                    
                    # Skip players with low market value
                    # This way we keep expensive players that are more likely to be well-known
                    if market_value < 5000000:  # Less than 5M euros
                        print(f"Skipping {name} - Value: {market_value/1000000:.1f}M")
                        continue
                    
                    processed_players.add(name.lower())
                    
                    # Get position - clean up and maintain specific position
                    position_cell = row.select_one("td:nth-child(2)")
                    position = "Unknown"
                    if position_cell:
                        try:
                            # Get the position text
                            position_text = position_cell.text.strip()
                            # Remove the player name if it appears in the position
                            position_text = position_text.replace(name, "").strip()
                            
                            # Clean and standardize position names
                            position_text = position_text.lower()
                            
                            # Map common position variations to standardized names
                            position_standardization = {
                                'rw': 'Right Wing',
                                'lw': 'Left Wing',
                                'rm': 'Right Midfield',
                                'lm': 'Left Midfield',
                                'cam': 'Attacking Midfield',
                                'cdm': 'Defensive Midfield',
                                'cm': 'Central Midfield',
                                'rb': 'Right-Back',
                                'lb': 'Left-Back',
                                'cb': 'Centre-Back',
                                'cf': 'Centre-Forward',
                                'st': 'Striker',
                                'gk': 'Goalkeeper'
                            }
                            
                            # Try to match position abbreviations
                            matched = False
                            for abbrev, full_name in position_standardization.items():
                                if abbrev in position_text.split():
                                    position = full_name
                                    matched = True
                                    break
                            
                            # If no abbreviation match, try to standardize full position names
                            if not matched:
                                if 'right wing' in position_text:
                                    position = 'Right Wing'
                                elif 'left wing' in position_text:
                                    position = 'Left Wing'
                                elif 'attacking midfield' in position_text:
                                    position = 'Attacking Midfield'
                                elif 'defensive midfield' in position_text:
                                    position = 'Defensive Midfield'
                                elif 'central midfield' in position_text:
                                    position = 'Central Midfield'
                                elif 'right-back' in position_text or 'right back' in position_text:
                                    position = 'Right-Back'
                                elif 'left-back' in position_text or 'left back' in position_text:
                                    position = 'Left-Back'
                                elif 'centre-back' in position_text or 'center back' in position_text:
                                    position = 'Centre-Back'
                                elif 'striker' in position_text:
                                    position = 'Striker'
                                elif 'goalkeeper' in position_text:
                                    position = 'Goalkeeper'
                                elif 'forward' in position_text:
                                    position = 'Centre-Forward'
                                else:
                                    position = position_text.title()
                            
                        except Exception as e:
                            print(f"Error parsing position for {name}: {e}")
                            position = "Unknown"
                    
                    print(f"Processing {name} ({position}, {market_value/1000000:.1f}M)")
                    
                    # Format market value for display
                    if market_value >= 1000000000:  # Billion
                        market_value_display = f"€{market_value/1000000000:.1f}B"
                    elif market_value >= 1000000:  # Million
                        market_value_display = f"€{market_value/1000000:.1f}M"
                    else:  # Thousand
                        market_value_display = f"€{market_value/1000:.0f}K"
                    
                    # Get nationality
                    nation_cell = row.select_one("td.zentriert img.flaggenrahmen")
                    nation = nation_cell['title'].strip() if nation_cell else "Unknown"
                    nation_code = nation_cell['src'].split('/')[-1].split('.')[0].upper() if nation_cell else ""
                    
                    players_data.append({
                        "name": name,
                        "nation": nation,
                        "nation_code": nation_code,
                        "league": "Premier League",
                        "team": team_info['name'],
                        "position": position,
                        "position_group": get_position_group(position),
                        "age": age,
                        "market_value": market_value,
                        "market_value_display": market_value_display,
                        "last_updated": datetime.now().strftime('%Y-%m-%d')
                    })
                    print(f"Added {name} to database")
                    
                except Exception as e:
                    print(f"Error processing player: {e}")
                    continue
            
            # Add delay between teams
            time.sleep(random.uniform(10, 20))
        
        print(f"Successfully fetched players from {len(teams)} Premier League teams")
        
        if len(players_data) == 0:
            print("No players were added. This might indicate an issue with the scraping.")
            return []
        
        # Update database
        with closing(get_db()) as db:
            # Clear existing players
            db.execute('DELETE FROM players')
            
            # Insert new players
            db.executemany('''
                INSERT INTO players (name, nation, nation_code, league, team, position, position_group, age, market_value, market_value_display, last_updated)
                VALUES (:name, :nation, :nation_code, :league, :team, :position, :position_group, :age, :market_value, :market_value_display, :last_updated)
            ''', players_data)
            
            db.commit()
        
        return players_data
        
    except Exception as e:
        print(f"Error fetching players: {e}")
        return []

def get_position_group(position):
    """Convert specific position to position group"""
    position = position.lower()
    
    # Dictionary mapping specific positions to their groups
    position_mappings = {
        # Forwards
        'right wing': 'Right Wing',
        'left wing': 'Left Wing',
        'centre-forward': 'Striker',
        'striker': 'Striker',
        # Midfielders
        'attacking midfield': 'Central Mid',
        'central midfield': 'Central Mid',
        'defensive midfield': 'Central Mid',
        'right midfield': 'Right Mid',
        'left midfield': 'Left Mid',
        # Defenders
        'centre-back': 'Centre-Back',
        'right-back': 'Right-Back',
        'left-back': 'Left-Back',
        'sweeper': 'Centre-Back',
        # Goalkeepers
        'goalkeeper': 'Goalkeeper'
    }
    
    # Try to find an exact match first
    for pos, group in position_mappings.items():
        if pos in position:
            return group
    
    # Fallback to basic categories if no specific match
    if 'right wing' in position:
        return 'Right Wing'
    elif 'left wing' in position:
        return 'Left Wing'
    elif 'striker' in position or 'forward' in position:
        return 'Striker'
    elif 'midfield' in position:
        if 'right' in position:
            return 'Right Mid'
        elif 'left' in position:
            return 'Left Mid'
        else:
            return 'Central Mid'
    elif 'back' in position or 'defence' in position:
        if 'right' in position:
            return 'Right-Back'
        elif 'left' in position:
            return 'Left-Back'
        else:
            return 'Centre-Back'
    elif 'keeper' in position:
        return 'Goalkeeper'
    else:
        return position.title()

def are_positions_similar(pos1, pos2):
    """Determine if two positions are similar enough to warrant a yellow indicator"""
    # Convert positions to lowercase for comparison
    pos1 = pos1.lower()
    pos2 = pos2.lower()
    
    # Get standardized position groups
    group1 = get_position_group(pos1)
    group2 = get_position_group(pos2)
    
    # If they're the same group, they're similar
    if group1 == group2:
        return True
        
    # Define pairs of similar positions
    similar_positions = [
        {'Right Wing', 'Right Mid'},
        {'Left Wing', 'Left Mid'},
        {'Attacking Midfield', 'Central Midfield', 'Defensive Midfield'},
        {'Central Mid'}  # This group includes all central midfield variations
    ]
    
    # Check if positions are in any of the similar groups
    for group in similar_positions:
        if group1 in group and group2 in group:
            return True
            
    # Special case for wings - opposite sides are similar
    wing_pairs = [
        ('Right Wing', 'Left Wing'),
        ('Right Mid', 'Left Mid')
    ]
    
    for pos_a, pos_b in wing_pairs:
        if (group1 == pos_a and group2 == pos_b) or (group1 == pos_b and group2 == pos_a):
            return True
    
    return False

def load_players():
    """Load players from database"""
    with closing(get_db()) as db:
        players = db.execute('SELECT * FROM players').fetchall()
        return [dict(player) for player in players]

def get_daily_player():
    """Get the daily player using date as seed"""
    with closing(get_db()) as db:
        # For testing, let's get a specific player (Erling Haaland)
        player = db.execute('''
            SELECT * FROM players 
            WHERE name LIKE '%Haaland%' 
            LIMIT 1
        ''').fetchone()
        
        # If we can't find the test player, fall back to random
        if not player:
            players = db.execute('SELECT * FROM players').fetchall()
            if not players:
                return None
            
            today = datetime.now().strftime('%Y-%m-%d')
            random.seed(today)
            player = random.choice(players)
        
        return dict(player) if player else None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/players/search')
def search_players():
    """Search players by name (for autocomplete)"""
    query = request.args.get('q', '').lower()
    
    with closing(get_db()) as db:
        # First get all matching players
        players = db.execute('''
            SELECT DISTINCT id, name, team, league, position, age, nation, market_value_display 
            FROM players 
            WHERE LOWER(name) LIKE ?
            ORDER BY 
                CASE WHEN LOWER(name) = ? THEN 1
                     WHEN LOWER(name) LIKE ? THEN 2
                     ELSE 3 END,
                CASE WHEN team != 'Unknown' THEN 1 ELSE 2 END,
                name
        ''', [f'%{query}%', query, f'{query}%']).fetchall()
        
        # Filter out duplicates, preferring entries with known teams
        seen_players = {}
        filtered_players = []
        for player in players:
            name = player['name']
            if name not in seen_players:
                seen_players[name] = player
            elif player['team'] != 'Unknown' and seen_players[name]['team'] == 'Unknown':
                # Replace the Unknown team version with the known team version
                seen_players[name] = player
        
        filtered_players = list(seen_players.values())[:10]  # Limit to 10 results
        
        return jsonify([{
            'id': player['id'],
            'name': player['name'],
            'team': player['team'],
            'league': player['league'],
            'position': player['position'],
            'age': player['age'],
            'nation': player['nation'],
            'market_value_display': player['market_value_display'],
            'label': f"{player['name']} ({player['team']}" + (")" if player['team'] != "Unknown" else ")")
        } for player in filtered_players])

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
                'similar': are_positions_similar(guessed_player['position'], daily_player['position'])
            },
            'age': {
                'correct': guessed_player['age'] == daily_player['age'],
                'close': abs(guessed_player['age'] - daily_player['age']) <= 2,
                'higher': guessed_player['age'] < daily_player['age'],
                'lower': guessed_player['age'] > daily_player['age']
            },
            'market_value': {
                'correct': guessed_player['market_value'] == daily_player['market_value'],
                'close': abs(guessed_player['market_value'] - daily_player['market_value']) <= 10000000,  # Within 10M
                'higher': guessed_player['market_value'] < daily_player['market_value'],
                'lower': guessed_player['market_value'] > daily_player['market_value'],
                'display': daily_player['market_value_display']
            },
            'correct': guessed_player['id'] == daily_player['id']
        }
        
        return jsonify(feedback)

@app.route('/api/update-players')
def update_players():
    """Admin route to update player database"""
    force_update = request.args.get('force', '').lower() == 'true'
    
    try:
        with closing(get_db()) as db:
            # Check if we have any players
            player_count = db.execute('SELECT COUNT(*) as count FROM players').fetchone()['count']
            
            if player_count == 0:
                print("Database is empty, forcing update...")
                force_update = True
            else:
                # Check last update time
                last_update = db.execute('SELECT last_updated FROM players LIMIT 1').fetchone()
                if last_update:
                    last_update = datetime.strptime(last_update['last_updated'], '%Y-%m-%d')
                    days_since_update = (datetime.now() - last_update).days
                    
                    if not force_update and days_since_update < 7:
                        return jsonify({
                            "message": f"Database was updated {days_since_update} days ago. Next update in {7 - days_since_update} days.",
                            "player_count": player_count
                        })
    except Exception as e:
        print(f"Error checking database: {e}")
        force_update = True
    
    players = fetch_players()
    return jsonify({
        "message": f"Updated {len(players)} players",
        "player_count": len(players)
    })

if __name__ == '__main__':
    # Make sure the data directory exists
    os.makedirs('data', exist_ok=True)
    # Run the Flask app on port 5002 instead of 5001
    app.run(debug=True, host='0.0.0.0', port=5002) 
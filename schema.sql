DROP TABLE IF EXISTS players;
CREATE TABLE players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    nation TEXT NOT NULL,
    nation_code TEXT NOT NULL,
    league TEXT NOT NULL,
    team TEXT NOT NULL,
    position TEXT NOT NULL,
    position_group TEXT NOT NULL,
    age INTEGER NOT NULL,
    market_value INTEGER NOT NULL,
    market_value_display TEXT NOT NULL,
    last_updated TEXT NOT NULL
); 
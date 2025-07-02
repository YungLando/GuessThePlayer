from flask import Flask, render_template, request, jsonify
from datetime import datetime
import json
import random
import requests
import time
import sqlite3
from contextlib import closing
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

# Configuration
DATABASE = 'players.db'

# Initialize Flask app
app = Flask(__name__)

def get_db():
    """Get database connection"""
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def setup_database():
    """Create database tables if they don't exist"""
    with get_db() as db:
        # Drop existing table to ensure schema consistency
        db.execute('DROP TABLE IF EXISTS players')
        
        db.execute('''
        CREATE TABLE players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            position TEXT,
            nationality TEXT,
            age INTEGER,
            team TEXT,
            league TEXT DEFAULT 'Premier League',
            appearances INTEGER,
            starts INTEGER,
            market_value INTEGER,
            market_value_display TEXT,
            last_updated TEXT
        )
        ''')
        db.commit()

def get_premier_league_players():
    """Get relevant players from Premier League"""
    # Comprehensive database of Premier League players
    # Criteria: 15+ appearances OR €10M+ market value
    players_data = [
        # ARSENAL
        {
            'name': 'Bukayo Saka',
            'position': 'Right Wing',
            'nationality': 'England',
            'age': 22,
            'team': 'Arsenal',
            'league': 'Premier League',
            'appearances': 35,
            'starts': 34,
            'market_value': 120000000,
            'market_value_display': '€120M'
        },
        {
            'name': 'Martin Odegaard',
            'position': 'Attacking Midfield',
            'nationality': 'Norway',
            'age': 25,
            'team': 'Arsenal',
            'league': 'Premier League',
            'appearances': 35,
            'starts': 34,
            'market_value': 110000000,
            'market_value_display': '€110M'
        },
        {
            'name': 'William Saliba',
            'position': 'Centre-Back',
            'nationality': 'France',
            'age': 23,
            'team': 'Arsenal',
            'league': 'Premier League',
            'appearances': 38,
            'starts': 38,
            'market_value': 80000000,
            'market_value_display': '€80M'
        },
        {
            'name': 'Declan Rice',
            'position': 'Defensive Midfield',
            'nationality': 'England',
            'age': 25,
            'team': 'Arsenal',
            'league': 'Premier League',
            'appearances': 37,
            'starts': 37,
            'market_value': 100000000,
            'market_value_display': '€100M'
        },
        {
            'name': 'Kai Havertz',
            'position': 'Centre-Forward',
            'nationality': 'Germany',
            'age': 25,
            'team': 'Arsenal',
            'league': 'Premier League',
            'appearances': 37,
            'starts': 30,
            'market_value': 70000000,
            'market_value_display': '€70M'
        },
        {
            'name': 'Gabriel Martinelli',
            'position': 'Left Wing',
            'nationality': 'Brazil',
            'age': 23,
            'team': 'Arsenal',
            'league': 'Premier League',
            'appearances': 35,
            'starts': 28,
            'market_value': 80000000,
            'market_value_display': '€80M'
        },
        {
            'name': 'Ben White',
            'position': 'Right-Back',
            'nationality': 'England',
            'age': 26,
            'team': 'Arsenal',
            'league': 'Premier League',
            'appearances': 37,
            'starts': 37,
            'market_value': 55000000,
            'market_value_display': '€55M'
        },
        {
            'name': 'Gabriel Magalhaes',
            'position': 'Centre-Back',
            'nationality': 'Brazil',
            'age': 26,
            'team': 'Arsenal',
            'league': 'Premier League',
            'appearances': 34,
            'starts': 34,
            'market_value': 65000000,
            'market_value_display': '€65M'
        },
        {
            'name': 'Oleksandr Zinchenko',
            'position': 'Left-Back',
            'nationality': 'Ukraine',
            'age': 27,
            'team': 'Arsenal',
            'league': 'Premier League',
            'appearances': 20,
            'starts': 18,
            'market_value': 42000000,
            'market_value_display': '€42M'
        },
        {
            'name': 'Jakub Kiwior',
            'position': 'Centre-Back',
            'nationality': 'Poland',
            'age': 24,
            'team': 'Arsenal',
            'league': 'Premier League',
            'appearances': 20,
            'starts': 15,
            'market_value': 25000000,
            'market_value_display': '€25M'
        },
        {
            'name': 'Takehiro Tomiyasu',
            'position': 'Right-Back',
            'nationality': 'Japan',
            'age': 25,
            'team': 'Arsenal',
            'league': 'Premier League',
            'appearances': 18,
            'starts': 12,
            'market_value': 30000000,
            'market_value_display': '€30M'
        },
        {
            'name': 'Jorginho',
            'position': 'Central Midfield',
            'nationality': 'Italy',
            'age': 32,
            'team': 'Arsenal',
            'league': 'Premier League',
            'appearances': 32,
            'starts': 20,
            'market_value': 15000000,
            'market_value_display': '€15M'
        },
        {
            'name': 'Leandro Trossard',
            'position': 'Left Wing',
            'nationality': 'Belgium',
            'age': 29,
            'team': 'Arsenal',
            'league': 'Premier League',
            'appearances': 34,
            'starts': 15,
            'market_value': 35000000,
            'market_value_display': '€35M'
        },
        {
            'name': 'David Raya',
            'position': 'Goalkeeper',
            'nationality': 'Spain',
            'age': 28,
            'team': 'Arsenal',
            'league': 'Premier League',
            'appearances': 32,
            'starts': 32,
            'market_value': 30000000,
            'market_value_display': '€30M'
        },
        {
            'name': 'Aaron Ramsdale',
            'position': 'Goalkeeper',
            'nationality': 'England',
            'age': 26,
            'team': 'Arsenal',
            'league': 'Premier League',
            'appearances': 6,
            'starts': 6,
            'market_value': 28000000,
            'market_value_display': '€28M'
        },
        
        # ASTON VILLA
        {
            'name': 'Ollie Watkins',
            'position': 'Centre-Forward',
            'nationality': 'England',
            'age': 28,
            'team': 'Aston Villa',
            'league': 'Premier League',
            'appearances': 37,
            'starts': 37,
            'market_value': 65000000,
            'market_value_display': '€65M'
        },
        {
            'name': 'Douglas Luiz',
            'position': 'Central Midfield',
            'nationality': 'Brazil',
            'age': 26,
            'team': 'Aston Villa',
            'league': 'Premier League',
            'appearances': 35,
            'starts': 35,
            'market_value': 60000000,
            'market_value_display': '€60M'
        },
        {
            'name': 'Leon Bailey',
            'position': 'Right Wing',
            'nationality': 'Jamaica',
            'age': 26,
            'team': 'Aston Villa',
            'league': 'Premier League',
            'appearances': 35,
            'starts': 25,
            'market_value': 45000000,
            'market_value_display': '€45M'
        },
        {
            'name': 'John McGinn',
            'position': 'Central Midfield',
            'nationality': 'Scotland',
            'age': 29,
            'team': 'Aston Villa',
            'league': 'Premier League',
            'appearances': 35,
            'starts': 34,
            'market_value': 35000000,
            'market_value_display': '€35M'
        },
        {
            'name': 'Ezri Konsa',
            'position': 'Centre-Back',
            'nationality': 'England',
            'age': 26,
            'team': 'Aston Villa',
            'league': 'Premier League',
            'appearances': 35,
            'starts': 35,
            'market_value': 35000000,
            'market_value_display': '€35M'
        },
        {
            'name': 'Emiliano Martinez',
            'position': 'Goalkeeper',
            'nationality': 'Argentina',
            'age': 31,
            'team': 'Aston Villa',
            'league': 'Premier League',
            'appearances': 35,
            'starts': 35,
            'market_value': 28000000,
            'market_value_display': '€28M'
        },
        {
            'name': 'Pau Torres',
            'position': 'Centre-Back',
            'nationality': 'Spain',
            'age': 27,
            'team': 'Aston Villa',
            'league': 'Premier League',
            'appearances': 33,
            'starts': 32,
            'market_value': 45000000,
            'market_value_display': '€45M'
        },
        {
            'name': 'Lucas Digne',
            'position': 'Left-Back',
            'nationality': 'France',
            'age': 30,
            'team': 'Aston Villa',
            'league': 'Premier League',
            'appearances': 25,
            'starts': 24,
            'market_value': 20000000,
            'market_value_display': '€20M'
        },
        {
            'name': 'Matty Cash',
            'position': 'Right-Back',
            'nationality': 'Poland',
            'age': 26,
            'team': 'Aston Villa',
            'league': 'Premier League',
            'appearances': 28,
            'starts': 27,
            'market_value': 25000000,
            'market_value_display': '€25M'
        },
        {
            'name': 'Moussa Diaby',
            'position': 'Right Wing',
            'nationality': 'France',
            'age': 25,
            'team': 'Aston Villa',
            'league': 'Premier League',
            'appearances': 35,
            'starts': 30,
            'market_value': 50000000,
            'market_value_display': '€50M'
        },
        {
            'name': 'Youri Tielemans',
            'position': 'Central Midfield',
            'nationality': 'Belgium',
            'age': 27,
            'team': 'Aston Villa',
            'league': 'Premier League',
            'appearances': 32,
            'starts': 20,
            'market_value': 25000000,
            'market_value_display': '€25M'
        },
        {
            'name': 'Nicolo Zaniolo',
            'position': 'Attacking Midfield',
            'nationality': 'Italy',
            'age': 25,
            'team': 'Aston Villa',
            'league': 'Premier League',
            'appearances': 25,
            'starts': 12,
            'market_value': 25000000,
            'market_value_display': '€25M'
        },
        
        # BOURNEMOUTH
        {
            'name': 'Dominic Solanke',
            'position': 'Centre-Forward',
            'nationality': 'England',
            'age': 26,
            'team': 'Bournemouth',
            'league': 'Premier League',
            'appearances': 38,
            'starts': 38,
            'market_value': 40000000,
            'market_value_display': '€40M'
        },
        {
            'name': 'Philip Billing',
            'position': 'Central Midfield',
            'nationality': 'Denmark',
            'age': 28,
            'team': 'Bournemouth',
            'league': 'Premier League',
            'appearances': 32,
            'starts': 30,
            'market_value': 25000000,
            'market_value_display': '€25M'
        },
        {
            'name': 'Neto',
            'position': 'Goalkeeper',
            'nationality': 'Brazil',
            'age': 34,
            'team': 'Bournemouth',
            'league': 'Premier League',
            'appearances': 37,
            'starts': 37,
            'market_value': 12000000,
            'market_value_display': '€12M'
        },
        {
            'name': 'Marcus Tavernier',
            'position': 'Right Wing',
            'nationality': 'England',
            'age': 25,
            'team': 'Bournemouth',
            'league': 'Premier League',
            'appearances': 30,
            'starts': 28,
            'market_value': 22000000,
            'market_value_display': '€22M'
        },
        {
            'name': 'Ryan Christie',
            'position': 'Attacking Midfield',
            'nationality': 'Scotland',
            'age': 29,
            'team': 'Bournemouth',
            'league': 'Premier League',
            'appearances': 35,
            'starts': 32,
            'market_value': 18000000,
            'market_value_display': '€18M'
        },
        {
            'name': 'Lloyd Kelly',
            'position': 'Centre-Back',
            'nationality': 'England',
            'age': 25,
            'team': 'Bournemouth',
            'league': 'Premier League',
            'appearances': 25,
            'starts': 24,
            'market_value': 20000000,
            'market_value_display': '€20M'
        },
        {
            'name': 'Adam Smith',
            'position': 'Right-Back',
            'nationality': 'England',
            'age': 33,
            'team': 'Bournemouth',
            'league': 'Premier League',
            'appearances': 28,
            'starts': 27,
            'market_value': 8000000,
            'market_value_display': '€8M'
        },
        {
            'name': 'Milos Kerkez',
            'position': 'Left-Back',
            'nationality': 'Hungary',
            'age': 20,
            'team': 'Bournemouth',
            'league': 'Premier League',
            'appearances': 30,
            'starts': 29,
            'market_value': 25000000,
            'market_value_display': '€25M'
        },
        {
            'name': 'Justin Kluivert',
            'position': 'Left Wing',
            'nationality': 'Netherlands',
            'age': 25,
            'team': 'Bournemouth',
            'league': 'Premier League',
            'appearances': 32,
            'starts': 25,
            'market_value': 20000000,
            'market_value_display': '€20M'
        },
        
        # BRENTFORD
        {
            'name': 'Ivan Toney',
            'position': 'Centre-Forward',
            'nationality': 'England',
            'age': 28,
            'team': 'Brentford',
            'league': 'Premier League',
            'appearances': 17,
            'starts': 17,
            'market_value': 50000000,
            'market_value_display': '€50M'
        },
        {
            'name': 'Bryan Mbeumo',
            'position': 'Right Wing',
            'nationality': 'Cameroon',
            'age': 24,
            'team': 'Brentford',
            'league': 'Premier League',
            'appearances': 25,
            'starts': 24,
            'market_value': 45000000,
            'market_value_display': '€45M'
        },
        {
            'name': 'Yoane Wissa',
            'position': 'Left Wing',
            'nationality': 'DR Congo',
            'age': 27,
            'team': 'Brentford',
            'league': 'Premier League',
            'appearances': 35,
            'starts': 30,
            'market_value': 30000000,
            'market_value_display': '€30M'
        },
        {
            'name': 'Mark Flekken',
            'position': 'Goalkeeper',
            'nationality': 'Netherlands',
            'age': 30,
            'team': 'Brentford',
            'league': 'Premier League',
            'appearances': 38,
            'starts': 38,
            'market_value': 20000000,
            'market_value_display': '€20M'
        },
        {
            'name': 'Christian Norgaard',
            'position': 'Defensive Midfield',
            'nationality': 'Denmark',
            'age': 30,
            'team': 'Brentford',
            'league': 'Premier League',
            'appearances': 28,
            'starts': 28,
            'market_value': 25000000,
            'market_value_display': '€25M'
        },
        {
            'name': 'Mathias Jensen',
            'position': 'Central Midfield',
            'nationality': 'Denmark',
            'age': 28,
            'team': 'Brentford',
            'league': 'Premier League',
            'appearances': 35,
            'starts': 33,
            'market_value': 22000000,
            'market_value_display': '€22M'
        },
        {
            'name': 'Vitaly Janelt',
            'position': 'Central Midfield',
            'nationality': 'Germany',
            'age': 25,
            'team': 'Brentford',
            'league': 'Premier League',
            'appearances': 32,
            'starts': 28,
            'market_value': 20000000,
            'market_value_display': '€20M'
        },
        {
            'name': 'Ethan Pinnock',
            'position': 'Centre-Back',
            'nationality': 'Jamaica',
            'age': 31,
            'team': 'Brentford',
            'league': 'Premier League',
            'appearances': 35,
            'starts': 35,
            'market_value': 18000000,
            'market_value_display': '€18M'
        },
        {
            'name': 'Nathan Collins',
            'position': 'Centre-Back',
            'nationality': 'Ireland',
            'age': 23,
            'team': 'Brentford',
            'league': 'Premier League',
            'appearances': 30,
            'starts': 29,
            'market_value': 25000000,
            'market_value_display': '€25M'
        },
        {
            'name': 'Aaron Hickey',
            'position': 'Right-Back',
            'nationality': 'Scotland',
            'age': 22,
            'team': 'Brentford',
            'league': 'Premier League',
            'appearances': 19,
            'starts': 18,
            'market_value': 25000000,
            'market_value_display': '€25M'
        },
        {
            'name': 'Rico Henry',
            'position': 'Left-Back',
            'nationality': 'England',
            'age': 26,
            'team': 'Brentford',
            'league': 'Premier League',
            'appearances': 15,
            'starts': 15,
            'market_value': 20000000,
            'market_value_display': '€20M'
        },
        {
            'name': 'Neal Maupay',
            'position': 'Centre-Forward',
            'nationality': 'France',
            'age': 27,
            'team': 'Brentford',
            'league': 'Premier League',
            'appearances': 25,
            'starts': 15,
            'market_value': 15000000,
            'market_value_display': '€15M'
        },
        
        # BRIGHTON
        {
            'name': 'Evan Ferguson',
            'position': 'Centre-Forward',
            'nationality': 'Ireland',
            'age': 19,
            'team': 'Brighton',
            'league': 'Premier League',
            'appearances': 25,
            'starts': 15,
            'market_value': 65000000,
            'market_value_display': '€65M'
        },
        {
            'name': 'Joao Pedro',
            'position': 'Centre-Forward',
            'nationality': 'Brazil',
            'age': 22,
            'team': 'Brighton',
            'league': 'Premier League',
            'appearances': 32,
            'starts': 20,
            'market_value': 45000000,
            'market_value_display': '€45M'
        },
        {
            'name': 'Simon Adingra',
            'position': 'Left Wing',
            'nationality': 'Ivory Coast',
            'age': 22,
            'team': 'Brighton',
            'league': 'Premier League',
            'appearances': 27,
            'starts': 18,
            'market_value': 35000000,
            'market_value_display': '€35M'
        },
        {
            'name': 'Pascal Gross',
            'position': 'Central Midfield',
            'nationality': 'Germany',
            'age': 32,
            'team': 'Brighton',
            'league': 'Premier League',
            'appearances': 38,
            'starts': 37,
            'market_value': 20000000,
            'market_value_display': '€20M'
        },
        {
            'name': 'Bart Verbruggen',
            'position': 'Goalkeeper',
            'nationality': 'Netherlands',
            'age': 21,
            'team': 'Brighton',
            'league': 'Premier League',
            'appearances': 27,
            'starts': 27,
            'market_value': 25000000,
            'market_value_display': '€25M'
        },
        {
            'name': 'Jason Steele',
            'position': 'Goalkeeper',
            'nationality': 'England',
            'age': 33,
            'team': 'Brighton',
            'league': 'Premier League',
            'appearances': 11,
            'starts': 11,
            'market_value': 8000000,
            'market_value_display': '€8M'
        },
        {
            'name': 'Lewis Dunk',
            'position': 'Centre-Back',
            'nationality': 'England',
            'age': 32,
            'team': 'Brighton',
            'league': 'Premier League',
            'appearances': 35,
            'starts': 35,
            'market_value': 25000000,
            'market_value_display': '€25M'
        },
        {
            'name': 'Jan Paul van Hecke',
            'position': 'Centre-Back',
            'nationality': 'Netherlands',
            'age': 23,
            'team': 'Brighton',
            'league': 'Premier League',
            'appearances': 30,
            'starts': 28,
            'market_value': 20000000,
            'market_value_display': '€20M'
        },
        {
            'name': 'Tariq Lamptey',
            'position': 'Right-Back',
            'nationality': 'Ghana',
            'age': 23,
            'team': 'Brighton',
            'league': 'Premier League',
            'appearances': 20,
            'starts': 12,
            'market_value': 18000000,
            'market_value_display': '€18M'
        },
        {
            'name': 'Pervis Estupinan',
            'position': 'Left-Back',
            'nationality': 'Ecuador',
            'age': 26,
            'team': 'Brighton',
            'league': 'Premier League',
            'appearances': 20,
            'starts': 20,
            'market_value': 35000000,
            'market_value_display': '€35M'
        },
        {
            'name': 'Billy Gilmour',
            'position': 'Central Midfield',
            'nationality': 'Scotland',
            'age': 23,
            'team': 'Brighton',
            'league': 'Premier League',
            'appearances': 25,
            'starts': 20,
            'market_value': 20000000,
            'market_value_display': '€20M'
        },
        {
            'name': 'Carlos Baleba',
            'position': 'Defensive Midfield',
            'nationality': 'Cameroon',
            'age': 20,
            'team': 'Brighton',
            'league': 'Premier League',
            'appearances': 22,
            'starts': 15,
            'market_value': 25000000,
            'market_value_display': '€25M'
        },
        {
            'name': 'Facundo Buonanotte',
            'position': 'Attacking Midfield',
            'nationality': 'Argentina',
            'age': 19,
            'team': 'Brighton',
            'league': 'Premier League',
            'appearances': 25,
            'starts': 12,
            'market_value': 20000000,
            'market_value_display': '€20M'
        },
        {
            'name': 'Kaoru Mitoma',
            'position': 'Left Wing',
            'nationality': 'Japan',
            'age': 27,
            'team': 'Brighton',
            'league': 'Premier League',
            'appearances': 19,
            'starts': 18,
            'market_value': 50000000,
            'market_value_display': '€50M'
        },
        {
            'name': 'Danny Welbeck',
            'position': 'Centre-Forward',
            'nationality': 'England',
            'age': 33,
            'team': 'Brighton',
            'league': 'Premier League',
            'appearances': 25,
            'starts': 15,
            'market_value': 8000000,
            'market_value_display': '€8M'
        },
        
        # BURNLEY
        {
            'name': 'Lyle Foster',
            'position': 'Centre-Forward',
            'nationality': 'South Africa',
            'age': 24,
            'team': 'Burnley',
            'league': 'Premier League',
            'appearances': 24,
            'starts': 20,
            'market_value': 15000000,
            'market_value_display': '€15M'
        },
        {
            'name': 'James Trafford',
            'position': 'Goalkeeper',
            'nationality': 'England',
            'age': 21,
            'team': 'Burnley',
            'league': 'Premier League',
            'appearances': 28,
            'starts': 28,
            'market_value': 20000000,
            'market_value_display': '€20M'
        },
        {
            'name': 'Dara OShea',
            'position': 'Centre-Back',
            'nationality': 'Ireland',
            'age': 25,
            'team': 'Burnley',
            'league': 'Premier League',
            'appearances': 30,
            'starts': 30,
            'market_value': 15000000,
            'market_value_display': '€15M'
        },
        {
            'name': 'Jordan Beyer',
            'position': 'Centre-Back',
            'nationality': 'Germany',
            'age': 23,
            'team': 'Burnley',
            'league': 'Premier League',
            'appearances': 25,
            'starts': 25,
            'market_value': 18000000,
            'market_value_display': '€18M'
        },
        {
            'name': 'Connor Roberts',
            'position': 'Right-Back',
            'nationality': 'Wales',
            'age': 28,
            'team': 'Burnley',
            'league': 'Premier League',
            'appearances': 25,
            'starts': 24,
            'market_value': 12000000,
            'market_value_display': '€12M'
        },
        {
            'name': 'Charlie Taylor',
            'position': 'Left-Back',
            'nationality': 'England',
            'age': 30,
            'team': 'Burnley',
            'league': 'Premier League',
            'appearances': 28,
            'starts': 27,
            'market_value': 8000000,
            'market_value_display': '€8M'
        },
        {
            'name': 'Josh Cullen',
            'position': 'Central Midfield',
            'nationality': 'Ireland',
            'age': 28,
            'team': 'Burnley',
            'league': 'Premier League',
            'appearances': 35,
            'starts': 35,
            'market_value': 15000000,
            'market_value_display': '€15M'
        },
        {
            'name': 'Sander Berge',
            'position': 'Central Midfield',
            'nationality': 'Norway',
            'age': 26,
            'team': 'Burnley',
            'league': 'Premier League',
            'appearances': 32,
            'starts': 30,
            'market_value': 20000000,
            'market_value_display': '€20M'
        },
        {
            'name': 'Wilson Odobert',
            'position': 'Left Wing',
            'nationality': 'France',
            'age': 19,
            'team': 'Burnley',
            'league': 'Premier League',
            'appearances': 30,
            'starts': 25,
            'market_value': 20000000,
            'market_value_display': '€20M'
        },
        {
            'name': 'Zeki Amdouni',
            'position': 'Centre-Forward',
            'nationality': 'Switzerland',
            'age': 23,
            'team': 'Burnley',
            'league': 'Premier League',
            'appearances': 30,
            'starts': 25,
            'market_value': 18000000,
            'market_value_display': '€18M'
        },
        {
            'name': 'Jacob Bruun Larsen',
            'position': 'Right Wing',
            'nationality': 'Denmark',
            'age': 25,
            'team': 'Burnley',
            'league': 'Premier League',
            'appearances': 25,
            'starts': 20,
            'market_value': 12000000,
            'market_value_display': '€12M'
        },
        {
            'name': 'Martin Odegaard',
            'position': 'Attacking Midfield',
            'nationality': 'Norway',
            'age': 25,
            'team': 'Arsenal',
            'league': 'Premier League',
            'appearances': 35,
            'starts': 34,
            'market_value': 110000000,
            'market_value_display': '€110M'
        },
        {
            'name': 'William Saliba',
            'position': 'Centre-Back',
            'nationality': 'France',
            'age': 23,
            'team': 'Arsenal',
            'league': 'Premier League',
            'appearances': 38,
            'starts': 38,
            'market_value': 80000000,
            'market_value_display': '€80M'
        },
        {
            'name': 'Declan Rice',
            'position': 'Defensive Midfield',
            'nationality': 'England',
            'age': 25,
            'team': 'Arsenal',
            'league': 'Premier League',
            'appearances': 37,
            'starts': 37,
            'market_value': 100000000,
            'market_value_display': '€100M'
        },
        {
            'name': 'Kai Havertz',
            'position': 'Centre-Forward',
            'nationality': 'Germany',
            'age': 25,
            'team': 'Arsenal',
            'league': 'Premier League',
            'appearances': 37,
            'starts': 30,
            'market_value': 70000000,
            'market_value_display': '€70M'
        },
        {
            'name': 'Gabriel Martinelli',
            'position': 'Left Wing',
            'nationality': 'Brazil',
            'age': 23,
            'team': 'Arsenal',
            'league': 'Premier League',
            'appearances': 35,
            'starts': 28,
            'market_value': 80000000,
            'market_value_display': '€80M'
        },
        {
            'name': 'Ben White',
            'position': 'Right-Back',
            'nationality': 'England',
            'age': 26,
            'team': 'Arsenal',
            'league': 'Premier League',
            'appearances': 37,
            'starts': 37,
            'market_value': 55000000,
            'market_value_display': '€55M'
        },
        {
            'name': 'Gabriel Magalhaes',
            'position': 'Centre-Back',
            'nationality': 'Brazil',
            'age': 26,
            'team': 'Arsenal',
            'league': 'Premier League',
            'appearances': 34,
            'starts': 34,
            'market_value': 65000000,
            'market_value_display': '€65M'
        },
        {
            'name': 'Oleksandr Zinchenko',
            'position': 'Left-Back',
            'nationality': 'Ukraine',
            'age': 27,
            'team': 'Arsenal',
            'league': 'Premier League',
            'appearances': 20,
            'starts': 18,
            'market_value': 42000000,
            'market_value_display': '€42M'
        },
        
        # ASTON VILLA
        {
            'name': 'Ollie Watkins',
            'position': 'Centre-Forward',
            'nationality': 'England',
            'age': 28,
            'team': 'Aston Villa',
            'league': 'Premier League',
            'appearances': 37,
            'starts': 37,
            'market_value': 65000000,
            'market_value_display': '€65M'
        },
        {
            'name': 'Douglas Luiz',
            'position': 'Central Midfield',
            'nationality': 'Brazil',
            'age': 26,
            'team': 'Aston Villa',
            'league': 'Premier League',
            'appearances': 35,
            'starts': 35,
            'market_value': 60000000,
            'market_value_display': '€60M'
        },
        {
            'name': 'Leon Bailey',
            'position': 'Right Wing',
            'nationality': 'Jamaica',
            'age': 26,
            'team': 'Aston Villa',
            'league': 'Premier League',
            'appearances': 35,
            'starts': 25,
            'market_value': 45000000,
            'market_value_display': '€45M'
        },
        {
            'name': 'John McGinn',
            'position': 'Central Midfield',
            'nationality': 'Scotland',
            'age': 29,
            'team': 'Aston Villa',
            'league': 'Premier League',
            'appearances': 35,
            'starts': 34,
            'market_value': 35000000,
            'market_value_display': '€35M'
        },
        {
            'name': 'Ezri Konsa',
            'position': 'Centre-Back',
            'nationality': 'England',
            'age': 26,
            'team': 'Aston Villa',
            'league': 'Premier League',
            'appearances': 35,
            'starts': 35,
            'market_value': 35000000,
            'market_value_display': '€35M'
        },
        
        # BOURNEMOUTH
        {
            'name': 'Dominic Solanke',
            'position': 'Centre-Forward',
            'nationality': 'England',
            'age': 26,
            'team': 'Bournemouth',
            'league': 'Premier League',
            'appearances': 38,
            'starts': 38,
            'market_value': 40000000,
            'market_value_display': '€40M'
        },
        {
            'name': 'Philip Billing',
            'position': 'Central Midfield',
            'nationality': 'Denmark',
            'age': 28,
            'team': 'Bournemouth',
            'league': 'Premier League',
            'appearances': 32,
            'starts': 30,
            'market_value': 25000000,
            'market_value_display': '€25M'
        },
        
        # BRENTFORD
        {
            'name': 'Ivan Toney',
            'position': 'Centre-Forward',
            'nationality': 'England',
            'age': 28,
            'team': 'Brentford',
            'league': 'Premier League',
            'appearances': 17,
            'starts': 17,
            'market_value': 50000000,
            'market_value_display': '€50M'
        },
        {
            'name': 'Bryan Mbeumo',
            'position': 'Right Wing',
            'nationality': 'Cameroon',
            'age': 24,
            'team': 'Brentford',
            'league': 'Premier League',
            'appearances': 25,
            'starts': 24,
            'market_value': 45000000,
            'market_value_display': '€45M'
        },
        {
            'name': 'Yoane Wissa',
            'position': 'Left Wing',
            'nationality': 'DR Congo',
            'age': 27,
            'team': 'Brentford',
            'league': 'Premier League',
            'appearances': 35,
            'starts': 30,
            'market_value': 30000000,
            'market_value_display': '€30M'
        },
        
        # BRIGHTON
        {
            'name': 'Evan Ferguson',
            'position': 'Centre-Forward',
            'nationality': 'Ireland',
            'age': 19,
            'team': 'Brighton',
            'league': 'Premier League',
            'appearances': 25,
            'starts': 15,
            'market_value': 65000000,
            'market_value_display': '€65M'
        },
        {
            'name': 'Joao Pedro',
            'position': 'Centre-Forward',
            'nationality': 'Brazil',
            'age': 22,
            'team': 'Brighton',
            'league': 'Premier League',
            'appearances': 32,
            'starts': 20,
            'market_value': 45000000,
            'market_value_display': '€45M'
        },
        {
            'name': 'Simon Adingra',
            'position': 'Left Wing',
            'nationality': 'Ivory Coast',
            'age': 22,
            'team': 'Brighton',
            'league': 'Premier League',
            'appearances': 27,
            'starts': 18,
            'market_value': 35000000,
            'market_value_display': '€35M'
        },
        {
            'name': 'Pascal Gross',
            'position': 'Central Midfield',
            'nationality': 'Germany',
            'age': 32,
            'team': 'Brighton',
            'league': 'Premier League',
            'appearances': 38,
            'starts': 37,
            'market_value': 20000000,
            'market_value_display': '€20M'
        },
        
        # BURNLEY
        {
            'name': 'Lyle Foster',
            'position': 'Centre-Forward',
            'nationality': 'South Africa',
            'age': 24,
            'team': 'Burnley',
            'league': 'Premier League',
            'appearances': 24,
            'starts': 20,
            'market_value': 15000000,
            'market_value_display': '€15M'
        },
        
        # CHELSEA
        {
            'name': 'Cole Palmer',
            'position': 'Right Wing',
            'nationality': 'England',
            'age': 22,
            'team': 'Chelsea',
            'league': 'Premier League',
            'appearances': 33,
            'starts': 30,
            'market_value': 80000000,
            'market_value_display': '€80M'
        },
        {
            'name': 'Enzo Fernandez',
            'position': 'Central Midfield',
            'nationality': 'Argentina',
            'age': 23,
            'team': 'Chelsea',
            'league': 'Premier League',
            'appearances': 32,
            'starts': 31,
            'market_value': 80000000,
            'market_value_display': '€80M'
        },
        {
            'name': 'Moises Caicedo',
            'position': 'Defensive Midfield',
            'nationality': 'Ecuador',
            'age': 22,
            'team': 'Chelsea',
            'league': 'Premier League',
            'appearances': 33,
            'starts': 32,
            'market_value': 90000000,
            'market_value_display': '€90M'
        },
        {
            'name': 'Nicolas Jackson',
            'position': 'Centre-Forward',
            'nationality': 'Senegal',
            'age': 23,
            'team': 'Chelsea',
            'league': 'Premier League',
            'appearances': 35,
            'starts': 30,
            'market_value': 55000000,
            'market_value_display': '€55M'
        },
        {
            'name': 'Conor Gallagher',
            'position': 'Central Midfield',
            'nationality': 'England',
            'age': 24,
            'team': 'Chelsea',
            'league': 'Premier League',
            'appearances': 37,
            'starts': 35,
            'market_value': 42000000,
            'market_value_display': '€42M'
        },
        {
            'name': 'Malo Gusto',
            'position': 'Right-Back',
            'nationality': 'France',
            'age': 20,
            'team': 'Chelsea',
            'league': 'Premier League',
            'appearances': 25,
            'starts': 23,
            'market_value': 35000000,
            'market_value_display': '€35M'
        },
        {
            'name': 'Robert Sanchez',
            'position': 'Goalkeeper',
            'nationality': 'Spain',
            'age': 26,
            'team': 'Chelsea',
            'league': 'Premier League',
            'appearances': 20,
            'starts': 20,
            'market_value': 25000000,
            'market_value_display': '€25M'
        },
        {
            'name': 'Djordje Petrovic',
            'position': 'Goalkeeper',
            'nationality': 'Serbia',
            'age': 24,
            'team': 'Chelsea',
            'league': 'Premier League',
            'appearances': 18,
            'starts': 18,
            'market_value': 20000000,
            'market_value_display': '€20M'
        },
        {
            'name': 'Thiago Silva',
            'position': 'Centre-Back',
            'nationality': 'Brazil',
            'age': 39,
            'team': 'Chelsea',
            'league': 'Premier League',
            'appearances': 27,
            'starts': 27,
            'market_value': 2000000,
            'market_value_display': '€2M'
        },
        {
            'name': 'Axel Disasi',
            'position': 'Centre-Back',
            'nationality': 'France',
            'age': 26,
            'team': 'Chelsea',
            'league': 'Premier League',
            'appearances': 35,
            'starts': 35,
            'market_value': 45000000,
            'market_value_display': '€45M'
        },
        {
            'name': 'Levi Colwill',
            'position': 'Centre-Back',
            'nationality': 'England',
            'age': 21,
            'team': 'Chelsea',
            'league': 'Premier League',
            'appearances': 32,
            'starts': 30,
            'market_value': 55000000,
            'market_value_display': '€55M'
        },
        {
            'name': 'Ben Chilwell',
            'position': 'Left-Back',
            'nationality': 'England',
            'age': 27,
            'team': 'Chelsea',
            'league': 'Premier League',
            'appearances': 13,
            'starts': 12,
            'market_value': 35000000,
            'market_value_display': '€35M'
        },
        {
            'name': 'Marc Cucurella',
            'position': 'Left-Back',
            'nationality': 'Spain',
            'age': 26,
            'team': 'Chelsea',
            'league': 'Premier League',
            'appearances': 20,
            'starts': 18,
            'market_value': 25000000,
            'market_value_display': '€25M'
        },
        {
            'name': 'Raheem Sterling',
            'position': 'Left Wing',
            'nationality': 'England',
            'age': 29,
            'team': 'Chelsea',
            'league': 'Premier League',
            'appearances': 31,
            'starts': 28,
            'market_value': 45000000,
            'market_value_display': '€45M'
        },
        {
            'name': 'Mykhailo Mudryk',
            'position': 'Left Wing',
            'nationality': 'Ukraine',
            'age': 23,
            'team': 'Chelsea',
            'league': 'Premier League',
            'appearances': 25,
            'starts': 15,
            'market_value': 40000000,
            'market_value_display': '€40M'
        },
        {
            'name': 'Noni Madueke',
            'position': 'Right Wing',
            'nationality': 'England',
            'age': 22,
            'team': 'Chelsea',
            'league': 'Premier League',
            'appearances': 25,
            'starts': 15,
            'market_value': 30000000,
            'market_value_display': '€30M'
        },
        {
            'name': 'Christopher Nkunku',
            'position': 'Centre-Forward',
            'nationality': 'France',
            'age': 26,
            'team': 'Chelsea',
            'league': 'Premier League',
            'appearances': 10,
            'starts': 8,
            'market_value': 60000000,
            'market_value_display': '€60M'
        },
        {
            'name': 'Armando Broja',
            'position': 'Centre-Forward',
            'nationality': 'Albania',
            'age': 22,
            'team': 'Chelsea',
            'league': 'Premier League',
            'appearances': 15,
            'starts': 8,
            'market_value': 25000000,
            'market_value_display': '€25M'
        },
        {
            'name': 'Lesley Ugochukwu',
            'position': 'Defensive Midfield',
            'nationality': 'France',
            'age': 20,
            'team': 'Chelsea',
            'league': 'Premier League',
            'appearances': 15,
            'starts': 8,
            'market_value': 25000000,
            'market_value_display': '€25M'
        },
        {
            'name': 'Romeo Lavia',
            'position': 'Defensive Midfield',
            'nationality': 'Belgium',
            'age': 20,
            'team': 'Chelsea',
            'league': 'Premier League',
            'appearances': 1,
            'starts': 1,
            'market_value': 35000000,
            'market_value_display': '€35M'
        },
        
        # CRYSTAL PALACE
        {
            'name': 'Eberechi Eze',
            'position': 'Attacking Midfield',
            'nationality': 'England',
            'age': 26,
            'team': 'Crystal Palace',
            'league': 'Premier League',
            'appearances': 27,
            'starts': 25,
            'market_value': 50000000,
            'market_value_display': '€50M'
        },
        {
            'name': 'Michael Olise',
            'position': 'Right Wing',
            'nationality': 'France',
            'age': 22,
            'team': 'Crystal Palace',
            'league': 'Premier League',
            'appearances': 19,
            'starts': 18,
            'market_value': 55000000,
            'market_value_display': '€55M'
        },
        {
            'name': 'Jean-Philippe Mateta',
            'position': 'Centre-Forward',
            'nationality': 'France',
            'age': 27,
            'team': 'Crystal Palace',
            'league': 'Premier League',
            'appearances': 35,
            'starts': 25,
            'market_value': 25000000,
            'market_value_display': '€25M'
        },
        {
            'name': 'Sam Johnstone',
            'position': 'Goalkeeper',
            'nationality': 'England',
            'age': 31,
            'team': 'Crystal Palace',
            'league': 'Premier League',
            'appearances': 20,
            'starts': 20,
            'market_value': 15000000,
            'market_value_display': '€15M'
        },
        {
            'name': 'Dean Henderson',
            'position': 'Goalkeeper',
            'nationality': 'England',
            'age': 27,
            'team': 'Crystal Palace',
            'league': 'Premier League',
            'appearances': 18,
            'starts': 18,
            'market_value': 18000000,
            'market_value_display': '€18M'
        },
        {
            'name': 'Joachim Andersen',
            'position': 'Centre-Back',
            'nationality': 'Denmark',
            'age': 28,
            'team': 'Crystal Palace',
            'league': 'Premier League',
            'appearances': 35,
            'starts': 35,
            'market_value': 35000000,
            'market_value_display': '€35M'
        },
        {
            'name': 'Marc Guehi',
            'position': 'Centre-Back',
            'nationality': 'England',
            'age': 23,
            'team': 'Crystal Palace',
            'league': 'Premier League',
            'appearances': 30,
            'starts': 30,
            'market_value': 45000000,
            'market_value_display': '€45M'
        },
        {
            'name': 'Nathaniel Clyne',
            'position': 'Right-Back',
            'nationality': 'England',
            'age': 33,
            'team': 'Crystal Palace',
            'league': 'Premier League',
            'appearances': 25,
            'starts': 25,
            'market_value': 8000000,
            'market_value_display': '€8M'
        },
        {
            'name': 'Daniel Munoz',
            'position': 'Right-Back',
            'nationality': 'Colombia',
            'age': 28,
            'team': 'Crystal Palace',
            'league': 'Premier League',
            'appearances': 12,
            'starts': 12,
            'market_value': 15000000,
            'market_value_display': '€15M'
        },
        {
            'name': 'Tyrick Mitchell',
            'position': 'Left-Back',
            'nationality': 'England',
            'age': 24,
            'team': 'Crystal Palace',
            'league': 'Premier League',
            'appearances': 30,
            'starts': 30,
            'market_value': 20000000,
            'market_value_display': '€20M'
        },
        {
            'name': 'Cheick Doucoure',
            'position': 'Defensive Midfield',
            'nationality': 'Mali',
            'age': 24,
            'team': 'Crystal Palace',
            'league': 'Premier League',
            'appearances': 15,
            'starts': 15,
            'market_value': 35000000,
            'market_value_display': '€35M'
        },
        {
            'name': 'Will Hughes',
            'position': 'Central Midfield',
            'nationality': 'England',
            'age': 29,
            'team': 'Crystal Palace',
            'league': 'Premier League',
            'appearances': 25,
            'starts': 20,
            'market_value': 12000000,
            'market_value_display': '€12M'
        },
        {
            'name': 'Jefferson Lerma',
            'position': 'Central Midfield',
            'nationality': 'Colombia',
            'age': 29,
            'team': 'Crystal Palace',
            'league': 'Premier League',
            'appearances': 30,
            'starts': 28,
            'market_value': 20000000,
            'market_value_display': '€20M'
        },
        {
            'name': 'Jordan Ayew',
            'position': 'Right Wing',
            'nationality': 'Ghana',
            'age': 32,
            'team': 'Crystal Palace',
            'league': 'Premier League',
            'appearances': 35,
            'starts': 30,
            'market_value': 12000000,
            'market_value_display': '€12M'
        },
        {
            'name': 'Odsonne Edouard',
            'position': 'Centre-Forward',
            'nationality': 'France',
            'age': 26,
            'team': 'Crystal Palace',
            'league': 'Premier League',
            'appearances': 25,
            'starts': 15,
            'market_value': 18000000,
            'market_value_display': '€18M'
        },
        
        # EVERTON
        {
            'name': 'Jarrad Branthwaite',
            'position': 'Centre-Back',
            'nationality': 'England',
            'age': 22,
            'team': 'Everton',
            'league': 'Premier League',
            'appearances': 35,
            'starts': 35,
            'market_value': 45000000,
            'market_value_display': '€45M'
        },
        {
            'name': 'Dominic Calvert-Lewin',
            'position': 'Centre-Forward',
            'nationality': 'England',
            'age': 27,
            'team': 'Everton',
            'league': 'Premier League',
            'appearances': 32,
            'starts': 30,
            'market_value': 25000000,
            'market_value_display': '€25M'
        },
        {
            'name': 'Abdoulaye Doucoure',
            'position': 'Central Midfield',
            'nationality': 'Mali',
            'age': 31,
            'team': 'Everton',
            'league': 'Premier League',
            'appearances': 32,
            'starts': 30,
            'market_value': 20000000,
            'market_value_display': '€20M'
        },
        {
            'name': 'Jordan Pickford',
            'position': 'Goalkeeper',
            'nationality': 'England',
            'age': 30,
            'team': 'Everton',
            'league': 'Premier League',
            'appearances': 38,
            'starts': 38,
            'market_value': 25000000,
            'market_value_display': '€25M'
        },
        {
            'name': 'James Tarkowski',
            'position': 'Centre-Back',
            'nationality': 'England',
            'age': 31,
            'team': 'Everton',
            'league': 'Premier League',
            'appearances': 38,
            'starts': 38,
            'market_value': 20000000,
            'market_value_display': '€20M'
        },
        {
            'name': 'Vitalii Mykolenko',
            'position': 'Left-Back',
            'nationality': 'Ukraine',
            'age': 25,
            'team': 'Everton',
            'league': 'Premier League',
            'appearances': 30,
            'starts': 30,
            'market_value': 20000000,
            'market_value_display': '€20M'
        },
        {
            'name': 'Seamus Coleman',
            'position': 'Right-Back',
            'nationality': 'Ireland',
            'age': 35,
            'team': 'Everton',
            'league': 'Premier League',
            'appearances': 20,
            'starts': 20,
            'market_value': 5000000,
            'market_value_display': '€5M'
        },
        {
            'name': 'Ashley Young',
            'position': 'Right-Back',
            'nationality': 'England',
            'age': 38,
            'team': 'Everton',
            'league': 'Premier League',
            'appearances': 18,
            'starts': 18,
            'market_value': 2000000,
            'market_value_display': '€2M'
        },
        {
            'name': 'Idrissa Gueye',
            'position': 'Defensive Midfield',
            'nationality': 'Senegal',
            'age': 34,
            'team': 'Everton',
            'league': 'Premier League',
            'appearances': 30,
            'starts': 28,
            'market_value': 8000000,
            'market_value_display': '€8M'
        },
        {
            'name': 'Amadou Onana',
            'position': 'Defensive Midfield',
            'nationality': 'Belgium',
            'age': 22,
            'team': 'Everton',
            'league': 'Premier League',
            'appearances': 30,
            'starts': 28,
            'market_value': 50000000,
            'market_value_display': '€50M'
        },
        {
            'name': 'James Garner',
            'position': 'Central Midfield',
            'nationality': 'England',
            'age': 23,
            'team': 'Everton',
            'league': 'Premier League',
            'appearances': 25,
            'starts': 20,
            'market_value': 25000000,
            'market_value_display': '€25M'
        },
        {
            'name': 'Jack Harrison',
            'position': 'Left Wing',
            'nationality': 'England',
            'age': 27,
            'team': 'Everton',
            'league': 'Premier League',
            'appearances': 30,
            'starts': 28,
            'market_value': 20000000,
            'market_value_display': '€20M'
        },
        {
            'name': 'Dwight McNeil',
            'position': 'Left Wing',
            'nationality': 'England',
            'age': 24,
            'team': 'Everton',
            'league': 'Premier League',
            'appearances': 35,
            'starts': 32,
            'market_value': 25000000,
            'market_value_display': '€25M'
        },
        {
            'name': 'Beto',
            'position': 'Centre-Forward',
            'nationality': 'Portugal',
            'age': 26,
            'team': 'Everton',
            'league': 'Premier League',
            'appearances': 25,
            'starts': 15,
            'market_value': 20000000,
            'market_value_display': '€20M'
        },
        {
            'name': 'Arnaut Danjuma',
            'position': 'Left Wing',
            'nationality': 'Netherlands',
            'age': 27,
            'team': 'Everton',
            'league': 'Premier League',
            'appearances': 20,
            'starts': 10,
            'market_value': 18000000,
            'market_value_display': '€18M'
        },
        
        # FULHAM
        {
            'name': 'Joao Palhinha',
            'position': 'Defensive Midfield',
            'nationality': 'Portugal',
            'age': 28,
            'team': 'Fulham',
            'league': 'Premier League',
            'appearances': 33,
            'starts': 33,
            'market_value': 45000000,
            'market_value_display': '€45M'
        },
        {
            'name': 'Andreas Pereira',
            'position': 'Attacking Midfield',
            'nationality': 'Brazil',
            'age': 28,
            'team': 'Fulham',
            'league': 'Premier League',
            'appearances': 33,
            'starts': 32,
            'market_value': 25000000,
            'market_value_display': '€25M'
        },
        {
            'name': 'Willian',
            'position': 'Left Wing',
            'nationality': 'Brazil',
            'age': 35,
            'team': 'Fulham',
            'league': 'Premier League',
            'appearances': 30,
            'starts': 28,
            'market_value': 8000000,
            'market_value_display': '€8M'
        },
        {
            'name': 'Bernd Leno',
            'position': 'Goalkeeper',
            'nationality': 'Germany',
            'age': 32,
            'team': 'Fulham',
            'league': 'Premier League',
            'appearances': 38,
            'starts': 38,
            'market_value': 18000000,
            'market_value_display': '€18M'
        },
        {
            'name': 'Tosin Adarabioyo',
            'position': 'Centre-Back',
            'nationality': 'England',
            'age': 26,
            'team': 'Fulham',
            'league': 'Premier League',
            'appearances': 25,
            'starts': 25,
            'market_value': 20000000,
            'market_value_display': '€20M'
        },
        {
            'name': 'Calvin Bassey',
            'position': 'Centre-Back',
            'nationality': 'Nigeria',
            'age': 24,
            'team': 'Fulham',
            'league': 'Premier League',
            'appearances': 25,
            'starts': 22,
            'market_value': 20000000,
            'market_value_display': '€20M'
        },
        {
            'name': 'Issa Diop',
            'position': 'Centre-Back',
            'nationality': 'France',
            'age': 27,
            'team': 'Fulham',
            'league': 'Premier League',
            'appearances': 20,
            'starts': 18,
            'market_value': 15000000,
            'market_value_display': '€15M'
        },
        {
            'name': 'Kenny Tete',
            'position': 'Right-Back',
            'nationality': 'Netherlands',
            'age': 28,
            'team': 'Fulham',
            'league': 'Premier League',
            'appearances': 25,
            'starts': 25,
            'market_value': 15000000,
            'market_value_display': '€15M'
        },
        {
            'name': 'Antonee Robinson',
            'position': 'Left-Back',
            'nationality': 'USA',
            'age': 26,
            'team': 'Fulham',
            'league': 'Premier League',
            'appearances': 35,
            'starts': 35,
            'market_value': 25000000,
            'market_value_display': '€25M'
        },
        {
            'name': 'Harrison Reed',
            'position': 'Central Midfield',
            'nationality': 'England',
            'age': 29,
            'team': 'Fulham',
            'league': 'Premier League',
            'appearances': 30,
            'starts': 25,
            'market_value': 15000000,
            'market_value_display': '€15M'
        },
        {
            'name': 'Tom Cairney',
            'position': 'Central Midfield',
            'nationality': 'Scotland',
            'age': 33,
            'team': 'Fulham',
            'league': 'Premier League',
            'appearances': 25,
            'starts': 20,
            'market_value': 8000000,
            'market_value_display': '€8M'
        },
        {
            'name': 'Alex Iwobi',
            'position': 'Right Wing',
            'nationality': 'Nigeria',
            'age': 28,
            'team': 'Fulham',
            'league': 'Premier League',
            'appearances': 35,
            'starts': 32,
            'market_value': 20000000,
            'market_value_display': '€20M'
        },
        {
            'name': 'Bobby De Cordova-Reid',
            'position': 'Right Wing',
            'nationality': 'Jamaica',
            'age': 31,
            'team': 'Fulham',
            'league': 'Premier League',
            'appearances': 35,
            'starts': 30,
            'market_value': 12000000,
            'market_value_display': '€12M'
        },
        {
            'name': 'Raul Jimenez',
            'position': 'Centre-Forward',
            'nationality': 'Mexico',
            'age': 33,
            'team': 'Fulham',
            'league': 'Premier League',
            'appearances': 25,
            'starts': 20,
            'market_value': 8000000,
            'market_value_display': '€8M'
        },
        {
            'name': 'Rodrigo Muniz',
            'position': 'Centre-Forward',
            'nationality': 'Brazil',
            'age': 23,
            'team': 'Fulham',
            'league': 'Premier League',
            'appearances': 20,
            'starts': 15,
            'market_value': 15000000,
            'market_value_display': '€15M'
        },
        
        # LIVERPOOL
        {
            'name': 'Mohamed Salah',
            'position': 'Right Wing',
            'nationality': 'Egypt',
            'age': 32,
            'team': 'Liverpool',
            'league': 'Premier League',
            'appearances': 32,
            'starts': 31,
            'market_value': 65000000,
            'market_value_display': '€65M'
        },
        {
            'name': 'Virgil van Dijk',
            'position': 'Centre-Back',
            'nationality': 'Netherlands',
            'age': 33,
            'team': 'Liverpool',
            'league': 'Premier League',
            'appearances': 36,
            'starts': 36,
            'market_value': 45000000,
            'market_value_display': '€45M'
        },
        {
            'name': 'Darwin Nunez',
            'position': 'Centre-Forward',
            'nationality': 'Uruguay',
            'age': 25,
            'team': 'Liverpool',
            'league': 'Premier League',
            'appearances': 36,
            'starts': 25,
            'market_value': 70000000,
            'market_value_display': '€70M'
        },
        {
            'name': 'Luis Diaz',
            'position': 'Left Wing',
            'nationality': 'Colombia',
            'age': 27,
            'team': 'Liverpool',
            'league': 'Premier League',
            'appearances': 36,
            'starts': 32,
            'market_value': 75000000,
            'market_value_display': '€75M'
        },
        {
            'name': 'Trent Alexander-Arnold',
            'position': 'Right-Back',
            'nationality': 'England',
            'age': 25,
            'team': 'Liverpool',
            'league': 'Premier League',
            'appearances': 28,
            'starts': 28,
            'market_value': 70000000,
            'market_value_display': '€70M'
        },
        {
            'name': 'Andy Robertson',
            'position': 'Left-Back',
            'nationality': 'Scotland',
            'age': 30,
            'team': 'Liverpool',
            'league': 'Premier League',
            'appearances': 23,
            'starts': 22,
            'market_value': 35000000,
            'market_value_display': '€35M'
        },
        {
            'name': 'Alisson',
            'position': 'Goalkeeper',
            'nationality': 'Brazil',
            'age': 31,
            'team': 'Liverpool',
            'league': 'Premier League',
            'appearances': 28,
            'starts': 28,
            'market_value': 32000000,
            'market_value_display': '€32M'
        },
        {
            'name': 'Caoimhin Kelleher',
            'position': 'Goalkeeper',
            'nationality': 'Ireland',
            'age': 25,
            'team': 'Liverpool',
            'league': 'Premier League',
            'appearances': 10,
            'starts': 10,
            'market_value': 20000000,
            'market_value_display': '€20M'
        },
        {
            'name': 'Ibrahima Konate',
            'position': 'Centre-Back',
            'nationality': 'France',
            'age': 25,
            'team': 'Liverpool',
            'league': 'Premier League',
            'appearances': 25,
            'starts': 25,
            'market_value': 45000000,
            'market_value_display': '€45M'
        },
        {
            'name': 'Joel Matip',
            'position': 'Centre-Back',
            'nationality': 'Cameroon',
            'age': 32,
            'team': 'Liverpool',
            'league': 'Premier League',
            'appearances': 10,
            'starts': 9,
            'market_value': 8000000,
            'market_value_display': '€8M'
        },
        {
            'name': 'Joe Gomez',
            'position': 'Centre-Back',
            'nationality': 'England',
            'age': 27,
            'team': 'Liverpool',
            'league': 'Premier League',
            'appearances': 32,
            'starts': 25,
            'market_value': 25000000,
            'market_value_display': '€25M'
        },
        {
            'name': 'Kostas Tsimikas',
            'position': 'Left-Back',
            'nationality': 'Greece',
            'age': 28,
            'team': 'Liverpool',
            'league': 'Premier League',
            'appearances': 15,
            'starts': 13,
            'market_value': 20000000,
            'market_value_display': '€20M'
        },
        {
            'name': 'Conor Bradley',
            'position': 'Right-Back',
            'nationality': 'Northern Ireland',
            'age': 20,
            'team': 'Liverpool',
            'league': 'Premier League',
            'appearances': 10,
            'starts': 10,
            'market_value': 25000000,
            'market_value_display': '€25M'
        },
        {
            'name': 'Alexis Mac Allister',
            'position': 'Central Midfield',
            'nationality': 'Argentina',
            'age': 25,
            'team': 'Liverpool',
            'league': 'Premier League',
            'appearances': 35,
            'starts': 33,
            'market_value': 70000000,
            'market_value_display': '€70M'
        },
        {
            'name': 'Dominik Szoboszlai',
            'position': 'Central Midfield',
            'nationality': 'Hungary',
            'age': 23,
            'team': 'Liverpool',
            'league': 'Premier League',
            'appearances': 28,
            'starts': 28,
            'market_value': 75000000,
            'market_value_display': '€75M'
        },
        {
            'name': 'Wataru Endo',
            'position': 'Defensive Midfield',
            'nationality': 'Japan',
            'age': 31,
            'team': 'Liverpool',
            'league': 'Premier League',
            'appearances': 25,
            'starts': 20,
            'market_value': 15000000,
            'market_value_display': '€15M'
        },
        {
            'name': 'Curtis Jones',
            'position': 'Central Midfield',
            'nationality': 'England',
            'age': 23,
            'team': 'Liverpool',
            'league': 'Premier League',
            'appearances': 25,
            'starts': 20,
            'market_value': 35000000,
            'market_value_display': '€35M'
        },
        {
            'name': 'Harvey Elliott',
            'position': 'Right Wing',
            'nationality': 'England',
            'age': 21,
            'team': 'Liverpool',
            'league': 'Premier League',
            'appearances': 35,
            'starts': 20,
            'market_value': 35000000,
            'market_value_display': '€35M'
        },
        {
            'name': 'Cody Gakpo',
            'position': 'Centre-Forward',
            'nationality': 'Netherlands',
            'age': 25,
            'team': 'Liverpool',
            'league': 'Premier League',
            'appearances': 35,
            'starts': 25,
            'market_value': 55000000,
            'market_value_display': '€55M'
        },
        {
            'name': 'Diogo Jota',
            'position': 'Left Wing',
            'nationality': 'Portugal',
            'age': 27,
            'team': 'Liverpool',
            'league': 'Premier League',
            'appearances': 20,
            'starts': 15,
            'market_value': 45000000,
            'market_value_display': '€45M'
        },
        {
            'name': 'Ryan Gravenberch',
            'position': 'Central Midfield',
            'nationality': 'Netherlands',
            'age': 22,
            'team': 'Liverpool',
            'league': 'Premier League',
            'appearances': 25,
            'starts': 15,
            'market_value': 35000000,
            'market_value_display': '€35M'
        },
        
        # LUTON TOWN
        {
            'name': 'Carlton Morris',
            'position': 'Centre-Forward',
            'nationality': 'England',
            'age': 28,
            'team': 'Luton Town',
            'league': 'Premier League',
            'appearances': 37,
            'starts': 35,
            'market_value': 12000000,
            'market_value_display': '€12M'
        },
        {
            'name': 'Thomas Kaminski',
            'position': 'Goalkeeper',
            'nationality': 'Belgium',
            'age': 31,
            'team': 'Luton Town',
            'league': 'Premier League',
            'appearances': 35,
            'starts': 35,
            'market_value': 8000000,
            'market_value_display': '€8M'
        },
        {
            'name': 'Teden Mengi',
            'position': 'Centre-Back',
            'nationality': 'England',
            'age': 22,
            'team': 'Luton Town',
            'league': 'Premier League',
            'appearances': 30,
            'starts': 30,
            'market_value': 12000000,
            'market_value_display': '€12M'
        },
        {
            'name': 'Gabriel Osho',
            'position': 'Centre-Back',
            'nationality': 'England',
            'age': 25,
            'team': 'Luton Town',
            'league': 'Premier League',
            'appearances': 25,
            'starts': 25,
            'market_value': 10000000,
            'market_value_display': '€10M'
        },
        {
            'name': 'Alfie Doughty',
            'position': 'Left-Back',
            'nationality': 'England',
            'age': 24,
            'team': 'Luton Town',
            'league': 'Premier League',
            'appearances': 35,
            'starts': 35,
            'market_value': 12000000,
            'market_value_display': '€12M'
        },
        {
            'name': 'Ross Barkley',
            'position': 'Central Midfield',
            'nationality': 'England',
            'age': 30,
            'team': 'Luton Town',
            'league': 'Premier League',
            'appearances': 32,
            'starts': 30,
            'market_value': 8000000,
            'market_value_display': '€8M'
        },
        {
            'name': 'Albert Sambi Lokonga',
            'position': 'Central Midfield',
            'nationality': 'Belgium',
            'age': 24,
            'team': 'Luton Town',
            'league': 'Premier League',
            'appearances': 15,
            'starts': 15,
            'market_value': 15000000,
            'market_value_display': '€15M'
        },
        {
            'name': 'Jordan Clark',
            'position': 'Central Midfield',
            'nationality': 'England',
            'age': 30,
            'team': 'Luton Town',
            'league': 'Premier League',
            'appearances': 30,
            'starts': 28,
            'market_value': 8000000,
            'market_value_display': '€8M'
        },
        {
            'name': 'Chiedozie Ogbene',
            'position': 'Right Wing',
            'nationality': 'Ireland',
            'age': 26,
            'team': 'Luton Town',
            'league': 'Premier League',
            'appearances': 35,
            'starts': 32,
            'market_value': 12000000,
            'market_value_display': '€12M'
        },
        {
            'name': 'Elijah Adebayo',
            'position': 'Centre-Forward',
            'nationality': 'England',
            'age': 26,
            'team': 'Luton Town',
            'league': 'Premier League',
            'appearances': 25,
            'starts': 20,
            'market_value': 10000000,
            'market_value_display': '€10M'
        },
        {
            'name': 'Tahith Chong',
            'position': 'Left Wing',
            'nationality': 'Netherlands',
            'age': 24,
            'team': 'Luton Town',
            'league': 'Premier League',
            'appearances': 30,
            'starts': 25,
            'market_value': 10000000,
            'market_value_display': '€10M'
        },
        
        # MANCHESTER CITY
        {
            'name': 'Erling Haaland',
            'position': 'Centre-Forward',
            'nationality': 'Norway',
            'age': 24,
            'team': 'Manchester City',
            'league': 'Premier League',
            'appearances': 35,
            'starts': 33,
            'market_value': 180000000,
            'market_value_display': '€180M'
        },
        {
            'name': 'Kevin De Bruyne',
            'position': 'Attacking Midfield',
            'nationality': 'Belgium',
            'age': 33,
            'team': 'Manchester City',
            'league': 'Premier League',
            'appearances': 18,
            'starts': 15,
            'market_value': 60000000,
            'market_value_display': '€60M'
        },
        {
            'name': 'Phil Foden',
            'position': 'Right Wing',
            'nationality': 'England',
            'age': 24,
            'team': 'Manchester City',
            'league': 'Premier League',
            'appearances': 35,
            'starts': 32,
            'market_value': 130000000,
            'market_value_display': '€130M'
        },
        {
            'name': 'Ruben Dias',
            'position': 'Centre-Back',
            'nationality': 'Portugal',
            'age': 27,
            'team': 'Manchester City',
            'league': 'Premier League',
            'appearances': 30,
            'starts': 29,
            'market_value': 80000000,
            'market_value_display': '€80M'
        },
        {
            'name': 'Rodri',
            'position': 'Defensive Midfield',
            'nationality': 'Spain',
            'age': 28,
            'team': 'Manchester City',
            'league': 'Premier League',
            'appearances': 34,
            'starts': 33,
            'market_value': 110000000,
            'market_value_display': '€110M'
        },
        {
            'name': 'Bernardo Silva',
            'position': 'Right Wing',
            'nationality': 'Portugal',
            'age': 29,
            'team': 'Manchester City',
            'league': 'Premier League',
            'appearances': 35,
            'starts': 32,
            'market_value': 80000000,
            'market_value_display': '€80M'
        },
        {
            'name': 'Jack Grealish',
            'position': 'Left Wing',
            'nationality': 'England',
            'age': 28,
            'team': 'Manchester City',
            'league': 'Premier League',
            'appearances': 20,
            'starts': 15,
            'market_value': 55000000,
            'market_value_display': '€55M'
        },
        {
            'name': 'Ederson',
            'position': 'Goalkeeper',
            'nationality': 'Brazil',
            'age': 30,
            'team': 'Manchester City',
            'league': 'Premier League',
            'appearances': 35,
            'starts': 35,
            'market_value': 40000000,
            'market_value_display': '€40M'
        },
        {
            'name': 'Stefan Ortega',
            'position': 'Goalkeeper',
            'nationality': 'Germany',
            'age': 31,
            'team': 'Manchester City',
            'league': 'Premier League',
            'appearances': 3,
            'starts': 3,
            'market_value': 15000000,
            'market_value_display': '€15M'
        },
        {
            'name': 'John Stones',
            'position': 'Centre-Back',
            'nationality': 'England',
            'age': 30,
            'team': 'Manchester City',
            'league': 'Premier League',
            'appearances': 16,
            'starts': 15,
            'market_value': 35000000,
            'market_value_display': '€35M'
        },
        {
            'name': 'Manuel Akanji',
            'position': 'Centre-Back',
            'nationality': 'Switzerland',
            'age': 28,
            'team': 'Manchester City',
            'league': 'Premier League',
            'appearances': 30,
            'starts': 28,
            'market_value': 35000000,
            'market_value_display': '€35M'
        },
        {
            'name': 'Nathan Ake',
            'position': 'Centre-Back',
            'nationality': 'Netherlands',
            'age': 29,
            'team': 'Manchester City',
            'league': 'Premier League',
            'appearances': 25,
            'starts': 22,
            'market_value': 35000000,
            'market_value_display': '€35M'
        },
        {
            'name': 'Kyle Walker',
            'position': 'Right-Back',
            'nationality': 'England',
            'age': 34,
            'team': 'Manchester City',
            'league': 'Premier League',
            'appearances': 30,
            'starts': 30,
            'market_value': 15000000,
            'market_value_display': '€15M'
        },
        {
            'name': 'Rico Lewis',
            'position': 'Right-Back',
            'nationality': 'England',
            'age': 19,
            'team': 'Manchester City',
            'league': 'Premier League',
            'appearances': 20,
            'starts': 15,
            'market_value': 35000000,
            'market_value_display': '€35M'
        },
        {
            'name': 'Josko Gvardiol',
            'position': 'Left-Back',
            'nationality': 'Croatia',
            'age': 22,
            'team': 'Manchester City',
            'league': 'Premier League',
            'appearances': 30,
            'starts': 28,
            'market_value': 75000000,
            'market_value_display': '€75M'
        },
        {
            'name': 'Matheus Nunes',
            'position': 'Central Midfield',
            'nationality': 'Portugal',
            'age': 25,
            'team': 'Manchester City',
            'league': 'Premier League',
            'appearances': 25,
            'starts': 15,
            'market_value': 45000000,
            'market_value_display': '€45M'
        },
        {
            'name': 'Mateo Kovacic',
            'position': 'Central Midfield',
            'nationality': 'Croatia',
            'age': 30,
            'team': 'Manchester City',
            'league': 'Premier League',
            'appearances': 25,
            'starts': 20,
            'market_value': 25000000,
            'market_value_display': '€25M'
        },
        {
            'name': 'Kalvin Phillips',
            'position': 'Defensive Midfield',
            'nationality': 'England',
            'age': 28,
            'team': 'Manchester City',
            'league': 'Premier League',
            'appearances': 4,
            'starts': 2,
            'market_value': 20000000,
            'market_value_display': '€20M'
        },
        {
            'name': 'Jeremy Doku',
            'position': 'Left Wing',
            'nationality': 'Belgium',
            'age': 22,
            'team': 'Manchester City',
            'league': 'Premier League',
            'appearances': 25,
            'starts': 15,
            'market_value': 50000000,
            'market_value_display': '€50M'
        },
        {
            'name': 'Julian Alvarez',
            'position': 'Centre-Forward',
            'nationality': 'Argentina',
            'age': 24,
            'team': 'Manchester City',
            'league': 'Premier League',
            'appearances': 35,
            'starts': 25,
            'market_value': 90000000,
            'market_value_display': '€90M'
        },
        {
            'name': 'Oscar Bobb',
            'position': 'Right Wing',
            'nationality': 'Norway',
            'age': 20,
            'team': 'Manchester City',
            'league': 'Premier League',
            'appearances': 15,
            'starts': 8,
            'market_value': 25000000,
            'market_value_display': '€25M'
        },
        # Add Leicester City
        {
            'name': 'Kiernan Dewsbury-Hall',
            'position': 'Central Midfield',
            'nationality': 'England',
            'age': 25,
            'team': 'Leicester City',
            'league': 'Premier League',
            'appearances': 44,
            'starts': 43,
            'market_value': 28_000_000,
            'market_value_display': '€28M'
        },
        {
            'name': 'Jamie Vardy',
            'position': 'Centre-Forward',
            'nationality': 'England',
            'age': 37,
            'team': 'Leicester City',
            'league': 'Premier League',
            'appearances': 37,
            'starts': 20,
            'market_value': 2_000_000,
            'market_value_display': '€2M'
        },
        {
            'name': 'Wout Faes',
            'position': 'Centre-Back',
            'nationality': 'Belgium',
            'age': 26,
            'team': 'Leicester City',
            'league': 'Premier League',
            'appearances': 44,
            'starts': 44,
            'market_value': 18_000_000,
            'market_value_display': '€18M'
        },
        {
            'name': 'Mads Hermansen',
            'position': 'Goalkeeper',
            'nationality': 'Denmark',
            'age': 24,
            'team': 'Leicester City',
            'league': 'Premier League',
            'appearances': 44,
            'starts': 44,
            'market_value': 10_000_000,
            'market_value_display': '€10M'
        },
        {
            'name': 'Wilfred Ndidi',
            'position': 'Defensive Midfield',
            'nationality': 'Nigeria',
            'age': 27,
            'team': 'Leicester City',
            'league': 'Premier League',
            'appearances': 32,
            'starts': 28,
            'market_value': 16_000_000,
            'market_value_display': '€16M'
        },
        {
            'name': 'Stephy Mavididi',
            'position': 'Left Wing',
            'nationality': 'England',
            'age': 26,
            'team': 'Leicester City',
            'league': 'Premier League',
            'appearances': 44,
            'starts': 41,
            'market_value': 12_000_000,
            'market_value_display': '€12M'
        },
        # Add Ipswich Town
        {
            'name': 'Leif Davis',
            'position': 'Left-Back',
            'nationality': 'England',
            'age': 24,
            'team': 'Ipswich Town',
            'league': 'Premier League',
            'appearances': 46,
            'starts': 46,
            'market_value': 10_000_000,
            'market_value_display': '€10M'
        },
        {
            'name': 'Conor Chaplin',
            'position': 'Attacking Midfield',
            'nationality': 'England',
            'age': 27,
            'team': 'Ipswich Town',
            'league': 'Premier League',
            'appearances': 46,
            'starts': 44,
            'market_value': 5_000_000,
            'market_value_display': '€5M'
        },
        {
            'name': 'Sam Morsy',
            'position': 'Central Midfield',
            'nationality': 'Egypt',
            'age': 32,
            'team': 'Ipswich Town',
            'league': 'Premier League',
            'appearances': 44,
            'starts': 44,
            'market_value': 2_000_000,
            'market_value_display': '€2M'
        },
        {
            'name': 'Vaclav Hladky',
            'position': 'Goalkeeper',
            'nationality': 'Czech Republic',
            'age': 33,
            'team': 'Ipswich Town',
            'league': 'Premier League',
            'appearances': 46,
            'starts': 46,
            'market_value': 1_000_000,
            'market_value_display': '€1M'
        },
        {
            'name': 'George Hirst',
            'position': 'Centre-Forward',
            'nationality': 'England',
            'age': 25,
            'team': 'Ipswich Town',
            'league': 'Premier League',
            'appearances': 32,
            'starts': 25,
            'market_value': 3_000_000,
            'market_value_display': '€3M'
        },
        # Add Southampton
        {
            'name': 'Adam Armstrong',
            'position': 'Centre-Forward',
            'nationality': 'England',
            'age': 27,
            'team': 'Southampton',
            'league': 'Premier League',
            'appearances': 46,
            'starts': 44,
            'market_value': 10_000_000,
            'market_value_display': '€10M'
        },
        {
            'name': 'Kyle Walker-Peters',
            'position': 'Right-Back',
            'nationality': 'England',
            'age': 27,
            'team': 'Southampton',
            'league': 'Premier League',
            'appearances': 44,
            'starts': 44,
            'market_value': 18_000_000,
            'market_value_display': '€18M'
        },
        {
            'name': 'Gavin Bazunu',
            'position': 'Goalkeeper',
            'nationality': 'Ireland',
            'age': 22,
            'team': 'Southampton',
            'league': 'Premier League',
            'appearances': 44,
            'starts': 44,
            'market_value': 10_000_000,
            'market_value_display': '€10M'
        },
        {
            'name': 'Che Adams',
            'position': 'Centre-Forward',
            'nationality': 'Scotland',
            'age': 28,
            'team': 'Southampton',
            'league': 'Premier League',
            'appearances': 40,
            'starts': 30,
            'market_value': 10_000_000,
            'market_value_display': '€10M'
        },
        {
            'name': 'Will Smallbone',
            'position': 'Central Midfield',
            'nationality': 'Ireland',
            'age': 24,
            'team': 'Southampton',
            'league': 'Premier League',
            'appearances': 44,
            'starts': 40,
            'market_value': 6_000_000,
            'market_value_display': '€6M'
        },
        {
            'name': 'Jan Bednarek',
            'position': 'Centre-Back',
            'nationality': 'Poland',
            'age': 28,
            'team': 'Southampton',
            'league': 'Premier League',
            'appearances': 44,
            'starts': 44,
            'market_value': 8_000_000,
            'market_value_display': '€8M'
        },
        {
            'name': 'Flynn Downes',
            'position': 'Defensive Midfield',
            'nationality': 'England',
            'age': 25,
            'team': 'Southampton',
            'league': 'Premier League',
            'appearances': 37,
            'starts': 35,
            'market_value': 8_000_000,
            'market_value_display': '€8M'
        }
    ]
    
    return players_data

def fetch_players():
    """Fetch players using static data"""
    print("Fetching Premier League players from static data...")
    
    players_data = get_premier_league_players()
    
    # Save to database
    save_players_to_db(players_data)
    print(f"Successfully fetched and saved {len(players_data)} players")
    
    # Debug: Show some of the players we found
    if players_data:
        print("Sample players found:")
        for i, player in enumerate(players_data[:5]):
            print(f"  {i+1}. {player['name']} ({player['team']}) - {player['appearances']} apps")
    
    return players_data

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

def save_players_to_db(players_data):
    """Save players to database"""
    with get_db() as db:
        # Clear existing players
        db.execute('DELETE FROM players')
        
        # Insert new players
        db.executemany('''
            INSERT INTO players 
            (name, position, nationality, age, team, league, appearances, starts, market_value, market_value_display, last_updated)
            VALUES 
            (:name, :position, :nationality, :age, :team, :league, :appearances, :starts, :market_value, :market_value_display, :last_updated)
        ''', [dict(p, 
                   league='Premier League',
                   last_updated=datetime.now().strftime('%Y-%m-%d')) for p in players_data])
        
        db.commit()

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
            SELECT DISTINCT id, name, team, league, position, age, nationality as nation, market_value_display 
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
            'nation': guessed_player['nationality'] == daily_player['nationality'],
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
    # Initialize database
    setup_database()
    
    # Make sure the data directory exists
    os.makedirs('data', exist_ok=True)
    # Run the Flask app on port 5002 instead of 5001
    app.run(debug=True, host='0.0.0.0', port=5002) 
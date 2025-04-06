import sqlite3
import os
import hashlib
import json
from datetime import datetime

# Database file path
DB_FILE = 'ratemyhousing.db'

def init_db():
    """Initialize the database with required tables if they don't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create properties table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS properties (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        location TEXT NOT NULL
    )
    ''')
    
    # Create reviews table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        property_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        rating INTEGER NOT NULL,
        review_text TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (property_id) REFERENCES properties (id),
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password):
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, email, password):
    """Register a new user."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        hashed_password = hash_password(password)
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, hashed_password)
        )
        conn.commit()
        user_id = cursor.lastrowid
        return {"success": True, "user_id": user_id}
    except sqlite3.IntegrityError:
        return {"success": False, "error": "Username or email already exists"}
    finally:
        conn.close()

def login_user(username, password):
    """Authenticate a user."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    hashed_password = hash_password(password)
    cursor.execute(
        "SELECT id, username FROM users WHERE username = ? AND password = ?",
        (username, hashed_password)
    )
    
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {"success": True, "user_id": user[0], "username": user[1]}
    else:
        return {"success": False, "error": "Invalid username or password"}

def get_user_by_id(user_id):
    """Get user information by ID."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, username, email FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {"id": user[0], "username": user[1], "email": user[2]}
    return None

def add_property(title, location):
    """Add a new property to the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO properties (title, location) VALUES (?, ?)",
        (title, location)
    )
    property_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return property_id

def get_all_properties():
    """Get all properties from the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, title, location FROM properties")
    properties = cursor.fetchall()
    conn.close()
    
    return [{"id": p[0], "title": p[1], "location": p[2]} for p in properties]

def add_review(property_id, user_id, rating, review_text):
    """Add a new review for a property."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO reviews (property_id, user_id, rating, review_text) VALUES (?, ?, ?, ?)",
        (property_id, user_id, rating, review_text)
    )
    review_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return review_id

def get_property_reviews(property_id):
    """Get all reviews for a specific property."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT r.id, r.rating, r.review_text, r.created_at, u.username
        FROM reviews r
        JOIN users u ON r.user_id = u.id
        WHERE r.property_id = ?
        ORDER BY r.created_at DESC
    """, (property_id,))
    
    reviews = cursor.fetchall()
    conn.close()
    
    return [
        {
            "id": r[0],
            "rating": r[1],
            "review": r[2],
            "date": r[3],
            "username": r[4]
        }
        for r in reviews
    ]

def get_property_rating(property_id):
    """Get the average rating for a property."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT AVG(rating) FROM reviews WHERE property_id = ?",
        (property_id,)
    )
    
    result = cursor.fetchone()
    conn.close()
    
    if result[0] is not None:
        return round(result[0], 1)
    return 0

def import_initial_data():
    """Import initial property data from the listingsData array in listings.html."""
    # Check if properties already exist
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM properties")
    count = cursor.fetchone()[0]
    
    if count == 0:
        # Import properties from the listingsData array
        properties = [
            {"title": "The Vintage Lofts at West End", "location": "801 N Rome Ave, Tampa, FL 33606"},
            {"title": "Sarasota Condo", "location": "4631 Longwater Chase, Sarasota, FL 34235"},
            {"title": "The Cottages at Cypress Cay", "location": "15081 Cypress Cay Blvd, Lutz, FL 33559"},
            {"title": "Escape Tampa Bay Tiny House", "location": "11014 US-301, Thonotosassa, FL 33592"},
            {"title": "Captiva Club Apartments", "location": "4401 Club Captiva Dr, Tampa, FL 33615"},
            {"title": "Charming early 1900's 2/1 Bungalow", "location": "813 East Frierson Avenue, Tampa, FL 33603"},
            {"title": "Mezzo of Tampa Palms", "location": "15210 Amberly Dr, Tampa, FL 33647"},
            {"title": "**Newly Renovated Master Suite **", "location": "15406 Manning Drive, Tampa, FL 33613"},
            {"title": "College Town at USF", "location": "2301 Aberdeen Court, Tampa, FL 33612"},
            {"title": "4214 W Union St", "location": "4214 W Union St, Tampa, FL 33607"},
            {"title": "Fernwood Grove Apartments", "location": "4900 N Macdill Ave, Tampa, FL 33614"},
            {"title": "Condo w/ Private yard and water view", "location": "13812 Orange Sunset Drive, Tampa, FL 33618"},
            {"title": "The Retreat at Tampa Cottages", "location": "11326 N 46th St, Tampa, FL 33617"},
            {"title": "4x4 unit across the street from USF", "location": "5035 Sunridge Palms Drive #101, Tampa, FL 33617"},
            {"title": "The Province Apartments", "location": "10921 McKinley Drive, Tampa, FL 33612"},
            {"title": "Furnished 1 Bedroom in Gated Community", "location": "2866 Somerset Park Drive #102, Tampa, FL 33613"},
            {"title": "The Flats at Seminole Heights", "location": "4111 N Poplar Ave, Tampa, FL 33603"},
            {"title": "1611 E 18th Ave", "location": "1611 E 18th Ave, Tampa, FL 33605"},
            {"title": "The Livingston", "location": "15420 Livingston Ave, Lutz, FL 33559"},
            {"title": "4050 Lofts, walk to USF Campus, on Bull Runner Line", "location": "4050 Rocky Circle, Tampa, FL 33613"},
            {"title": "Halo 46: Off-Campus Student Housing", "location": "14500 N 46th St, Tampa, FL 33613"},
            {"title": "Furnished All Inclusive Private Single Bedrooms & Whole Homes for Students --RCAD, USF, New College", "location": "1067 41st Street, Sarasota, FL 34234"},
            {"title": "AZORA AT CYPRESS RANCH", "location": "17583 Bellavista Loop, Lutz, FL 33558"},
            {"title": "Furnished Rentals for Students & Young Professionals", "location": "3011 6th Street, Sarasota, FL 34237"},
            {"title": "Reflections", "location": "14525 Prism Cir, Tampa, FL 33613"},
            {"title": "Three Bedroom Home w/ Three Private Baths! Near Downtown St. Petersburg", "location": "4725 15th Avenue South, St. Petersburg, FL 33711"},
            {"title": "Armature Gate Townhomes", "location": "13835 Heritage Club Dr, Tampa, FL 33613"},
            {"title": "Sunridge Palms on 50th Street", "location": "5166 Sunridge Palms Drive, Tampa, FL 33617"},
            {"title": "Apella on Newport", "location": "311 N Newport Ave, Tampa, FL 33606"},
            {"title": "Summer Sublease Available (Girls Only) // May Rent Paid", "location": "3600 E Fletcher Avenue, Tampa, FL 33613"},
            {"title": "Bayside Arbors of Clearwater", "location": "2729 Seville Blvd, Clearwater, FL 33764"},
            {"title": "Vue Tampa South", "location": "5610 Graduate Circle, Tampa, FL 33617"},
            {"title": "Park Place at Tampa", "location": "3400 Park Sq E, Tampa, FL 33613"},
            {"title": "Avalon Heights", "location": "13508 Avalon Heights Blvd, Tampa, FL 33613"},
            {"title": "Urban Place Apartments", "location": "13401 N 50th St, Tampa, FL 33617"},
            {"title": "Avalon Heights Apartments", "location": "13508 Avalon Heights Boulevard, Tampa, FL 33613"},
            {"title": "*Summer Term* Forest Lake Apartments!!", "location": "15004 Turtle Lake Court, Lutz, FL 33559"},
            {"title": "Anchor Riverwalk", "location": "109 W Fortune St, Tampa, FL 33602"},
            {"title": "College Town", "location": "2301 Aberdeen Court, Tampa, FL 33612"}
        ]
        
        for prop in properties:
            cursor.execute(
                "INSERT INTO properties (title, location) VALUES (?, ?)",
                (prop["title"], prop["location"])
            )
        
        conn.commit()
    
    conn.close()

# Initialize the database when this module is imported
init_db()
import_initial_data() 
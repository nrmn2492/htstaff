import os
import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Function to scrape data from a Hot Wheels page for a specific year
def scrape_hot_wheels(url, year):
    response = requests.get(url.format(year))
    soup = BeautifulSoup(response.text, 'html.parser')

    # Assuming the table is the first one on the page
    table = soup.find('table')

    # Connect to SQLite database
    conn = sqlite3.connect('hot_wheels.db')
    cursor = conn.cursor()

    # Create tables if they don't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hot_wheels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            toy_number TEXT UNIQUE,
            release_year INTEGER,
            collection_number TEXT,
            model_name TEXT,
            series TEXT,
            series_number TEXT,
            photo_url TEXT
        )
    ''')
    conn.commit()

    # Insert data into the database
    for row in table.find_all('tr')[1:]:
        columns = row.find_all('td')
        if len(columns) == 6:
            toy_number, collection_number, model_name, series, series_number = [col.text.strip() for col in columns[:-1]]
            photo_td = columns[-1]
            photo_url = photo_td.find('a')['href'] if photo_td.find('a') else None

            # Check if toy_number already exists in the database
            cursor.execute('SELECT id FROM hot_wheels WHERE toy_number = ?', (toy_number,))
            existing_row = cursor.fetchone()

            if existing_row:
                logging.info(f"Toy {toy_number} already exists. Skipping.")
                continue  # Skip existing toys

            # Download the image
            if photo_url:
                try:
                    response = requests.get(photo_url)
                    response.raise_for_status()  # Raise an HTTPError for bad responses
                    if response.status_code == 200:
                        image_filename = f'static/images/{toy_number}.jpg'
                        img_database_link = f'/static/images/{toy_number}.jpg'
                        with open(image_filename, 'wb') as f:
                            f.write(response.content)
                    else:
                        logging.error(f"Failed to download image for {toy_number}. Status code: {response.status_code}")
                        img_database_link = '/static/images/placeholder.jpeg'
                except requests.exceptions.RequestException as e:
                    logging.error(f"Error downloading image for {toy_number}: {e}")
                    img_database_link = '/static/images/placeholder.jpeg'
                    time.sleep(5)  # Add a delay before retrying

                # Save image data to the database
                cursor.execute('''
                    INSERT OR IGNORE INTO hot_wheels (toy_number, collection_number, model_name, series, series_number, photo_url, release_year)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (toy_number, collection_number, model_name, series, series_number, img_database_link, year))
                conn.commit()

    # Close the database connection
    conn.close()

# Example usage
base_url = 'https://hotwheels.fandom.com/wiki/List_of_{}_Hot_Wheels'
for year in range(2000, 2024):
    scrape_hot_wheels(base_url, year)

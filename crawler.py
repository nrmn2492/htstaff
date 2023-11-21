import os
import requests
from bs4 import BeautifulSoup
import sqlite3
from tqdm import tqdm

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

    # Get the total number of rows for progress tracking
    total_rows = len(table.find_all('tr')[1:])

    # Create a progress bar for rows
    row_bar = tqdm(total=total_rows, unit=" row", position=1)

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

            if not existing_row:
                # Kép letöltése a statikus mappába
                if photo_url:
                    response = requests.get(photo_url)
                    if response.status_code == 200:
                        image_filename = f'static/images/{toy_number}.jpg'  # Képfájl neve a toy_number alapján
                        img_database_link = f'/static/images/{toy_number}.jpg'
                        with open(image_filename, 'wb') as f:
                            f.write(response.content)
                    else:
                        img_database_link = f'/static/images/placeholder.jpeg'

                # Adatok mentése az adatbázisba, beleértve a kép elérési útvonalát és a release évet
                cursor.execute('''
                    INSERT INTO hot_wheels (toy_number, collection_number, model_name, series, series_number, photo_url, release_year)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (toy_number, collection_number, model_name, series, series_number, img_database_link, year))
                conn.commit()

                # Növeljük a sorok progress bar-ját
                row_bar.update(1)

    # Kiírjuk az éppen feldolgozott év számát

    # Bezárjuk a progress bar-okat
    row_bar.close()

    # Close the database connection
    conn.close()

# Example usage
base_url = 'https://hotwheels.fandom.com/wiki/List_of_{}_Hot_Wheels'
for year in range(2000, 2024):
    scrape_hot_wheels(base_url, year)

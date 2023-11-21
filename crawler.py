# Crawler
import os
import requests
from bs4 import BeautifulSoup
import sqlite3

# Function to scrape data from a Hot Wheels page
def scrape_hot_wheels(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Assuming the table is the first one on the page
    table = soup.find('table')

    # Connect to SQLite database
    conn = sqlite3.connect('hot_wheels.db')
    cursor = conn.cursor()

    # Create table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hot_wheels (
            toy_number TEXT,
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

            # Kép letöltése a statikus mappába
            if photo_url:
                response = requests.get(photo_url)
                if response.status_code == 200:
                    image_filename = f'static/{toy_number}.jpg'  # Képfájl neve a toy_number alapján
                    with open(image_filename, 'wb') as f:
                        f.write(response.content)

            # Adatok mentése az adatbázisba, beleértve a kép elérési útvonalát
            cursor.execute('''
                INSERT INTO hot_wheels (toy_number, collection_number, model_name, series, series_number, photo_url)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (toy_number, collection_number, model_name, series, series_number, f'/static/{toy_number}.jpg'))
            conn.commit()

    # Close the database connection
    conn.close()

# Example usage
base_url = 'https://hotwheels.fandom.com/wiki/List_of_{}_Hot_Wheels'
urls = [
    base_url.format(year) for year in range(2022, 2023)
]

for url in urls:
    scrape_hot_wheels(url)
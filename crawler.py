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
            photo TEXT
        )
    ''')
    conn.commit()

    # Insert data into the database
    for row in table.find_all('tr')[1:]:  # Skipping the header row
        columns = row.find_all('td')
        if len(columns) == 6:  # Ensure it's a valid row
            toy_number, collection_number, model_name, series, series_number, photo = [col.text.strip() for col in columns]

            # Insert data into the database
            cursor.execute('''
                INSERT INTO hot_wheels (toy_number, collection_number, model_name, series, series_number, photo)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (toy_number, collection_number, model_name, series, series_number, photo))
            conn.commit()

    # Close the database connection
    conn.close()

# Example usage
base_url = 'https://hotwheels.fandom.com/wiki/List_of_{}_Hot_Wheels'
urls = [
    base_url.format(year) for year in range(1968, 2025)
]

for url in urls:
    scrape_hot_wheels(url)
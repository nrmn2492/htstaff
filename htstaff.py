from flask import Flask, render_template, jsonify, request
import sqlite3

app = Flask(__name__)

# Create the users table if it doesn't exist
with sqlite3.connect('hot_wheels.db') as conn:
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT
        )
    ''')
    conn.commit()

# Create the user_collection table if it doesn't exist
with sqlite3.connect('hot_wheels.db') as conn:
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users_collection (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
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


# Function to query the database
def search_hot_wheels(query):
    conn = sqlite3.connect('hot_wheels.db')
    cursor = conn.cursor()

    # Search for the query in the database
    cursor.execute('''
        SELECT * FROM hot_wheels
        WHERE toy_number LIKE ? OR model_name LIKE ? OR series LIKE ?
    ''', ('%' + query + '%', '%' + query + '%', '%' + query + '%'))

    result = cursor.fetchall()

    # Close the database connection
    conn.close()

    return result

# Route for the home page
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_hot_wheels_data')
def get_hot_wheels_data():
    page = int(request.args.get('page', 1))  # Aktuális oldalszám
    per_page = int(request.args.get('per_page', 10))  # Oldalankénti találatok száma

    # Connect to SQLite database
    conn = sqlite3.connect('hot_wheels.db')
    cursor = conn.cursor()

    # Lekérdezi az összes találat számát
    cursor.execute('SELECT COUNT(*) FROM hot_wheels')
    total_items = cursor.fetchone()[0]

    # Kiszámolja az adatok lekérésének tartományát
    start_index = (page - 1) * per_page
    end_index = start_index + per_page

    # Execute a query to fetch data with pagination
    cursor.execute('SELECT * FROM hot_wheels LIMIT ? OFFSET ?', (per_page, start_index))

    # Fetch the rows for the current page
    data = cursor.fetchall()

    # Close the database connection
    conn.close()

    # Convert the data to a list of dictionaries
    keys = ['id', 'toy_number', 'release_year', 'collection_number', 'model_name', 'series', 'series_number', 'photo_url']
    result = [dict(zip(keys, row)) for row in data]

    # Számolja ki az összes oldalt
    total_pages = (total_items + per_page - 1) // per_page

    # Use jsonify correctly here
    response_data = {
        "data": result,
        "currentPage": page,
        "totalPages": total_pages,
        "totalItems": total_items
    }
    return jsonify(response_data)

@app.route('/get_all_hot_wheels_data')
def get_all_hot_wheels_data():
    try:
        # Connect to SQLite database
        conn = sqlite3.connect('hot_wheels.db')
        cursor = conn.cursor()

        # Execute a query to fetch all data without pagination
        cursor.execute('SELECT * FROM hot_wheels')

        # Fetch all the rows
        data = cursor.fetchall()

        # Close the database connection
        conn.close()

        # Convert the data to a list of dictionaries
        keys = ['id', 'toy_number', 'collection_number', 'release_year', 'model_name', 'series', 'series_number', 'photo_url']
        result = [dict(zip(keys, row)) for row in data]

        # Use jsonify correctly here
        return jsonify({"data": result})

    except Exception as e:
        return jsonify({'error': str(e)})

# Route for the profile page
@app.route('/profile')
def profile():
    return render_template('profile.html')

# New route to get the user's Hot Wheels collection
@app.route('/get_my_hot_wheels_collection')
def get_my_hot_wheels_collection():
    # Connect to SQLite database
    conn = sqlite3.connect('hot_wheels.db')
    cursor = conn.cursor()

    # Execute a query to fetch all data from the 'users_collection' table (modify table name as needed)
    cursor.execute('SELECT * FROM users_collection')

    # Fetch all rows
    data = cursor.fetchall()

    # Close the database connection
    conn.close()

    # Convert the data to a list of dictionaries
    keys = ['id', 'toy_number', 'release_year', 'collection_number', 'model_name', 'series', 'series_number', 'photo_url']
    result = [dict(zip(keys, row)) for row in data]

    # Use jsonify correctly here
    return jsonify({"data": result})  # You can wrap the result in a dictionary if needed

# Route to add items to the user's collection
@app.route('/add_to_collection', methods=['POST'])
def add_to_collection():
    try:
        selected_data = request.json.get('selectedData', [])

        # Connect to SQLite database
        conn = sqlite3.connect('hot_wheels.db')
        cursor = conn.cursor()

        # Insert selected items into the 'users_collection' table (modify table name as needed)
        for item in selected_data:
            cursor.execute('''
                INSERT INTO users_collection (id, user_id, toy_number, release_year, collection_number, model_name, series, series_number, photo_url)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                item['id'],
                item['user_id'],
                item['toy_number'],
                item['release_year'],
                item['collection_number'],
                item['model_name'],
                item['series'],
                item['series_number'],
                item['photo_url'],
            ))

        # Commit changes and close the database connection
        conn.commit()
        conn.close()

        # Return a success response
        return jsonify({"message": "Items added to the collection successfully"})
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)
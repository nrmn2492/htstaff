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

@app.route('/get_hot_wheels_data')
def get_hot_wheels_data():
    page = int(request.args.get('page', 1))  # Aktuális oldalszám
    per_page = int(request.args.get('per_page', 15))  # Oldalankénti találatok száma

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
    
@app.route('/')
def home():
    try:
        # Connect to SQLite database
        conn = sqlite3.connect('hot_wheels.db')
        cursor = conn.cursor()

        # Fetch all users from the database
        cursor.execute('SELECT name FROM users')
        existing_users = [row[0] for row in cursor.fetchall()]

        # Check if each user from the predefined list exists in the database
        users_to_add = [user for user in ["Gergő", "Norbi", "Máté", "Tomi", "Antal"] if user not in existing_users]

        # Add users to the database who don't exist
        for user_to_add in users_to_add:
            cursor.execute('INSERT INTO users (name) VALUES (?)', (user_to_add,))

        # Commit the changes and close the database connection
        conn.commit()
        conn.close()

        # Fetch the list of users from the database again
        conn = sqlite3.connect('hot_wheels.db')
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM users')
        users = [row[0] for row in cursor.fetchall()]
        conn.close()

        return render_template('index.html', users=users)

    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/add_to_collection', methods=['POST'])
def add_to_collection():
    try:
        data = request.get_json()
        selected_data = data.get('selectedData')

        with sqlite3.connect('hot_wheels.db') as conn:
            cursor = conn.cursor()

            for user_data in selected_data:
                toy_number = user_data['toy_number']

                # Check if the toy_number already exists
                cursor.execute('SELECT * FROM users_collection WHERE toy_number = ?', (toy_number,))
                existing_record = cursor.fetchone()

                if existing_record:
                    # Handle the situation where the toy_number already exists
                    print(f"Record with toy_number {toy_number} already exists.")
                else:
                    # If photo_url is empty, fetch it from the hot_wheels table
                    if not user_data['photo']:
                        cursor.execute('SELECT photo_url FROM hot_wheels WHERE toy_number = ?', (toy_number,))
                        hot_wheels_data = cursor.fetchone()
                        if hot_wheels_data:
                            user_data['photo'] = hot_wheels_data[0]

                    # Insert the new record since toy_number does not exist
                    cursor.execute('''
                        INSERT OR IGNORE INTO users_collection (user_id, toy_number, release_year, collection_number, model_name, series, series_number, photo_url)
                        VALUES ((SELECT id FROM users WHERE name = ?), ?, ?, ?, ?, ?, ?, ?)
                    ''', (user_data['user'], toy_number, user_data['release_year'],
                          user_data['collection_number'], user_data['model_name'],
                          user_data['series'], user_data['series_number'], user_data['photo']))

        return jsonify({'message': 'Items added to collection successfully'})

    except Exception as e:
        return jsonify({'error': str(e)})
    
@app.route('/view_collection')
def view_collection():
    user_name = request.args.get('user')

    try:
        # Connect to SQLite database
        conn = sqlite3.connect('hot_wheels.db')
        cursor = conn.cursor()

        # Fetch the user's collection from the database
        cursor.execute('''
            SELECT * FROM users_collection
            WHERE user_id = (SELECT id FROM users WHERE name = ?)
        ''', (user_name,))

        # Fetch all the rows
        data = cursor.fetchall()

        # Print the fetched data to the console
        print("Fetched Data:", data)

        # Close the database connection
        conn.close()

        # Convert the data to a list of dictionaries
        keys = ['id', 'user_id', 'toy_number', 'collection_number', 'release_year', 'model_name', 'series', 'series_number', 'photo_url']
        result = [dict(zip(keys, row)) for row in data]

        # Render the template with the user's collection data
        return render_template('view_collection.html', user_name=user_name, collection_data=result)

    except Exception as e:
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    app.run(debug=True)
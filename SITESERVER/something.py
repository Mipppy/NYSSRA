from flask import Flask, request, g, jsonify
from flask_cors import CORS
import sqlite3, os


app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
DATABASE = "sql.sqlite3"
VALID_DB_COLUMNS = ['author', 'markdown', 'header', 'date', 'event', 'event_date', 'category']
PER_PAGE = 25


@app.after_request
def after_request(response):
    response.headers["Access-Control-Allow-Origin"] = '*'
    response.headers["Access-Control-Allow-Credentials"] = '*'
    return response


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
    return g.db


@app.teardown_appcontext
def close_db(error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


@app.route("/new_post", methods=["POST"])
def new_post():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    if request.json.get('the_magic_word') != os.environ.get('SPECIAL_KEY'):
        return jsonify({"error": "Unauthorized"}), 403

    required_fields = ['author', 'markdown', 'date', 'event', 'event_date', 'category', 'header']
    if not all(field in request.json for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO posts (author, markdown, date, event, event_date, category, header) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                request.json['author'],
                request.json['markdown'],
                request.json['date'],
                request.json['event'],
                request.json['event_date'],
                request.json['category'],
                request.json['header']
            )
        )
        db.commit()
        return jsonify({"success": "Post created successfully"}), 200
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        db.close()   

@app.route("/get_specific_unique_table", methods=["POST"])
def get_specific_unique_table():
    url_param = request.args.get('type')
    
    if not url_param:
        return jsonify({"error": "Missing 'type' parameter"}), 400
    
    if url_param not in VALID_DB_COLUMNS:
        return jsonify({"error": "Invalid column name"}), 400
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute(f"SELECT DISTINCT {url_param} FROM posts")
        results = cursor.fetchall()
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        db.close()

@app.route("/get_recent_posts", methods=["POST", 'GET'])
def get_recent_posts():
    page = request.args.get('page', default=0, type=int)
    
    offset = page * PER_PAGE

    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT * FROM posts ORDER BY date DESC LIMIT ? OFFSET ?",
            (PER_PAGE, offset))
        posts = cursor.fetchall()

        return jsonify(posts), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        db.close()

@app.route("/get_events")
def get_events():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM posts WHERE event = true")
    return jsonify(cursor.fetchall()), 200

if __name__ == "__main__":
    app.run(debug=True)


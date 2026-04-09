from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('surfacelens.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    assets = conn.execute('SELECT * FROM assets ORDER BY last_seen DESC').fetchall()
    conn.close()
    return render_template('index.html', assets=assets)

if __name__ == '__main__':
    print("[+] SurfaceLens Dashboard running at http://127.0.0.1:5000")
    app.run(debug=True)
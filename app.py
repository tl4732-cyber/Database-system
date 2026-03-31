from flask import Flask, render_template, request
import psycopg2

app = Flask(__name__)

# Database connection


def get_db_connection():
    conn = psycopg2.connect(
        dbname="flights_db",
        user="postgres",
        host="localhost",
        port="5432"
    )
    return conn


# Home page (search form)
@app.route('/')
def index():
    return render_template("index.html")


# Search results page
@app.route('/search', methods=['POST'])
def search():
    origin = request.form['origin'].lower()
    dest = request.form['destination'].lower()
    start_date = request.form['start_date']
    end_date = request.form['end_date']

    conn = get_db_connection()
    cur = conn.cursor()

    query = """
        SELECT fs.flight_number, f.departure_date, fs.origin_code, fs.dest_code
        FROM flightservice fs
        JOIN flight f ON fs.flight_number = f.flight_number
        WHERE LOWER(fs.origin_code) = %s
        AND LOWER(fs.dest_code) = %s
        AND f.departure_date BETWEEN %s AND %s
    """
    cur.execute(query, (origin, dest, start_date, end_date))
    flights = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("results.html", flights=flights)


# Flight detail page
@app.route('/flight/<flight_number>/<date>')
def flight_detail(flight_number, date):

    conn = get_db_connection()
    cur = conn.cursor()

    # Get capacity
    cur.execute("""
        SELECT a.capacity
        FROM aircraft a
        JOIN flight f ON a.plane_type = f.plane_type
        WHERE f.flight_number = %s
    """, (flight_number,))
    capacity = cur.fetchone()[0]

    # Get booked seats
    cur.execute("""
        SELECT COUNT(*)
        FROM booking
        WHERE flight_number = %s
        AND departure_date = %s
    """, (flight_number, date))
    booked = cur.fetchone()[0]

    cur.close()
    conn.close()

    available = capacity - booked

    return render_template(
        "flight.html",
        flight_number=flight_number,
        date=date,
        capacity=capacity,
        booked=booked,
        available=available
    )


if __name__ == '__main__':
    app.run(debug=True)

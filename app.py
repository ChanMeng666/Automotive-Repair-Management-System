from flask import Flask, render_template, request
from flask_paginate import Pagination
import mysql.connector
import connect

app = Flask(__name__)

dbconn = None
connection = None
app.secret_key = 'some_secret'


def getCursor():
    """
    Connect to the database and return the cursor.
    """
    global dbconn
    global connection

    connection = mysql.connector.connect(
        user=connect.dbuser,
        password=connect.dbpass,
        host=connect.dbhost,
        database=connect.dbname,
        autocommit=True
    )

    dbconn = connection.cursor()

    return dbconn


@app.route('/')
def hello_world():
    return render_template("base.html")


@app.route('/currentjoblist', methods=['GET'])
def current_job_list():
    cursor = getCursor()

    page = int(request.args.get('page', 1))
    selection = request.args.get('selection', '')
    search = request.args.get('search', '')
    per_page = 5
    offset = (page - 1) * per_page

    cursor.execute("SELECT COUNT(*) FROM job WHERE completed=0;")
    total = cursor.fetchone()[0]

    if selection == 'Customer ID':
        selection_query = 'customer.customer_id'
    elif selection == 'Customer Name':
        selection_query = "CONCAT(customer.first_name, ' ', customer.family_name)"
    elif selection == 'Job Date':
        selection_query = 'job.job_date'
    else:
        selection_query = None

    if selection_query:
        search = f'%{search}%'
        cursor.execute(
            f"SELECT customer.customer_id, customer.first_name, customer.family_name, job.job_date "
            f"FROM job "
            f"INNER JOIN customer ON job.customer = customer.customer_id "
            f"WHERE {selection_query} LIKE %s "
            f"AND job.completed=0 "
            f"LIMIT %s OFFSET %s;",
            (search, per_page, offset)
        )
    else:
        cursor.execute(
            "SELECT customer.customer_id, customer.first_name, customer.family_name, job.job_date "
            "FROM job "
            "INNER JOIN customer ON job.customer = customer.customer_id "
            "WHERE job.completed=0 "
            "LIMIT %s OFFSET %s;",
            (per_page, offset)
        )

    data = cursor.fetchall()

    pagination = Pagination(page=page, total=total, per_page=per_page, record_name=' current jobs')

    return render_template(
        'currentjoblist.html',
        data=data,
        pagination=pagination,
        selection=selection,
        search=search
    )


if __name__ == '__main__':
    app.run()
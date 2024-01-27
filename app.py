from flask import Flask, url_for, render_template, request, redirect, flash
from flask_paginate import Pagination
import re
from datetime import datetime
import mysql.connector
from mysql.connector import FieldType
import connect

# Initialize the app
app = Flask(__name__)

# Initialize database connection and cursor
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


@app.route("/")
def home():
    """Homepage route. Returns the base page."""
    return render_template("base.html")


@app.route("/currentjobs")
def currentjobs():
    """Current jobs route. Returns a paginated list of current jobs."""
    connection = getCursor()

    page = int(request.args.get('page', 1))
    selection = request.args.get('selection', '')
    search = request.args.get('search', '')
    per_page = 10
    offset = (page - 1) * per_page

    connection.execute("SELECT COUNT(*) FROM job WHERE completed=0;")
    total = connection.fetchone()[0]

    if selection and search:
        connection.execute(
            f"SELECT job.job_id, job.customer, customer.first_name, customer.family_name, job.job_date "
            f"FROM job INNER JOIN customer ON job.customer = customer.customer_id "
            f"WHERE job.customer LIKE %s AND job.completed=0 LIMIT %s OFFSET %s;",
            (f'%{search}%', per_page, offset)
        )
    else:
        connection.execute(
            "SELECT job.job_id, job.customer, customer.first_name, customer.family_name, job.job_date "
            "FROM job INNER JOIN customer ON job.customer = customer.customer_id "
            "WHERE job.completed=0 LIMIT %s OFFSET %s;",
            (per_page, offset)
        )

    jobList = connection.fetchall()

    no_result = False
    if len(jobList) == 0:
        no_result = True

    pagination = Pagination(page=page, total=total, per_page=per_page, record_name='jobs')

    return render_template(
        'currentjoblist.html',
        job_list=jobList,
        pagination=pagination,
        no_result=no_result,
        selection=selection,
        search=search
    )


@app.route("/technician")
def technician():
    """Technician route. Redirects to 'currentjobs'."""
    return redirect("/currentjobs")


@app.route("/modify_job/<int:job_id>", methods=["GET", "POST"])
def modify_job(job_id):
    """Modify job route. Allows adding parts and services via a form. Returns all data related to jobs."""
    connection = getCursor()

    part_id = part_qty = service_id = service_qty = None

    if request.method == "POST":
        part_id = request.form.get('part')
        part_qty = request.form.get('part_qty')
        service_id = request.form.get('service')
        service_qty = request.form.get('service_qty')

        if part_id and part_qty:
            connection.execute(
                "INSERT INTO job_part (job_id, part_id, qty) VALUES (%s, %s, %s);",
                (job_id, part_id, part_qty)
            )
            flash('Part added successfully!', 'success')

        if service_id and service_qty:
            # ensure service_qty is an integer
            try:
                service_qty = int(service_qty)
            except ValueError:
                flash('Service quantity should be an integer!', 'error')
                return redirect(request.url)

            connection.execute(
                "INSERT INTO job_service (job_id, service_id, qty) VALUES (%s, %s, %s);",
                (job_id, service_id, service_qty)
            )
            flash('Service added successfully!', 'success')

    connection.execute(
        "SELECT job.customer, CONCAT_WS(' ', customer.first_name, customer.family_name), job.job_date, "
        "part.part_name, SUM(job_part.qty), service.service_name, SUM(job_service.qty) "
        "FROM job INNER JOIN customer ON job.customer = customer.customer_id "
        "LEFT JOIN job_part ON job.job_id = job_part.job_id LEFT JOIN part ON job_part.part_id = part.part_id "
        "LEFT JOIN job_service ON job.job_id = job_service.job_id LEFT JOIN service ON job_service.service_id = service.service_id "
        "WHERE job.job_id=%s GROUP BY part.part_id, service.service_id;",
        (job_id,)
    )
    job_parts_services_raw_data = connection.fetchall()

    job_parts_services_qty = {}


    for data in job_parts_services_raw_data:
        customer_id = data[0]
        if customer_id not in job_parts_services_qty:
            job_parts_services_qty[customer_id] = {
                'name': data[1],
                'date': data[2],
                'parts': {},
                'services': {}
            }



        part_name = data[3]
        part_qty = data[4]
        service_name = data[5]
        service_qty = data[6]

        if part_name is not None:
            # Accumulating the quantity for a given part
            current_part_qty = job_parts_services_qty[customer_id]['parts'].get(part_name, 0)
            job_parts_services_qty[customer_id]['parts'][part_name] = current_part_qty + part_qty

        if service_name is not None:
            # Accumulating the quantity for a given service
            current_service_qty = job_parts_services_qty[customer_id]['services'].get(service_name, 0)
            job_parts_services_qty[customer_id]['services'][service_name] = current_service_qty + service_qty




    connection.execute("SELECT part_id, part_name FROM part;")
    parts = connection.fetchall()

    connection.execute("SELECT service_id, service_name FROM service;")
    services = connection.fetchall()

    return render_template(
        'modify_job.html',
        job_parts_services_qty=job_parts_services_qty,
        parts=parts,
        services=services,
        part_id=part_id,
        part_qty=part_qty,
        service_id=service_id,
        service_qty=service_qty
    )


@app.route("/customer_management")
def customer_management():
    """Customer Management route. Displays a paginated list of customers with optional search."""
    connection = getCursor()

    page = int(request.args.get('page', 1))
    search = request.args.get('search', '')
    per_page = 10
    offset = (page - 1) * per_page

    if search:
        connection.execute(
            f"SELECT COUNT(*) FROM customer WHERE first_name LIKE %s OR family_name LIKE %s ORDER BY family_name, first_name;",
            (f'%{search}%', f'%{search}%')
        )
    else:
        connection.execute("SELECT COUNT(*) FROM customer ORDER BY family_name, first_name;")
    total = connection.fetchone()[0]

    if search:
        connection.execute(
            f"SELECT * FROM customer WHERE first_name LIKE %s OR family_name LIKE %s ORDER BY family_name, first_name LIMIT %s OFFSET %s;",
            (f'%{search}%', f'%{search}%', per_page, offset)
        )
    else:
        connection.execute("SELECT * FROM customer ORDER BY family_name, first_name LIMIT %s OFFSET %s;", (per_page, offset))
    customers = connection.fetchall()

    no_result = False
    if len(customers) == 0:
        no_result = True

    pagination = Pagination(page=page, total=total, per_page=per_page, record_name='customers')

    return render_template(
        'customer_management.html',
        customers=customers,
        pagination=pagination,
        search=search,
        no_result=no_result
    )


@app.route("/add_customer", methods=["GET", "POST"])
def add_customer():
    if request.method == "POST":
        first_name = request.form.get('first_name')
        family_name = request.form.get('family_name')
        email = request.form.get('email')
        phone = request.form.get('phone')

        connection = getCursor()

        connection.execute(
            "INSERT INTO customer (first_name, family_name, email, phone) VALUES (%s, %s, %s, %s);",
            (first_name, family_name, email, phone)
        )

        flash('Customer added successfully!', 'success')

        return redirect(url_for('customer_management'))

    return render_template('add_customer.html')


@app.route("/add_service", methods=["GET", "POST"])
def add_service():
    if request.method == "POST":
        service_name = request.form.get('service_name')
        cost = request.form.get('cost')

        connection = getCursor()
        connection.execute(
            "INSERT INTO service (service_name, cost) VALUES (%s, %s);",
            (service_name, cost)
        )

        flash('Service added successfully!', 'success')

        return redirect(url_for('customer_management'))

    return render_template('add_service.html')


@app.route("/add_part", methods=["GET", "POST"])
def add_part():
    if request.method == "POST":
        part_name = request.form.get('part_name')
        cost = request.form.get('cost')

        connection = getCursor()
        connection.execute(
            "INSERT INTO part (part_name, cost) VALUES (%s, %s);",
            (part_name, cost)
        )

        flash('Part added successfully!', 'success')

        return redirect(url_for('customer_management'))

    return render_template('add_part.html')

if __name__ == "__main__":
    app.run(debug=True)
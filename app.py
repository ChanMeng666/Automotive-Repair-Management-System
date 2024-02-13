from flask import Flask, flash
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
import re
from datetime import datetime
import mysql.connector
from mysql.connector import FieldType
import connect

app = Flask(__name__)
app.secret_key = '123456'

dbconn = None
connection = None


def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(
        user=connect.dbuser,
        password=connect.dbpass,
        host=connect.dbhost,
        database=connect.dbname,
        autocommit=True
    )
    dbconn = connection.cursor(dictionary=True, buffered=True)
    return dbconn


@app.route("/")
def home():
    return render_template('base.html')


@app.route("/currentjoblist", methods=['GET', 'POST'])
def currentjoblist():
    page = request.args.get('page', 1, type=int)
    per_page = 5
    offset = (page - 1) * per_page

    cursor = getCursor()
    cursor.execute(
        "SELECT c.customer_id, c.first_name, c.family_name, j.job_id, j.job_date, j.total_cost, j.completed, j.paid "
        "FROM customer AS c JOIN job AS j ON c.customer_id = j.customer "
        "WHERE j.completed = 0 "
        "ORDER BY c.first_name, c.family_name, j.job_date DESC "
        "LIMIT %s OFFSET %s", (per_page, offset)
    )
    data = cursor.fetchall()

    if request.method == 'POST':
        jobid = request.form.get('job_select')
        # Check if job_select is empty
        if not jobid:
            # If empty, return current page
            return render_template('currentjoblist.html', data=data, message="Please select a job before modify.")
        return redirect(url_for('modifyjob', job_id=jobid))

    return render_template('currentjoblist.html', data=data, page=page)


@app.route("/job/<int:job_id>", methods= ['GET', 'POST'])
def modifyjob(job_id):
    cursor = getCursor()

    cursor.execute(
        "SELECT c.customer_id, c.first_name, c.family_name, j.job_id, j.job_date, j.total_cost, j.completed, j.paid "
        "FROM customer AS c JOIN job AS j ON c.customer_id = j.customer "
        "WHERE j.job_id= %s", (job_id,)
    )
    job_data = cursor.fetchone()

    cursor.execute(
        "SELECT s.service_name, js.qty "
        "FROM service AS s JOIN job_service AS js ON s.service_id = js.service_id "
        "WHERE js.job_id= %s ORDER BY s.service_name", (job_id,)

    )
    services_data = cursor.fetchall()

    cursor.execute(
        "SELECT p.part_name, jp.qty "
        "FROM part AS p JOIN job_part AS jp ON p.part_id = jp.part_id "
        "WHERE jp.job_id= %s ORDER BY p.part_name ", (job_id,)
    )
    parts_data = cursor.fetchall()

    cursor.execute("SELECT * FROM service ORDER BY service_name")
    all_services_data = cursor.fetchall()

    cursor.execute("SELECT * FROM part ORDER BY part_name")
    all_parts_data = cursor.fetchall()

    job_completed = True if job_data['completed'] else False

    return render_template('technician_modify_job.html', data=job_data, services=services_data, parts=parts_data, all_services=all_services_data, all_parts=all_parts_data, job_completed=job_completed)


@app.route("/add_service_to_job/<int:job_id>", methods=['POST'])
def add_service_to_job(job_id):
    service_id = request.form.get('service_id')
    qty = request.form.get('service_qty')

    if not service_id or not qty:
        flash('Please select a service and enter the quantity', 'error')
        return redirect(url_for('modifyjob', job_id=job_id))

    cursor = getCursor()
    cursor.execute(
        "INSERT INTO job_service (job_id, service_id, qty) VALUES (%s, %s, %s)",
        (job_id, service_id, qty)
    )
    return redirect(url_for('modifyjob', job_id=job_id))

@app.route("/add_part_to_job/<int:job_id>", methods=['POST'])
def add_part_to_job(job_id):
    part_id = request.form.get('part_id')
    qty = request.form.get('part_qty')

    if not part_id or not qty:
        flash('Please select a part and enter the quantity', 'error')
        return redirect(url_for('modifyjob', job_id=job_id))

    cursor = getCursor()
    cursor.execute(
        "INSERT INTO job_part (job_id, part_id, qty) VALUES (%s, %s, %s)",
        (job_id, part_id, qty)
    )
    return redirect(url_for('modifyjob', job_id=job_id))


@app.route("/job/<int:job_id>/mark_as_completed", methods=['POST'])
def mark_job_as_completed(job_id):
    cursor = getCursor()
    cursor.execute("UPDATE job SET completed=1 WHERE job_id = %s", (job_id,))
    flash('Job marked as completed!', 'info')
    return redirect(url_for('modifyjob', job_id=job_id))



@app.route("/administrator_customer_list", methods=['POST', 'GET'])
def administrator_customer_list():
    cursor = getCursor()

    if request.method == 'POST':
        customer_id = request.form.get('customer_select')
        job_date = request.form.get('job_date')

        if customer_id and job_date:
            cursor.execute(
                "INSERT INTO job (job_date, customer, completed, paid, total_cost) VALUES (%s, %s, %s, %s, %s)",
                (job_date, customer_id, 0, 0, 0.0))
            cursor.execute("SELECT * FROM customer ORDER BY family_name, first_name")
        elif 'customer_search' in request.form and 'search_text' in request.form:
            search_option = request.form.get('customer_search')
            search_text = request.form.get('search_text')

            if search_option == 'first_name':
                cursor.execute("SELECT * FROM customer WHERE first_name LIKE %s", ("%" + search_text + "%",))
            elif search_option == 'family_name':
                cursor.execute("SELECT * FROM customer WHERE family_name LIKE %s", ("%" + search_text + "%",))
            else:
                cursor.execute("SELECT * FROM customer ORDER BY family_name, first_name")
        else:
            cursor.execute("SELECT * FROM customer ORDER BY family_name, first_name")

        selected_customer = request.form.get('selected_customer')

        if selected_customer != "Choose...":
            cursor.execute(
                "SELECT * FROM customer WHERE CONCAT(first_name, ' ', family_name) = %s ORDER BY family_name, first_name",
                (selected_customer,))
        else:
            cursor.execute("SELECT * FROM customer ORDER BY family_name, first_name")

    else:
        cursor.execute("SELECT * FROM customer ORDER BY family_name, first_name")


    cursor.execute("""SELECT c.customer_id, c.first_name,
                      c.family_name, j.job_id, j.job_date, j.total_cost,
                      CASE WHEN j.completed = 0 THEN 'NO' ELSE 'YES' END as completed,
                      CASE WHEN j.paid = 0 THEN 'NO' END as paid 
                      FROM job j JOIN customer c ON j.customer = c.customer_id 
                      WHERE j.paid = 0
                      ORDER BY j.job_date""")


    customers = cursor.fetchall()

    cursor.execute("SELECT * FROM service ORDER BY service_name")
    services = cursor.fetchall()

    cursor.execute("SELECT * FROM part ORDER BY part_name")
    parts = cursor.fetchall()

    return render_template('administrator_customer_list.html', customers=customers,
                           services=services, parts=parts)


@app.route("/add_customer", methods=['POST'])
def add_customer():
    cursor = getCursor()
    first_name = request.form.get('first_name', default=None)
    family_name = request.form.get('family_name')
    email = request.form.get('email')
    phone = request.form.get('phone')

    cursor.execute(
        "INSERT INTO customer (first_name, family_name, email, phone) VALUES (%s, %s, %s, %s)",
        (first_name, family_name, email, phone))

    return redirect(url_for('administrator_customer_list'))

@app.route("/add_service", methods=['POST'])
def add_service():
    cursor = getCursor()
    service_name = request.form.get('service_name', default=None)
    service_cost = request.form.get('service_cost')
    cursor.execute(
        "INSERT INTO service (service_name, cost) VALUES (%s, %s)",
        (service_name, service_cost))

    return redirect(url_for('administrator_customer_list'))

@app.route("/add_part", methods=['POST'])
def add_part():
    cursor = getCursor()
    part_name = request.form.get('part_name', default=None)
    part_cost = request.form.get('part_cost')

    cursor.execute(
        "INSERT INTO part (part_name, cost) VALUES (%s, %s)",
        (part_name, part_cost))

    return redirect(url_for('administrator_customer_list'))


@app.route("/administrator_customer_list/mark_as_paid", methods=['POST'])
def mark_as_paid():
    cursor = getCursor()
    # get the customer_id from the form
    customer_id = request.form.get('bill_select')

    if customer_id:
        customer_id = int(customer_id)
        cursor.execute(
            "UPDATE job SET paid = 1 WHERE customer = %s",
            (customer_id,))
        return 'Success'
    return 'Failure'
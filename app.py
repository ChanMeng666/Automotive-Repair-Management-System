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
    cursor = getCursor()
    cursor.execute(
        "SELECT c.customer_id, c.first_name, c.family_name, j.job_id, j.job_date, j.total_cost, j.completed, j.paid "
        "FROM customer AS c JOIN job AS j ON c.customer_id = j.customer "
        "WHERE j.completed = 0 "
        "ORDER BY c.first_name, c.family_name, j.job_date DESC"
    )
    data = cursor.fetchall()

    if request.method == 'POST':
        jobid = request.form.get('job_select')
        # Check if job_select is empty
        if not jobid:
            # If empty, return current page
            return render_template('currentjoblist.html', data=data, message="Please select a job before modify.")
        return redirect(url_for('modifyjob', job_id=jobid))

    return render_template('currentjoblist.html', data=data)


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




@app.route("/administrator_customer_list")
def administrator_customer_list():

    return render_template('administrator_customer_list.html')




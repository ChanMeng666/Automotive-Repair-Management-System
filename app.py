from flask import Flask, url_for
from flask import render_template
from flask import request
from flask import redirect
from flask_paginate import Pagination
import re
from datetime import datetime
import mysql.connector
from mysql.connector import FieldType
import connect

app = Flask(__name__)

dbconn = None
connection = None

def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect.dbuser,password=connect.dbpass,host=connect.dbhost,database=connect.dbname,autocommit=True)
    dbconn = connection.cursor()
    return dbconn

@app.route("/")
def home():
    return render_template("base.html")

@app.route("/currentjobs")
def currentjobs():
    connection = getCursor()
    page = int(request.args.get('page', 1))
    selection = request.args.get('selection', '')
    search = request.args.get('search', '')
    per_page = 10
    offset = (page - 1) * per_page
    connection.execute("SELECT COUNT(*) FROM job WHERE completed=0;")
    total = connection.fetchone()[0]

    column_map = {
        "Job ID": "job.job_id",
        "Customer ID": "job.customer",
        "First Name": "customer.first_name",
        "Family Name": "customer.family_name",
        "Date": "job.job_date"
    }

    column_name = column_map.get(selection)

    if selection and search and column_name:
        connection.execute(f"SELECT job.job_id,job.customer,customer.first_name,customer.family_name,job.job_date FROM job INNER JOIN customer ON job.customer = customer.customer_id WHERE {column_name} LIKE %s AND job.completed=0 LIMIT %s OFFSET %s;", (f'%{search}%', per_page, offset))
    else:
        connection.execute("SELECT job.job_id,job.customer,customer.first_name,customer.family_name,job.job_date FROM job INNER JOIN customer ON job.customer = customer.customer_id WHERE job.completed=0 LIMIT %s OFFSET %s;", (per_page, offset))

    jobList = connection.fetchall()

    no_result = False
    if len(jobList) == 0:
        no_result = True

    pagination = Pagination(page=page, total=total, per_page=per_page, record_name='jobs')

    job_parts_services = dict()
    for job in jobList:
        job_id = job[0]
        connection.execute("SELECT part_id, qty FROM job_part WHERE job_id=%s;", (job_id,))
        parts = connection.fetchall()

        connection.execute("SELECT service_id, qty FROM job_service WHERE job_id=%s;", (job_id,))
        services = connection.fetchall()

        job_parts_services[job_id] = {
            "parts": parts,
            "services": services,
        }

    return render_template('currentjoblist.html', job_list=jobList, job_parts_services=job_parts_services, pagination=pagination, no_result=no_result, selection=selection, search=search)

@app.route("/technician")
def technician():
    return redirect("/currentjobs")

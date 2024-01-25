from flask import Flask, url_for, render_template, request, redirect, flash
from flask_paginate import Pagination
import re
from datetime import datetime
import mysql.connector
from mysql.connector import FieldType
import connect


# 初始化app
app = Flask(__name__)


# 初始化数据库连接和游标
dbconn = None
connection = None


# 连接数据库函数
def getCursor():
    """
    获取数据库游标的函数。创建与数据库的连接并返回连接游标。
    """
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect.dbuser,password=connect.dbpass,host=connect.dbhost,database=connect.dbname,autocommit=True)
    dbconn = connection.cursor()
    return dbconn


@app.route("/")
def home():
    """主页路由。返回基础页面。"""
    return render_template("base.html")


@app.route("/currentjobs")
def currentjobs():
    """当前工作路由。返回一个带分页的当前工作列表。"""
    connection = getCursor()

    page = int(request.args.get('page', 1))
    selection = request.args.get('selection', '')
    search = request.args.get('search', '')
    per_page = 10
    offset = (page - 1) * per_page
    connection.execute("SELECT COUNT(*) FROM job WHERE completed=0;")
    total = connection.fetchone()[0]

    if selection and search:
        connection.execute(f"SELECT job.job_id,job.customer,customer.first_name,customer.family_name,job.job_date FROM job INNER JOIN customer ON job.customer = customer.customer_id WHERE job.customer LIKE %s AND job.completed=0 LIMIT %s OFFSET %s;", (f'%{search}%', per_page, offset))
    else:
        connection.execute("SELECT job.job_id,job.customer,customer.first_name,customer.family_name,job.job_date FROM job INNER JOIN customer ON job.customer = customer.customer_id WHERE job.completed=0 LIMIT %s OFFSET %s;", (per_page, offset))

    jobList = connection.fetchall()

    no_result = False
    if len(jobList) == 0:
        no_result = True

    pagination = Pagination(page=page, total=total, per_page=per_page, record_name='jobs')

    return render_template('currentjoblist.html', job_list=jobList, pagination=pagination, no_result=no_result, selection=selection, search=search)


@app.route("/technician")
def technician():
    """技术员路由。重定向到currentjobs。"""
    return redirect("/currentjobs")


@app.route("/modify_job/<int:job_id>", methods=["GET", "POST"])
def modify_job(job_id):
    """修改工作路由。允许通过表单添加parts和services，然后返回与jobs相关的所有信息。"""
    connection = getCursor()

    part_id = part_qty = service_id = service_qty = None

    if request.method == "POST":
        part_id = request.form.get('part')
        part_qty = request.form.get('part_qty')
        service_id = request.form.get('service')
        service_qty = request.form.get('service_qty')

        if part_id and part_qty:
            connection.execute("INSERT INTO job_part (job_id, part_id, qty) VALUES (%s, %s, %s);", (job_id, part_id, part_qty))
            flash('Part added successfully!', 'success')

        if service_id and service_qty:
            connection.execute("INSERT INTO job_service (job_id, service_id, qty) VALUES (%s, %s, %s);", (job_id, service_id, service_qty))
            flash('Service added successfully!', 'success')



    connection.execute("SELECT job.job_id, job.customer, customer.first_name, customer.family_name, job.job_date, part.part_name, COUNT(job_part.part_id) as part_qty, service.service_name, COUNT(job_service.service_id) as service_qty FROM job INNER JOIN customer ON job.customer = customer.customer_id LEFT JOIN job_part ON job.job_id = job_part.job_id LEFT JOIN part ON job_part.part_id = part.part_id LEFT JOIN job_service ON job.job_id = job_service.job_id LEFT JOIN service ON job_service.service_id = service.service_id WHERE job.job_id=%s GROUP BY part.part_id, service.service_id;", (job_id,))
    job_parts_services_qty = connection.fetchall()

    connection.execute("SELECT part_id, part_name FROM part;")
    parts = connection.fetchall()

    connection.execute("SELECT service_id, service_name FROM service;")
    services = connection.fetchall()

    return render_template('modify_job.html', job_parts_services_qty=job_parts_services_qty, parts=parts, services=services, part_id=part_id, part_qty=part_qty, service_id=service_id, service_qty=service_qty)


if __name__ == "__main__":
    app.run(debug=True)
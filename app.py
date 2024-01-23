from flask import Flask
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


# 设置基础的路由("/")，返回base.html页面
@app.route("/")
def home():
    return render_template("base.html")


# 设置currentjobs的路由，用以执行分页,并显示结果在currentjoblist.html页面
@app.route("/currentjobs")
def currentjobs():
    connection = getCursor()
    page = int(request.args.get('page', 1))

    selection = request.args.get('selection', '')
    search = request.args.get('search', '')

    per_page = 10
    offset = (page - 1) * per_page

    # 获取当前工作列表（即未完成的工作）的总长度（即总行数）
    connection.execute("SELECT COUNT(*) FROM job WHERE completed=0;")
    total = connection.fetchone()[0]

    #对应的字段名映射，防止SQL注入
    column_map = {
        "Job ID": "job.job_id",
        "Customer ID": "job.customer",
        "First Name": "customer.first_name",
        "Family Name": "customer.family_name",
        "Date": "job.job_date"
    }

    column_name = column_map.get(selection)

    if selection and search and column_name:
        # 参数化值以防止sql注入
        connection.execute(f"SELECT job.job_id,job.customer,customer.first_name,customer.family_name,job.job_date FROM job INNER JOIN customer ON job.customer = customer.customer_id WHERE {column_name} LIKE %s AND job.completed=0 LIMIT %s OFFSET %s;", (f'%{search}%', per_page, offset))
    else:
        # 如果没有提供选中的字段或搜索内容，则返回所有记录
        connection.execute("SELECT job.job_id,job.customer,customer.first_name,customer.family_name,job.job_date FROM job INNER JOIN customer ON job.customer = customer.customer_id WHERE job.completed=0 LIMIT %s OFFSET %s;", (per_page, offset))

    jobList = connection.fetchall()

    # 判断查询结果是否为空
    no_result = False
    if len(jobList) == 0:
        no_result = True

    pagination = Pagination(page=page, total=total, per_page=per_page, record_name='jobs')
    # 向模板传递一个新的变量no_result
    return render_template('currentjoblist.html', job_list=jobList, pagination=pagination, no_result=no_result)



# 设置technician的路由，重定向到"/currentjobs"路由
@app.route("/technician")
def technician():
    return redirect("/currentjobs")





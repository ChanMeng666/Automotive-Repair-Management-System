from flask import Flask, render_template, request, redirect, url_for
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


@app.route('/currentjoblist', methods=['GET', 'POST'])
def current_job_list():
    cursor = getCursor()

    if request.method == "POST":
        selected_job = request.form.get('jobSelect')
        return redirect(url_for('modify_job', customer_id=selected_job))

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

    no_result = False
    if len(data) == 0:
        no_result = True

    pagination = Pagination(page=page, total=total, per_page=per_page, record_name=' current jobs')

    return render_template(
        'currentjoblist.html',
        data=data,
        pagination=pagination,
        no_result=no_result,
        selection=selection,
        search=search
    )

@app.route('/modifyjob', methods=['GET', 'POST'])
def modify_job():
    customer_id = request.args.get('customer_id')
    cursor = getCursor()

    # Fetching the latest job_id
    cursor.execute(
        "SELECT job_id FROM job WHERE customer=%s ORDER BY job_date DESC LIMIT 1;",
        (customer_id,)
    )
    job_id = cursor.fetchone()[0]

    def calculate_total_cost():
        cursor.execute(
            "SELECT sum(service.cost * job_service.qty) "
            "FROM service JOIN job_service ON service.service_id = job_service.service_id "
            "JOIN job ON job_service.job_id = job.job_id "
            "WHERE job.job_id=%s",
            (job_id,)
        )
        service_cost = cursor.fetchone()[0] or 0

        cursor.execute(
            "SELECT sum(part.cost * job_part.qty) "
            "FROM part JOIN job_part ON part.part_id = job_part.part_id "
            "JOIN job ON job_part.job_id = job.job_id "
            "WHERE job.job_id=%s",
            (job_id,)
        )
        part_cost = cursor.fetchone()[0] or 0

        total_cost = service_cost + part_cost
        cursor.execute(
            "UPDATE job SET total_cost=%s WHERE job_id=%s",
            (total_cost, job_id,)
        )
        return total_cost

    if request.method == 'POST':
        service_id = request.form.get('selectionService')
        qtyService = request.form.get('qtyService')

        if service_id and qtyService:
            cursor.execute(
                "INSERT INTO job_service (job_id, service_id, qty) VALUES (%s, %s, %s)",
                (job_id, service_id, qtyService)
            )
            return redirect(url_for('modify_job', customer_id=customer_id))

        part_id = request.form.get('selectionPart')
        qtyPart = request.form.get('qtyPart')

        if part_id and qtyPart:
            cursor.execute(
                "INSERT INTO job_part (job_id, part_id, qty) VALUES (%s, %s, %s)",
                (job_id, part_id, qtyPart)
            )
            return redirect(url_for('modify_job', customer_id=customer_id))

        completion_status = request.form.get('completionStatus')

        if completion_status.lower() == 'yes':
            cursor.execute(
                "UPDATE job SET completed=1 WHERE job_id=%s",
                (job_id,)
            )
            return redirect(url_for('modify_job', customer_id=customer_id))

        # 删除服务和零件 功能待做！！！
        service_id_to_delete = request.form.get('deleteService')

        if service_id_to_delete:
            cursor.execute(
                "DELETE FROM job_service WHERE job_id=%s AND service_id=%s",
                (job_id, service_id_to_delete)
            )
            return redirect(url_for('modify_job', customer_id=customer_id))

        part_id_to_delete = request.form.get('deletePart')

        if part_id_to_delete:
            cursor.execute(
                "DELETE FROM job_part WHERE job_id=%s AND part_id=%s",
                (job_id, part_id_to_delete)
            )
            return redirect(url_for('modify_job', customer_id=customer_id))

    cursor.execute(
        "SELECT customer.customer_id, customer.first_name, customer.family_name, " 
        "job.job_date, job.completed, job.paid "
        "FROM job "
        "INNER JOIN customer ON job.customer = customer.customer_id "
        "WHERE customer.customer_id=%s;",
        (customer_id,)
    )
    data = cursor.fetchall()

    cursor.execute(
        "SELECT service.service_id, service.service_name, service.cost, job_service.qty "
        "FROM service "
        "JOIN job_service ON service.service_id = job_service.service_id "
        "JOIN job ON job_service.job_id = job.job_id "
        "WHERE job.customer=%s;",
        (customer_id,)
    )
    services = cursor.fetchall()

    cursor.execute(
        "SELECT part.part_id, part.part_name, part.cost, job_part.qty "
        "FROM part "
        "JOIN job_part ON part.part_id = job_part.part_id "
        "JOIN job ON job_part.job_id = job.job_id "
        "WHERE job.customer=%s;",
        (customer_id,)
    )
    parts = cursor.fetchall()

    cursor.execute(
        "SELECT service_id, service_name "
        "FROM service ORDER BY service_name"
    )
    service_names = cursor.fetchall()

    cursor.execute(
        "SELECT part_id, part_name "
        "FROM part ORDER BY part_name"
    )
    part_names = cursor.fetchall()

    total_cost = calculate_total_cost()

    return render_template(
        "modify_job.html",
        data=data,
        services=services,
        parts=parts,
        service_names=service_names,
        part_names=part_names,
        total_cost=total_cost
    )

@app.route('/customerlist', methods=['GET', 'POST'])
def customer_list():
    cursor = getCursor()

    cursor.execute(
        "SELECT customer.customer_id, customer.first_name, "
        "customer.family_name, customer.email, customer.phone "
        "FROM customer "
        "ORDER BY customer.family_name, customer.first_name"
    )

    customers = cursor.fetchall()
    job_data = {}

    for customer in customers:
        cursor.execute(
            "SELECT job.job_date, job.total_cost "
            "FROM job "
            "WHERE customer=%s;", (customer[0],)
        )

        jobs = cursor.fetchall()
        job_data[customer[0]] = jobs

    return render_template("customer_list.html", customers=customers, job_data=job_data)

if __name__ == '__main__':
    app.run(debug=True)
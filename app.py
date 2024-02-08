from flask import Flask, render_template, request, redirect, url_for
from flask_paginate import Pagination
import mysql.connector
import connect
from datetime import datetime

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

    selection = request.args.get('selection', '')
    search = request.args.get('search', '')
    page = int(request.args.get('page', 1))
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
            f"SELECT customer.customer_id, customer.first_name, customer.family_name, job.job_date, job.job_id "
            f"FROM job "
            f"INNER JOIN customer ON job.customer = customer.customer_id "
            f"WHERE {selection_query} LIKE %s "
            f"AND job.completed=0 "
            f"LIMIT %s OFFSET %s;",
            (search, per_page, offset)
        )
    else:
        cursor.execute(
            "SELECT customer.customer_id, customer.first_name, customer.family_name, job.job_date, job.job_id "
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
    cursor = getCursor()

    customer_id = request.args.get('customer_id')

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
        "job.job_date, job.completed, job.paid, job.job_id "
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

    if request.method == 'POST':
        if 'first_name' in request.form:
            first_name = request.form.get('first_name', '')
            family_name = request.form.get('family_name', '')
            email = request.form.get('email', '')
            phone = request.form.get('phone', '')

            if family_name and email and phone:
                # cursor = getCursor()
                cursor.execute(
                    "INSERT INTO customer (first_name, family_name, email, phone) VALUES (%s, %s, %s, %s);",
                    (first_name, family_name, email, phone)
                )
            else:
                # Handle the case where required fields are missing.
                return "Error: Family Name, Email, and Phone must be provided."

        elif 'service_name' in request.form:
            service_name = request.form.get('service_name', '')
            service_cost = request.form.get('service_cost', '')

            if service_name and service_cost:
                cursor.execute(
                    "INSERT INTO service (service_name, cost) VALUES (%s, %s);",
                    (service_name, service_cost)
                )
            else:
                return "Error: Service Name and Cost must be provided."

        elif 'part_name' in request.form:
            part_name = request.form.get('part_name', '')
            part_cost = request.form.get('part_cost', '')

            if part_name and part_cost:
                cursor.execute(
                    "INSERT INTO part (part_name, cost) VALUES (%s, %s);",
                    (part_name, part_cost)
                )
            else:
                return "Error: Part Name and Cost must be provided."


        # Check if both 'customerSelect' and 'job_date' keys are in the request form:
        if 'customerSelect' in request.form and 'job_date' in request.form:
            customer_id = request.form.get('customerSelect')
            job_date = request.form.get('job_date')

            cursor.execute(
                "INSERT INTO job (job_date, customer, total_cost, completed, paid) VALUES (%s, %s, 0.00, 0, 0);",
                (job_date, customer_id)
            )



    # Existing GET request handling code follows...


    selection = request.args.get('selection', '')
    search = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 5
    offset = (page - 1) * per_page

    if selection == 'Family Name':
        selection_query = 'customer.family_name'
    elif selection == 'First Name':
        selection_query = 'customer.first_name'
    else:
        selection_query = None

    # customers = []

    no_result = False

    if selection_query:
        search = f'%{search}%'
        cursor.execute(
            f"SELECT COUNT(*) FROM customer WHERE {selection_query} LIKE %s ;", (search,)
        )
        total = cursor.fetchone()[0]

        if total == 0:
            no_result = True

        cursor.execute(
            f"SELECT customer.customer_id, customer.first_name, "
            f"customer.family_name, customer.email, customer.phone "
            f"FROM customer "
            f"WHERE {selection_query} LIKE %s "
            f"ORDER BY customer.family_name, customer.first_name "
            f"LIMIT %s OFFSET %s;",
            (search, per_page, offset)
        )
        customers = cursor.fetchall()

    else:
        cursor.execute("SELECT COUNT(*) FROM customer")
        total = cursor.fetchone()[0]

        cursor.execute(
            "SELECT customer.customer_id, customer.first_name, "
            "customer.family_name, customer.email, customer.phone "
            "FROM customer "
            "ORDER BY customer.family_name, customer.first_name "
            f"LIMIT %s OFFSET %s;",
            (per_page, offset)
        )
        customers = cursor.fetchall()

    customer_ids = [customer[0] for customer in customers]
    job_data = {}

    for customer_id in customer_ids:
        cursor.execute(
            "SELECT job.job_date, job.total_cost, job.completed, job.paid, job_id "
            "FROM job "
            "WHERE customer=%s;", (customer_id,)
        )

        jobs = cursor.fetchall()
        if jobs:
            job_data[customer_id] = jobs

    pagination = Pagination(page=page, total=total, per_page=per_page, record_name='customers')

    cursor.execute("SELECT service_id, service_name, cost FROM service ORDER BY service_name;")
    services = cursor.fetchall()

    cursor.execute("SELECT part_id, part_name, cost FROM part ORDER BY part_name;")
    parts = cursor.fetchall()


    today = datetime.today().strftime('%Y-%m-%d')


    return render_template("customer_list.html", customers=customers, job_data=job_data, pagination=pagination,
                           selection=selection, search=search, no_result=no_result, services=services, parts=parts, today=today)


@app.route('/unpaid_bills', methods=['GET', 'POST'])
def unpaid_bills():
    cursor = getCursor()
    search = ""

    no_result = False

    if request.method == 'POST':
        if 'search_submit' in request.form:
            search = request.form.get('search')
            selection = request.form.get('selection')
            if selection == 'Family Name':
                cursor.execute(
                    f"SELECT customer.family_name, customer.first_name, job.job_id, job.job_date, job.total_cost, job.completed FROM job INNER JOIN customer ON job.customer = customer.customer_id WHERE job.paid = 0 AND customer.family_name LIKE '%{search}%'")
            else:
                cursor.execute(
                    f"SELECT customer.family_name, customer.first_name, job.job_id, job.job_date, job.total_cost, job.completed FROM job INNER JOIN customer ON job.customer = customer.customer_id WHERE job.paid = 0 AND customer.first_name LIKE '%{search}%'")
            jobs = cursor.fetchall()

            if not jobs:
                no_result = True

        elif 'pay_submit' in request.form:
            job_id = request.form.get('jobSelect')
            cursor.execute(f"UPDATE job SET paid = 1 WHERE job_id = {job_id}")
            return redirect(url_for('unpaid_bills'))  # 刷新页面
    else:
        cursor.execute(
            "SELECT customer.family_name, customer.first_name, job.job_id, job.job_date, job.total_cost, job.completed FROM job INNER JOIN customer ON job.customer = customer.customer_id WHERE job.paid = 0")
    jobs = cursor.fetchall()

    return render_template("unpaid_bills.html", jobs=jobs, no_result=no_result)


@app.route('/billing_history', methods=['GET', 'POST'])
def billing_history():

    return render_template("billing_history.html")

if __name__ == '__main__':
    app.run(debug=True)
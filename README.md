 ```markdown
# Web Application Structure

## Overview

The web application is designed to manage a panel beating service, with separate interfaces for technicians and administrators. The application is structured using Flask, a micro web framework in Python, and utilizes MySQL for database operations. The application consists of several routes, functions, and templates that work together to provide the desired functionality.

## Routes & Functions

The application has the following main routes:

1. `/` - Home page, which serves as the entry point for both technicians and administrators.
2. `/currentjoblist` - Lists current jobs for technicians.
3. `/job/<int:job_id>` - Allows technicians to modify job details.
4. `/administrator_customer_list` - Lists customers and allows administrators to schedule jobs.
5. `/administrator_pay_bills` - Lists unpaid bills for administrators to mark as paid.
6. `/administrator_overdue_bills` - Lists overdue bills for administrators.

Each route corresponds to a specific function in `app.py` that handles the request, interacts with the database, and renders the appropriate template.

## Templates

Templates are used to define the HTML structure of the application's pages. They are located in a separate directory and are rendered by Flask using the `render_template` function. The base template `base.html` is extended by other templates to maintain a consistent layout across pages.

## Data Flow

Data flows between routes and functions through the use of form submissions (GET and POST requests). For example, when a technician wants to modify a job, they select a job from the list on `/currentjoblist` and submit the form to `/job/<int:job_id>`. The job details are then fetched from the database and passed to the `technician_modify_job.html` template for editing.

# Design Decisions

### Design Considerations

The application was designed with a clear separation of concerns in mind. Technicians and administrators have different roles and permissions, which is reflected in the routes they can access. The use of separate templates for different user roles ensures that the interface is tailored to their specific needs.

### Editing Functionality

Editing functionality is implemented using the same template with conditional statements (IF statements) to enable editing. This approach keeps the code clean and avoids redundancy by not creating separate templates for viewing and editing.

### Data Transmission

GET requests are used for retrieving data (e.g., listing jobs or customers), while POST requests are used for submitting data (e.g., modifying job details or marking bills as paid). This follows the RESTful design principles, where GET requests are idempotent and POST requests are used for creating or updating resources.

# Database Questions

### Job Table Creation

The SQL statement that creates the `job` table is:

```sql
CREATE TABLE IF NOT EXISTS job
(
    job_id INT auto_increment PRIMARY KEY NOT NULL,
    job_date date NOT NULL,
    customer int NOT NULL,
    total_cost decimal(6,2) default null,
    completed tinyint default 0,
    paid tinyint default 0,
    FOREIGN KEY (customer) REFERENCES customer(customer_id)
    ON UPDATE CASCADE
);
```

### Customer-Job Relationship

The relationship between the `customer` and `job` tables is set up with the following line:

```sql
FOREIGN KEY (customer) REFERENCES customer(customer_id)
ON UPDATE CASCADE
```

### Parts Table Insertion

Details are inserted into the `parts` table with the following lines:

```sql
INSERT INTO part (`part_name`, `cost`) VALUES ('Windscreen', '560.65');
INSERT INTO part (`part_name`, `cost`) VALUES ('Headlight', '35.65');
-- ... other parts
```

### Audit Trail Fields

To record the time and date a service or part was added to a job, the following fields/columns would be added:

- In the `job_service` table:
  - `created_at` column of type `DATETIME`
- In the `job_part` table:
  - `created_at` column of type `DATETIME`

### Logins and Access Control

Implementing logins is crucial for ensuring that technicians and administrators can only access the routes relevant to their roles. For example, if all facilities were available to everyone:

1. A technician might accidentally mark a job as completed when it's not, leading to incorrect job status and potential customer dissatisfaction.
2. An unauthorized user could access sensitive customer information or modify job details, causing operational chaos and potential financial loss.

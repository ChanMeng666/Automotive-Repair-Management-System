# Web Application Structure

## Overview

The web application is designed to manage Selwyn Panel Beaters Online service, with separate interfaces for technicians and administrators. The application is structured using Flask, a micro web framework in Python, and utilizes MySQL for database operations. The application consists of several routes, functions, and templates that work together to provide the desired functionality.

## Development Process

The development process began with the front-end design using WebStorm, which facilitated the creation of a user-friendly interface. The back-end functionality was then implemented using PyCharm, ensuring a seamless integration between the front-end and back-end components.

## Templates

Templates are used to define the HTML structure of the application's pages. They are designed according to the Bootstrap documentation (https://getbootstrap.com/docs/5.3/getting-started/introduction/), which provided guidelines for page layout and component usage. WebStorm was used to visually check the design effects in real-time, ensuring consistency and responsiveness across different devices.

## Navigation

The application uses Bootstrap's `navs-tabs` component for the navigation bar, which allows for a clear and organized layout. By nesting `<div class="container">` elements, we successfully resolved the issue of having multiple `class="nav-link active"` elements on a single page, which is a common limitation in Bootstrap.

## Overall Layout

The application's overall layout is designed to divert technicians and administrators to their respective pages from the home page. This diversion approach ensures that each user role has a tailored experience, reducing the chance of confusion or accidental actions. All pages inherit the Bootstrap styling and JavaScript from `base.html`, which includes `bootstrap.min.css` and `bootstrap.bundle.min.js`, providing a consistent look and feel across the application.

## Design Decisions

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
```

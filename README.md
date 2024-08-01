# Selwyn Panel Beaters Online Service

## Overview

Selwyn Panel Beaters Online Service is a web application designed to manage the services of Selwyn Panel Beaters, with dedicated interfaces for technicians and administrators. The application is built using Flask, a micro web framework in Python, and MySQL for database operations. It encompasses several routes, functions, and templates to deliver the required functionality.

## Development Process

### Front-End Development

The front-end design was initiated using WebStorm, facilitating the creation of an intuitive and user-friendly interface. The design adheres to the Bootstrap documentation, ensuring a consistent and responsive layout across various devices.

### Back-End Development

The back-end functionality was implemented using PyCharm, integrating seamlessly with the front-end components. Flask handles the routing and processing, while MySQL manages the data storage and retrieval.

## Application Structure

### Templates

Templates define the HTML structure of the application's pages. Designed according to Bootstrap guidelines, these templates ensure a consistent look and feel. The design was visually checked in real-time using WebStorm.

### Navigation

The application employs Bootstrap's `navs-tabs` component for the navigation bar, offering a clear and organised layout. The use of nested `<div class="container">` elements resolves the common Bootstrap issue of having multiple `class="nav-link active"` elements on a single page.

### Overall Layout

The application's layout directs technicians and administrators to their respective pages from the home page, ensuring a tailored experience for each user role. All pages inherit Bootstrap styling and JavaScript from `base.html`, maintaining a consistent interface.

### Design Decisions

#### Separation of Concerns

The application is designed with a clear separation of concerns. Technicians and administrators have distinct roles and permissions, reflected in the routes they can access. Separate templates for different user roles ensure a tailored interface.

#### Editing Functionality

Editing functionality is implemented using conditional statements within the same template, keeping the code clean and avoiding redundancy.

#### Data Transmission

GET requests retrieve data (e.g., listing jobs or customers), while POST requests submit data (e.g., modifying job details or marking bills as paid), adhering to RESTful design principles.

## Database Schema

### Job Table Creation

The `job` table is created using the following SQL statement:

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

### Customer-Job Relationship

The relationship between the customer and job tables is defined as:

```sql
FOREIGN KEY (customer) REFERENCES customer(customer_id)
ON UPDATE CASCADE

### Parts Table Insertion

Parts are inserted into the parts table with the following lines:

```sql
INSERT INTO part (`part_name`, `cost`) VALUES ('Windscreen', '560.65');
INSERT INTO part (`part_name`, `cost`) VALUES ('Headlight', '35.65');
-- ... other parts

### Audit Trail Fields

To record the time and date a service or part was added to a job, the following fields are added:

- In the job_service table: created_at column of type DATETIME
- In the job_part table: created_at column of type DATETIME

### Logins and Access Control

Implementing logins ensures that technicians and administrators can only access relevant routes. Without this control, unauthorised access could lead to:

1. Technicians accidentally marking jobs as paid, causing incorrect job status.
2. Unauthorised users accessing sensitive customer information or modifying job details, leading to operational chaos and potential financial loss.

## Getting Started
To get started with the project, follow these steps:

1. Clone the repository: `git clone https://github.com/ChanMeng666/Automotive-Repair-Management-System.git`
2. Install the required dependencies: `pip install -r requirements.txt`
3. Set up the database using the provided SQL scripts.
4. Run the application: `flask run`

## Contributing
We welcome contributions! Please fork the repository and submit a pull request with your changes. Ensure that your code adheres to our coding standards and includes appropriate tests.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Contact
For any questions or suggestions, please contact us at ChanMeng666@outlook.com.

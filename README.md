# Python Flask Application: Technical Report

## Web Application Structure

The Python Flask web application follows a Model-View-Controller (MVC) design pattern. The Flask application script serves as the controller, HTML templates provide the view, and the MySQL database serves as the model for the application.

### Routes and Functions

- `"/"` : The home route renders the base template.
- `"/currentjobs"` : The current jobs route connects to the database, fetches the job data and renders the current job list template with the fetched data and other parameters for pagination and search functionalities.
- `"/technician"` : This route redirects to the current jobs route.

### Data Flow

The home route renders the base template which gives the user a choice to select their role. The selected role then directs the application on which route to take next.

In the `"/currentjobs"` route, it calculates the offset for pagination, fetches data from the database, constructs a dictionary mapping containing the job related data, and passes it on to the 'currentjoblist.html' template.

## Design Decisions

Decisions regarding the application design and flow were made with usability, scalability, and security in mind.

### Structure and Navigation

The application uses a structure that separates the home page from the "Current Jobs" page. This segregation allows role-based navigation and accessibility. Upon selecting the 'Technician' role, the user is redirected to the current jobs page.

Implementing a redirect route for technicians leaves room for expanding the application's functionality in the future. For example, setting up separate routes for technicians and administrators.

### Templates and Layout

The decision to extend from the base template for all routes was made to ensure the application has a consistent design without redundantly writing the base HTML structure in every template.

The application uses separate templates for various pages. For data modification functionality, it leverages bootstrap modal pop-up in the current jobs template instead of using a different template or including IF conditions in the same template.

### GET vs POST

For fetching data for display or searching, the application uses GET requests. This decision was based on the fact that the operation would be safe, idempotent, and cacheable - all qualities associated with GET requests as per the HTTP/1.1 specification.

By using Flask's request object, the application accesses data sent through GET requests. As a result, pagination and search functionalities that require parameters to fetch specific data are achieved effectively.

By making clear design decisions and understanding the nature of functionalities required in different parts of the application, a well-structured, extensible, and user-friendly web application was developed.

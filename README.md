# Python Flask Application: Technical Report

## Web Application Structure

The Python Flask web application follows the Model-View-Controller (MVC) structure. The Flask application script serves as the controller, HTML templates as the view, and the MySQL database as the model for the application.

### Proposed Project Changes and Code Modifications

This section presents the process and associated code modifications to enhance application functionalities and user experiences. These are chronologically ordered as a sequence of modification suggestions and their justifications.

### Modification 1: Paginator and Table Design

One of the first changes includes adding pagination to the 'Current Job List' and enhancing the table aesthetics to make it aesthetically pleasing while ensuring the website is compatible with various screen sizes and browsers.

These changes have been implemented by using the `flask_paginate` library to control pagination. As per design specifications, only 10 data entries are displayed per page. Additionally, utilizing Bootstrap's `container` class, the table has been repositioned for improved aesthetics. Bootstrap's responsive design principle has been relied upon to ensure compatibility across multiple screens.

```python
from flask_paginate import Pagination
```

### Routes and Functions

- `"/"` : The home route renders the base template.
- `"/currentjobs"` : The current jobs route connects to the database, fetches the job data and performs pagination before rendering the 'currentjoblist.html' template alongside the fetched data and other parameters for pagination and search functionalities.
- `"/technician"` : This route redirects to the current jobs route.

### Data Flow

The home route renders the base template which provides the user a choice to select their role. Based on the selected role, the user is navigated to the appropriate route.

In the `"/currentjobs"` route, it calculates the offset for pagination, fetches data from the database, constructs a dictionary mapping containing the job related data, and passes it on to the 'currentjoblist.html' template.

### Design Decisions

App design decisions largely hinged on usability, scalability, and security.

### Structure and Navigation

Navigation is based on user role selection on the home page, which redirects users to their respective page, like 'Current Jobs' for technicians, enhancing accessibility and role-based navigation.

### Templates and Layout

The application uses separate templates for the home and jobs list pages, enhancing modularity and reducing redundancy. A base template is extended across all templates to maintain consistency. Within each job list entry on the jobs list page, a bootstrap modal pop-up is used for data modification functionality. This design choice promotes easy data update without navigating away from the current page.

### Modification 2: Changing Paginator position and Page Number

To enhance user interaction, changes were suggested for paginator positioning and page number display. The paginator was moved to the bottom right corner of the screen using CSS for easier visibility and access. Furthermore, the '(current)' text next to the current page number was removed using JavaScript for cleaner display.

### GET vs POST

GET requests are used to fetch data for display or search, ensuring safe, idempotent and cacheable operations as per HTTP/1.1 specifications. Flask's request object is used to access data sent through these GET requests, aiding in achieving pagination and search functionalities that require specific data fetching.

Thus, through methodical design decisions and understanding of requisite functionalities, an extensible and user-friendly web application is developed.

### Notes

Install the `flask_paginate` library by running `pip install flask_paginate` before running these changes. Tailor modifications to align with your boilerplate code as required.

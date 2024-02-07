# Lerndise: Getting Started Guide

Welcome to our Lerndise! This guide will help you get started with setting up the project, understanding its structure, and using its endpoints.
Prerequisites

Before you begin, ensure you have the following installed:

    Python (3.6 or higher)
    Django
    pip (Python package installer)
    Virtualenv (optional but recommended)

Installation

    Clone this repository to your local machine:

bash

    git clone <repository_url>

Navigate to the project directory:

bash

cd <project_directory>

Create a virtual environment (optional but recommended):

bash

    virtualenv venv

Activate the virtual environment:

bash

# On Windows
    venv\Scripts\activate

# On macOS/Linux
    source venv/bin/activate

Install project dependencies:

bash

    pip install -r requirements.txt

Running the Server

To run the Django development server, execute the following command:

bash

    python manage.py runserver

The server will start running locally at http://127.0.0.1:8000/.
Endpoints
User Authentication

    Register: POST /api/register/
        Register a new user.
    Login: POST /api/login/
        Log in with username and password.
    User Details: GET /api/user/
        Retrieve details of the logged-in user.
    Logout: POST /api/logout/
        Log out the current user.

Courses

    List Courses: GET /api/courses/
        Retrieve a list of all available courses.
    Course Request: POST /api/course-request/
        Request generation of course content.
        Payload: { "course": "Course ID or Title" }

<!-- Add more endpoints and descriptions as needed -->
Contributing

If you'd like to contribute to this project, please follow these steps:

    Fork the repository on GitHub.
    Create a new branch with a descriptive name for your feature or bug fix.
    Commit your changes and push the branch to your fork.
    Submit a pull request to the main repository.

License

This project is licensed under the MIT License.

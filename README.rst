=========
Gradify
=========

The purpose of this project is to provide a tool for teachers to aggregate
selected grades for a given class.

************
Installation
************

Gradify is still under development and not packaged for release yet. ::

    # clone the repository
    git clone git@gitlab.com:dlmarrero/gradify.git
    cd gradify

    # create and source a virtualenv w/ Python 3 support
    virtualenv -p python3 .venv
    source .venv/bin/activate

    # install requirements
    pip install -r requirements.txt

    # create and populate initial sqlite3 database
    python manage.py migrate

    # create admin user
    python manage.py createsuperuser

    # run application
    python manage.py runserver



*******
Testing
*******

See https://docs.djangoproject.com/en/2.2/topics/testing/overview/ for more
information on testing in Django.

For this project, all application directories will contain a tests directory
where all of the unit tests should reside.  In most cases, there should be a
1:1 relation of tests to python files.  E.g. if there is a views.py file,
there should be a corresponding tests/test_views.py file.

To run the tests, use the Django management command that exists for testing. ::

    python manage.py test


***************
Static Analysis
***************

This project is configured to use flake8, pylint and bandit to provide static
analysis of the code base.  You can run these individually by looking at how
they are called in our .gitlab-ci.yml file in the project root.  You can install
these tools by installing the test-requirements file in the project root. ::

    pip install -r test-requirements.txt
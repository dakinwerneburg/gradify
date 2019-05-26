=========
gradify
=========

The purpose of this project is to provide a tool for teachers to aggregate
selected grades for a given class.

************
Installation
************

gradify is still under development and not packaged for release yet. ::

    # create anad source a virtualenv w/ Python 3 support
    virtualenv -p python3 .gradify
    source .gradify/bin/activate

    # clone the repository
    git clone git@gitlab.com:dlmarrero/gradify.git
    cd gradify

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

See https://docs.djangoproject.com/en/2.2/topics/testing/overview/
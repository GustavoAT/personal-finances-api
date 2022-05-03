# personal-finances

API to store and manage personal financial data with multiple users.

## How to

Create a `.env` file on the root of the project.
Fill with `dotenv.example` file environment variable names and correct values of your environment.

Create the python virtual environment

`python3 -m venv <path/to/your/virtual/env>`

and activate (on linux)

`source <path/to/your/virtual/env>/bin/activate`

install requirements

`pip install -r requirements.txt`

config database schema first time

`./manage.py makemigrations`

`./manage.py migrate`

create super user

`./manage.py createsuperuser`

start Django development server

`./manage.py runserver`

or Doker compose:

`sudo docker-compose up -d --build`

This example project use sqlite. Make the configurations of django and compose file to use other database engine. For help, the documentations:
https://docs.djangoproject.com/en/4.0/topics/install/#database-installation
https://docs.djangoproject.com/en/4.0/intro/tutorial02/#database-setup
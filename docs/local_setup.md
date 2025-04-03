# Setting up the project on your computer

If at any point in this process you encounter an error, ping me (Alexander) on teams and I will gladly help you.

Prerequisites:

- Git
- Python 3
- Pip
- VsCode or other text editor

## First Time Setup

### Clone repo (Step 1)

Clone the repo to your computer

```shell
git clone https://github.com/bjgill33/6th-Street-Pizza
```

Switch branches to the production branch (this step may change in the future)

```shell
git switch Production
```

### Setup Env (Step 2)

Open up the terminal/command prompt. In VsCode this can be easily done py pressing `CTRL+~`

Install pipenv to your computer. [Pipenv](https://pipenv.pypa.io/en/latest/) manages the virtual environment.

```shell
pip install --user pipenv
```

Install dependencies into the environment

```shell
pipenv install --dev
```

Activate environment

```shell
pipenv shell
```

### Django Setup (Step 3)

If everything worked in step 2, django should already be installed. All that remains is to setup the database.

In your editor, create a file called `local-dev.txt`. Create this file in the same directory which has `Pipfile` and `.gitignore.
The existence of this file makes the django installation use a local SQLite3 database instead of MySQL which is used on the production server.

Create database migrations

```shell
python manage.py makemigrations
```

Apply database migrations

```shell
python manage.py migrate
```

Load base data into the database

```shell
python manage.py loaddata database_dump.json
```

Start local Django server

```shell
python manage.py runserver
```

Everything should be setup now!

## Following Runs

After setting up the environment, running the local django server should be as simple as:

Activate the virtual environment

```shell
pipenv shell
```

Run server

```shell
python manage.py runserver
```

## Additional Notes

This information is not needed for regular setup.

If something breaks horribly with the env or with pipenv, you can delete the environment with:

```shell
pipenv --rm
```

To dump the database of a Django installation:

```shell
python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission -e admin.Logentry > dump.json
```

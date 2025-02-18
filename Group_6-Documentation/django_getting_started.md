# Getting Started with Django

## Dependencies

- Python must be installed on your computer
- This guide will use VsCode.

## Step 1: Creating venv

After [Cloning the repo](./cloning_repo.md), open up the VsCode terminal by pressing `CTRL+~`. Ensure that the terminal is located in the repo folder. If not `cd` to it.

Inside the terminal, type `python --version` to ensure you have python installed. It should print something like:

```
Python 3.12.3
```

Inside the terminal, create a venv (virtual environment) and then activate it.

To create:

```
python -m venv .venv
```

To activate:

```
.venv\Scripts\Activate.ps1
```

If this worked, you should see your command prompt begin with `(.venv)`.

All further steps assume you have the venv active.

## Step 2: Installing Django

Inside the VsCode terminal, django can now be installed for the project.

```
python -m pip install django~=5.0.0
```

To test if you have installed Django, run:

```
django-admin --version
```

You should see something like below.

```
5.0.12
```

## Step 3 (TEMPORARY): Creating Django Project.

> [!NOTE]
> Once we get a Django project merged into the main branch of the repo, you will be able to skip this step.

In the VsCode terminal create the project:

```
django-admin startproject django_project .
```

Then, create the app for the project

```
python manage.py startapp pizza
```

Then, create the database with the `migrate` command.

```
python manage.py migrate
```

Inside the `settings.py` file (`django_project/settings.py`), add `pizza` as an installed app inside of `INSTALLED_APPS`. It should now look like this.

```python
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "pizza",
]
```

## Step 4: Running the app

Inside the VsCode terminal, start the app with the `runserver` command.

```
python manage.py runserver
```

Now you should be able to see a page in your browser. Navigate to `http://127.0.0.1:8000/`. To see if it worked.

If it worked, nice! You're ready to start working with Django.

If any step in this guide did not work, feel free to ping me (Alexander) or anyone else in the project for help on teams.

## Note 1: Testing the app

Django includes automated testing as a built-in functionality.
Once tests have been written, it will be essential that we regularly test to ensure we don't introduce regressions. Run the `test` command to run all tests.

```
python manage.py test
```

## Note 2: Database model changes

Whenever the database model changes, it must be migrated. Just like in step #3, we will be using the `migrate` command. Migrating is a two step process.

- First: the migrations must be made for the app,
- Second: the migrations must be applied.

To make the migrations:

```
python manage.py makemigrations pizza
```

To apply the migrations:

```
python manage.py migrate
```

## Further Reading

If you want to learn more about Django I (Alexander) highly recommend [Django for Beginners](https://learndjango.com/courses/django-for-beginners/). It's a paid book/online course but the first 4 chapters are free.

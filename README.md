# ECOBUY - Backend
Backend for Flashtrip

# Setup
Install all the packages:
```
pip install -r requirements.txt
```

Install populartime packages this way as it is not in PyPi:
```
pip install --upgrade git+https://github.com/m-wrzr/populartimes
```

Make database migrations:
```
python manage.py makemigrations django_server_app
```

Make database tables to migrate to actual version:
```
python manage.py migrate
```

# Running the server
To run over localhost (not visible through Android/iOS emulators):
```
python manage.py runserver 
```
To run in your local or public IP (visible through emulators and other computers in the same network if is a local IP, visible to everyone if is your public IP):
```
ython manage.py runserver 10.0.0.161:8000
```

# Runing load stress testing
We use Locust
```
pip install -r locust
```

1. Modify locustfile to run the test you want.
2. Run server in localhost.
3. Run command locust in a new terminal window.
4. Acces http://127.0.0.1:8089 and check errors.

DOCS: https://docs.locust.io/en/stable/api.html

# Problems with Django?
To delete the migrations folder and the database:
```
rm -f db.sqlite3
rm -r django_server_app/migrations
```
After that, run again the makemigrations and migrate commands above.

# Using a new pacakge?
To add packages to the `requirements.txt`:`
```
pip freeze > requirements.txt
```

# Documenation
For this project we are going to use [pdoc3](https://pdoc3.github.io/pdoc/) module.

> Documentation is like sex: when it is good, it is very, very good; 
and when it is bad, it is better than nothing.
> — Dick B.

#### Where does pdoc get documentation from?
```python
def file_function():
     """Docstring for file_function"""
     pass
     
module_variable = 1
"""Docstring for module_variable."""

class C:
    class_variable = 2
    """Docstring for class_variable."""

    def __init__(self):
        self.instance_variable = 3
        """Docstring for instance_variable."""
        
    def class_function(self):
     """Docstring for class_function"""
     pass
```

Full documentation of pdoc3 can be found [here](https://pdoc3.github.io/pdoc/doc/pdoc/#what-objects-are-documented).


# Deployment
To login to heroku:
```
heroku login
Email: flashtripapp@gmail.com
Password: The password
```

Add Heroku remote branch:
```
heroku git:remote -a django-heroku-flashtripapp
```

Go to deployment branch and merge from master:
```
git checkout deployment
git merge master
```

In `setttings.py` change `DEBUG` to `False`.

Collect all the static files:
```
python manage.py collectstatic
```

Commit the changes:
```
git add --all 
git commit -m “Prepared to deploy“
git push
```

Push the changes to heroku branch:
```
git push heroku deployment:master
```

_If you are not able to push because of the following error:_
```
error: failed to push some refs to 'https://git.heroku.com/django-heroku-flashtripapp.git'
```
_You may want to do this before continuing:_
```
git pull heroku master
```

If you need to migrate the database run the following commands (please note that the `makemigrations` commands should be done before pushing to heroku):
```
heroku run python manage.py migrate
```

Once all the data is uploaded to Heroku go back to master and merge the changes:
```
git checkout master
git merge deployment
```

Finally, in `setttings.py` change `DEBUG` to `True` and:
```
git add --all 
git commit -m “After deploy“
git push
```



### Setting up venv:
- `cd src` to enter src directory.
- `python3 -m venv venv` to make a virtual environment.
- `source ./venv/bin/activate` to activate.
- `pip3 install -r requirements.txt` to install necessary packages.

Run `python3 seed.py` in your virtual environment to reset the database and pre-populate it with all Cornell eateries, dummy users, dummy connections, and dummy reviews.

Then, run `python3 app.py` to run the app.
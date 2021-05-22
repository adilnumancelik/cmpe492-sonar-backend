# CMPE492 - SONAR - Backend repo

Production deployment to [https://boun-sonar.herokuapp.com/](https://boun-sonar.herokuapp.com/)

## Getting Started on Local

First, create a virtual environment and activate it:

```bash
python3 -m venv env
source env/bin/activate
```

For windows:
```bash
python -m venv env
.\env\Scripts\activate
```

Then, install the requirements:
```bash
pip install -r requirements.txt
```

Create a .env file and add this line:
```bash
DATABASE_URL=postgres://{db username}:{db password}@{endpoint url}:{port}/{development db name}
```
This will make sure that application connects to our development PostgreSQL database.

Finally run the server by:
```bash
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) with your browser to see the result.


## Deployment
- `master` is the production branch

Pushing to `master` will make Heroku automatically deploy the production app. 

Visit [https://boun-sonar.herokuapp.com/swagger/](https://boun-sonar.herokuapp.com/swagger/) to see the documentation.

Production database is a PostgreSQL database.

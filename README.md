# HACKATHON

[Learn more and book online at our website](https://HACKATHON-a4a079b504db.herokuapp.com/).

## Screenshot

![](docs/overview.png)

## Features


## User Roles and Stories

### Roles


### Completed Stories


### Deferred Stories


## Data Model

### Reservations

``` mermaid
erDiagram
    User ||--o{ Reservation : booked
    User {
        int user_id PK
        string name
        string email
        string first_name
        string last_name
        string phone_number
    }
    Reservation {
        int reservation_id PK
        string svc_date
        string res_date
        string time
        int duration "minutes"
        int guest_count
        int status
        int user_id FK
    }
    Table {
        int table_id PK
        int table_number UK
        int seat_count
    }
    ServiceTime {
        int hours_id PK
        int day_of_week "0-mon to 6-sun"
        string start_time "24-hour clock"
        string end_time "24-hour clock"
    }
    ServiceException {
        int exception_id PK
        string date
        string start_time "24-hour clock"
        string end_time "24-hour clock"
    }
```

## UX Design

## Technology

### Overview

The project is a web application developed using the Django backend web framework.

The Django framework uses the Python lanaguage to dynamically generate HTML pages.
Styling is provided by Bootstrap with some custom CSS.
A little JavaScript provides client-side interactivity.

In addition to the Django core and its dependencies the project uses a number of additional Python libraries:

* [django-crispy-forms](https://github.com/django-crispy-forms/django-crispy-forms) and [crispy-bootstrap5](https://github.com/django-crispy-forms/crispy-bootstrap5) to automatically format forms with bootstrap
* [dotenv](https://github.com/pedroburon/dotenv) and [python-dotenv](https://pypi.org/project/python-dotenv/) to read environment variables from `.env`
* [dj-database-url](https://jazzband.co/projects/dj-database-url) to parse database URLs
* [django-allauth](https://allauth.org) to authenticate end-users
* [gunicorn](https://gunicorn.org) to serve the content over HTTP
* [psycopg2-binary](https://psycopg.org/) to connect to the PostgreSQL database
* [whitenoise](https://whitenoise.readthedocs.io/en/latest/) to serve static files via WSGI

### Database

The deployed project requires access to a PostgreSQL database instance in the cloud.

For development it is possible to use a local database instance, either PostgreSQL or SQLite, but these instructions assume a cloud instance.

Many companies offer PostgreSQL (or PostgreSQL-compatible) cloud database instances and most require payment.  [Neon](https://neon.com/pricing) has a generous free tier.

To create a cloud database you need to:

1. Choose a cloud PostgreSQL database provider.
2. Create an account.
3. Create a database - you will receive a database URL.
4. Store the URL somewhere safe - it provides complete access to the live database.

The database URL should be something like:

`postgresql://neondb_owner:ngy_rtfGRGRg56g@battery-horse-staple-56dfdf7.c-6.eu-central-1.aws.neon.tech/nuncle_pig_654321`

In the following sections you will copy your database URL into your `.env` file for local development and into your Heroku app config vars for deployment.

### Fork

To develop or deploy this project you first need to fork it on GitHub.

1. Login to your GitHub account.
2. Navigate to [HACKATHON on GitHub](https://github.com/ctr-code/HACKATHON/).
3. Click on the Fork button (on the right, near the top).
4. The `Create a new fork` page opens.
5. Click on `Create fork`.

### Develop

This section describes how to configure your environment to run the project locally.

The instructions work on Linux, WSL and maybe the VSCode bash prompt, but that's untested.

Having [forked the project](#fork), open a terminal, switch to a suitable parent directory and run this command with your github username:

```bash
git clone https://github.com/<your-github-username>/HACKATHON/
```

Then run:

```bash
cd HACKATHON
python3 -m venv .venv
source .venv/bin/activate
echo "DJANGO_DEBUG = True" > .env
echo "DJANGO_SECRET_KEY = 'somerubbishhere'" >> .env
echo "DJANGO_ALLOWED_HOSTS = '127.0.0.1'" >> .env
echo "DATABASE_URL = 'put_database_url_here'" >> .env
pip install -r requirements.txt
mkdir fixtures
curl -L "https://github.com/validator/validator/releases/download/latest/vnu.jar" > fixtures/vnu.jar
```

Edit the `.env` file to include the [database url created previously](#database).  Install the database schema with:

```bash
./manage.py migrate
```

And start the local webserver with:

```bash
./manage.py runserver
```

### Deploy to Heroku

Having [forked the project](#fork) and [created a database](#database).

1. Create a Heroku account.
2. Login to your account dashboard.
3. Click on `New | Create new app`.
4. Choose and enter a name for the new app.
5. Choose a location (probably Europe).
6. Click on `Create App`.
7. Click on the `Open App` button.
8. Make a note of the host name (something like `blah-1a2b3c4d5e6f.herokuapp.com`).
9. Open the `Settings` tab.
10. Click on `Reveal Config Vars`.
11. Enter the [database url created earlier](#database) as `DATABASE_URL`.
12. Enter the host name from step 8 as `DJANGO_ALLOWED_HOSTS`.
13. Enter some random data as `DJANGO_SECRET_KEY`.
14. Open the `Deploy` tab.
15. Choose `GitHub - Connect to GitHub`.
16. Connect to your GitHub user account and select `HACKATHON`.
17. Click on `Connect`.
18. Click on `Deploy`.
19. Click on `Open App`.
20. Enjoy!

## Copilot AI Assistance

## Testing

Details can be found on the [testing page](TESTING.md).

## Credit and Thanks

* [Code Institute](https://codeinstitute.net/) and its tutors for teaching, support and the navbar collapser
* [West Midlands Combined Authority](https://www.wmca.org.uk/) for funding the course
* [Tim Berners-Lee](https://www.w3.org/People/Berners-Lee/) *et al* for the web
* [Brendan Eich](https://en.wikipedia.org/wiki/Brendan_Eich) *et al* for JavaScript
* [Linus Torvalds](https://en.wikipedia.org/wiki/Linus_torvalds) *et al* for Linux
* [Guido van Rossum](https://gvanrossum.github.io/) *et al* for Python
* [The PostgreSQL Authors](https://www.postgresql.org/docs/current/history.html) for the database
* [GitHub](https://github.com/) for hosting the repository and the project plan
* [Heroku](https://www.heroku.com/) for hosting the site
* [Neon](https://neon.com/) for hosting PostgreSQL
* [The Django Authors](https://github.com/django/django/blob/main/AUTHORS) for the web framework
* [Bootstrap](https://getbootstrap.com/) for the CSS framework
* [ParaType](https://www.paratype.com/) for the PT Serif font
* [Font Awesome](https://fontawesome.com/) for icons
* [Fort Awesome](https://github.com/FortAwesome/Font-Awesome/releases) for collating the Font Awesome assets
* [Bunny CDN](https://fonts.bunny.net/) for font hosting
* [Microsoft](https://www.microsoft.com/) for [Visual Studio Code](https://code.visualstudio.com/)
* [Copilot](https://copilot.microsoft.com/) for various tasks as described above
* [W3C](https://www.w3.org/) for the [HTML and CSS validator](https://github.com/validator/validator/)
* [Code Institute](https://pep8ci.herokuapp.com/) again for the Python validator
* [JSHint](https://jshint.com/) for the JavaScript validator
* [WebAIM](https://webaim.org/) for the [WAVE accessibility extension](https://wave.webaim.org/extension/)
* [Inkscape](https://inkscape.org/) for rendering the logo and favicons
* [GIMP](https://www.gimp.org/) for cropping many screenshots
* [Coolors](https://coolors.co/) for the palette generator
* [Fireship](https://fireship.dev/amiresponsive) for the multi-device screenshot
* [Raymond1922A](https://commons.wikimedia.org/wiki/File:Flag_of_Prussia_without_regalia.svg) for the Prussian eagle

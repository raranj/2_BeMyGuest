# BeMyGuest

**Meet new people, share a meal, and bring a recipe to the table.**

BeMyGuest is a social dining and recipe-sharing project for students, people
new to a community, and anyone who enjoys cooking and cultural exchange.
The current version lets you:

- **introduce yourself** with a display name, contact email, and dietary preference;
- **share your allergies** using searchable tags, with a shared vocabulary that avoids duplicate terms;
- **browse recipes** with ingredients, cooking steps, preparation time, servings, and difficulty;
- **contribute a recipe** with an optional photo, dietary tags, and allergen information;
- **view your community ratings** as a host and guest, with scores left empty until you are rated.

Meal gatherings, joining requests, and host approval are part of the intended
experience. Posts and invitations currently display sample content rather than
working event-management flows.

Built by Em Bensinger, Chu-Yun Hwang, Karen Huang, and Ranjana Rajagopalan.

---

## Run it

Use Python 3.11 or newer. From the folder containing `manage.py`, create an
environment or activate your existing one.

```powershell
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
New-Item -ItemType Directory -Force data
```

On macOS or Linux, the equivalent setup is:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
mkdir -p data
```

`requirements.txt` installs Django, python-dotenv, and Pillow. Pillow provides
image support for recipe uploads through Django's `ImageField`.

### The secret key

Generate a key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Create a file named `.env` beside `manage.py` and paste the generated value:

```dotenv
DJANGO_SECRET_KEY='paste-your-generated-key-here'
```

The key is required: without it, settings fail with
`KeyError: 'DJANGO_SECRET_KEY'`. Keep `.env` out of Git; it is already ignored.

Then start the application:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open <http://127.0.0.1:8000>, log in with the account you created, and visit
**My Profile**. Click **Edit**, enter your information, and save.
Public sign-up is not implemented; administrators can create additional accounts
at <http://127.0.0.1:8000/admin/>.

### Pages

| URL | What it does |
|---|---|
| `/` | Home page |
| `/user/` | Your profile; login required |
| `/user/?edit=1` | Create or edit your profile details |
| `/user/allergies/?q=pea` | JSON allergy suggestions; login required |
| `/recipes/` | Browse saved recipes |
| `/recipes/create/` | Create a recipe; login required |
| `/recipes/<id>/` | View a recipe's details |
| `/posts/` | Sample event posts |
| `/invitations/` | Sample invitations |
| `/accounts/login/` | Log in |
| `/accounts/logout/` | Log out using the navigation button; POST required |
| `/admin/` | Django administration; staff access required |

---

## How it's built

Django 5.2, SQLite, server-rendered templates, and vanilla JavaScript. No frontend
build step.

| Location | Responsibility |
|---|---|
| `bemyguest/settings/` | Shared, development, and production settings |
| `bemyguest/urls.py` | Project routes, including recipe list/create/detail pages |
| `bemyguest/templates/` | Shared layout, home, recipe pages, posts, and invitations |
| `bemyguest/ui-ux/` | Normalize, Skeleton, and application CSS |
| `features/users/models.py` | User profiles, dietary choices, shared allergy terms, and rating constraints |
| `features/users/forms.py` | Profile validation and allergy normalization |
| `features/users/views.py` | Profile display/save and allergy suggestions |
| `features/users/templates/` | Profile and login templates |
| `features/users/static/users/allergies.js` | Allergy suggestions and removable tags |
| `features/recipes/` | Recipe model, form, views, migration, and admin registration |
| `features/posts/`, `features/invitations/` | App scaffolding for future gathering and invitation features |
| `data/db.sqlite3` | Development database |
| `docs/notes/notes.txt` | Team contribution notes and development context |

### Profiles and allergies

Django's authentication account stores login credentials. The separate
`features.users.models.User` profile links to that account through a
`OneToOneField`; it does not replace Django's authentication model.

Each profile has a name, contact email, one dietary preference, shared allergies,
creation timestamp, and host/guest scores. The contact email is separate from
the authentication account's email. Dietary preferences come from a fixed
selection, including vegetarian, vegan, pescatarian, halal, kosher, and others.

Allergies use a many-to-many relationship with `Allergy`. Names are normalized
to lowercase with consistent spacing. Users can select suggestions, add a new
term, or remove a tag. Without JavaScript, the field accepts comma-separated
terms. Removing a tag from one profile preserves the shared term and other
users' selections.

Profile reads and writes are scoped to the signed-in account. Ratings are
read-only on the profile page, nullable until rated, and constrained to 1–5.
Administrators can enter scores; review collection and score aggregation are
not implemented.

### Recipes

Each recipe belongs to a Django authentication account and stores its name,
description, ingredients, ordered instructions, preparation/cooking time,
servings, difficulty, dietary tags, allergens, optional image, and creation time.

The form converts ingredients and instructions entered on separate lines into
JSON lists. Dietary tags and allergens accept comma-separated text. Recipe
allergens currently use their own JSON field; they do not yet share the
profile allergy table or perform automatic dietary matching.

Uploaded images are stored under `media/recipes/` and served by Django during
local development. Production needs separate static/media serving and host
configuration; the supplied production settings are not a complete deployment.

## Tests

With the environment active and `.env` configured:

```bash
python manage.py check
python manage.py test features.users
python manage.py makemigrations --check --dry-run
```

The user app contains 11 tests covering login requirements, profile display and
editing, account isolation, dietary choices, rating constraints, shared allergy
suggestions, term validation, CSRF protection, logout, and migration of legacy
allergy data. Recipe, posts, and invitation test files are currently placeholders.

## More

- [User page setup notes](USER_PAGE_SETUP.md) — earlier implementation notes; its JSON-list and always-visible-form descriptions predate the current profile UI.
- [Team contributions and project notes](docs/notes/notes.txt) — includes gathering work described on another branch; the supplied main snapshot still has placeholder posts models and views.

Next steps include database-backed gatherings and invitations, join/accept/deny
workflows, public registration, review-based ratings, recipe tests, and deployment.

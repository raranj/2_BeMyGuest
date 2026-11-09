# BeMyGuest user page

The Django project package is `bemyguest`; feature apps live in `features`.
The user model belongs in `features/users/models.py`, alongside the existing
recipes, posts, and invitations apps. Django discovers `models.py` (plural).
The profile class is `features.users.models.User`. It links one-to-one to
Django's existing authentication account; this is not a replacement AUTH_USER_MODEL.

## Files

- `features/users/models.py`: requested fields, account link, JSON-list validation,
  and rating validators plus database constraints.
- `features/users/forms.py`: editable name/email and comma-separated food lists.
- `features/users/views.py`: authenticated GET and POST operations scoped to the
  current account. GET displays the form; POST creates or updates its profile;
  valid saves redirect to prevent repeated form submission.
- `features/users/urls.py`: namespaced `users:user` route.
- `features/users/templates/users/user.html`: extends the existing styled base.
- `features/users/templates/registration/login.html`: login template.
- `features/users/migrations/0001_initial.py`: database schema.
- `features/users/admin.py`: profile management and rating entry for admins.
- `features/users/tests.py`: six tests for access, editing, isolation, validation,
  template rendering, logout, and CSRF.

Settings register the app, fix template discovery, and set login redirects.
Project URLs mount `/user/`, login/logout, and the existing static page templates.
The shared base now uses Django static/URL tags and POST logout. Other feature
pages still display their existing mock content.

## Run locally

Activate your existing environment, then from the folder containing manage.py:

```powershell
python -m pip install -r requirements.txt
# If you have no .env yet, create one with DJANGO_SECRET_KEY=<your own secret>
New-Item -ItemType Directory -Force data
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit http://127.0.0.1:8000/user/ and log in. Create the first profile by filling
in and saving the form. Cancel changes reloads the saved profile. Accounts can
also be created through Django admin; public signup is outside this change.
Preferences/allergies are typed as comma-separated text and stored as JSON lists.
Scores are nullable until rated, then constrained to 1–5. They and created_at
cannot be submitted through the profile form. Administrators can enter scores;
review aggregation is not implemented. The profile email is a contact field,
separate from the authentication account email. created_at records profile creation.

## Verify

```powershell
python manage.py check
python manage.py test features.users
python manage.py makemigrations --check --dry-run
```

All six tests passed with Django 5.2.19. No migration drift was detected.

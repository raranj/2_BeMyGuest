from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase, TransactionTestCase
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.urls import reverse
from .models import Allergy, DietaryPreference, User
from .forms import UserForm


class UserPageTests(TestCase):
    def setUp(self):
        self.account = get_user_model().objects.create_user(username='alice', password='test-password', email='alice@example.com')
        self.url = reverse('users:user')

    def test_login_required(self):
        self.assertRedirects(self.client.get(self.url), reverse('login') + '?next=' + self.url)

    def test_read_only_edit_save_and_cancel(self):
        self.client.force_login(self.account)
        response = self.client.get(self.url)
        self.assertContains(response, 'Edit profile details')
        self.assertContains(response, 'alice@example.com')
        self.assertNotContains(response, 'name="email"')
        response = self.client.get(self.url, {'edit': '1'})
        self.assertContains(response, 'name="email"')
        self.assertContains(response, 'Cancel changes')
        response = self.client.post(self.url, {'name': 'Alice', 'email': 'invalid'})
        self.assertContains(response, 'name="email"')
        self.assertContains(response, 'Enter a valid email address')
        response = self.client.post(self.url, {
            'name': 'Alice Saved', 'email': 'alice@example.com',
            'dietary_preferences': 'vegan', 'allergies': 'peanut',
        }, follow=True)
        self.assertContains(response, 'Alice Saved')
        self.assertContains(response, 'Vegan')
        self.assertContains(response, 'peanut')
        self.assertNotContains(response, 'name="email"')
        response = self.client.get(self.url)
        self.assertNotContains(response, 'name="email"')

    def test_create_update_and_protect_ratings(self):
        self.client.force_login(self.account)
        self.assertContains(self.client.get(self.url), 'Not rated yet')
        self.assertFalse(User.objects.exists())
        data = {'name': 'Alice', 'email': 'alice@example.com', 'dietary_preferences': 'vegan', 'allergies': 'peanut, shellfish', 'host_score': '5'}
        self.assertRedirects(self.client.post(self.url, data), self.url)
        profile = User.objects.get(account=self.account)
        self.assertEqual(profile.dietary_preferences, 'vegan')
        self.assertEqual(list(profile.allergies.values_list('name', flat=True)), ['peanut', 'shellfish'])
        self.assertIsNone(profile.host_score)
        data.update(name='Alice Updated', dietary_preferences='omnivore', allergies='')
        self.client.post(self.url, data)
        profile.refresh_from_db()
        self.assertEqual(profile.name, 'Alice Updated')
        self.assertFalse(profile.allergies.exists())
        self.assertEqual(User.objects.count(), 1)

    def test_invalid_form_and_isolation(self):
        other = get_user_model().objects.create_user(username='bob')
        profile = User.objects.create(account=other, name='Bob', email='bob@example.com')
        self.client.force_login(self.account)
        response = self.client.post(self.url, {'name': '', 'email': 'invalid', 'id': profile.pk, 'account': other.pk})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Enter a valid email address')
        self.client.post(self.url, {'name': 'Alice', 'email': 'alice@example.com', 'dietary_preferences': 'others', 'id': profile.pk, 'account': other.pk})
        profile.refresh_from_db()
        self.assertEqual(profile.name, 'Bob')
        self.assertTrue(User.objects.filter(account=self.account, name='Alice').exists())

    def test_dietary_preference_choices(self):
        self.client.force_login(self.account)
        response = self.client.get(self.url, {'edit': '1'})
        self.assertContains(response, '<select name="dietary_preferences"')
        for value in DietaryPreference.values:
            form = UserForm(data={'name': 'Alice', 'email': 'alice@example.com', 'dietary_preferences': value})
            self.assertTrue(form.is_valid(), form.errors)
        data = {'name': 'Alice', 'email': 'alice@example.com', 'dietary_preferences': 'vegan, halal'}
        self.assertFalse(UserForm(data=data).is_valid())
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(account=self.account).exists())
        profile = User(account=self.account, name='Alice', email='alice@example.com', dietary_preferences='invalid')
        with self.assertRaises(ValidationError):
            profile.full_clean()
        with self.assertRaises(IntegrityError), transaction.atomic():
            profile.save()

    def test_rating_and_json_validation(self):
        profile = User(account=self.account, name='Alice', email='alice@example.com', host_score=6)
        with self.assertRaises(ValidationError):
            profile.full_clean()
        with self.assertRaises(IntegrityError), transaction.atomic():
            profile.save()
        profile.host_score = 1
        profile.guest_score = 5
        profile.full_clean()

    def test_shared_allergies_suggestions_and_removal(self):
        self.client.force_login(self.account)
        data = {'name': 'Alice', 'email': 'alice@example.com', 'dietary_preferences': 'others', 'allergies': ' Peanut , PEANUT, Tree   Nuts'}
        self.assertRedirects(self.client.post(self.url, data), self.url)
        profile = User.objects.get(account=self.account)
        self.assertEqual(list(profile.allergies.values_list('name', flat=True)), ['peanut', 'tree nuts'])
        other = get_user_model().objects.create_user(username='charlie')
        other_profile = User.objects.create(account=other, name='Charlie', email='charlie@example.com')
        other_profile.allergies.add(Allergy.objects.get(name='peanut'))
        response = self.client.get(reverse('users:allergy_suggestions'), {'q': 'PEA'})
        self.assertEqual(response.json(), {'results': ['peanut']})
        self.assertEqual(self.client.get(reverse('users:allergy_suggestions'), {'q': 'unknown'}).json(), {'results': []})
        self.assertContains(self.client.get(self.url, {'edit': '1'}), 'peanut, tree nuts')
        data['allergies'] = 'sesame'
        self.client.post(self.url, data)
        self.assertEqual(list(profile.allergies.values_list('name', flat=True)), ['sesame'])
        self.assertTrue(other_profile.allergies.filter(name='peanut').exists())
        self.assertTrue(Allergy.objects.filter(name='peanut').exists())
        data.update(name='', allergies='unsaved term')
        self.client.post(self.url, data)
        self.assertFalse(Allergy.objects.filter(name='unsaved term').exists())
        self.client.logout()
        self.assertEqual(self.client.get(reverse('users:allergy_suggestions'), {'q': 'pea'}).status_code, 302)

    def test_allergy_term_length(self):
        form = UserForm(data={'name': 'Alice', 'email': 'alice@example.com', 'dietary_preferences': 'others', 'allergies': 'x' * 101})
        self.assertFalse(form.is_valid())
        self.assertIn('allergies', form.errors)

    def test_navigation_and_login_templates(self):
        for url in ['/', '/recipes/', '/posts/', '/invitations/', '/accounts/login/']:
            self.assertEqual(self.client.get(url).status_code, 200)
        self.client.force_login(self.account)
        self.assertEqual(self.client.get(reverse('logout')).status_code, 405)
        self.assertRedirects(self.client.post(reverse('logout')), reverse('login'))

    def test_csrf_required(self):
        from django.test import Client
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.account)
        self.assertEqual(client.post(self.url, {'name': 'Alice'}).status_code, 403)


class AllergyMigrationTests(TransactionTestCase):
    def test_existing_allergies_are_preserved_and_shared(self):
        previous = [('users', '0002_alter_user_dietary_preferences_and_more')]
        current = [('users', '0003_shared_allergy_terms')]
        executor = MigrationExecutor(connection)
        executor.migrate(previous)
        try:
            apps = executor.loader.project_state(previous).apps
            Account = apps.get_model('auth', 'User')
            Profile = apps.get_model('users', 'User')
            for index, allergies in enumerate([['Peanut', ' peanut ', 'Tree Nuts'], ['PEANUT'], []]):
                account = Account.objects.create(username=f'legacy-{index}')
                Profile.objects.create(account=account, name='Legacy', email='legacy@example.com', allergies=allergies)
            executor = MigrationExecutor(connection)
            executor.migrate(current)
            apps = executor.loader.project_state(current).apps
            AllergyTerm = apps.get_model('users', 'Allergy')
            Profile = apps.get_model('users', 'User')
            self.assertEqual(AllergyTerm.objects.count(), 2)
            self.assertEqual(Profile.objects.filter(allergies__name='peanut').count(), 2)
            self.assertEqual(Profile.objects.filter(allergies__name='tree nuts').count(), 1)
        finally:
            MigrationExecutor(connection).migrate(current)

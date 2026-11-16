from django.db import migrations, models


def copy_terms(apps, schema_editor):
    User = apps.get_model('users', 'User')
    Allergy = apps.get_model('users', 'Allergy')
    alias = schema_editor.connection.alias
    for profile in User.objects.using(alias).all().iterator():
        terms = []
        for value in profile.legacy_allergies:
            name = ' '.join(value.split()).casefold()
            if name:
                terms.append(Allergy.objects.using(alias).get_or_create(name=name)[0])
        profile.allergies.set(terms)


def restore_lists(apps, schema_editor):
    User = apps.get_model('users', 'User')
    alias = schema_editor.connection.alias
    for profile in User.objects.using(alias).all().iterator():
        profile.legacy_allergies = list(profile.allergies.values_list('name', flat=True))
        profile.save(using=alias, update_fields=['legacy_allergies'])


class Migration(migrations.Migration):
    dependencies = [('users', '0002_alter_user_dietary_preferences_and_more')]
    operations = [
        migrations.CreateModel(
            name='Allergy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
            options={'ordering': ['name']},
        ),
        migrations.RenameField(model_name='user', old_name='allergies', new_name='legacy_allergies'),
        migrations.AddField(model_name='user', name='allergies', field=models.ManyToManyField(blank=True, related_name='profiles', to='users.allergy')),
        migrations.RunPython(copy_terms, restore_lists),
        migrations.RemoveField(model_name='user', name='legacy_allergies'),
    ]

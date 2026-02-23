# Generated manually for DE/EN legal pages

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('info', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='legalpage',
            name='page_type',
            field=models.CharField(
                choices=[('privacy', 'Privacy Policy'), ('imprint', 'Imprint'), ('terms', 'Terms of Service')],
                help_text='Type of legal page',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='legalpage',
            name='language',
            field=models.CharField(
                choices=[('de', 'Deutsch'), ('en', 'English')],
                default='de',
                help_text='Content language',
                max_length=5,
            ),
        ),
        migrations.AlterUniqueTogether(
            name='legalpage',
            unique_together={('page_type', 'language')},
        ),
    ]

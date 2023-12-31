# Generated by Django 4.2.7 on 2023-12-02 10:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clientplans',
            name='client_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='client_plans', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='clientplans',
            name='plan_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apis.plans', to_field='plan_type'),
        ),
        migrations.AlterField(
            model_name='usertokens',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_tokens', to=settings.AUTH_USER_MODEL),
        ),
    ]

# Generated for hackathon feature update
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_faceid_roles_prescriptions'),
    ]

    operations = [
        migrations.AddField(
            model_name='institution',
            name='address',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='institution',
            name='region',
            field=models.CharField(blank=True, default='', max_length=120),
        ),
        migrations.AddField(
            model_name='institution',
            name='latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='institution',
            name='longitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='medicineclaim',
            name='doctor_marked_given',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='medicineclaim',
            name='patient_confirmed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='medicineclaim',
            name='patient_confirmed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]

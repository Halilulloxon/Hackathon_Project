# Generated manually for Hackathon_project feature upgrade
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def fill_face_hash(apps, schema_editor):
    FaceIDRecord = apps.get_model('app', 'FaceIDRecord')
    for rec in FaceIDRecord.objects.all():
        if not rec.face_hash:
            rec.face_hash = '0' * 64
            rec.save(update_fields=['face_hash'])


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0002_faceidrecord_face_image_alter_faceidrecord_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='faceidrecord',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='face_profile', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='faceidrecord',
            name='face_hash',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='faceidrecord',
            name='is_registered',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='faceidrecord',
            name='last_verified_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='faceidrecord',
            name='role',
            field=models.CharField(choices=[('citizen', 'Oddiy aholi'), ('doctor', 'Shifokor'), ('pharmacy', 'Dorixona'), ('admin', 'Admin')], default='citizen', max_length=100),
        ),
        migrations.CreateModel(
            name='FaceIDAttempt',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(blank=True, max_length=150)),
                ('status', models.CharField(choices=[('verified', 'Tasdiqlandi'), ('failed', 'Rad etildi'), ('suspicious', 'Shubhali')], default='failed', max_length=30)),
                ('purpose', models.CharField(default='login', max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Prescription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('diagnosis', models.CharField(max_length=255)),
                ('dosage', models.CharField(max_length=120)),
                ('instructions', models.TextField()),
                ('ai_risk', models.CharField(choices=[('safe', 'Xavfsiz'), ('warning', 'Diqqat'), ('danger', 'Xavfli')], default='safe', max_length=20)),
                ('ai_analysis', models.TextField(blank=True)),
                ('free_medicine', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='written_prescriptions', to=settings.AUTH_USER_MODEL)),
                ('medicine', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app.medicine')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prescriptions', to='app.faceidrecord')),
            ],
        ),
        migrations.CreateModel(
            name='MedicineClaim',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(blank=True, max_length=64, unique=True)),
                ('is_used', models.BooleanField(default=False)),
                ('confirmed_by_faceid', models.BooleanField(default=False)),
                ('used_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('prescription', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='claim', to='app.prescription')),
            ],
        ),
        migrations.RunPython(fill_face_hash, migrations.RunPython.noop),
    ]

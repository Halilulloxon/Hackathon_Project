from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import secrets


ROLE_CHOICES = [
    ('citizen', 'Oddiy aholi'),
    ('doctor', 'Shifokor'),
    ('pharmacy', 'Dorixona'),
    ('admin', 'Admin'),
]


class DashboardStat(models.Model):
    title = models.CharField(max_length=100)
    value = models.CharField(max_length=50)
    trend = models.CharField(max_length=100)
    trend_type = models.CharField(max_length=20, choices=[('positive', 'Positive'), ('negative', 'Negative')])

    def __str__(self):
        return self.title


class Institution(models.Model):
    name = models.CharField(max_length=150)
    institution_type = models.CharField(max_length=100)
    address = models.CharField(max_length=255, blank=True, default='')
    region = models.CharField(max_length=120, blank=True, default='')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    rating = models.IntegerField(default=100)
    complaints = models.CharField(max_length=100, default='0')
    checks_count = models.IntegerField(default=0)
    status = models.CharField(max_length=100, default='Faol')

    def __str__(self):
        return self.name


class FaceIDRecord(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='face_profile', null=True, blank=True)
    full_name = models.CharField(max_length=150)
    role = models.CharField(max_length=100, choices=ROLE_CHOICES, default='citizen')
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='face_records')
    face_image = models.ImageField(upload_to='face_id/', blank=True, null=True)
    face_hash = models.TextField(blank=True, default='')
    is_registered = models.BooleanField(default=True)
    last_verified_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=[('verified', 'Tasdiqlandi'), ('suspicious', 'Shubhali'), ('failed', 'Rad etildi')], default='verified')
    checked_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Face ID profil'
        verbose_name_plural = 'Face ID profillar'

    def __str__(self):
        return f'{self.full_name} ({self.role})'


class FaceIDAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    full_name = models.CharField(max_length=150, blank=True)
    status = models.CharField(max_length=30, choices=[('verified', 'Tasdiqlandi'), ('failed', 'Rad etildi'), ('suspicious', 'Shubhali')], default='failed')
    purpose = models.CharField(max_length=100, default='login')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.full_name or self.user} - {self.status}'


class AIAlert(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    details = models.CharField(max_length=255, blank=True)
    severity = models.CharField(max_length=20, choices=[('high', 'Yuqori'), ('medium', 'O‘rta'), ('low', 'Past')])
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Medicine(models.Model):
    name = models.CharField(max_length=150)
    manufacturer = models.CharField(max_length=150)
    batch_number = models.CharField(max_length=100)
    qr_code = models.CharField(max_length=100, unique=True)
    expiry_date = models.DateField()
    quantity = models.IntegerField()
    location = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class MedicineTracking(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='trackings')
    status_title = models.CharField(max_length=150)
    location = models.CharField(max_length=150)
    date = models.DateField()
    status = models.CharField(max_length=30, choices=[('completed', 'Bajarildi'), ('current', 'Jarayonda'), ('pending', 'Kutilmoqda')])

    def __str__(self):
        return f'{self.medicine.name} - {self.status_title}'


class ExpirationMonitoring(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='expiration_records')
    days_left = models.IntegerField()
    risk_level = models.CharField(max_length=20, choices=[('critical', 'Juda xavfli'), ('warning', 'Diqqat kerak'), ('safe', 'Xavfsiz')])
    action_required = models.CharField(max_length=150)

    def __str__(self):
        return f'{self.medicine.name} - {self.days_left} kun'


class Prescription(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='written_prescriptions')
    patient = models.ForeignKey(FaceIDRecord, on_delete=models.CASCADE, related_name='prescriptions')
    medicine = models.ForeignKey(Medicine, on_delete=models.PROTECT)
    diagnosis = models.CharField(max_length=255)
    dosage = models.CharField(max_length=120)
    instructions = models.TextField()
    ai_risk = models.CharField(max_length=20, choices=[('safe', 'Xavfsiz'), ('warning', 'Diqqat'), ('danger', 'Xavfli')], default='safe')
    ai_analysis = models.TextField(blank=True)
    free_medicine = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.patient.full_name} - {self.medicine.name}'


class MedicineClaim(models.Model):
    prescription = models.OneToOneField(Prescription, on_delete=models.CASCADE, related_name='claim')
    token = models.CharField(max_length=64, unique=True, blank=True)
    doctor_marked_given = models.BooleanField(default=True)
    patient_confirmed = models.BooleanField(default=False)
    patient_confirmed_at = models.DateTimeField(null=True, blank=True)
    is_used = models.BooleanField(default=False)
    confirmed_by_faceid = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)

    def confirm(self):
        now = timezone.now()
        self.is_used = True
        self.confirmed_by_faceid = True
        self.patient_confirmed = True
        self.patient_confirmed_at = now
        self.used_at = now
        self.save(update_fields=['is_used', 'confirmed_by_faceid', 'patient_confirmed', 'patient_confirmed_at', 'used_at'])

    def __str__(self):
        return f'QR claim: {self.prescription}'

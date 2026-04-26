from django.contrib import admin
from .models import (
    DashboardStat, Institution, FaceIDRecord, FaceIDAttempt, AIAlert, Medicine,
    MedicineTracking, ExpirationMonitoring, Prescription, MedicineClaim
)

@admin.register(FaceIDRecord)
class FaceIDRecordAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'role', 'institution', 'status', 'checked_time', 'last_verified_at')
    list_filter = ('role', 'status', 'institution')
    search_fields = ('full_name', 'user__username')

@admin.register(FaceIDAttempt)
class FaceIDAttemptAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'status', 'purpose', 'created_at')
    list_filter = ('status', 'purpose')

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'medicine', 'ai_risk', 'free_medicine', 'created_at')
    list_filter = ('ai_risk', 'free_medicine')

@admin.register(MedicineClaim)
class MedicineClaimAdmin(admin.ModelAdmin):
    list_display = ('prescription', 'token', 'doctor_marked_given', 'patient_confirmed', 'is_used', 'confirmed_by_faceid', 'used_at')
    list_filter = ('doctor_marked_given', 'patient_confirmed', 'is_used', 'confirmed_by_faceid')

@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('name', 'institution_type', 'region', 'rating', 'status', 'checks_count')
    list_filter = ('institution_type', 'region', 'status')
    search_fields = ('name', 'address', 'region')

admin.site.register(DashboardStat)
admin.site.register(AIAlert)
admin.site.register(Medicine)
admin.site.register(MedicineTracking)
admin.site.register(ExpirationMonitoring)

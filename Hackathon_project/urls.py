from django.contrib import admin
from django.urls import path
from app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('admin-register/', views.admin_register, name='admin_register'),
    path('faceid_capture/', views.faceid_capture, name='faceid_capture'),
    path('doctor/', views.doctor_dashboard, name='doctor_dashboard'),
    path('profile/', views.patient_profile, name='patient_profile'),
    path('profile/claim/<int:claim_id>/confirm/', views.patient_confirm_claim, name='patient_confirm_claim'),
    path('map/', views.institutions_map, name='institutions_map'),
    path('claim-verify/', views.claim_verify, name='claim_verify'),
    path('alert/<int:alert_id>/resolve/', views.resolve_alert, name='resolve_alert'),
    path('alert/<int:alert_id>/later/', views.later_alert, name='later_alert'),
    path('medicine/<int:item_id>/delete-expired/', views.delete_expired, name='delete_expired'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

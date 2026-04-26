from datetime import datetime
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.db import IntegrityError

from .models import (
    DashboardStat, Institution, FaceIDRecord, FaceIDAttempt, AIAlert, Medicine,
    ExpirationMonitoring, Prescription, MedicineClaim
)
from .faceid_utils import decode_base64_image, face_hash_from_binary, verify_face, hash_distance
from .ai_module import analyze_prescription


def user_in_group(user, group_name):
    return user.is_authenticated and user.groups.filter(name=group_name).exists()


def get_user_role(user):
    if not user.is_authenticated:
        return 'citizen'
    if user.is_superuser or user_in_group(user, 'admin'):
        return 'admin'
    for role in ['doctor', 'pharmacy', 'citizen']:
        if user_in_group(user, role):
            return role
    return 'citizen'


def can_change_data(user):
    return user.is_authenticated and (user.is_superuser or user_in_group(user, 'admin') or user_in_group(user, 'doctor') or user_in_group(user, 'pharmacy'))


def can_delete_medicine(user):
    return user.is_authenticated and (user.is_superuser or user_in_group(user, 'admin') or user_in_group(user, 'pharmacy'))


def is_doctor(user):
    return user.is_authenticated and (user.is_superuser or user_in_group(user, 'doctor') or user_in_group(user, 'admin'))


def is_pharmacy(user):
    return user.is_authenticated and (user.is_superuser or user_in_group(user, 'pharmacy') or user_in_group(user, 'admin'))




UZ_REGION_COORDS = {
    'toshkent': (41.3111, 69.2797), 'tashkent': (41.3111, 69.2797),
    'samarqand': (39.6542, 66.9597), 'samarkand': (39.6542, 66.9597),
    'buxoro': (39.7747, 64.4286), 'bukhara': (39.7747, 64.4286),
    'andijon': (40.7821, 72.3442), 'andijan': (40.7821, 72.3442),
    'farg': (40.3894, 71.7830), 'fergana': (40.3894, 71.7830),
    'namangan': (40.9983, 71.6726), 'qarshi': (38.8606, 65.7890),
    'qashqadaryo': (38.8606, 65.7890), 'termiz': (37.2242, 67.2783),
    'surxondaryo': (37.2242, 67.2783), 'nukus': (42.4619, 59.6166),
    'qoraqalpog': (42.4619, 59.6166), 'urganch': (41.5500, 60.6333),
    'xorazm': (41.5500, 60.6333), 'navoiy': (40.0844, 65.3792),
    'jizzax': (40.1158, 67.8422), 'guliston': (40.4897, 68.7842),
    'sirdaryo': (40.4897, 68.7842),
}





def ensure_demo_data():
    """Demo uchun bazani bo'sh qoldirmaydi: guruhlar, muassasalar va dorilarni yaratadi."""
    for role in ['admin', 'doctor', 'pharmacy', 'citizen']:
        Group.objects.get_or_create(name=role)

    demo_stats = [
        ('Nazoratdagi dorilar', '285+', 'AI monitoring faol', 'positive'),
        ('FaceID tekshiruvlar', '99%', 'Shaxs tasdiqlash kuchaytirildi', 'positive'),
        ('Shifoxona reytingi', '82%', 'Ochiq xarita asosida', 'positive'),
        ('Shubhali holatlar', '12', 'AI ogohlantirishlari', 'negative'),
    ]
    for title, value, trend, trend_type in demo_stats:
        DashboardStat.objects.get_or_create(title=title, defaults={'value': value, 'trend': trend, 'trend_type': trend_type})

    demo_institutions = [
        ('Respublika Shoshilinch Tibbiy Yordam Markazi', 'Shifoxona', 'Toshkent', 'Toshkent shahri, Chilonzor', 41.285, 69.203, 92, 'Faol, nazorat yaxshi', '3', 18),
        ('Samarqand Viloyat Klinik Shifoxonasi', 'Shifoxona', 'Samarqand', 'Samarqand shahri', 39.654, 66.959, 84, 'Faol, o‘rta xavf', '7', 11),
        ('Buxoro Oilaviy Poliklinikasi', 'Poliklinika', 'Buxoro', 'Buxoro shahri', 39.774, 64.428, 76, 'Qo‘shimcha tekshiruv kerak', '12', 8),
        ('Andijon Markaziy Dorixona Ombori', 'Dorixona/Ombor', 'Andijon', 'Andijon shahri', 40.782, 72.344, 88, 'Faol', '4', 14),
        ('Farg‘ona Tuman Tibbiyot Birlashmasi', 'Tibbiyot birlashmasi', 'Farg‘ona', 'Farg‘ona shahri', 40.389, 71.783, 68, 'Xavfli holat, audit kerak', '18', 5),
    ]
    for name, typ, region, addr, lat, lng, rating, status, complaints, checks in demo_institutions:
        Institution.objects.get_or_create(
            name=name,
            defaults={'institution_type': typ, 'region': region, 'address': addr, 'latitude': lat, 'longitude': lng, 'rating': rating, 'status': status, 'complaints': complaints, 'checks_count': checks}
        )

    today = timezone.now().date()
    demo_meds = [
        ('Paratsetamol 500mg', 'UzPharm', 'PARA-2026-01', 'QR-PARA-001', 120, 'Toshkent ombori'),
        ('Amoksitsillin 250mg', 'MediLine', 'AMOX-2026-02', 'QR-AMOX-002', 60, 'Samarqand dorixona'),
        ('Insulin Regular', 'BioMed', 'INS-2026-03', 'QR-INS-003', 25, 'Buxoro ombori'),
        ('Loratadin 10mg', 'HealthCare', 'LOR-2026-04', 'QR-LOR-004', 80, 'Andijon ombori'),
    ]
    for name, manufacturer, batch, qr, qty, loc in demo_meds:
        med, _ = Medicine.objects.get_or_create(
            qr_code=qr,
            defaults={'name': name, 'manufacturer': manufacturer, 'batch_number': batch, 'expiry_date': today.replace(year=today.year + 1), 'quantity': qty, 'location': loc}
        )
        days_left = (med.expiry_date - today).days
        ExpirationMonitoring.objects.get_or_create(
            medicine=med,
            defaults={'days_left': days_left, 'risk_level': 'safe', 'action_required': 'Doimiy monitoring'}
        )


def institution_coords(inst, index=0):
    if inst.latitude and inst.longitude:
        return float(inst.latitude), float(inst.longitude)
    text = f'{inst.name} {inst.address} {inst.region} {inst.status}'.lower()
    for key, coords in UZ_REGION_COORDS.items():
        if key in text:
            return coords
    fallback = list(UZ_REGION_COORDS.values())
    return fallback[index % len(fallback)]


def get_rating_state(rating):
    if rating >= 85:
        return 'Yaxshi'
    if rating >= 70:
        return 'O‘rta nazorat'
    return 'Xavfli / tekshiruv kerak'

def run_ai_analysis():
    today = datetime.now().date()
    for med in Medicine.objects.filter(quantity__gt=0):
        days_left = (med.expiry_date - today).days
        if days_left <= 7:
            AIAlert.objects.get_or_create(title=f'Muddati juda yaqin dori: {med.name}', is_resolved=False, defaults={'description': f'{med.name} dorisining muddati {days_left} kun ichida tugaydi.', 'details': f'Joylashuv: {med.location}, miqdor: {med.quantity} dona', 'severity': 'high'})
        elif days_left <= 30:
            AIAlert.objects.get_or_create(title=f'Muddati yaqin dori: {med.name}', is_resolved=False, defaults={'description': f'{med.name} dorisining muddati {days_left} kun ichida tugaydi.', 'details': f'Joylashuv: {med.location}, miqdor: {med.quantity} dona', 'severity': 'medium'})
    suspicious_count = FaceIDAttempt.objects.filter(status='suspicious').count()
    failed_count = FaceIDAttempt.objects.filter(status='failed').count()
    if suspicious_count >= 5:
        AIAlert.objects.get_or_create(title='Face ID shubhali holatlar ko‘paydi', is_resolved=False, defaults={'description': f'{suspicious_count} ta shubhali Face ID holati aniqlandi.', 'details': 'Boshqa odam xodim nomidan kirishga uringan bo‘lishi mumkin.', 'severity': 'high'})
    if failed_count >= 5:
        AIAlert.objects.get_or_create(title='Face ID rad etilgan urinishlar ko‘paydi', is_resolved=False, defaults={'description': f'{failed_count} ta rad etilgan Face ID urinishlari bor.', 'details': 'Kirish xavfsizligi bo‘yicha tekshiruv kerak.', 'severity': 'medium'})
    for inst in Institution.objects.filter(rating__lt=80):
        AIAlert.objects.get_or_create(title=f'Halollik reytingi past: {inst.name}', is_resolved=False, defaults={'description': f'{inst.name} reytingi {inst.rating}% ga tushgan.', 'details': f'Muassasa turi: {inst.institution_type}, holat: {inst.status}', 'severity': 'medium'})


def home(request):
    assert isinstance(request, HttpRequest)
    ensure_demo_data()
    run_ai_analysis()
    qr_query = request.GET.get('qr', '').strip()
    medicines = Medicine.objects.filter(qr_code__icontains=qr_query) if qr_query else Medicine.objects.all()[:20]
    context = {
        'title': 'Tibbiyot Halollik Tizimi',
        'year': datetime.now().year,
        'today': datetime.now().strftime('%d.%m.%Y'),
        'dashboard_stats': DashboardStat.objects.all(),
        'face_records': FaceIDRecord.objects.select_related('institution', 'user').all().order_by('-checked_time')[:50],
        'face_attempts': FaceIDAttempt.objects.select_related('user').all().order_by('-created_at')[:30],
        'ai_alerts': AIAlert.objects.filter(is_resolved=False).order_by('-created_at')[:30],
        'medicines': medicines,
        'institutions': Institution.objects.all().order_by('-rating'),
        'expiration_records': ExpirationMonitoring.objects.select_related('medicine').filter(medicine__quantity__gt=0),
        'recent_prescriptions': Prescription.objects.select_related('doctor', 'patient', 'medicine').order_by('-created_at')[:10],
        'recent_claims': MedicineClaim.objects.select_related('prescription__patient', 'prescription__medicine').order_by('-created_at')[:10],
        'qr_query': qr_query,
        'is_admin': get_user_role(request.user) == 'admin',
        'is_doctor': get_user_role(request.user) == 'doctor',
        'is_pharmacy': get_user_role(request.user) == 'pharmacy',
        'is_citizen': get_user_role(request.user) == 'citizen',
        'can_change_data': can_change_data(request.user),
        'can_delete_medicine': can_delete_medicine(request.user),
    }
    map_items = []
    for i, inst in enumerate(Institution.objects.all().order_by('-rating')):
        lat, lng = institution_coords(inst, i)
        map_items.append({
            'name': inst.name,
            'type': inst.institution_type,
            'rating': inst.rating,
            'status': inst.status,
            'state': get_rating_state(inst.rating),
            'complaints': inst.complaints,
            'checks': inst.checks_count,
            'lat': lat,
            'lng': lng,
        })
    context['institutions_map_json'] = json.dumps(map_items, ensure_ascii=False)
    return render(request, 'app/index.html', context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        image_data = request.POST.get('face_image', '')
        user = authenticate(request, username=username, password=password)
        if user is None:
            messages.error(request, 'Login yoki parol noto‘g‘ri.')
            return redirect('login')
        try:
            profile = user.face_profile
        except FaceIDRecord.DoesNotExist:
            messages.error(request, 'Bu akkauntda Face ID profil yo‘q. Avval Face ID ro‘yxatdan o‘ting.')
            return redirect('login')
        try:
            image_file, binary = decode_base64_image(image_data)
            new_hash = face_hash_from_binary(binary)
        except Exception:
            FaceIDAttempt.objects.create(user=user, full_name=username, status='failed', purpose='login')
            messages.error(request, 'Kirish uchun kamera orqali Face ID rasm oling.')
            return redirect('login')
        if verify_face(profile.face_hash, new_hash):
            login(request, user)
            profile.last_verified_at = timezone.now()
            profile.status = 'verified'
            profile.save(update_fields=['last_verified_at', 'status'])
            FaceIDAttempt.objects.create(user=user, full_name=profile.full_name, status='verified', purpose='login')
            messages.success(request, 'Face ID tasdiqlandi. Tizimga kirdingiz.')
            if get_user_role(user) == 'doctor':
                return redirect('doctor_dashboard')
            if get_user_role(user) == 'citizen':
                return redirect('patient_profile')
            return redirect('home')
        FaceIDAttempt.objects.create(user=user, full_name=profile.full_name, status='suspicious', purpose='login')
        messages.error(request, f'Face ID mos kelmadi. Masofa: {hash_distance(profile.face_hash, new_hash)}')
    return render(request, 'app/login.html')


def logout_view(request):
    logout(request)
    return redirect('home')


def register_view(request):
    return redirect('faceid_capture')


@login_required(login_url='login')
def admin_register(request):
    if not (request.user.is_superuser or user_in_group(request.user, 'admin')):
        messages.error(request, 'Faqat admin foydalanuvchi qo‘sha oladi.')
        return redirect('home')
    roles = ['admin', 'doctor', 'pharmacy', 'citizen']
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        role = request.POST.get('role', 'citizen')
        if not username or not password:
            messages.error(request, 'Login va parol kiritilishi shart.')
            return redirect('admin_register')
        if role not in roles:
            messages.error(request, 'Noto‘g‘ri rol tanlandi.')
            return redirect('admin_register')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Bu login allaqachon mavjud.')
            return redirect('admin_register')
        user = User.objects.create_user(username=username, password=password)
        group, _ = Group.objects.get_or_create(name=role)
        user.groups.add(group)
        messages.success(request, f'{username} foydalanuvchisi {role} roli bilan yaratildi. Endi Face ID profil biriktiring.')
        return redirect('faceid_capture')
    return render(request, 'app/admin_register.html', {'roles': roles})


@login_required(login_url='login')
def resolve_alert(request, alert_id):
    if not can_change_data(request.user):
        messages.error(request, 'Sizda bu amalni bajarish huquqi yo‘q.')
        return redirect('home')
    alert = get_object_or_404(AIAlert, id=alert_id)
    if request.method == 'POST':
        alert.is_resolved = True
        alert.details = f'{alert.details} | Holat: tekshirildi va hal qilindi'
        alert.save()
        messages.success(request, 'AI ogohlantirish database’da hal qilindi.')
    return redirect('home')


@login_required(login_url='login')
def later_alert(request, alert_id):
    if not can_change_data(request.user):
        messages.error(request, 'Sizda bu amalni bajarish huquqi yo‘q.')
        return redirect('home')
    alert = get_object_or_404(AIAlert, id=alert_id)
    if request.method == 'POST':
        alert.severity = 'low'
        alert.details = f'{alert.details} | Holat: keyinroq ko‘rish uchun belgilandi'
        alert.save()
        messages.info(request, 'Ogohlantirish past xavfga o‘tkazildi.')
    return redirect('home')


@login_required(login_url='login')
def delete_expired(request, item_id):
    if not can_delete_medicine(request.user):
        messages.error(request, 'Siz dorilar bazasini o‘zgartira olmaysiz.')
        return redirect('home')
    item = get_object_or_404(ExpirationMonitoring, id=item_id)
    if request.method == 'POST':
        medicine = item.medicine
        item.delete()
        medicine.delete()
        messages.success(request, 'Dori bazadan butunlay o‘chirildi.')
    return redirect('home')


def faceid_capture(request):
    ensure_demo_data()
    institutions = Institution.objects.all()
    roles = ['citizen', 'doctor', 'pharmacy', 'admin']
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        full_name = request.POST.get('full_name', '').strip()
        image_data = request.POST.get('face_image', '')
        institution_id = request.POST.get('institution')
        role = request.POST.get('role', 'citizen')
        if not username or not password or not full_name or not image_data or not institution_id or not role:
            messages.error(request, 'Login, parol, ism, muassasa, rol va rasm to‘liq yuborilmadi.')
            return render(request, 'app/faceid.html', {'institutions': institutions, 'roles': roles})
        if role not in roles:
            messages.error(request, 'Noto‘g‘ri rol tanlandi.')
            return redirect('faceid_capture')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Bu login allaqachon mavjud. Har bir odam Face ID ro‘yxatdan faqat bir marta o‘tadi.')
            return redirect('faceid_capture')
        if FaceIDRecord.objects.filter(full_name__iexact=full_name).exists():
            messages.error(request, 'Bu ism bilan Face ID profil allaqachon bor. Qayta ro‘yxatdan o‘tish mumkin emas.')
            return redirect('faceid_capture')
        try:
            image_file, binary = decode_base64_image(image_data)
            face_hash = face_hash_from_binary(binary)
            institution = Institution.objects.get(id=institution_id)
        except Exception as exc:
            messages.error(request, f'Face ID rasm yoki muassasa xato: {exc}')
            return redirect('faceid_capture')
        try:
            user = User.objects.create_user(username=username, password=password, first_name=full_name)
            group, _ = Group.objects.get_or_create(name=role)
            user.groups.add(group)
            FaceIDRecord.objects.create(user=user, full_name=full_name, institution=institution, role=role, face_image=image_file, face_hash=face_hash, status='verified')
        except IntegrityError:
            messages.error(request, 'Bu foydalanuvchiga Face ID profil oldin yaratilgan.')
            return redirect('faceid_capture')
        messages.success(request, 'Face ID profil yaratildi. Endi har safar login parol + Face ID bilan kiriladi.')
        return redirect('login')
    return render(request, 'app/faceid.html', {'institutions': institutions, 'roles': roles})


@login_required(login_url='login')
def doctor_dashboard(request):
    if not is_doctor(request.user):
        messages.error(request, 'Bu sahifa faqat shifokor uchun.')
        return redirect('home')
    patients = FaceIDRecord.objects.filter(role='citizen').select_related('institution')
    medicines = Medicine.objects.filter(quantity__gt=0).order_by('name')
    prescriptions = Prescription.objects.filter(doctor=request.user).select_related('patient', 'medicine').order_by('-created_at')[:30]
    if request.method == 'POST':
        patient_id = request.POST.get('patient')
        medicine_id = request.POST.get('medicine')
        diagnosis = request.POST.get('diagnosis', '').strip()
        dosage = request.POST.get('dosage', '').strip()
        instructions = request.POST.get('instructions', '').strip()
        free_medicine = request.POST.get('free_medicine') == 'on'
        if not patient_id or not medicine_id or not diagnosis or not dosage or not instructions:
            messages.error(request, 'Retsept uchun barcha maydonlarni to‘ldiring.')
            return redirect('doctor_dashboard')
        patient = get_object_or_404(FaceIDRecord, id=patient_id, role='citizen')
        medicine = get_object_or_404(Medicine, id=medicine_id, quantity__gt=0)
        ai_risk, ai_analysis = analyze_prescription(medicine.name, dosage, instructions)
        prescription = Prescription.objects.create(doctor=request.user, patient=patient, medicine=medicine, diagnosis=diagnosis, dosage=dosage, instructions=instructions, ai_risk=ai_risk, ai_analysis=ai_analysis, free_medicine=free_medicine)
        MedicineClaim.objects.create(prescription=prescription)
        messages.success(request, 'Retsept yozildi. AI tahlil qilindi. Bemor profilida FaceID orqali tasdiqlashi uchun bepul dori claim yaratildi.')
        return redirect('doctor_dashboard')
    return render(request, 'app/doctor_dashboard.html', {'patients': patients, 'medicines': medicines, 'prescriptions': prescriptions})



@login_required(login_url='login')
def patient_profile(request):
    try:
        profile = request.user.face_profile
    except FaceIDRecord.DoesNotExist:
        messages.error(request, 'Profil topilmadi. Avval Face ID ro‘yxatdan o‘ting.')
        return redirect('faceid_capture')
    claims = MedicineClaim.objects.select_related('prescription__doctor', 'prescription__patient', 'prescription__medicine').filter(prescription__patient=profile).order_by('-created_at')
    return render(request, 'app/patient_profile.html', {'profile': profile, 'claims': claims})


@login_required(login_url='login')
def patient_confirm_claim(request, claim_id):
    try:
        profile = request.user.face_profile
    except FaceIDRecord.DoesNotExist:
        messages.error(request, 'Face ID profil topilmadi.')
        return redirect('faceid_capture')
    claim = get_object_or_404(MedicineClaim.objects.select_related('prescription__patient', 'prescription__medicine'), id=claim_id, prescription__patient=profile)
    if request.method != 'POST':
        return redirect('patient_profile')
    if claim.patient_confirmed or claim.is_used:
        messages.info(request, 'Bu dori oldin tasdiqlangan.')
        return redirect('patient_profile')
    image_data = request.POST.get('face_image', '')
    try:
        image_file, binary = decode_base64_image(image_data)
        new_hash = face_hash_from_binary(binary)
    except Exception:
        messages.error(request, 'Tasdiqlash uchun kameradan Face ID rasm oling.')
        return redirect('patient_profile')
    if not verify_face(profile.face_hash, new_hash):
        FaceIDAttempt.objects.create(user=request.user, full_name=profile.full_name, status='failed', purpose='patient_claim_confirm')
        messages.error(request, 'Face ID mos kelmadi. Dori olindi deb tasdiqlanmadi.')
        return redirect('patient_profile')
    medicine = claim.prescription.medicine
    if medicine.quantity <= 0:
        messages.error(request, 'Bu dori omborda qolmagan.')
        return redirect('patient_profile')
    medicine.quantity -= 1
    medicine.save(update_fields=['quantity'])
    claim.confirm()
    FaceIDAttempt.objects.create(user=request.user, full_name=profile.full_name, status='verified', purpose='patient_claim_confirm')
    messages.success(request, 'Face ID tasdiqlandi. Profilingizda bepul dori olingani qayd qilindi.')
    return redirect('patient_profile')


def institutions_map(request):
    ensure_demo_data()
    institutions = Institution.objects.all().order_by('-rating')
    map_items = []
    for i, inst in enumerate(institutions):
        lat, lng = institution_coords(inst, i)
        map_items.append({
            'name': inst.name,
            'type': inst.institution_type,
            'rating': inst.rating,
            'status': inst.status,
            'state': get_rating_state(inst.rating),
            'complaints': inst.complaints,
            'checks': inst.checks_count,
            'lat': lat,
            'lng': lng,
        })
    return render(request, 'app/institutions_map.html', {
        'institutions': institutions,
        'institutions_map_json': json.dumps(map_items, ensure_ascii=False),
    })

@login_required(login_url='login')
def claim_verify(request):
    if not is_pharmacy(request.user):
        messages.error(request, 'Bu sahifa faqat dorixona/admin uchun.')
        return redirect('home')
    token = request.GET.get('token', '').strip() or request.POST.get('token', '').strip()
    claim = None
    if token:
        claim = MedicineClaim.objects.select_related('prescription__patient', 'prescription__medicine').filter(token=token).first()
        if not claim:
            messages.error(request, 'Bu QR token bazada topilmadi. Doktor panelidan yangi token oling.')
    if request.method == 'POST':
        image_data = request.POST.get('face_image', '')
        if not claim:
            messages.error(request, 'QR token topilmadi.')
            return redirect('claim_verify')
        if claim.is_used:
            messages.error(request, 'Bu QR avval ishlatilgan.')
            return redirect('claim_verify')
        try:
            image_file, binary = decode_base64_image(image_data)
            new_hash = face_hash_from_binary(binary)
        except Exception:
            messages.error(request, 'Bemor Face ID rasmini oling.')
            return redirect(f'/claim-verify/?token={claim.token}')
        patient = claim.prescription.patient
        if not verify_face(patient.face_hash, new_hash):
            FaceIDAttempt.objects.create(user=patient.user, full_name=patient.full_name, status='failed', purpose='medicine_claim')
            messages.error(request, 'Bemor Face ID tasdiqlanmadi. Dori berilmadi.')
            return redirect(f'/claim-verify/?token={claim.token}')
        medicine = claim.prescription.medicine
        if medicine.quantity <= 0:
            messages.error(request, 'Bu dori omborda qolmagan.')
            return redirect(f'/claim-verify/?token={claim.token}')
        medicine.quantity -= 1
        medicine.save(update_fields=['quantity'])
        claim.confirm()
        FaceIDAttempt.objects.create(user=patient.user, full_name=patient.full_name, status='verified', purpose='medicine_claim')
        messages.success(request, 'QR + Face ID tasdiqlandi. Bemorga bepul dori berildi.')
        return redirect('claim_verify')
    return render(request, 'app/claim_verify.html', {'claim': claim, 'token': token})

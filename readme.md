<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="uz">
<head>
<meta charset="utf-8" />




</head>

<body>

<h1>🛡️ Tibbiyot Halollik Monitoring Tizimi</h1>
<img src="app/static/app/fonts/5431887870340830101_121.jpg" alt="Loyiha rasmi">
<p>
Ushbu loyiha sog‘liqni saqlash tizimida shaffoflikni oshirish va korrupsiyani kamaytirish uchun ishlab chiqilgan.
Platforma dorilarni nazorat qilish, tizimdagi faoliyatlarni kuzatish va shubhali holatlarni aniqlash imkonini beradi.
  
  
🤖 AI Monitoring

Tizim sun’iy intellekt yordamida sog‘liqni saqlash tizimidagi
shubhali faoliyatlarni aniqlaydi.

AI quyidagilarni tahlil qiladi:

- dori yozilish statistikasi
- dorilar harakati
- narxlar o‘zgarishi
- foydalanuvchi faoliyati

AI yordamida korrupsiya xavfi bo‘lgan holatlar avtomatik aniqlanadi.
</p>

<div class="section">

<h2> 🚀Asosiy imkoniyatlar</h2>

<ul>
<li>Dori vositalarini monitoring qilish</li>
<li>Tizimdagi statistik ma'lumotlarni ko‘rsatish</li>
<li>Admin panel orqali boshqaruv</li>
<li>Foydalanuvchi rollari orqali ruxsatlarni boshqarish</li>
<li>Tizimdagi faoliyatni kuzatish</li>
</ul>

</div>

<div class="section">

<h2>🛠 Foydalanilgan texnologiyalar</h2>

<ul>
<li>Python</li>
<li>Django</li>
<li>HTML</li>
<li>CSS</li>
<li>JavaScript</li>
<li>SQLite</li>
</ul>

</div>

<div class="section">

<h2>⚙️ Loyihani ishga tushirish</h2>


<p>Loyiha papkasiga kirish:</p>

<code>
cd Hackathon_project
</code>

<p>Kutubxonalarni o‘rnatish:</p>

<code>
pip install -r requirements.txt
</code>

<p>Database yaratish:</p>

<code>
python manage.py migrate
</code>

<p>Admin foydalanuvchi yaratish:</p>

<code>
python manage.py createsuperuser
</code>

<p>Serverni ishga tushirish:</p>

<code>
python manage.py runserver
</code>

<p>Brauzer orqali ochish:</p>

<code>
http://127.0.0.1:8000
</code>

</div>

<div class="section box">

<h2>⚠️ Muhim eslatma</h2>

<p>
Loyihani ishga tushirishdan oldin superuser yaratish tavsiya qilinadi.
Database sifatida SQLite ishlatiladi.
Admin panel orqali tizimni boshqarish mumkin.
</p>

</div>

<div class="section">

<h2>🎯 Loyiha maqsadi</h2>

<ul>
<li>Sog‘liqni saqlash tizimida shaffoflikni oshirish</li>
<li>Korrupsiyani kamaytirish</li>
<li>Dorilar harakatini nazorat qilish</li>
<li>Tizimdagi jarayonlarni monitoring qilish</li>
</ul>

</div>

<div class="section">

<h2>👨‍💻 Mualliflar</h2>
<h2> Tursunaliyev Ozodbek </h2>
<h2> Vaqqosov Halilulloxon </h2>
<h2> Ikromov Husniddin </h2>
<p>
Ushbu loyiha hackathon jamoasi tomonidan ishlab chiqilgan.
</p>

</div>

</body>
</html>

## Yangi qo‘shilgan funksiyalar
- Doktor bepul dori belgilasa, bemor profilida kutish holatida ko‘rinadi.
- Bemor `Profilim` sahifasiga FaceID login orqali kiradi va dorini olganini kamera FaceID bilan tasdiqlaydi.
- Tasdiqlanganda dori miqdori DB da 1 taga kamayadi va claim ishlatilgan deb belgilanadi.
- Hamma uchun ochiq `Xarita` sahifasi qo‘shildi: DB dagi tibbiyot muassasalari O‘zbekiston xaritasida reyting va holati bilan chiqadi.
- Institution modeliga `address`, `region`, `latitude`, `longitude` maydonlari qo‘shildi.

Ishga tushirishdan oldin:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

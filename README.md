AdGen: AI-Powered Advertising Content Generator

1. Proje Tanımı

AdGen, küçük ve orta ölçekli işletmelerin (KOBİ’lerin) dijital pazarlama süreçlerini kolaylaştırmak amacıyla geliştirilmiş yapay zekâ tabanlı bir reklam içerik üretim platformudur.
Uygulama; reklam metni oluşturma, görsel tasarım promptu üretme, gerçek yapay zekâ görseli oluşturma ve rakip analizi gibi modülleri tek bir arayüz altında birleştirir.

Bu proje, uygulamalı yapay zekâ tekniklerinin gerçek bir iş problemi üzerine uygulanmasını amaçlar. Ayrıca çok dilli (Türkçe + İngilizce) kullanım desteği sunar.

2. Özellikler
2.1 Reklam Metni Üretimi

Gemini Pro modeli kullanılarak profesyonel ve platformlara uygun reklam metinleri oluşturulur.

Üretilen içerikler; başlıklar, sloganlar, A/B test metinleri ve hashtag önerilerinden oluşur.

Türkçe ve İngilizce içerik üretimi desteklenir.

2.2 Görsel Tasarım Promptu Üretimi

Ürün, hedef kitle ve platform bilgilerine göre detaylı bir görsel promptu oluşturulur.

Prompt; kompozisyon, ışıklandırma, arka plan, kamera açısı ve renk paleti gibi öğeleri içerir.

SDXL için optimize edilmiş tek satır İngilizce prompt üretimi yapılır.

2.3 AI Görsel Üretimi (SDXL)

Stability AI’ın SDXL modeli kullanılır.

Ürün odaklı, yüksek çözünürlüklü (1024×1024) görseller oluşturulur.

Base64’den PNG’ye dönüştürme işlemi yapılır ve kullanıcı görseli indirebilir.

2.4 Rakip Analizi Modülü

Girilen ürün/hizmet adına göre benzer marka ve kampanyalara yönelik analiz çıkarılır.

Rakiplerin kampanya mesajları, slogan trendleri, platform tercihleri ve farklılaşma önerileri sunulur.

Hem Türkçe hem İngilizce analiz üretilebilir.

2.5 Çok Dilli Arayüz

Kullanıcı arayüzü Türkçe ve İngilizce arasında değiştirilebilir.

Arayüzdeki tüm metinler ve üretilen reklam içerikleri dil seçimine göre yeniden oluşturulur.

2.6 Modern Arayüz Tasarımı

Streamlit üzerinde özel CSS ile geliştirilen temiz ve minimal bir UI yapısı vardır.

Turuncu–mor degrade temalı AdGen tasarım kimliği kullanılmıştır.

3. Kullanılan Teknolojiler
3.1 Programlama Dili ve Arayüz

Python

Streamlit

HTML ve CSS tabanlı stil özelleştirmeleri

3.2 Yapay Zekâ Modelleri

Gemini Pro (Text Generation, Competitor Analysis)

Stable Diffusion XL – SDXL (Image Generation)

3.3 API ve Veri Yapıları

REST API

JSON tabanlı istek/cevap formatı

Base64 görsel verisi çözümleme

HTTP POST istekleri

3.4 Python Kütüphaneleri

streamlit

google-generativeai

requests

pillow (PIL)

io

base64

4. Dosya Yapısı
AdGen-MVP/
│
├── app.py                 # Ana uygulama dosyası
├── requirements.txt       # Gerekli Python paketleri
└── README.md              # Proje açıklaması

5. Kurulum ve Çalıştırma
5.1 Bağımlılıkların yüklenmesi
pip install -r requirements.txt

5.2 API anahtarlarının eklenmesi

Aşağıdaki dosyayı oluşturun:

.streamlit/secrets.toml

İçine şunları yazın:

GEMINI_API_KEY = "your-gemini-key"
STABILITY_API_KEY = "your-stability-key"

5.3 Uygulamanın çalıştırılması
streamlit run app.py

6. Uygulama Akışı

Kullanıcı ürün, hedef kitle, platform, üslup ve dil seçimini yapar.

Reklam metni oluşturma modülü çalışır.

Görsel tasarım promptu oluşturulur.

İngilizce optimize prompt SDXL API'ye gönderilir.

Görsel üretilir, ekranda gösterilir ve indirilebilir.

Rakip analizi modülü rakip stratejilerini analiz eder ve raporlar.

Tüm işlemler tek bir modern arayüz üzerinden gerçekleştirilir.

7. Mimari Yapı
7.1 Uygulama Bileşenleri

Kullanıcı Arayüzü (Streamlit tabanlı)

Prompt Oluşturucu Fonksiyonlar

Gemini Pro Metin Motoru

SDXL Görsel Motoru

Rakip Analizi Motoru

Sonuç Görselleştirme Modülü

7.2 Veri Akış Diyagramı

Kullanıcı → Prompt Builder → Gemini/SDXL → İşlenen Çıktı → Arayüz

8. Gelecek Planlar

Video reklam oluşturma

Meta Ads API ile otomatik reklam yayını

Kullanıcı hesabı ve geçmiş kampanya kaydı

Kişiselleştirilmiş marka kimliği hafızası

Çoklu görsel kombinasyonu

Mobil uygulama (Flutter)

PDF kampanya raporu oluşturma

9. Geliştiriciler

Amine Yıldırım – AI ve Backend Geliştirici

(Diğer ekip üyesi) – Sunum

(Diğer ekip üyesi) – Raporlama ve Araştırma

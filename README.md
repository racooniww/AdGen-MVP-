AI-powered Advertising Content Generator MVP for SMEs

1. Proje Hakkında

AdGen, küçük ve orta ölçekli işletmelerin (KOBİ’lerin) dijital pazarlama süreçlerinde kullanmak üzere geliştirilmiş, yapay zeka tabanlı reklam içeriği üretme aracıdır.

Kullanıcıdan alınan bilgiler (ürün, hedef kitle, platform, üslup…) doğrultusunda:

Reklam başlıkları

Açıklama metinleri

Hashtag önerileri

Görsel fikirleri

üreten bir generative AI uygulamasıdır.

Bu proje, YBS öğrencileri tarafından geliştirilen bir Minimum Uygulanabilir Ürün (MVP) örneğidir.

2. Projenin Amacı

KOBİ’ler profesyonel ajanslara erişemediği veya bütçe ayıramadığı için sosyal medya reklamlarını kendileri hazırlamak zorunda kalır.
Bu süreç:

zaman alıcı

yaratıcılık gerektiren

teknik bilgi isteyen

bir süreçtir.

AdGen, işletmelerin sadece birkaç bilgi girişiyle profesyonel reklam içerikleri oluşturmasını sağlayarak zaman kazandırır ve reklam kalitesini artırır.

 3. Kullanılan Teknolojiler
Alan	Teknoloji
Backend	Python
UI	Streamlit
Yapay Zeka	OpenAI GPT-4o / GPT-4o-mini
Veritabanı (opsiyonel)	SQLite
Repository	GitHub

 5. Uygulama Özellikleri

Ürün/Hizmet girişi

Hedef kitle tanımı

Platform seçimi (Instagram, TikTok, LinkedIn, Facebook)

Marka üslubu seçimi

Tek tıkla reklam içeriği oluşturma

Üretilen metinleri ekranda gösterme

Görsel önerisi sunma

5. Kurulum ve Çalıştırma
 Gerekli Kurulumlar

Python 3.10+ önerilir.

1. Depoyu Klonla
git clone https://github.com/racooniww/AdGen-MVP-.git
cd AdGen-MVP-

2. Gerekli Paketleri Kur
pip install -r requirements.txt

3. OpenAI API Anahtarı Ekle

Streamlit için şu klasöre bir dosya oluştur:

 .streamlit/secrets.toml

İçine şunu yaz:

OPENAI_API_KEY = "buraya_anahtarını_yaz"

4. Uygulamayı Başlat
streamlit run app.py


Uygulama tarayıcıda otomatik açılır.

6. Dosya Yapısı
AdGen-MVP/
│── app.py                # Ana uygulama dosyası
│── requirements.txt      # Gerekli Python paketleri
│── README.md             # Proje dokümantasyonu
│── .gitignore            # Gereksiz dosyaları dışlama
└── .streamlit/
      └── secrets.toml    # API anahtarı (local)

7. Örnek Kullanım

Ürün:
Soğuk kahve

Hedef Kitle:
Üniversite öğrencileri

Platform:
Instagram

Üslup:
Eğlenceli

AdGen çıktısı:

3 farklı reklam metni

Vurucu başlık

Hashtag önerileri

Görsel tahmini (ör: “buz küpleri arasında ferahlatıcı bir kahve bardağı”)

8. Gelecek Geliştirme Fikirleri

Çok dilli reklam üretimi (TR/EN)

Görsel üretimi (DALL·E, Stable Diffusion)

KPI analizi (etkileşim tahmini)

Tam otomatik reklam yayınlama (Meta / Google Ads API)

Kullanıcı hesabı oluşturma ve proje kaydı

9. Proje Ekibi

AdGen üç kişilik bir ekip tarafından geliştirilmiştir.
Ekip görev dağılımı proje raporunda detaylı açıklanacaktır.

10. Lisans

Bu proje eğitim amaçlıdır.

AdGen: AI-Powered Advertising Content Generator
	1.	Proje Tanımı
AdGen, küçük ve orta ölçekli işletmelerin (KOBİ’lerin) dijital pazarlama süreçlerini kolaylaştırmak için geliştirilmiş yapay zekâ tabanlı bir reklam üretim platformudur.

Uygulama, tek bir web arayüzü üzerinden:
	•	Reklam metni üretimi
	•	Görsel tasarım promptu üretimi
	•	Gerçek AI görsel üretimi (Stability SDXL)
	•	Rakip analizi (competitor intelligence)

işlevlerini bir araya getirir.

Arayüz çok dilli çalışır: Türkçe, İngilizce ve “Dual (TR + EN Output)” modları desteklenir. Böylece hem yerel KOBİ’ler hem de uluslararası markalar için kullanılabilir.
	2.	Özellikler
2.1 Reklam Metni Üretimi
	•	Gemini 2.5 Flash metin modeli kullanılarak, ürün/hizmet, hedef kitle, platform ve üslup bilgilerine göre reklam metni üretilir.
	•	Çıktı yapısı:
	•	3 kısa başlık (headline)
	•	2 farklı reklam metni (A/B testi için)
	•	1 kampanya sloganı
	•	8 adet hashtag önerisi
	•	Dil modu:
	•	Sadece Türkçe
	•	Sadece İngilizce
	•	Dual mod: Türkçe + İngilizce çıktılar tek seferde

2.2 Görsel Tasarım Promptu Üretimi
	•	Reklam görseli için ayrıntılı bir açıklama üretir.
	•	İçerik:
	•	Kompozisyon
	•	Arka plan
	•	Işıklandırma
	•	Renk paleti
	•	Kamera açısı
	•	SDXL için tek satırlık İngilizce prompt önerisi
	•	Tasarımcı ya da grafik ekibi bu promptu doğrudan kullanabilir veya düzenleyebilir.

2.3 AI Görsel Üretimi (Stability SDXL)
	•	Stability AI’ın stable-image/generate/core endpoint’i üzerinden SDXL tabanlı görsel üretimi yapılır.
	•	Uygulama iki katmanlı prompt yaklaşımı kullanır:
	1.	Gemini ile otomatik oluşturulan, ürün/kitlenin bağlamını taşıyan İngilizce SDXL promptu
	2.	Kullanıcının girdiği “ek yönlendirme” (refinement) metni
	•	Son prompt şu şekilde oluşur:
base_prompt + "\n\nRefinement / extra details: " + user_custom_prompt
	•	Üretilen görsel Streamlit arayüzünde gösterilir ve .png formatında indirilebilir.

2.4 Kullanıcı Tarafından Prompt İyileştirme
	•	Öğretmen geri bildirimi doğrultusunda, görsel bazen beklentiden uzak olduğunda kullanıcıya müdahale imkânı eklenmiştir.
	•	“Görseli iyileştirmek için ek yönlendirme (opsiyonel)” alanına kullanıcı şunları yazabilir:
	•	“daha sıcak renkler, ürüne yakın çekim, sade arka plan”
	•	“modern minimal stil, soft ışık, ürün merkeze yakın”
	•	Bu ifade, temel SDXL promptunun üzerine eklenerek daha kontrollü görsel üretimi sağlanır.

2.5 Rakip Analizi Modülü
	•	Girilen ürün/kategori adına göre rakip analizi metni üretir.
	•	Analiz içeriği:
	•	Rakip marka türleri
	•	Mesaj ve slogan temaları
	•	Reklamlarda ön plana çıkan faydalar ve açılar
	•	Ton ve örnek ifade kalıpları
	•	Sektör trendleri
	•	Pazar boşlukları
	•	Ürün için 3 farklılaşma önerisi
	•	Türkçe veya İngilizce olarak çalıştırılabilir (dil seçimine bağlı).

2.6 Çok Dilli Arayüz
	•	Arayüzdeki tüm sabit metinler ve butonlar LANG sözlüğü üzerinden yönetilir.
	•	Seçenekler:
	•	Türkçe
	•	English
	•	Dual (TR + EN Output) – metin üretimi iki dilde birden yapılır.
	•	Ton seçenekleri de dile göre değişir:
	•	Türkçe: Eğlenceli, Profesyonel, Samimi, İkna Edici
	•	İngilizce: Playful, Professional, Friendly, Persuasive

2.7 Modern Arayüz ve Marka Kimliği
	•	Streamlit üzerinde özel CSS ile modern bir kart tasarımı uygulanmıştır.
	•	AdGen logo dosyası (adgen_logo.jpg) hem favicon (page_icon) hem de başlık alanında kullanılır.
	•	Üst kısımda logolu başlık, altına proje açıklaması ve mor–pembe degrade çizgi yerleştirilmiştir.
	•	Bileşenler iki ana kartta toplanır:
	•	Reklam üretim kartı (metin, prompt, görsel)
	•	Rakip analizi kartı

	3.	Kullanılan Teknolojiler

3.1 Programlama Dili ve Arayüz
	•	Python
	•	Streamlit (web arayüzü)
	•	HTML/CSS ile özelleştirilmiş stil

3.2 Yapay Zekâ Modelleri
	•	Gemini 2.5 Flash
	•	Reklam metni üretimi
	•	Görsel tasarım açıklaması
	•	İngilizce SDXL prompt üretimi
	•	Rakip analizi metni
	•	Stability AI – SDXL (stable-image/generate/core)
	•	Metinden görsel üretme (text-to-image)
	•	1:1 oranlı, PNG formatında çıktı

3.3 API ve Veri Yapıları
	•	REST API çağrıları
	•	JSON tabanlı istek/cevaplar (Gemini)
	•	HTTP multipart/form-data (Stability SDXL)
	•	Görsellerin bytes olarak alınıp Pillow ile açılması

3.4 Python Kütüphaneleri
	•	streamlit
	•	google-generativeai
	•	requests
	•	Pillow (PIL)
	•	io (BytesIO)

	4.	Dosya Yapısı

AdGen-MVP/
│
├── app.py            # Ana Streamlit uygulaması
├── requirements.txt  # Gerekli Python paketleri
├── adgen_logo.jpg    # Uygulama logosu (favicon + header)
└── README.md         # Proje dokümantasyonu

	5.	Kurulum ve Çalıştırma

5.1 Bağımlılıkların Yüklenmesi

pip install -r requirements.txt

requirements.txt içeriği örneği:

streamlit
google-generativeai
requests
pillow

5.2 API Anahtarlarının Eklenmesi

Proje kök dizininde .streamlit/secrets.toml dosyasını oluşturun:

GEMINI_API_KEY = "your-gemini-key"
STABILITY_API_KEY = "your-stability-key"

Streamlit, bu anahtarları st.secrets["GEMINI_API_KEY"] ve st.secrets["STABILITY_API_KEY"] üzerinden okur.

5.3 Uygulamanın Çalıştırılması

streamlit run app.py

Komut çalıştıktan sonra lokalde belirtilen URL üzerinden (genellikle http://localhost:8501) uygulamaya erişilebilir.

	6.	Uygulama Akışı

	1.	Kullanıcı dili seçer: Türkçe, İngilizce veya Dual.
	2.	Ürün/hizmet detayları, hedef kitle, platform ve üslup bilgilerini girer.
	3.	Kullanıcı:
	•	“Reklam Metni Üret” butonuna basarsa:
	•	Gemini, seçilen dil modunda reklam metinlerini oluşturur.
	•	“Görsel Tasarım Promptu” butonuna basarsa:
	•	Gemini, görsel için ayrıntılı bir açıklama ve SDXL uyumlu prompt üretir.
	•	“AI Görseli Üret” butonuna basarsa:
	•	Gemini, İngilizce SDXL temel promptunu üretir.
	•	Kullanıcı ek yönlendirme girdiyse, bu ifade temel promptun sonuna eklenir.
	•	Son prompt Stability SDXL API’sine gönderilir, görsel üretilir ve indirilebilir hale gelir.
	4.	Kullanıcı “Rakip Analizi” kartında ürün/kategori adını yazar ve “Rakipleri Tara” butonuna basar:
	•	Gemini, rakip türleri, mesaj temaları ve farklılaşma önerilerini içeren metinsel analiz döndürür.

	7.	Mimari Yapı

7.1 Bileşenler
	•	Streamlit Kullanıcı Arayüzü
	•	Prompt oluşturucu fonksiyonlar (build_ad_text_prompt, build_visual_prompt)
	•	Gemini metin motoru (text_model)
	•	SDXL görsel motoru (generate_image_stability)
	•	Rakip analizi fonksiyonu (scan_competitors)
	•	Sonuç görselleştirme (metin alanları, görüntü alanı, indirme butonları)

7.2 Veri Akış Diyagramı (Özet)

Kullanıcı Girdisi
      ↓
Prompt Builder (metin / görsel / rakip analizi)
      ↓
Gemini 2.5 Flash  ───→  Reklam metni / tasarım açıklaması / analiz
      ↓
Stability SDXL    ───→  Nihai reklam görseli
      ↓
Streamlit Arayüzünde Gösterim + İndirme


	8.	Gelecek Geliştirme Fikirleri

	•	Video reklam senaryosu ve storyboard çıkarma
	•	Meta / Google Ads API entegrasyonları ile otomatik reklam yayını
	•	Kullanıcı hesabı ve geçmiş kampanya arşivi
	•	Marka kimliği hafızası (ton, renk paleti, logo vb. saklama)
	•	Çoklu görsel varyasyonu üretimi (A/B test için)
	•	Mobil uygulama (Flutter ile)

	9.	Geliştirici Ekibi


	•	Amine Yıldırım – Yapay Zekâ ve Uygulama Geliştirme
	•	Ekip Üyesi 2 – Sunum Tasarımı ve Demo Hazırlığı
	•	Ekip Üyesi 3 – Raporlama, literatür taraması ve iş analizi

import streamlit as st
import google.generativeai as genai
import requests
import base64
from io import BytesIO
from PIL import Image

st.set_page_config(
    page_title="AdGen – AI Reklam Üretici",
    page_icon="🎯",
    layout="centered"
)

def inject_custom_css():
    st.markdown(
        """
        <style>
        /* Genel arka plan ve font */
        .stApp {
            background: #f5f7fb;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }

        /* Başlık alanı */
        .adgen-header {
            text-align: center;
            padding: 1.5rem 0 1rem 0;
        }
        .adgen-title {
            font-size: 2.2rem;
            font-weight: 800;
            color: #222;
            margin-bottom: 0.2rem;
        }
        .adgen-subtitle {
            font-size: 0.95rem;
            color: #666;
        }

        /* Ana kart */
        .adgen-card {
            background: #ffffff;
            padding: 1.5rem 1.8rem;
            border-radius: 1.1rem;
            box-shadow: 0 10px 25px rgba(15, 23, 42, 0.08);
            border: 1px solid rgba(148, 163, 184, 0.25);
        }

        /* Bölüm başlıkları */
        .section-title {
            font-weight: 600;
            font-size: 0.95rem;
            color: #475569;
            margin-bottom: 0.3rem;
        }

        /* Input’ların üstündeki ikon + yazı */
        .field-label {
            display: flex;
            align-items: center;
            gap: 0.35rem;
            font-size: 0.90rem;
            color: #334155;
            margin-bottom: 0.2rem;
        }

        .field-label span.icon {
            font-size: 1rem;
        }

        /* Butonlar */
        .stButton>button {
            border-radius: 999px;
            padding: 0.5rem 1.2rem;
            border: none;
            font-size: 0.9rem;
            font-weight: 600;
            cursor: pointer;
        }

        /* Turuncu ana buton */
        .btn-primary {
            background: linear-gradient(135deg, #f97316, #ec4899);
            color: white;
        }

        /* İkincil buton */
        .btn-secondary {
            background: #0f172a;
            color: white;
        }

        /* Üçüncü buton */
        .btn-outline {
            background: white;
            color: #0f172a;
            border: 1px solid #cbd5f5 !important;
        }

        /* Butonlar için sütun boşluğu */
        .button-row {
            margin-top: 1rem;
        }

        /* Çıktı bölümü */
        .output-box {
            margin-top: 1.4rem;
            padding: 1rem 1.1rem;
            border-radius: 0.9rem;
            background: #f9fafb;
            border: 1px dashed #cbd5e1;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


# ---------------------------------------------------
# Streamlit Secrets
# ---------------------------------------------------
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
STABILITY_API_KEY = st.secrets["STABILITY_API_KEY"]

# Stability SDXL endpoint
STABILITY_URL = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"

# Gemini text model
text_model = genai.GenerativeModel("models/gemini-pro-latest")


# ---------------------------------------------------
# SAFE TEXT EXTRACTION (Gemini empty response fix)
# ---------------------------------------------------
def extract_text_safe(response):
    """Gemini bazen response.text verir, bazen candidates içinde döndürür. Güvenli şekilde metni çıkarır."""
    # 1 — Normal text
    if hasattr(response, "text") and response.text:
        return response.text.strip()

    # 2 — Candidates → parts
    if hasattr(response, "candidates") and response.candidates:
        cand = response.candidates[0]
        if hasattr(cand, "content") and hasattr(cand.content, "parts"):
            if cand.content.parts and hasattr(cand.content.parts[0], "text"):
                txt = cand.content.parts[0].text
                if txt:
                    return txt.strip()

    # 3 — Tamamen boş → return ""
    return ""


# ---------------------------------------------------
# STABILITY SDXL IMAGE GENERATION
# ---------------------------------------------------
def generate_image_stability(prompt: str):
    headers = {
        "Authorization": f"Bearer {STABILITY_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
        "text_prompts": [{"text": prompt}],
        "cfg_scale": 7,
        "height": 1024,
        "width": 1024,
        "samples": 1,
        "steps": 30
    }

    response = requests.post(STABILITY_URL, headers=headers, json=payload)

    if response.status_code != 200:
        raise ValueError(f"Stability API Hatası: {response.text}")

    data = response.json()
    image_b64 = data["artifacts"][0]["base64"]
    img_bytes = base64.b64decode(image_b64)
    return Image.open(BytesIO(img_bytes))


# ---------------------------------------------------
# PROMPT BUILDER (TEXT)
# ---------------------------------------------------
def build_text_prompt(product, audience, platform, tone):
    return f"""
Sen bir dijital pazarlama uzmanısın.

Ürün: {product}
Hedef kitle: {audience}
Platform: {platform}
Üslup: {tone}

Aşağıdaki formatta reklam içeriği oluştur:

- 3 kısa başlık
- 2 farklı reklam metni (A/B testi için)
- Kampanya sloganı
- 8 hashtag
"""


def build_image_prompt(product, audience, platform, tone):
    return f"""
Sen profesyonel bir reklam tasarımcısın.

Ürün: {product}
Hedef kitle: {audience}
Platform: {platform}
Üslup: {tone}

Reklam görseli için detaylı tasarım promptu oluştur:

1. Kompozisyon
2. Arka plan
3. Işıklandırma
4. Kamera açısı
5. Renk paleti
6. SDXL için tek satırlık İngilizce prompt
"""


# ---------------------------------------------------
# TURKISH → HIGH-QUALITY ENGLISH PROMPT (Fixes LANGUAGE + EMPTY PROMPT ERRORS)
# ---------------------------------------------------
def translate_to_english_for_image(product, audience, platform, tone):

    prompt = f"""
You are a senior advertising image prompt engineer.

Translate the following Turkish inputs into a high-quality, professional, 100% ENGLISH prompt
for creating an advertisement image using SDXL:

Product: {product}
Target Audience: {audience}
Platform: {platform}
Tone: {tone}

REQUIREMENTS:
- Output MUST BE English only.
- Describe composition, lighting, background, camera angle, style, mood.
- End with ONE single SDXL-ready line.
- DO NOT include Turkish words.
"""

    response = text_model.generate_content(prompt)
    english = extract_text_safe(response)

    # Retry if empty
    if not english or len(english) < 5:
        retry = text_model.generate_content(f"""
Write ONLY one English SDXL prompt describing a professional advertisement photo of:
Product: {product}
Audience: {audience}
""")
        english = extract_text_safe(retry)

    # Final fallback
    if not english or len(english) < 5:
        english = (
            f"Professional advertisement photo of {product}, "
            f"targeted to {audience}, ultra realistic, studio lighting, 4K product shot."
        )

    return english

inject_custom_css()

# ---------------------------------------------------
# STREAMLIT UI
# ---------------------------------------------------
# Özel tasarım CSS
inject_custom_css()

# Başlık alanı (HTML ile)
st.markdown(
    """
    <div class="adgen-header">
        <div class="adgen-title">🎯 AdGen – AI Reklam Metni + Görsel + Prompt Üretici</div>
        <div class="adgen-subtitle">
            KOBİ'ler için tek ekranda metin, görsel fikir ve gerçek AI görsel desteği.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Ana kart
with st.container():
    st.markdown('<div class="adgen-card">', unsafe_allow_html=True)

    # --- Üst form alanı: Ürün, hedef kitle vs. ---
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="field-label"><span class="icon">🛍</span> Ürün / Hizmet</div>', unsafe_allow_html=True)
        product = st.text_input(label="", placeholder="Örn: El yapımı sabun")

        st.markdown('<div class="field-label"><span class="icon">📱</span> Platform</div>', unsafe_allow_html=True)
        platform = st.selectbox(label="", options=["Instagram", "TikTok", "LinkedIn", "Facebook"])

    with col2:
        st.markdown('<div class="field-label"><span class="icon">🎯</span> Hedef Kitle</div>', unsafe_allow_html=True)
        audience = st.text_input(label="", placeholder="Örn: Genç yetişkinler, anneler, kahve severler")

        st.markdown('<div class="field-label"><span class="icon">🎨</span> Üslup</div>', unsafe_allow_html=True)
        tone = st.selectbox(label="", options=["Eğlenceli", "Profesyonel", "Samimi", "İkna Edici"])

    st.markdown("---")

    # --- Butonlar satırı ---
    c1, c2, c3 = st.columns(3)

    with c1:
        text_clicked = st.button("📝 Reklam Metni Üret", key="btn_text")
    with c2:
        prompt_clicked = st.button("🎨 Görsel Tasarım Promptu", key="btn_prompt")
    with c3:
        image_clicked = st.button("🖼 Gerçek AI Görseli Üret", key="btn_image")

    # --- Çıktılar ---
    # Reklam metni
    if text_clicked:
        if not product or not audience:
            st.warning("⚠ Lütfen ürün ve hedef kitle alanlarını doldurun.")
        else:
            with st.spinner("Metin üretiliyor..."):
                try:
                    prompt_text = build_text_prompt(product, audience, platform, tone)
                    response = text_model.generate_content(prompt_text)
                    result_text = extract_text_safe(response)

                    st.markdown('<div class="output-box">', unsafe_allow_html=True)
                    st.subheader("📌 Reklam Metni")
                    st.write(result_text)
                    st.markdown('</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Hata: {e}")

    # Görsel tasarım promptu
    if prompt_clicked:
        if not product or not audience:
            st.warning("⚠ Lütfen ürün ve hedef kitle alanlarını doldurun.")
        else:
            with st.spinner("Görsel tasarım promptu üretiliyor..."):
                try:
                    prompt_design = build_image_prompt(product, audience, platform, tone)
                    response = text_model.generate_content(prompt_design)
                    result_prompt = extract_text_safe(response)

                    st.markdown('<div class="output-box">', unsafe_allow_html=True)
                    st.subheader("🖼 Tasarım Promptu")
                    st.write(result_prompt)
                    st.markdown('</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Hata: {e}")

    # Gerçek AI görseli
    if image_clicked:
        if not product or not audience:
            st.warning("⚠ Lütfen ürün ve hedef kitle alanlarını doldurun.")
        else:
            with st.spinner("İngilizce görsel promptu hazırlanıyor..."):
                try:
                    english_prompt = translate_to_english_for_image(product, audience, platform, tone)
                except Exception as e:
                    st.error(f"İngilizce prompt üretilemedi: {e}")
                    english_prompt = ""

            if not english_prompt or len(english_prompt) < 5:
                st.error("Geçerli bir İngilizce prompt üretilemedi, lütfen tekrar deneyin.")
            else:
                with st.spinner("Stability SDXL ile görsel üretiliyor..."):
                    try:
                        img = generate_image_stability(english_prompt)
                        st.markdown('<div class="output-box">', unsafe_allow_html=True)
                        st.subheader("🖼 Üretilen Görsel")
                        st.image(img, use_column_width=True)

                        buf = BytesIO()
                        img.save(buf, format="PNG")
                        st.download_button(
                            "📥 Görseli İndir",
                            buf.getvalue(),
                            "adgen_image.png",
                            "image/png"
                        )
                        st.markdown('</div>', unsafe_allow_html=True)

                    except Exception as e:
                        st.error(f"Görsel üretimi hatası: {e}")

    st.markdown('</div>', unsafe_allow_html=True)  # .adgen-card kapanışı


# ---------------------------------------------------
# 1) TEXT AD GENERATION
# ---------------------------------------------------
if st.button("📝 Reklam Metni Üret"):
    if not product or not audience:
        st.warning("⚠ Lütfen gerekli alanları doldurun.")
    else:
        with st.spinner("Metin üretiliyor..."):
            try:
                prompt = build_text_prompt(product, audience, platform, tone)
                response = text_model.generate_content(prompt)
                st.subheader("📌 Reklam Metni")
                st.write(extract_text_safe(response))
            except Exception as e:
                st.error(f"Hata: {e}")


# ---------------------------------------------------
# 2) VISUAL DESIGN PROMPT
# ---------------------------------------------------
if st.button("🎨 Görsel Tasarım Promptu Üret"):
    if not product or not audience:
        st.warning("⚠ Lütfen gerekli alanları doldurun.")
    else:
        with st.spinner("Prompt üretiliyor..."):
            try:
                prompt = build_image_prompt(product, audience, platform, tone)
                response = text_model.generate_content(prompt)
                st.subheader("🖼 Tasarım Promptu")
                st.write(extract_text_safe(response))
            except Exception as e:
                st.error(f"Hata: {e}")


# ---------------------------------------------------
# 3) REAL IMAGE GENERATION (STABILITY SDXL)
# ---------------------------------------------------
if st.button("🖼 Gerçek AI Görseli Üret"):
    if not product or not audience:
        st.warning("⚠ Lütfen gerekli alanları doldurun.")
    else:

        # Step 1 — Convert to English first
        with st.spinner("İngilizce görsel promptu hazırlanıyor..."):
            try:
                english_prompt = translate_to_english_for_image(product, audience, platform, tone)
            except Exception as e:
                st.error(f"İngilizce prompt üretilemedi: {e}")
                st.stop()

        # Step 2 — Validate
        if not english_prompt or len(english_prompt) < 5:
            st.error("Gemini geçerli bir İngilizce prompt üretmedi. Lütfen tekrar deneyin.")
            st.stop()

        # Step 3 — Generate SDXL image
        with st.spinner("Stability SDXL ile görsel üretiliyor..."):
            try:
                img = generate_image_stability(english_prompt)
                st.subheader("🖼 Üretilen Görsel")
                st.image(img, use_column_width=True)

                # Download button
                buf = BytesIO()
                img.save(buf, format="PNG")
                st.download_button(
                    "📥 Görseli İndir",
                    buf.getvalue(),
                    "adgen_image.png",
                    "image/png"
                )

            except Exception as e:
                st.error(f"Görsel üretimi hatası: {e}")

import streamlit as st
import google.generativeai as genai
import requests
import base64
from io import BytesIO
from PIL import Image

# ---------------------------------------------------
# MODERN UI AYARLARI
# ---------------------------------------------------
st.set_page_config(
    page_title="AdGen – AI Reklam Üretim Platformu",
    page_icon=None,
    layout="centered"
)


def inject_custom_css():
    st.markdown(
        """
        <style>
        .stApp {
            background: #f2f4f8;
            font-family: -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
        }

        /* Başlık alanı */
        .adgen-header {
            text-align: center;
            margin-top: 12px;
            margin-bottom: 30px;
        }
        .adgen-title {
            font-size: 2.3rem;
            font-weight: 750;
            color: #111827;
            letter-spacing: -0.04em;
        }
        .adgen-subtitle {
            font-size: 0.95rem;
            color: #6b7280;
            margin-top: 4px;
        }

        /* Ana kart */
        .adgen-card {
            background: #ffffff;
            padding: 1.9rem 2.1rem;
            border-radius: 1.1rem;
            max-width: 900px;
            margin: 0 auto 2rem auto;
            box-shadow: 0 18px 40px rgba(15, 23, 42, 0.08);
            border: 1px solid rgba(226, 232, 240, 0.9);
        }

        /* Input label */
        .field-label {
            font-size: 0.90rem;
            font-weight: 600;
            color: #374151;
            margin-bottom: 0.2rem;
        }

        /* Butonlar */
        .stButton>button {
            border-radius: 999px;
            padding: 0.5rem 1.3rem;
            border: none;
            font-size: 0.9rem;
            font-weight: 600;
            cursor: pointer;
        }

        .btn-primary {
            background: linear-gradient(135deg, #6366f1, #3b82f6);
            color: #ffffff;
        }

        .btn-secondary {
            background: #0f172a;
            color: #ffffff;
        }

        .btn-neutral {
            background: #f3f4f6;
            color: #111827;
            border: 1px solid #e5e7eb !important;
        }

        /* Output kutusu */
        .output-box {
            margin-top: 1.4rem;
            padding: 1.1rem 1.2rem;
            border-radius: 0.9rem;
            background: #f9fafb;
            border: 1px solid #e5e7eb;
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
    if hasattr(response, "text") and response.text:
        return response.text.strip()

    if hasattr(response, "candidates") and response.candidates:
        cand = response.candidates[0]
        if hasattr(cand, "content") and hasattr(cand.content, "parts"):
            if cand.content.parts and hasattr(cand.content.parts[0], "text"):
                txt = cand.content.parts[0].text
                if txt:
                    return txt.strip()

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
# TURKISH → HIGH-QUALITY ENGLISH PROMPT
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


# ---------------------------------------------------
# UI
# ---------------------------------------------------
inject_custom_css()

st.markdown(
    """
    <div class="adgen-header">
        <div class="adgen-title">AdGen – AI Reklam Üretim Platformu</div>
        <div class="adgen-subtitle">
            KOBİ'ler için tek ekranda reklam metni, görsel tasarım promptu ve gerçek AI görsel üretimi.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

with st.container():
    st.markdown('<div class="adgen-card">', unsafe_allow_html=True)

    # Üst form alanı
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="field-label">Ürün / Hizmet</div>', unsafe_allow_html=True)
        product = st.text_input(label="", placeholder="Örn: El yapımı sabun")

        st.markdown('<div class="field-label">Platform</div>', unsafe_allow_html=True)
        platform = st.selectbox(label="", options=["Instagram", "TikTok", "LinkedIn", "Facebook"])

    with col2:
        st.markdown('<div class="field-label">Hedef Kitle</div>', unsafe_allow_html=True)
        audience = st.text_input(label="", placeholder="Örn: Genç yetişkinler, anneler, kahve severler")

        st.markdown('<div class="field-label">Üslup</div>', unsafe_allow_html=True)
        tone = st.selectbox(label="", options=["Eğlenceli", "Profesyonel", "Samimi", "İkna Edici"])

    st.markdown("---")

    # Butonlar
    c1, c2, c3 = st.columns(3)
    with c1:
        text_clicked = st.button("Reklam Metni Üret", key="btn_text")
    with c2:
        prompt_clicked = st.button("Görsel Tasarım Promptu", key="btn_prompt")
    with c3:
        image_clicked = st.button("Gerçek AI Görseli Üret", key="btn_image")

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
                    st.subheader("Reklam Metni")
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
                    st.subheader("Görsel Tasarım Promptu")
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
                        st.subheader("Üretilen Görsel")
                        st.image(img, use_column_width=True)

                        buf = BytesIO()
                        img.save(buf, format="PNG")
                        st.download_button(
                            "Görseli İndir",
                            buf.getvalue(),
                            "adgen_image.png",
                            "image/png"
                        )
                        st.markdown('</div>', unsafe_allow_html=True)

                    except Exception as e:
                        st.error(f"Görsel üretimi hatası: {e}")

    st.markdown('</div>', unsafe_allow_html=True)

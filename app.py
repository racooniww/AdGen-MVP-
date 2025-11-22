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
# API KEY / MODELLER
# ---------------------------------------------------
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
STABILITY_API_KEY = st.secrets["STABILITY_API_KEY"]

STABILITY_URL = (
    "https://api.stability.ai/v1/generation/"
    "stable-diffusion-xl-1024-v1-0/text-to-image"
)

text_model = genai.GenerativeModel("models/gemini-pro-latest")


# ---------------------------------------------------
# GEMINI SAFE TEXT EXTRACTION
# ---------------------------------------------------
def extract_text_safe(response):
    """Gemini bazen response.text, bazen candidates döndürüyor; güvenli şekilde metni çıkar."""
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
# TR → EN YÜKSEK KALİTE GÖRSEL PROMPT
# ---------------------------------------------------
def translate_to_english_for_image(product, audience, platform, tone):
    base_prompt = f"""
You are an advertising image prompt generator.

Convert the following Turkish inputs into a fully detailed ENGLISH prompt for SDXL
(Stable Diffusion XL) advertising image generation:

Product: {product}
Audience: {audience}
Platform: {platform}
Tone: {tone}

Write ONE single, detailed SDXL image prompt describing:
- Scene & composition
- Background / environment
- Colors & mood
- Lighting
- Camera style / angle

Rules:
- OUTPUT MUST BE ONLY IN ENGLISH.
- Do NOT include any Turkish words.
- It should look like a real ad photo prompt.
"""

    response = text_model.generate_content(base_prompt)
    english = extract_text_safe(response).strip()

    # Eğer hâlâ kısa/boşsa → fallback
    if not english or len(english) < 10:
        english = (
            f"Ultra realistic advertisement photo of {product}, targeted to {audience}, "
            f"soft studio lighting, cinematic background, product-focused composition, "
            f"high detail, 4K."
        )

    # Stability limiti: 1–2000 karakter
    english = english[:1900]
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

    # Üst form alanı (ARTIK fazladan beyaz kutu yok)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="field-label">Ürün / Hizmet</div>', unsafe_allow_html=True)
        product = st.text_input("urun", label_visibility="collapsed",
                                placeholder="Örn: El yapımı sabun")

        st.markdown('<div class="field-label">Platform</div>', unsafe_allow_html=True)
        platform = st.selectbox("platform", ["Instagram", "TikTok", "LinkedIn", "Facebook"],
                                label_visibility="collapsed")

    with col2:
        st.markdown('<div class="field-label">Hedef Kitle</div>', unsafe_allow_html=True)
        audience = st.text_input("kitle", label_visibility="collapsed",
                                 placeholder="Örn: genç yetişkinler, kahve severler")

        st.markdown('<div class="field-label">Üslup</div>', unsafe_allow_html=True)
        tone = st.selectbox("uslup", ["Eğlenceli", "Profesyonel", "Samimi", "İkna Edici"],
                            label_visibility="collapsed")

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
                    english_prompt = translate_to_english_for_image(
                        product, audience, platform, tone
                    )
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

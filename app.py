import streamlit as st
import google.generativeai as genai
import requests
import base64
from io import BytesIO
from PIL import Image

# ---------------------------------------------------
# Streamlit Secrets
# ---------------------------------------------------
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
STABILITY_API_KEY = st.secrets["STABILITY_API_KEY"]

# Stability SDXL endpoint
STABILITY_URL = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"

# Gemini model
text_model = genai.GenerativeModel("models/gemini-pro-latest")


# ---------------------------------------------------
# Stability SDXL IMAGE GENERATION (working, JSON/base64)
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
# PROMPT GENERATION (TEXT)
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
- 2 farklı reklam metni
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

Reklam görseli için detaylı tasarım promptu üret:

1) Kompozisyon
2) Arka plan
3) Işıklandırma
4) Kamera açısı
5) Renk paleti
6) SDXL için tek satırlık İngilizce prompt
"""


# ---------------------------------------------------
# TRANSLATE TO ENGLISH FOR STABILITY (fixes language error)
# ---------------------------------------------------
def translate_to_english_for_image(product, audience, platform, tone):
    prompt = f"""
You are an expert advertising image prompt engineer.

Translate the following Turkish inputs into a high-quality, professional, 100% English prompt
for generating an advertisement image using SDXL.

Product: {product}
Target Audience: {audience}
Platform: {platform}
Tone: {tone}

Instructions:
- Output must be ONLY English.
- Describe composition, background, lighting, camera angle, style, mood.
- End with ONE single SDXL-ready prompt line.
"""

    result = text_model.generate_content(prompt)
    english = result.text.strip()

    # Retry if empty
    if not english or len(english) < 5:
        retry_prompt = f"""
Convert to English advertising image prompt:

Product: {product}
Audience: {audience}

ONLY output one English SDXL prompt.
"""
        retry = text_model.generate_content(retry_prompt).text.strip()
        english = retry

    # Final fallback
    if not english or len(english) < 5:
        english = (
            f"Professional advertisement photo of {product}, targeted to {audience}, "
            f"studio lighting, ultra realistic, 4K, clean background."
        )

    return english


# ---------------------------------------------------
# STREAMLIT UI
# ---------------------------------------------------
st.title("🎯 AdGen — AI Reklam Metni + Görsel + Prompt Üretici")

product = st.text_input("🛍 Ürün / Hizmet:")
audience = st.text_input("🎯 Hedef Kitle:")
platform = st.selectbox("📱 Platform:", ["Instagram", "TikTok", "LinkedIn", "Facebook"])
tone = st.selectbox("🎨 Üslup:", ["Eğlenceli", "Profesyonel", "Samimi", "İkna Edici"])


# ---------------------------------------------------
# GENERATE TEXT AD
# ---------------------------------------------------
if st.button("📝 Reklam Metni Üret"):
    if not product or not audience:
        st.warning("⚠ Lütfen tüm alanları doldurun.")
    else:
        with st.spinner("Metin üretiliyor..."):
            try:
                prompt = build_text_prompt(product, audience, platform, tone)
                response = text_model.generate_content(prompt)
                st.subheader("📌 Reklam Metni")
                st.write(response.text)
            except Exception as e:
                st.error(f"Hata: {e}")


# ---------------------------------------------------
# GENERATE VISUAL DESIGN PROMPT
# ---------------------------------------------------
if st.button("🎨 Görsel Tasarım Promptu Üret"):
    if not product or not audience:
        st.warning("⚠ Lütfen tüm alanları doldurun.")
    else:
        with st.spinner("Prompt üretiliyor..."):
            try:
                prompt = build_image_prompt(product, audience, platform, tone)
                response = text_model.generate_content(prompt)
                st.subheader("🖼 Tasarım Promptu")
                st.write(response.text)
            except Exception as e:
                st.error(f"Hata: {e}")


# ---------------------------------------------------
# GENERATE REAL IMAGE (STABILITY SDXL)
# ---------------------------------------------------
if st.button("🖼 Gerçek AI Görseli Üret"):
    if not product or not audience:
        st.warning("⚠ Lütfen tüm alanları doldurun.")
    else:

        # 1 — Translate to English
        with st.spinner("İngilizce prompt hazırlanıyor..."):
            try:
                english_prompt = translate_to_english_for_image(product, audience, platform, tone)
            except Exception as e:
                st.error(f"İngilizce prompt oluşturulamadı: {e}")
                english_prompt = None

        if english_prompt:
            # 2 — Generate image
            with st.spinner("Stability SDXL ile görsel üretiliyor..."):
                try:
                    img = generate_image_stability(english_prompt)
                    st.subheader("🖼 Üretilen Görsel")
                    st.image(img, use_column_width=True)

                    # download image
                    img_buf = BytesIO()
                    img.save(img_buf, format="PNG")
                    st.download_button(
                        label="📥 Görseli İndir",
                        data=img_buf.getvalue(),
                        file_name="adgen_image.png",
                        mime="image/png"
                    )

                except Exception as e:
                    st.error(f"Görsel üretimi hatası: {e}")

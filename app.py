import streamlit as st
import google.generativeai as genai
import requests
from io import BytesIO
from PIL import Image


# ---------------------------------------------------
# API KEYS (Streamlit Secrets)
# ---------------------------------------------------
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
STABILITY_API_KEY = st.secrets["STABILITY_API_KEY"]

# Stability AI endpoint (gerçek görsel)
STABILITY_URL = "https://api.stability.ai/v2beta/stable-image/generate/core"

# Gemini metin modeli
text_model = genai.GenerativeModel("models/gemini-pro-latest")


# ---------------------------------------------------
# STABILITY.AI GÖRSEL ÜRETİMİ (KESİN ÇALIŞAN)
# ---------------------------------------------------
def generate_image_stability(prompt):

    headers = {
        "Authorization": f"Bearer {STABILITY_API_KEY}",
        "Accept": "image/png"   # PNG çıktısı almak için zorunlu
    }

    # Form-data alanları
    data = {
        "prompt": prompt,
        "aspect_ratio": "1:1",
        "output_format": "png"
    }

    # Multipart'ı tetiklemek için boş file alanı zorunlu
    files = {
        "none": (None, "")
    }

    response = requests.post(
        STABILITY_URL,
        headers=headers,
        data=data,
        files=files
    )

    if response.status_code != 200:
        raise ValueError(f"Stability API Hatası: {response.text}")

    # PNG binary olarak döner
    return Image.open(BytesIO(response.content))


# ---------------------------------------------------
# PROMPT OLUŞTURUCU FONKSİYONLAR (GEMINI)
# ---------------------------------------------------
def build_text_prompt(product, audience, platform, tone):
    return f"""
Sen bir dijital pazarlama uzmanısın.

Ürün: {product}
Hedef Kitle: {audience}
Platform: {platform}
Üslup: {tone}

Aşağıdaki formatta reklam içeriği oluştur:

1) 3 kısa başlık
2) 2 farklı reklam metni (A/B testi)
3) Kampanya sloganı
4) 8 hashtag
"""


def build_image_prompt(product, audience, platform, tone):
    return f"""
Sen üst düzey bir reklam tasarımcısın.

Ürün: {product}
Hedef Kitle: {audience}
Platform: {platform}
Üslup: {tone}

Profesyonel bir reklam görseli için aşağıdaki formatta detaylı tasarım promptu üret:

1) Kompozisyon (ürün sahnede nerede?)
2) Arka plan (renk / doku / tema)
3) Işıklandırma (soft light, studio light)
4) Kamera açısı (macro / close-up / 45 degree)
5) Renk paleti (minimal / canlı / pastel)
6) SDXL – Midjourney – DALL·E için tek satırlık İngilizce prompt
"""


# ---------------------------------------------------
# STREAMLIT ARAYÜZÜ
# ---------------------------------------------------
st.title("🎯 AdGen – AI Reklam Metni + Prompt + Gerçek Görsel Üretici")

product = st.text_input("🛍 Ürün / Hizmet:")
audience = st.text_input("🎯 Hedef Kitle:")
platform = st.selectbox("📱 Platform:", ["Instagram", "TikTok", "LinkedIn", "Facebook"])
tone = st.selectbox("🎨 Üslup:", ["Eğlenceli", "Profesyonel", "Samimi", "İkna Edici"])


# ---------------------------------------------------
# 1) REKLAM METNİ (GEMINI)
# ---------------------------------------------------
if st.button("📝 Reklam Metni Üret"):
    if not product or not audience:
        st.warning("⚠ Lütfen tüm alanları doldurun.")
    else:
        with st.spinner("Metin üretiliyor..."):
            prompt = build_text_prompt(product, audience, platform, tone)
            response = text_model.generate_content(prompt)
            st.subheader("📌 Üretilen Reklam Metni")
            st.write(response.text)


# ---------------------------------------------------
# 2) GÖRSEL TASARIM PROMPTU (GEMINI)
# ---------------------------------------------------
if st.button("🎨 Görsel Tasarım Promptu Üret"):
    if not product or not audience:
        st.warning("⚠ Lütfen tüm alanları doldurun.")
    else:
        with st.spinner("Prompt üretiliyor..."):
            prompt = build_image_prompt(product, audience, platform, tone)
            response = text_model.generate_content(prompt)
            st.subheader("🖼 Görsel Tasarım Fikri")
            st.write(response.text)


# ---------------------------------------------------
# 3) GERÇEK GÖRSEL ÜRETİMİ (STABILITY AI)
# ---------------------------------------------------
if st.button("🖼 Gerçek Reklam Görseli Üret (AI – Stability AI)"):
    if not product or not audience:
        st.warning("⚠ Lütfen tüm alanları doldurun.")
    else:

        sd_prompt = (
            f"{product}, {audience} kitlesine yönelik profesyonel bir reklam fotoğrafı. "
            f"Studio lighting, ultra realistic, 4K, product shot, clean background."
        )

        with st.spinner("Gerçek AI görseli üretiliyor..."):
            try:
                img = generate_image_stability(sd_prompt)

                st.subheader("🖼 AI Tarafından Üretilen Görsel")
                st.image(img, use_column_width=True)

                # İndirme
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                st.download_button(
                    "📥 Görseli İndir",
                    buffer.getvalue(),
                    "adgen_reklam.png",
                    "image/png"
                )

            except Exception as e:
                st.error(f"Görsel üretimi hatası: {e}")

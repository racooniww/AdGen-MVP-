import streamlit as st
import google.generativeai as genai
import requests
import base64
from io import BytesIO
from PIL import Image

# ---------------------------------------------------
# API KEY'LER (Streamlit Secrets)
# ---------------------------------------------------
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
STABILITY_API_KEY = st.secrets["STABILITY_API_KEY"]

# Stability AI görsel üretim endpointi (Çalışan)
STABILITY_URL = "https://api.stability.ai/v2beta/stable-image/generate/core"

# Gemini metin modeli
text_model = genai.GenerativeModel("models/gemini-pro-latest")


# ---------------------------------------------------
# STABILITY AI GÖRSEL ÜRETİM FONKSİYONU
# ---------------------------------------------------
def generate_image_stability(prompt):
    headers = {
        "Authorization": f"Bearer {STABILITY_API_KEY}",
        "Accept": "application/json"
    }

    payload = {
        "prompt": prompt,
        "output_format": "png",
        "aspect_ratio": "1:1"
    }

    response = requests.post(STABILITY_URL, headers=headers, json=payload)

    if response.status_code != 200:
        raise ValueError(f"Stability API Hatası: {response.text}")

    data = response.json()
    image_base64 = data["image"]
    return Image.open(BytesIO(base64.b64decode(image_base64)))


# ---------------------------------------------------
# PROMPT OLUŞTURMA FONKSİYONLARI
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
2) 2 farklı reklam metni (A/B)
3) Kampanya sloganı
4) 8 hashtag
"""


def build_image_prompt(product, audience, platform, tone):
    return f"""
Sen üst düzey bir reklam tasarımcısısın.

Ürün: {product}
Hedef Kitle: {audience}
Platform: {platform}
Üslup: {tone}

Profesyonel bir reklam görseli için aşağıdaki formatta detaylı bir prompt oluştur:

1) Kompozisyon
2) Arka plan
3) Işıklandırma
4) Kamera açısı
5) Renk paleti
6) Midjourney / DALL·E / SDXL için tek satırlık İngilizce prompt
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
# 1) METİN ÜRETİMİ (GEMINI)
# ---------------------------------------------------
if st.button("📝 Reklam Metni Üret"):
    if not product or not audience:
        st.warning("⚠ Lütfen tüm alanları doldurun.")
    else:
        with st.spinner("Metin üretiliyor..."):
            prompt = build_text_prompt(product, audience, platform, tone)
            response = text_model.generate_content(prompt)
            st.subheader("📌 Reklam Metni")
            st.write(response.text)


# ---------------------------------------------------
# 2) GÖRSEL PROMPT ÜRETİMİ (GEMINI)
# ---------------------------------------------------
if st.button("🎨 Görsel Tasarım Promptu (Gemini)"):
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
if st.button("🖼 Gerçek Reklam Görseli Üret (AI)"):
    if not product or not audience:
        st.warning("⚠ Lütfen tüm alanları doldurun.")
    else:
        sd_prompt = f"""
        {product} için {audience} kitlesine uygun profesyonel bir reklam fotoğrafı.
        Studio lighting, ultra realistic, 4K, product shot, clean background.
        """

        with st.spinner("Görsel üretiliyor..."):
            try:
                img = generate_image_stability(sd_prompt)
                st.subheader("🖼 AI Üretilen Reklam Görseli")
                st.image(img, use_column_width=True)

                # İndirme butonu
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                st.download_button(
                    "📥 Görseli İndir",
                    buffer.getvalue(),
                    "adgen_gorsel.png",
                    "image/png"
                )

            except Exception as e:
                st.error(f"Görsel üretimi hatası: {e}")

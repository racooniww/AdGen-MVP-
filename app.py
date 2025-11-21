import streamlit as st
import google.generativeai as genai
import requests
import base64
from io import BytesIO
from PIL import Image

# ---------------------------------------------------
# API KEYS (Streamlit Secrets)
# ---------------------------------------------------
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
STABILITY_API_KEY = st.secrets["STABILITY_API_KEY"]

# Stability AI model endpoint
STABILITY_URL = "https://api.stability.ai/v2beta/stable-image/generate/core"

# Gemini text model
text_model = genai.GenerativeModel("models/gemini-pro-latest")


# ---------------------------------------------------
# 1) STABILITY.AI GÖRSEL ÜRETİM FONKSİYONU (KESİN ÇALIŞAN)
# ---------------------------------------------------
def generate_image_stability(prompt):
    headers = {
        "Authorization": f"Bearer {STABILITY_API_KEY}"
    }

    form_data = {
        "prompt": prompt,
        "output_format": "png",
        "aspect_ratio": "1:1"
    }

    # multipart form-data göndermek için files boş bile olsa şart
    response = requests.post(
        STABILITY_URL,
        headers=headers,
        data=form_data,
        files={}
    )

    if response.status_code != 200:
        raise ValueError(f"Stability API Hatası: {response.text}")

    # PNG görüntü olarak dönüyor (base64 değil!)
    return Image.open(BytesIO(response.content))


# ---------------------------------------------------
# 2) PROMPT OLUŞTURMA FONKSİYONLARI (GEMINI)
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
Sen üst düzey bir reklam tasarımcısısın.

Ürün: {product}
Hedef Kitle: {audience}
Platform: {platform}
Üslup: {tone}

Profesyonel bir reklam görseli için aşağıdaki formatta detaylı bir tasarım promptu oluştur:

1) Kompozisyon (ürün nasıl konumlanacak?)
2) Arka plan (renk, doku, tema)
3) Işıklandırma (soft light, dramatic light vs.)
4) Kamera açısı (macro, close-up, 45 derece vs.)
5) Renk paleti (minimal, canlı renkler vs.)
6) SDXL / Midjourney / DALL·E için tek satırlık İngilizce prompt
"""


# ---------------------------------------------------
# 3) STREAMLIT ARAYÜZÜ
# ---------------------------------------------------
st.title("🎯 AdGen – AI Reklam Metni + Prompt + Gerçek Görsel Üretici")

product = st.text_input("🛍 Ürün / Hizmet:")
audience = st.text_input("🎯 Hedef Kitle:")
platform = st.selectbox("📱 Platform:", ["Instagram", "TikTok", "LinkedIn", "Facebook"])
tone = st.selectbox("🎨 Üslup:", ["Eğlenceli", "Profesyonel", "Samimi", "İkna Edici"])


# ---------------------------------------------------
# 4) METİN ÜRETİMİ (GEMINI)
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
# 5) GÖRSEL TASARIM PROMPTU (GEMINI)
# ---------------------------------------------------
if st.button("🎨 Görsel Tasarım Promptu Üret (Gemini)"):
    if not product or not audience:
        st.warning("⚠ Lütfen tüm alanları doldurun.")
    else:
        with st.spinner("Prompt üretiliyor..."):
            prompt = build_image_prompt(product, audience, platform, tone)
            response = text_model.generate_content(prompt)
            st.subheader("🖼 Görsel Tasarım Fikri / Prompt")
            st.write(response.text)


# ---------------------------------------------------
# 6) GERÇEK GÖRSEL ÜRETİMİ (STABILITY AI)
# ---------------------------------------------------
if st.button("🖼 Gerçek Reklam Görseli Üret (AI – Stability AI)"):
    if not product or not audience:
        st.warning("⚠ Lütfen tüm alanları doldurun.")
    else:
        sd_prompt = (
            f"{product} için {audience} kitlesine uygun profesyonel reklam fotoğrafı, "
            f"studio lighting, ultra realistic, 4K, product shot, clean background."
        )

        with st.spinner("Gerçek AI görseli üretiliyor..."):
            try:
                img = generate_image_stability(sd_prompt)

                st.subheader("🖼 AI ile Üretilen Reklam Görseli")
                st.image(img, use_column_width=True)

                # İndirme
                buffer = BytesIO()
                img.save(buffer, format="PNG")

                st.download_button(
                    label="📥 Görseli İndir",
                    data=buffer.getvalue(),
                    file_name="adgen_gorsel.png",
                    mime="image/png"
                )

            except Exception as e:
                st.error(f"Görsel üretimi hatası: {e}")

import streamlit as st
import google.generativeai as genai
import requests
import base64
from io import BytesIO
from PIL import Image


# ---------------------------------------------------
# SECRETS (Streamlit Cloud)
# ---------------------------------------------------
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
STABILITY_API_KEY = st.secrets["STABILITY_API_KEY"]


# ---------------------------------------------------
# 1) STABILITY v1 — Base64 JSON Görsel Üretimi
#    (Streamlit Cloud ile %100 uyumlu)
# ---------------------------------------------------
def generate_image_stability(prompt):
    url = "https://api.stability.ai/v1/generation/stable-diffusion-512-v2-1/text-to-image"

    headers = {
        "Authorization": f"Bearer {STABILITY_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
        "text_prompts": [{"text": prompt}],
        "cfg_scale": 7,
        "height": 512,
        "width": 512,
        "samples": 1,
        "steps": 30
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        raise ValueError(f"Stability API Hatası: {response.text}")

    # Base64 → Görsel
    data = response.json()
    image_base64 = data["artifacts"][0]["base64"]
    image_bytes = base64.b64decode(image_base64)

    return Image.open(BytesIO(image_bytes))


# ---------------------------------------------------
# 2) Gemini Input Prompt Fonksiyonları
# ---------------------------------------------------
def build_text_prompt(product, audience, platform, tone):
    return f"""
Sen bir dijital pazarlama uzmanısın.

Ürün: {product}
Hedef kitle: {audience}
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
Hedef kitle: {audience}
Platform: {platform}
Üslup: {tone}

Profesyonel bir reklam görseli için detaylı tasarım promptu oluştur:

1) Kompozisyon
2) Arka plan
3) Işıklandırma
4) Kamera açısı
5) Renk paleti
6) SDXL – Midjourney – DALL·E için tek satırlık İngilizce prompt
"""


# ---------------------------------------------------
# 3) Gemini Metin Modeli
# ---------------------------------------------------
text_model = genai.GenerativeModel("models/gemini-pro-latest")


# ---------------------------------------------------
# 4) Streamlit Arayüzü
# ---------------------------------------------------
st.title("🎯 AdGen – AI Reklam İçeriği + Prompt + Görsel Üretici")

product = st.text_input("🛍 Ürün / Hizmet:")
audience = st.text_input("🎯 Hedef Kitle:")
platform = st.selectbox("📱 Platform:", ["Instagram", "TikTok", "LinkedIn", "Facebook"])
tone = st.selectbox("🎨 Üslup:", ["Eğlenceli", "Profesyonel", "Samimi", "İkna Edici"])


# ---------------------------------------------------
# 5) Reklam Metni (Gemini)
# ---------------------------------------------------
if st.button("📝 Reklam Metni Üret"):
    if not product or not audience:
        st.warning("⚠ Lütfen tüm alanları doldurun.")
    else:
        with st.spinner("Metin üretiliyor..."):
            try:
                prompt = build_text_prompt(product, audience, platform, tone)
                response = text_model.generate_content(prompt)
                st.subheader("📌 Üretilen Reklam Metni")
                st.write(response.text)
            except Exception as e:
                st.error(f"Metin üretimi hatası: {e}")


# ---------------------------------------------------
# 6) Görsel Tasarım Promptu (Gemini)
# ---------------------------------------------------
if st.button("🎨 Görsel Tasarım Promptu Üret"):
    if not product or not audience:
        st.warning("⚠ Lütfen tüm alanları doldurun.")
    else:
        with st.spinner("Prompt üretiliyor..."):
            try:
                prompt = build_image_prompt(product, audience, platform, tone)
                response = text_model.generate_content(prompt)
                st.subheader("🖼 Görsel Tasarım Promptu")
                st.write(response.text)
            except Exception as e:
                st.error(f"Prompt üretimi hatası: {e}")


# ---------------------------------------------------
# 7) Gerçek AI Görsel Üretimi (Stability)
# ---------------------------------------------------
if st.button("🖼 Gerçek AI Görseli Üret"):
    if not product or not audience:
        st.warning("⚠ Lütfen tüm alanları doldurun.")
    else:
        sd_prompt = (
            f"{product} için {audience} hedef kitlesine yönelik "
            "profesyonel reklam fotoğrafı. Studio lighting, ultra realistic, "
            "4K product shot."
        )

        with st.spinner("AI görseli üretiliyor..."):
            try:
                img = generate_image_stability(sd_prompt)

                st.subheader("🖼 Üretilen Reklam Görseli")
                st.image(img, use_column_width=True)

                # İndirilebilir dosya
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

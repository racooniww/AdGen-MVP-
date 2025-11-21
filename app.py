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


# ---------------------------------------------------
# Stability SDXL 1024 MODEL — %100 ÇALIŞIR
# ---------------------------------------------------
def generate_image_stability(prompt):
    url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"

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

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        raise ValueError(f"Stability API Hatası: {response.text}")

    # Base64 → PNG görüntüye çevir
    data = response.json()
    image_base64 = data["artifacts"][0]["base64"]
    image_bytes = base64.b64decode(image_base64)
    return Image.open(BytesIO(image_bytes))


# ---------------------------------------------------
# Gemini Prompt / Metin Fonksiyonları
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
Hedef Kitle: {audience}
Platform: {platform}
Üslup: {tone}

Reklam görseli için detaylı tasarım promptu üret:

1. Kompozisyon
2. Arka plan (renk/doku)
3. Işıklandırma (soft/studio light)
4. Kamera açısı
5. Renk paleti
6. SDXL/DALL·E/Midjourney için tek İngilizce prompt
"""


# Gemini modeli
text_model = genai.GenerativeModel("models/gemini-pro-latest")


# ---------------------------------------------------
# Streamlit Arayüzü
# ---------------------------------------------------
st.title("🎯 AdGen — AI Reklam Metni + Prompt + Görsel Üretici")

product = st.text_input("🛍 Ürün / Hizmet:")
audience = st.text_input("🎯 Hedef Kitle:")
platform = st.selectbox("📱 Platform:", ["Instagram", "TikTok", "LinkedIn", "Facebook"])
tone = st.selectbox("🎨 Üslup:", ["Eğlenceli", "Profesyonel", "Samimi", "İkna Edici"])


# ---------------------------------------------------
# Reklam Metni (Gemini)
# ---------------------------------------------------
if st.button("📝 Reklam Metni Üret"):
    if not product or not audience:
        st.warning("⚠ Lütfen gerekli bilgileri doldurun.")
    else:
        with st.spinner("Reklam metni üretiliyor..."):
            try:
                prompt = build_text_prompt(product, audience, platform, tone)
                result = text_model.generate_content(prompt)
                st.subheader("📌 Reklam Metni")
                st.write(result.text)
            except Exception as e:
                st.error(f"Metin üretimi hatası: {e}")


# ---------------------------------------------------
# Görsel Tasarım Promptu (Gemini)
# ---------------------------------------------------
if st.button("🎨 Görsel Tasarım Promptu Üret"):
    if not product or not audience:
        st.warning("⚠ Lütfen gerekli bilgileri doldurun.")
    else:
        with st.spinner("Prompt üretiliyor..."):
            try:
                prompt = build_image_prompt(product, audience, platform, tone)
                result = text_model.generate_content(prompt)
                st.subheader("🖼 Görsel Tasarım Promptu")
                st.write(result.text)
            except Exception as e:
                st.error(f"Prompt üretimi hatası: {e}")


# ---------------------------------------------------
# Gerçek Görsel Üretimi (Stability SDXL 1024)
# ---------------------------------------------------
if st.button("🖼 Gerçek AI Görseli Üret"):
    if not product or not audience:
        st.warning("⚠ Lütfen gerekli bilgileri doldurun.")
    else:
        sd_prompt = (
            f"{product} için {audience} hedef kitlesine yönelik "
            "profesyonel reklam fotoğrafı, ultra realistic, studio lighting, 4K product shot."
        )

        with st.spinner("Görsel üretiliyor..."):
            try:
                img = generate_image_stability(sd_prompt)
                st.subheader("🖼 Üretilen Görsel")
                st.image(img, use_column_width=True)

                # indirilebilir dosya
                buf = BytesIO()
                img.save(buf, format="PNG")
                st.download_button(
                    "📥 Görseli İndir",
                    buf.getvalue(),
                    "adgen_reklam.png",
                    "image/png"
                )

            except Exception as e:
                st.error(f"Görsel üretimi hatası: {e}")

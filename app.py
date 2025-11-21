import streamlit as st
import google.generativeai as genai
import requests
from io import BytesIO
from PIL import Image

# ============================================================
# API Keys (Streamlit Secrets)
# ============================================================

# Gemini API
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# HuggingFace Stable Diffusion XL (çalışan model)
HF_API_URL = "https://router.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"


# ============================================================
# Modeller
# ============================================================

# Gemini metin modeli
text_model = genai.GenerativeModel("models/gemini-pro-latest")


# ============================================================
# Yardımcı Fonksiyonlar
# ============================================================

def generate_image_hf(prompt):
    """
    HuggingFace SDXL ile gerçek görsel üretir.
    """
    headers = {
        "Authorization": f"Bearer {st.secrets['HF_API_KEY']}",
        "Content-Type": "application/json"
    }

    response = requests.post(HF_API_URL, headers=headers, json={"inputs": prompt})

    # Model yeni yükleniyorsa bekleme hatası döner
    if response.status_code == 503:
        raise ValueError("Model yükleniyor. 10 saniye sonra tekrar deneyin.")

    if response.status_code != 200:
        raise ValueError(f"HuggingFace API Hatası: {response.text}")

    return Image.open(BytesIO(response.content))


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


def build_image_prompt_prompt(product, audience, platform, tone):
    return f"""
Sen üst düzey bir reklam tasarımcısın.

Ürün: {product}
Hedef Kitle: {audience}
Platform: {platform}
Üslup: {tone}

Profesyonel bir reklam görseli için aşağıdaki formatta detaylı bir tasarım promptu oluştur:

1) Kompozisyon
2) Arka plan
3) Işıklandırma
4) Kamera açısı
5) Renk paleti
6) Midjourney, DALL·E, SDXL için tek satırlık İngilizce prompt
"""


# ============================================================
# Streamlit Arayüzü
# ============================================================

st.title("🎯 AdGen – AI Reklam Metni + Prompt + Gerçek Görsel Üretici")

product = st.text_input("🛍 Ürün / Hizmet:")
audience = st.text_input("🎯 Hedef Kitle:")
platform = st.selectbox("📱 Platform:", ["Instagram", "TikTok", "LinkedIn", "Facebook"])
tone = st.selectbox("🎨 Üslup:", ["Eğlenceli", "Profesyonel", "Samimi", "İkna Edici"])


# ============================================================
# Reklam Metni Üretimi (Gemini)
# ============================================================

if st.button("📝 Reklam Metni Üret"):
    if not product or not audience:
        st.warning("⚠ Lütfen ürün ve hedef kitleyi doldurun.")
    else:
        with st.spinner("Metin üretiliyor..."):
            prompt = build_text_prompt(product, audience, platform, tone)
            response = text_model.generate_content(prompt)
            st.subheader("📌 Üretilen Reklam Metni")
            st.write(response.text)


# ============================================================
# Görsel PROMPT üretimi (Gemini)
# ============================================================

if st.button("🎨 Görsel Prompt (Gemini) Üret"):
    if not product or not audience:
        st.warning("⚠ Lütfen ürün ve hedef kitleyi doldurun.")
    else:
        with st.spinner("Görsel prompt üretiliyor..."):
            prompt = build_image_prompt_prompt(product, audience, platform, tone)
            response = text_model.generate_content(prompt)
            st.subheader("🖼 Görsel Tasarım Fikri / Prompt")
            st.write(response.text)


# ============================================================
# Gerçek Görsel Üretimi (HuggingFace SDXL)
# ============================================================

if st.button("🖼 Gerçek Reklam Görseli Üret (AI)"):
    if not product or not audience:
        st.warning("⚠ Lütfen ürün ve hedef kitleyi doldurun.")
    else:
        sd_prompt = f"""
        {product}, {audience} için profesyonel bir reklam fotoğrafı.
        Clean background, modern aesthetic, ultra high detail,
        sharp focus, 8k, studio lighting, realistic, product shot.
        """

        with st.spinner("Gerçek AI görseli üretiliyor..."):
            try:
                img = generate_image_hf(sd_prompt)

                st.subheader("🖼 AI ile Üretilen Reklam Görseli")
                st.image(img, use_column_width=True)

                # İndirme
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                st.download_button(
                    label="📥 Görseli İndir",
                    data=buffer.getvalue(),
                    file_name="adgen_reklam_gorsel.png",
                    mime="image/png"
                )

            except Exception as e:
                st.error(f"Görsel üretilirken hata oluştu:\n{e}")

import streamlit as st
import google.generativeai as genai
import requests
from io import BytesIO
from PIL import Image

# -------------------------------------------------------
# Gemini API (Streamlit Secrets)
# -------------------------------------------------------
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Metin modeli
text_model = genai.GenerativeModel("models/gemini-pro-latest")

# HuggingFace ücretsiz görsel modeli
HF_API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"


def generate_image_hf(prompt):
    """HuggingFace'te ücretsiz gerçek görsel üretir."""
    response = requests.post(
        HF_API_URL,
        headers={"Content-Type": "application/json"},
        json={"inputs": prompt}
    )

    if response.status_code != 200:
        raise ValueError(f"HuggingFace API Hatası: {response.text}")

    image_bytes = response.content
    return Image.open(BytesIO(image_bytes))


# -------------------------------------------------------
# Streamlit arayüzü
# -------------------------------------------------------
st.title("🎯 AdGen – AI Reklam Metni + Görsel Prompt + Gerçek Görsel Üretici")

product = st.text_input("🛍 Ürün / Hizmet:")
audience = st.text_input("🎯 Hedef Kitle:")
platform = st.selectbox("📱 Platform:", ["Instagram", "TikTok", "LinkedIn", "Facebook"])
tone = st.selectbox("🎨 Üslup:", ["Eğlenceli", "Profesyonel", "Samimi", "İkna Edici"])


# -------------------------------------------------------
# PROMPT OLUŞTURMA (GEMINI)
# -------------------------------------------------------
def build_image_prompt(product, audience, platform, tone):
    return f"""
Sen bir reklam tasarımcısısın.
Aşağıdaki bilgilerle profesyonel bir reklam görseli için detaylı tasarım fikri oluştur:

- Ürün: {product}
- Hedef Kitle: {audience}
- Platform: {platform}
- Üslup: {tone}

Aşağıdaki formatta cevap ver:

1) Kompozisyon tarifi  
2) Arka plan tarifi  
3) Işıklandırma  
4) Renk paleti  
5) Kamera açısı  
6) Midjourney / DALL-E için tek satır İngilizce prompt  
"""

def build_text_prompt(product, audience, platform, tone):
    return f"""
Sen bir dijital pazarlama uzmanısın.  

Ürün: {product}  
Hedef Kitle: {audience}  
Platform: {platform}  
Üslup: {tone}  

Aşağıdaki formatta reklam içeriği üret:

1) 3 kısa başlık  
2) 2 farklı reklam metni  
3) Kampanya sloganı  
4) 8 hashtag  
"""


# -------------------------------------------------------
# 1️⃣ METİN ÜRETİMİ
# -------------------------------------------------------
if st.button("📝 Reklam Metni Üret"):
    if not product or not audience:
        st.warning("⚠ Lütfen ürün ve hedef kitleyi giriniz.")
    else:
        with st.spinner("Metin üretiliyor..."):
            prompt = build_text_prompt(product, audience, platform, tone)
            response = text_model.generate_content(prompt)
            st.subheader("📌 Üretilen Reklam Metni")
            st.write(response.text)


# -------------------------------------------------------
# 2️⃣ GÖRSEL PROMPT ÜRETİMİ (GEMINI)
# -------------------------------------------------------
if st.button("🎨 Görsel Promptu Üret (Gemini)"):
    if not product or not audience:
        st.warning("⚠ Lütfen ürün ve hedef kitleyi giriniz.")
    else:
        with st.spinner("Görsel prompt üretiliyor..."):
            prompt = build_image_prompt(product, audience, platform, tone)
            response = text_model.generate_content(prompt)
            st.subheader("🖼 Görsel Tasarım Fikri / Prompt")
            st.write(response.text)



# -------------------------------------------------------
# 3️⃣ GERÇEK GÖRSEL ÜRET (HUGGINGFACE)
# -------------------------------------------------------
if st.button("🖼 Gerçek Reklam Görseli Üret (AI)"):
    if not product or not audience:
        st.warning("⚠ Lütfen ürün ve hedef kitleyi giriniz.")
    else:
        with st.spinner("Gerçek görsel üretiliyor... (Stable Diffusion)"):
            try:
                # HuggingFace görsel prompt'u için daha net metin:
                sd_prompt = f"{product}, {audience} hedef kitlesine yönelik, professional advertising photo, modern, clean, HD, product focus, studio lighting"

                img = generate_image_hf(sd_prompt)

                st.image(img, caption="🖼 AI ile Üretilen Reklam Görseli", use_column_width=True)

                # indirilebilir hale getirme
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                st.download_button(
                    label="📥 Görseli İndir",
                    data=buffer.getvalue(),
                    file_name="adgen_reklam_gorsel.png",
                    mime="image/png"
                )
            except Exception as e:
                st.error(f"Görsel üretilirken hata oluştu: {e}")

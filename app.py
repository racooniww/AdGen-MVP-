import streamlit as st
import google.generativeai as genai
import requests
from io import BytesIO
from PIL import Image


# ============================================================
# 1) API KEY KONFİGÜRASYONLARI  (Streamlit Secrets)
# ============================================================

# Gemini API Key
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# HuggingFace API URL
HF_API_URL = "https://router.huggingface.co/models/runwayml/stable-diffusion-v1-5"


# ============================================================
# 2) MODELLER
# ============================================================

# Gemini metin modeli
text_model = genai.GenerativeModel("models/gemini-pro-latest")


# ============================================================
# 3) YARDIMCI FONKSİYONLAR
# ============================================================

def generate_image_hf(prompt):
    """
    HuggingFace Stable Diffusion ile gerçek görsel üretir.
    """
    headers = {
        "Authorization": f"Bearer {st.secrets['HF_API_KEY']}",
        "Content-Type": "application/json"
    }

    payload = {"inputs": prompt}

    response = requests.post(HF_API_URL, headers=headers, json=payload)

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
4) 8 platforma uygun hashtag
"""


def build_image_prompt_prompt(product, audience, platform, tone):
    return f"""
Sen bir reklam tasarımcısın.

Ürün: {product}
Hedef Kitle: {audience}
Platform: {platform}
Üslup: {tone}

Aşağıdaki formatta profesyonel bir reklam görseli tarifi oluştur:

1) Kompozisyon
2) Arka plan
3) Işıklandırma
4) Kamera açısı
5) Renk paleti
6) Midjourney / DALL·E için tek satırlık İngilizce prompt
"""


# ============================================================
# 4) STREAMLIT ARAYÜZÜ
# ============================================================

st.title("🎯 AdGen – AI Reklam Metni + Prompt + Gerçek Görsel Üretici")

product = st.text_input("🛍 Ürün / Hizmet:")
audience = st.text_input("🎯 Hedef Kitle:")
platform = st.selectbox("📱 Platform:", ["Instagram", "TikTok", "LinkedIn", "Facebook"])
tone = st.selectbox("🎨 Üslup:", ["Eğlenceli", "Profesyonel", "Samimi", "İkna Edici"])


# ============================================================
# 5) METİN ÜRETİMİ
# ============================================================

if st.button("📝 Reklam Metni Üret"):
    if not product or not audience:
        st.warning("⚠ Lütfen ürün ve hedef kitleyi girin.")
    else:
        with st.spinner("Metin üretiliyor..."):
            prompt = build_text_prompt(product, audience, platform, tone)
            response = text_model.generate_content(prompt)
            st.subheader("📌 Üretilen Reklam Metni")
            st.write(response.text)


# ============================================================
# 6) GÖRSEL PROMPT (GEMINI)
# ============================================================

if st.button("🎨 Görsel Prompt (Gemini) Üret"):
    if not product or not audience:
        st.warning("⚠ Lütfen ürün ve hedef kitleyi girin.")
    else:
        with st.spinner("Prompt üretiliyor..."):
            prompt = build_image_prompt_prompt(product, audience, platform, tone)
            response = text_model.generate_content(prompt)
            st.subheader("🖼 Görsel Tasarım Fikri / Prompt")
            st.write(response.text)
            st.info("Bu prompt'u Midjourney, DALL·E veya Leonardo.ai gibi görsel üreticilerde kullanabilirsin.")


# ============================================================
# 7) GERÇEK GÖRSEL ÜRETİMİ (HUGGINGFACE)
# ============================================================

if st.button("🖼 Gerçek Reklam Görseli Üret (AI)"):
    if not product or not audience:
        st.warning("⚠ Lütfen ürün ve hedef kitleyi girin.")
    else:
        sd_prompt = f"{product}, {audience} hedef kitlesine yönelik, professional advertisement photo, clean background, modern style, HD, sharp focus, studio lighting"

        with st.spinner("Gerçek AI görseli üretiliyor..."):
            try:
                img = generate_image_hf(sd_prompt)

                st.subheader("🖼 AI ile Üretilen Reklam Görseli")
                st.image(img, use_column_width=True)

                # indirme
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

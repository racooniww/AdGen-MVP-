import streamlit as st
import google.generativeai as genai
import requests
import base64
from io import BytesIO
from PIL import Image

# ---------------------------------------------------
# API KEYS (Streamlit Secrets)
# ---------------------------------------------------
# Streamlit Secrets içinde şunlar olmalı:
# GEMINI_API_KEY = "..."
# STABILITY_API_KEY = "..."
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
STABILITY_API_KEY = st.secrets["STABILITY_API_KEY"]

# Stability SDXL 1024 model endpoint
STABILITY_URL = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"

# Gemini metin modeli
text_model = genai.GenerativeModel("models/gemini-pro-latest")


# ---------------------------------------------------
# 1) STABILITY SDXL GÖRSEL ÜRETİMİ (JSON + base64)
# ---------------------------------------------------
def generate_image_stability(prompt: str) -> Image.Image:
    """
    Stability AI SDXL 1024 modeli ile görsel üretir.
    Girdi: İngilizce prompt (Türkçe OLAMAZ, o yüzden önce çeviri yapıyoruz).
    Çıktı: PIL Image objesi
    """
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
    image_base64 = data["artifacts"][0]["base64"]
    image_bytes = base64.b64decode(image_base64)
    return Image.open(BytesIO(image_bytes))


# ---------------------------------------------------
# 2) GEMINI – REKLAM METNİ PROMPTU
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


# ---------------------------------------------------
# 3) GEMINI – GÖRSEL TASARIM PROMPTU
# ---------------------------------------------------
def build_image_prompt(product, audience, platform, tone):
    return f"""
Sen profesyonel bir reklam tasarımcısın.

Ürün: {product}
Hedef kitle: {audience}
Platform: {platform}
Üslup: {tone}

Reklam görseli için detaylı tasarım promptu üret:

1. Kompozisyon
2. Arka plan (renk/doku)
3. Işıklandırma
4. Kamera açısı
5. Renk paleti
6. SDXL/Midjourney/DALL·E için tek satırlık İngilizce prompt
"""


# ---------------------------------------------------
# 4) GEMINI – TÜRKÇE BİLGİLERDEN İNGİLİZCE GÖRSEL PROMPT ÜRETME
# ---------------------------------------------------
def translate_to_english_for_image(product, audience, platform, tone) -> str:
    """
    Stability sadece İngilizce kabul ettiği için,
    Türkçe girilen alanlardan %100 İngilizce bir görsel prompt üretir.
    """
    prompt = f"""
You are an expert advertising art director.

I will give you product info in Turkish. 
Your job is to create a HIGH-QUALITY English prompt for generating a professional advertising image with the SDXL model.

Product (can be Turkish): {product}
Target Audience (can be Turkish): {audience}
Platform (can be Turkish): {platform}
Tone (can be Turkish): {tone}

Instructions:
- The OUTPUT must be 100% in English.
- Do NOT include any Turkish.
- Describe the scene clearly (composition, background, lighting, style, camera angle, mood).
- Optimize the prompt for a professional product ad (e.g., studio lighting, ultra realistic, 4K).
- At the end, give a SINGLE one-line SDXL prompt that can be sent directly to an image model.
"""

    result = text_model.generate_content(prompt)
    return result.text


# ---------------------------------------------------
# 5) STREAMLIT ARAYÜZÜ
# ---------------------------------------------------
st.title("🎯 AdGen — AI Reklam Metni + Prompt + Görsel Üretici")

product = st.text_input("🛍 Ürün / Hizmet:")
audience = st.text_input("🎯 Hedef Kitle:")
platform = st.selectbox("📱 Platform:", ["Instagram", "TikTok", "LinkedIn", "Facebook"])
tone = st.selectbox("🎨 Üslup:", ["Eğlenceli", "Profesyonel", "Samimi", "İkna Edici"])


# ---------------------------------------------------
# 6) REKLAM METNİ (Gemini)
# ---------------------------------------------------
if st.button("📝 Reklam Metni Üret"):
    if not product or not audience:
        st.warning("⚠ Lütfen gerekli alanları doldurun.")
    else:
        with st.spinner("Reklam metni üretiliyor..."):
            try:
                text_prompt = build_text_prompt(product, audience, platform, tone)
                result = text_model.generate_content(text_prompt)
                st.subheader("📌 Üretilen Reklam Metni")
                st.write(result.text)
            except Exception as e:
                st.error(f"Metin üretimi hatası: {e}")


# ---------------------------------------------------
# 7) GÖRSEL TASARIM PROMPTU (Gemini)
# ---------------------------------------------------
if st.button("🎨 Görsel Tasarım Promptu Üret"):
    if not product or not audience:
        st.warning("⚠ Lütfen gerekli alanları doldurun.")
    else:
        with st.spinner("Görsel tasarım promptu üretiliyor..."):
            try:
                img_prompt = build_image_prompt(product, audience, platform, tone)
                result = text_model.generate_content(img_prompt)
                st.subheader("🖼 Görsel Tasarım Promptu")
                st.write(result.text)
            except Exception as e:
                st.error(f"Prompt üretimi hatası: {e}")


# ---------------------------------------------------
# 8) GERÇEK GÖRSEL ÜRETİMİ (Stability SDXL + İngilizce Prompt)
# ---------------------------------------------------
if st.button("🖼 Gerçek AI Görseli Üret"):
    if not product or not audience:
        st.warning("⚠ Lütfen gerekli alanları doldurun.")
    else:
        with st.spinner("İngilizce görsel promptu oluşturuluyor..."):
            try:
                english_prompt = translate_to_english_for_image(product, audience, platform, tone)
            except Exception as e:
                st.error(f"İngilizce prompt oluşturulurken hata: {e}")
                english_prompt = None

        if english_prompt:
            with st.spinner("Stability SDXL ile görsel üretiliyor..."):
                try:
                    img = generate_image_stability(english_prompt)
                    st.subheader("🖼 Üretilen Reklam Görseli")
                    st.image(img, use_column_width=True)

                    # İndirme butonu
                    buf = BytesIO()
                    img.save(buf, format="PNG")
                    st.download_button(
                        "📥 Görseli İndir",
                        buf.getvalue(),
                        "adgen_reklam.png",
                        "image/png"
                    )

                    st.caption("Not: Görsel, Stability AI SDXL modeli ile otomatik olarak üretilmiştir.")

                except Exception as e:
                    st.error(f"Görsel üretimi hatası: {e}")

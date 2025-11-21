import google.generativeai as genai
import base64
from io import BytesIO
from PIL import Image
import streamlit as st
from openai import OpenAI

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])



def generate_image_gemini(prompt):
    model = genai.GenerativeModel("gemini-1.5-flash")
    result = model.generate_images(
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    image_data = result.images[0]
    return image_data



st.title("AdGen - Reklam İçerik Üretici")

product = st.text_input("Ürün/Hizmet:")
audience = st.text_input("Hedef Kitle:")
platform = st.selectbox("Platform", ["Instagram", "TikTok", "LinkedIn", "Facebook"])
tone = st.selectbox("Üslup", ["Eğlenceli", "Profesyonel", "Samimi"])

# -------------------------
# METİN ÜRETME KISMI
# -------------------------
if st.button("Reklam İçeriği Üret"):
    prompt = f"""
    Ürün: {product}
    Hedef kitle: {audience}
    Platform: {platform}
    Üslup: {tone}

    Bana bu bilgilerle 3 farklı reklam metni, 1 başlık ve 1 görsel fikri öner.
    """

  model = genai.GenerativeModel("gemini-1.5-flash")
response = model.generate_content(prompt)

st.write(response.text)


# -------------------------
# GÖRSEL ÜRETME KISMI
# -------------------------
if st.button("Görsel Oluştur"):
    if not product or not audience:
        st.warning("Lütfen ürün ve hedef kitle giriniz.")
    else:
        with st.spinner("Görsel üretiliyor..."):
            image_prompt = f"{product} için {audience} hedef kitlesine uygun profesyonel reklam görseli"
            try:
                img = generate_image_gemini(image_prompt)
                st.image(img, caption="Üretilen Görsel", use_column_width=True)
            except Exception as e:
                st.error(f"Görsel oluşturulurken hata oluştu: {e}")
import base64
from io import BytesIO
from PIL import Image

buffer = BytesIO()
img.save(buffer, format="PNG")

st.download_button(
    label="Görseli İndir",
    data=buffer.getvalue(),
    file_name="adgen_gemini_visual.png",
    mime="image/png"
)



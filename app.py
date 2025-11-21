import streamlit as st
import google.generativeai as genai
from io import BytesIO
from PIL import Image

# -------------------------
# GEMINI API KURULUMU
# -------------------------
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])


# -------------------------
# GÖRSEL ÜRETME FONKSİYONU
# -------------------------
def generate_image_gemini(prompt):
    genai.GenerativeModel("gemini-1.0-pro")
    result = model.generate_images(
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    return result.images[0]


# -------------------------
# UYGULAMA ARAYÜZÜ
# -------------------------
st.title("AdGen - Reklam İçerik Üretici")

product = st.text_input("Ürün/Hizmet:")
audience = st.text_input("Hedef Kitle:")
platform = st.selectbox("Platform", ["Instagram", "TikTok", "LinkedIn", "Facebook"])
tone = st.selectbox("Üslup", ["Eğlenceli", "Profesyonel", "Samimi"])


# =========================
# 1️⃣ METİN ÜRETME
# =========================
if st.button("Reklam İçeriği Üret"):

    prompt = f"""
    Ürün: {product}
    Hedef kitle: {audience}
    Platform: {platform}
    Üslup: {tone}

    Bana bu bilgilerle 3 farklı reklam metni, 1 başlık ve 1 görsel fikri üret.
    """

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)

    st.subheader("📝 Üretilen İçerikler")
    st.write(response.text)



# =========================
# 2️⃣ GÖRSEL ÜRETME
# =========================
if st.button("Görsel Oluştur"):

    if not product or not audience:
        st.warning("Lütfen ürün ve hedef kitle giriniz.")
    else:
        with st.spinner("Görsel üretiliyor..."):

            image_prompt = f"{product} için {audience} hedef kitlesine uygun profesyonel reklam görseli"

            try:
                img = generate_image_gemini(image_prompt)
                st.image(img, caption="Üretilen Görsel", use_column_width=True)

                # İndirilebilir hale getirme
                buffer = BytesIO()
                Image.open(BytesIO(img)).save(buffer, format="PNG")

                st.download_button(
                    label="Görseli İndir",
                    data=buffer.getvalue(),
                    file_name="adgen_gemini_visual.png",
                    mime="image/png"
                )

            except Exception as e:
                st.error(f"Görsel üretilirken hata oluştu: {e}")

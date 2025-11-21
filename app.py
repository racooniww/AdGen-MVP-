import streamlit as st
import google.generativeai as genai
from io import BytesIO
from PIL import Image

# ---------------------------------
# Gemini API Key (Streamlit Secrets)
# ---------------------------------
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Metin modeli
text_model = genai.GenerativeModel("models/gemini-pro-latest")

# Görsel modeli
image_model = genai.GenerativeModel("models/imagen-4.0-generate-001")


# ---------------------------------
# Streamlit Arayüzü
# ---------------------------------
st.title("🎯 AdGen – AI Reklam Metni + Görsel Üretici")

product = st.text_input("Ürün/Hizmet:")
audience = st.text_input("Hedef Kitle:")
platform = st.selectbox("Platform:", ["Instagram", "TikTok", "LinkedIn", "Facebook"])
tone = st.selectbox("Üslup:", ["Eğlenceli", "Profesyonel", "Samimi"])


# =================================
# 1️⃣ METİN ÜRETİMİ
# =================================
if st.button("Reklam Metni Üret"):
    if not product or not audience:
        st.warning("Lütfen ürün ve hedef kitle giriniz.")
    else:
        prompt = f"""
        Ürün: {product}
        Hedef kitle: {audience}
        Platform: {platform}
        Üslup: {tone}

        Bana 3 farklı reklam metni, 1 kampanya sloganı ve 1 görsel fikri öner.
        """

        try:
            response = text_model.generate_content(prompt)
            st.subheader("📝 Üretilen Reklam Metni:")
            st.write(response.text)
        except Exception as e:
            st.error(f"Metin oluşturulurken hata oluştu: {e}")



# =================================
# 2️⃣ GÖRSEL ÜRETİMİ
# =================================
if st.button("Reklam Görseli Üret"):
    if not product or not audience:
        st.warning("Lütfen ürün ve hedef kitle giriniz.")
    else:
        image_prompt = (
            f"{product} için, {audience} kitlesine uygun, modern ve profesyonel tarzda "
            f"yüksek kaliteli bir reklam görseli. "
            f"Platform: {platform}. Stil: {tone}."
        )

        with st.spinner("Görsel üretiliyor, lütfen bekleyin..."):
            try:
                img_response = image_model.generate_image(prompt=image_prompt)

                # Görseli streamlit'te göstermek için dönüştür
                img = Image.open(BytesIO(img_response.image))

                st.image(img, caption="🖼 Üretilen Reklam Görseli", use_column_width=True)

                # İndirme butonu
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                st.download_button(
                    label="Görseli İndir",
                    data=buffer.getvalue(),
                    file_name="adgen_reklam_gorsel.png",
                    mime="image/png"
                )

            except Exception as e:
                st.error(f"Görsel oluşturulurken hata oluştu: {e}")

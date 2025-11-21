import base64
from io import BytesIO
from PIL import Image
import streamlit as st
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


def generate_image(prompt, size="1024x1024"):
    result = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size=size
    )
    b64 = result.data[0].b64_json
    image_bytes = base64.b64decode(b64)
    return Image.open(BytesIO(image_bytes))


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

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    st.subheader("Üretilen İçerikler")
    st.write(response.choices[0].message.content)
    st.subheader("🎨 Reklam Görseli Oluştur")


# -------------------------
# GÖRSEL ÜRETME KISMI
# -------------------------
if st.button("Görsel Oluştur"):
    image_prompt = f"{product} ürünü için, {audience} kitlesine uygun, dikkat çekici bir reklam görseli"

    with st.spinner("Görsel üretiliyor..."):
        try:
            img = generate_image(image_prompt)
            st.image(img, caption="Üretilen Reklam Görseli", use_column_width=True)

            # Download button (sadece görsel üretildiyse)
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            st.download_button(
                label="Görseli İndir",
                data=buffer.getvalue(),
                file_name="adgen_visual.png",
                mime="image/png"
            )

        except Exception as e:
            st.error(f"Görsel oluşturulurken hata oluştu: {e}")



import streamlit as st
from openai import OpenAI
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("AdGen - Reklam İçerik Üretici")

product = st.text_input("Ürün/Hizmet:")
audience = st.text_input("Hedef Kitle:")
platform = st.selectbox("Platform", ["Instagram", "TikTok", "LinkedIn", "Facebook"])
tone = st.selectbox("Üslup", ["Eğlenceli", "Profesyonel", "Samimi"])

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



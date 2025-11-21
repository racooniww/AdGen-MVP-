import streamlit as st
import google.generativeai as genai

# -------------------------
# GEMINI API KEY (Streamlit Secrets)
# -------------------------
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Metin modeli
model = genai.GenerativeModel("models/gemini-pro-latest")

# -------------------------
# ARAYÜZ
# -------------------------
st.title("✍️ AdGen – AI Reklam Metni Üretici")

prompt = st.text_area(
    "Reklam metni oluşturmak için bir açıklama girin:",
    height=180,
    placeholder="Örn: Doğal zeytinyağlı sabun için Instagram reklam metni yaz..."
)

if st.button("Metin Üret"):
    if not prompt.strip():
        st.warning("⚠ Lütfen bir açıklama girin!")
    else:
        try:
            response = model.generate_content(prompt)
            st.subheader("📌 Üretilen Metin:")
            st.write(response.text)
        except Exception as e:
            st.error(f"Hata oluştu: {str(e)}")

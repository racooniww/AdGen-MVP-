import streamlit as st
import google.generativeai as genai
import requests
import base64
from io import BytesIO
from PIL import Image

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="AdGen – AI Ad Generator",
    page_icon="https://raw.githubusercontent.com/racooniww/AdGen-MVP-/main/adgen_logo.jpg",
    layout="centered"
)

# ---------------------------------------------------
# MULTI-LANGUAGE TEXTS
# ---------------------------------------------------
LANG = {
    "tr": {
        "title": "AdGen – Yapay Zeka Reklam Üretici",
        "subtitle": "KOBİ'ler ve markalar için metin, görsel fikri ve rakip analizi.",
        "language": "Dil",
        "product": "Ürün / Hizmet",
        "audience": "Hedef Kitle",
        "platform": "Platform",
        "tone": "Üslup",
        "generate_text": "Reklam Metni Üret",
        "generate_prompt": "Görsel Tasarım Promptu",
        "generate_image": "AI Görseli Üret",
        "manual_prompt": "Manuel Görsel Promptu (Kullanıcı Düzenleyebilir)",
        "competitor_scan": "Rakip Analizi",
        "competitor_placeholder": "Rakip analizi için ürün / kategori adı...",
        "output_competitor": "Rakip Analizi Sonuçları",
        "warning_fill": "⚠ Lütfen gerekli alanları doldurun.",
        "down_img": "Görseli İndir",
        "btn_scan": "Rakipleri Tara",
        "adcopy_spinner": "Reklam metni üretiliyor...",
        "visual_spinner": "Görsel tasarım promptu hazırlanıyor...",
        "comp_scan_spinner": "Web üzerinden rakipler analiz ediliyor...",
        "image_info": "Bu görsel Stability AI SDXL ile üretilecektir."
    },
    "en": {
        "title": "AdGen – AI Advertising Generator",
        "subtitle": "Text, visual concepts and competitor intelligence for SMEs and brands.",
        "language": "Language",
        "product": "Product / Service",
        "audience": "Target Audience",
        "platform": "Platform",
        "tone": "Tone",
        "generate_text": "Generate Ad Copy",
        "generate_prompt": "Generate Visual Prompt",
        "generate_image": "Generate AI Image",
        "manual_prompt": "Manual Image Prompt (User Editable)",
        "competitor_scan": "Competitor Scan",
        "competitor_placeholder": "Product / category name for competitor analysis...",
        "output_competitor": "Competitor Analysis Result",
        "warning_fill": "⚠ Please fill all required fields.",
        "down_img": "Download Image",
        "btn_scan": "Scan Competitors",
        "adcopy_spinner": "Generating ad copy...",
        "visual_spinner": "Generating visual design prompt...",
        "comp_scan_spinner": "Scanning competitors...",
        "image_info": "This image will be generated using Stability AI SDXL."
    }
}

# ---------------------------------------------------
# LANGUAGE SELECTOR
# ---------------------------------------------------
ui_language = st.selectbox("Language / Dil", ["Türkçe", "English", "Dual (TR + EN Output)"])

if ui_language == "Türkçe":
    L = LANG["tr"]
    output_mode = "tr"
    comp_lang = "tr"
elif ui_language == "English":
    L = LANG["en"]
    output_mode = "en"
    comp_lang = "en"
else:
    L = LANG["tr"]
    output_mode = "dual"
    comp_lang = "tr"

# ---------------------------------------------------
# GEMINI CONFIG
# ---------------------------------------------------
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
text_model = genai.GenerativeModel("models/gemini-2.5-flash")

# ---------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------
def inject_custom_css():
    st.markdown(
        """
        <style>
        .stApp { background: #f6f8fc; font-family: -apple-system, BlinkMacSystemFont, system-ui, sans-serif; }
        .adgen-header { text-align: center; margin-bottom: 1.4rem; }
        .adgen-title { font-size: 2.1rem; font-weight: 800; color: #111827; }
        .adgen-subtitle { font-size: 1rem; color: #4b5563; margin-top: -6px; }
        .field-label { font-size: 0.9rem; font-weight: 600; color: #374151; margin-bottom: 0.25rem; }
        .output-box { margin-top: 1.2rem; padding: 1rem 1.1rem; border-radius: 0.9rem; background: #f9fafb; border: 1px solid #e5e7eb; }
        </style>
        """,
        unsafe_allow_html=True
    )

inject_custom_css()

# ---------------------------------------------------
# SAFE TEXT EXTRACTION
# ---------------------------------------------------
def extract_text_safe(response):
    if hasattr(response, "text") and response.text:
        return response.text.strip()
    if hasattr(response, "candidates") and response.candidates:
        cand = response.candidates[0]
        if hasattr(cand, "content") and hasattr(cand.content, "parts"):
            parts = cand.content.parts
            if parts and hasattr(parts[0], "text"):
                return parts[0].text.strip()
    return ""

# ---------------------------------------------------
# PROMPT BUILDERS
# ---------------------------------------------------
def build_ad_text_prompt(product, audience, platform, tone, mode):
    if mode == "tr":
        return f"""
Sen bir dijital pazarlama uzmanısın.

Ürün: {product}
Hedef kitle: {audience}
Platform: {platform}
Üslup: {tone}

- 3 başlık
- 2 reklam metni (A/B)
- 1 slogan
- 8 hashtag
"""
    if mode == "en":
        return f"""
You are a senior digital marketer.

Product: {product}
Audience: {audience}
Platform: {platform}
Tone: {tone}

- 3 headlines
- 2 ad copies
- 1 slogan
- 8 hashtags
"""
    return f"TR + EN reklam içerikleri üret.\nÜrün: {product}\nAudience: {audience}"

def build_visual_prompt(product, audience, platform, tone, mode):
    return f"""
Generate a visual design description.

Product: {product}
Audience: {audience}
Platform: {platform}
Tone: {tone}

1) Composition
2) Background
3) Lighting
4) Colors
5) Camera angle
6) SDXL one-line prompt
"""

# ---------------------------------------------------
# TRANSLATE FOR SDXL
# ---------------------------------------------------
def translate_to_english_for_image(product, audience, platform, tone):
    prompt = f"""
Convert this into a professional English SDXL image prompt:

Product: {product}
Audience: {audience}
Platform: {platform}
Tone: {tone}

Return ONLY the English SDXL prompt.
"""
    r = text_model.generate_content(prompt)
    return extract_text_safe(r)

# ---------------------------------------------------
# STABILITY SDXL
# ---------------------------------------------------
STABILITY_API_KEY = st.secrets["STABILITY_API_KEY"]

def generate_image_stability(prompt):
    url = "https://api.stability.ai/v2beta/stable-image/generate/core"

    headers = {
        "Authorization": f"Bearer {STABILITY_API_KEY}",
        "Accept": "image/*"
    }

    files = {
        "prompt": (None, prompt),
        "mode": (None, "text-to-image"),
        "output_format": (None, "png"),
        "aspect_ratio": (None, "1:1")
    }

    response = requests.post(url, headers=headers, files=files)

    if response.status_code != 200:
        raise ValueError(f"Stability API Error: {response.text}")

    return Image.open(BytesIO(response.content))

# ---------------------------------------------------
# COMPETITOR ANALYSIS
# ---------------------------------------------------
def scan_competitors(product, lang):
    prompt = f"Analyze competitor patterns for: {product}. No URLs."
    r = text_model.generate_content(prompt)
    return extract_text_safe(r)

# ---------------------------------------------------
# HEADER WITH LOGO
# ---------------------------------------------------
st.image("https://raw.githubusercontent.com/racooniww/AdGen-MVP-/main/adgen_logo.jpg", width=150)

st.markdown(
    f"""
    <div class="adgen-header">
        <div class="adgen-title">{L["title"]}</div>
        <div class="adgen-subtitle">{L["subtitle"]}</div>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------
# MAIN INPUTS
# ---------------------------------------------------
product = st.text_area("Product Details", height=150)
audience = st.text_input("Audience")
platform = st.selectbox("Platform", ["Instagram", "TikTok", "LinkedIn", "Facebook"])
tone = st.selectbox("Tone", ["Playful", "Professional", "Friendly", "Persuasive"])

# USER MANUAL PROMPT (NEW)
manual_prompt = st.text_area(
    L["manual_prompt"],
    placeholder="You can manually edit the prompt before generating the image.",
    height=120
)

# ---------------------------------------------------
# BUTTONS
# ---------------------------------------------------
c1, c2, c3 = st.columns(3)

if c1.button(L["generate_text"]):
    prompt = build_ad_text_prompt(product, audience, platform, tone, output_mode)
    r = text_model.generate_content(prompt)
    st.write(extract_text_safe(r))

if c2.button(L["generate_prompt"]):
    prompt = build_visual_prompt(product, audience, platform, tone, output_mode)
    r = text_model.generate_content(prompt)
    st.write(extract_text_safe(r))

if c3.button(L["generate_image"]):
    final_prompt = manual_prompt.strip()

    if final_prompt == "":
        final_prompt = translate_to_english_for_image(product, audience, platform, tone)

    try:
        img = generate_image_stability(final_prompt)
        st.image(img)

        buf = BytesIO()
        img.save(buf, format="PNG")
        st.download_button(L["down_img"], buf.getvalue(), "adgen.png")
    except Exception as e:
        st.error(f"Görsel üretimi hatası: {e}")

# ---------------------------------------------------
# COMPETITOR SCAN
# ---------------------------------------------------
st.markdown("---")
st.subheader(L["competitor_scan"])

comp = st.text_input("competitor", placeholder=L["competitor_placeholder"])

if st.button(L["btn_scan"]):
    result = scan_competitors(comp, comp_lang)
    st.write(result)

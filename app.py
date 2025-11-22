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
    page_icon="🎯",
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
        "competitor_scan": "Rakip Analizi",
        "competitor_placeholder": "Rakip analizi için ürün / kategori adı...",
        "output_competitor": "Rakip Analizi Sonuçları",
        "warning_fill": "⚠ Lütfen gerekli alanları doldurun.",
        "down_img": "Görseli İndir",
        "btn_scan": "Rakipleri Tara",
        "adcopy_spinner": "Reklam metni üretiliyor...",
        "visual_spinner": "Görsel tasarım promptu hazırlanıyor...",
        "comp_scan_spinner": "Web üzerinden rakipler analiz ediliyor...",
        "comp_analysis_spinner": "Rakip analizi hazırlanıyor...",
        "image_info": "AI görsel üretimi Stability SDXL ile yapılacak."
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
        "competitor_scan": "Competitor Scan",
        "competitor_placeholder": "Product / category name for competitor analysis...",
        "output_competitor": "Competitor Analysis Result",
        "warning_fill": "⚠ Please fill all required fields.",
        "down_img": "Download Image",
        "btn_scan": "Scan Competitors",
        "adcopy_spinner": "Generating ad copy...",
        "visual_spinner": "Generating visual design prompt...",
        "comp_scan_spinner": "Scanning competitors using the web...",
        "comp_analysis_spinner": "Preparing competitor analysis...",
        "image_info": "AI image generation will use Stability SDXL."
    }
}

# ---------------------------------------------------
# LANGUAGE SELECTOR
# ---------------------------------------------------
ui_language = st.selectbox(
    "Language / Dil",
    ["Türkçe", "English", "Dual (TR + EN Output)"]
)

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
        .stApp {
            background: #f6f8fc;
            font-family: -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
        }
        .adgen-header {
            text-align: center;
            margin-bottom: 1.4rem;
        }
        .adgen-title {
            font-size: 2.1rem;
            font-weight: 800;
            color: #111827;
        }
        .adgen-subtitle {
            font-size: 1rem;
            color: #4b5563;
            margin-top: -6px;
        }
        .field-label {
            font-size: 0.9rem;
            font-weight: 600;
            color: #374151;
            margin-bottom: 0.25rem;
        }
        .stButton>button {
            border-radius: 999px !important;
            padding: 0.55rem 1.2rem !important;
            font-weight: 600 !important;
            border: 1px solid #d1d5db !important;
            background: white !important;
            color: #111827 !important;
        }
        .stButton>button:hover {
            border-color: #6366f1 !important;
        }
        .output-box {
            margin-top: 1.2rem;
            padding: 1rem 1.1rem;
            border-radius: 0.9rem;
            background: #f9fafb;
            border: 1px solid #e5e7eb;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

inject_custom_css()

# ---------------------------------------------------
# SAFE TEXT EXTRACTION FROM GEMINI
# ---------------------------------------------------
def extract_text_safe(response):
    if hasattr(response, "text") and response.text:
        return response.text.strip()

    if hasattr(response, "candidates") and response.candidates:
        cand = response.candidates[0]
        if hasattr(cand, "content") and hasattr(cand.content, "parts"):
            parts = cand.content.parts
            if parts and hasattr(parts[0], "text"):
                if parts[0].text:
                    return parts[0].text.strip()

    return ""
# ---------------------------------------------------
# AD COPY PROMPT BUILDER (TR / EN / DUAL)
# ---------------------------------------------------
def build_ad_text_prompt(product, audience, platform, tone, mode):
    if mode == "tr":
        return f"""
Sen bir dijital pazarlama uzmanısın.

Ürün: {product}
Hedef kitle: {audience}
Platform: {platform}
Üslup: {tone}

Aşağıdaki formatta reklam içeriği oluştur:

- 3 kısa başlık
- 2 farklı reklam metni (A/B testi için)
- 1 kampanya sloganı
- 8 hashtag
"""
    if mode == "en":
        return f"""
You are a senior digital marketing expert.

Product: {product}
Target audience: {audience}
Platform: {platform}
Tone: {tone}

Generate:

- 3 short headlines
- 2 different ad copies (A/B test)
- 1 campaign slogan
- 8 hashtags
"""
    # dual
    return f"""
You are a bilingual digital marketing specialist.
Create TWO versions: TR + EN.

=========================
🇹🇷 TÜRKÇE
=========================

Ürün: {product}
Hedef kitle: {audience}
Platform: {platform}
Üslup: {tone}

- 3 kısa başlık
- 2 reklam metni
- 1 slogan
- 8 hashtag

=========================
🇬🇧 ENGLISH
=========================

Product: {product}
Audience: {audience}
Platform: {platform}
Tone: {tone}

- 3 headlines
- 2 ad copies
- 1 slogan
- 8 hashtags
"""

# ---------------------------------------------------
# VISUAL PROMPT BUILDER (TR / EN / DUAL)
# ---------------------------------------------------
def build_visual_prompt(product, audience, platform, tone, mode):
    if mode == "tr":
        return f"""
Sen bir reklam görseli tasarım uzmanısın.

Ürün: {product}
Hedef kitle: {audience}
Platform: {platform}
Üslup: {tone}

Reklam görseli için aşağıdaki başlıklara göre detaylı bir tasarım açıklaması yap:

1) Kompozisyon  
2) Arka plan  
3) Işıklandırma  
4) Renk paleti  
5) Kamera açısı  
6) SDXL için tek satırlık İngilizce prompt ekle
"""
    if mode == "en":
        return f"""
You are an advertising visual designer.

Product: {product}
Audience: {audience}
Platform: {platform}
Tone: {tone}

Describe:

1) Composition
2) Background
3) Lighting
4) Color palette
5) Camera angle
6) One SDXL-style English prompt line
"""
    # dual
    return f"""
Create TWO SECTIONS: TR + EN

=========================
🇹🇷 TÜRKÇE
=========================
Ürün: {product}
Kitle: {audience}
Platform: {platform}
Üslup: {tone}

1) Kompozisyon  
2) Arka plan  
3) Işıklandırma  
4) Renk paleti  
5) Kamera açısı  

=========================
🇬🇧 ENGLISH
=========================
Product: {product}
Audience: {audience}
Platform: {platform}
Tone: {tone}

1) Composition  
2) Background  
3) Lighting  
4) Color palette  
5) Camera angle  
6) 1-line SDXL English prompt
"""

# ---------------------------------------------------
# ENGLISH PROMPT TRANSLATOR FOR SDXL
# ---------------------------------------------------
def translate_to_english_for_image(product, audience, platform, tone):
    prompt = f"""
You are a senior AI advertisement image prompt engineer.

Translate the following into a HIGH-QUALITY English SDXL prompt:

Product: {product}
Audience: {audience}
Platform: {platform}
Tone: {tone}

Requirements:
- English only
- Include composition, lighting, scene, style, camera angle
- End with 1 final SDXL prompt line
"""
    r = text_model.generate_content(prompt)
    english = extract_text_safe(r)

    if not english or len(english) < 5:
        english = f"SDXL product photo of {product}, targeted to {audience}, studio lighting, 4k, clean background."

    return english.strip()

# ---------------------------------------------------
# STABILITY SDXL – NEW 2024 API (WORKING)
# ---------------------------------------------------
STABILITY_API_KEY = st.secrets["STABILITY_API_KEY"]

def generate_image_stability(prompt):
    url = "https://api.stability.ai/v2beta/stable-image/generate/core"

    headers = {
        "Authorization": f"Bearer {STABILITY_API_KEY}",
        "Accept": "image/png"   # 🔥 Stability yeni API bunu ZORUNLU istiyor
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
# COMPETITOR SCAN (TR / EN)
# ---------------------------------------------------
def scan_competitors(product_name, lang="tr"):

    if lang == "tr":
        prompt = f"""
Sen bir rekabet analizi uzmanısın.

Görev:
'{product_name}' ile ilgili rakip markaları ve sektör trendlerini analiz et.
URL verme, özet çıkar.

Çıktı:
1) Rakip marka türleri  
2) Slogan / mesaj temaları  
3) Reklamlarda en çok vurgulanan özellikler  
4) Reklam tonu + örnekler  
5) Sektör trendleri  
6) Pazar boşlukları  
7) '{product_name}' için 3 farklılaşma önerisi  
"""
    else:
        prompt = f"""
You are a competitive intelligence expert.

Task:
Analyze competitor patterns for '{product_name}'.
No raw URLs.

Output:
1) Competitor brand types  
2) Message themes  
3) Most emphasized ad angles  
4) Tone + examples  
5) Category trends  
6) Market gaps  
7) 3 differentiation strategies  
"""

    r = text_model.generate_content(prompt)
    return extract_text_safe(r)
# ---------------------------------------------------
# UI – HEADER
# ---------------------------------------------------
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
# MAIN CARD – PRODUCT INPUTS + AD GENERATION
# ---------------------------------------------------
with st.container():
    st.markdown('<div class="adgen-card">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f'<div class="field-label">{L["product"]}</div>', unsafe_allow_html=True)
        product = st.text_input(
            "product",
            label_visibility="collapsed",
            placeholder="Handmade soap" if ui_language != "Türkçe" else "El yapımı sabun"
        )

        st.markdown(f'<div class="field-label">{L["platform"]}</div>', unsafe_allow_html=True)
        platform = st.selectbox(
            "platform",
            ["Instagram", "TikTok", "LinkedIn", "Facebook"],
            label_visibility="collapsed"
        )

    with col2:
        st.markdown(f'<div class="field-label">{L["audience"]}</div>', unsafe_allow_html=True)
        audience = st.text_input(
            "audience",
            label_visibility="collapsed",
            placeholder="e.g. young adults, mothers" if ui_language != "Türkçe" else "Genç yetişkinler, anneler"
        )

        st.markdown(f'<div class="field-label">{L["tone"]}</div>', unsafe_allow_html=True)
        tone = st.selectbox(
            "tone",
            ["Playful", "Professional", "Friendly", "Persuasive"]
            if ui_language != "Türkçe"
            else ["Eğlenceli", "Profesyonel", "Samimi", "İkna Edici"],
            label_visibility="collapsed"
        )

    st.markdown("---")

    # BUTTONS
    c1, c2, c3 = st.columns(3)
    with c1:
        btn_text = st.button(L["generate_text"])
    with c2:
        btn_visual = st.button(L["generate_prompt"])
    with c3:
        btn_image = st.button(L["generate_image"])

    # --- TEXT GENERATION ---
    if btn_text:
        if not product or not audience:
            st.warning(L["warning_fill"])
        else:
            with st.spinner(L["adcopy_spinner"]):
                p = build_ad_text_prompt(product, audience, platform, tone, output_mode)
                res = text_model.generate_content(p)
                txt = extract_text_safe(res)

                st.markdown('<div class="output-box">', unsafe_allow_html=True)
                st.subheader("Ad Copy / Reklam Metni")
                st.write(txt)
                st.markdown('</div>', unsafe_allow_html=True)

    # --- VISUAL PROMPT GENERATION ---
    if btn_visual:
        if not product or not audience:
            st.warning(L["warning_fill"])
        else:
            with st.spinner(L["visual_spinner"]):
                p = build_visual_prompt(product, audience, platform, tone, output_mode)
                res = text_model.generate_content(p)
                txt = extract_text_safe(res)

                st.markdown('<div class="output-box">', unsafe_allow_html=True)
                st.subheader("Visual Design Prompt")
                st.write(txt)
                st.markdown('</div>', unsafe_allow_html=True)

    # --- REAL STABILITY SDXL IMAGE GENERATION ---
    if btn_image:
        if not product or not audience:
            st.warning(L["warning_fill"])
        else:
            st.info(L["image_info"])

            # 1. Türkçe → İngilizce prompt çevir
            with st.spinner("Converting to English for SDXL..."):
                english_prompt = translate_to_english_for_image(product, audience, platform, tone)

            # 2. Stability SDXL üretim
            with st.spinner("Stability SDXL generating image..."):
                try:
                    img = generate_image_stability(english_prompt)

                    st.markdown('<div class="output-box">', unsafe_allow_html=True)
                    st.subheader("Generated Image")
                    st.image(img, use_column_width=True)

                    buf = BytesIO()
                    img.save(buf, format="PNG")

                    st.download_button(
                        L["down_img"],
                        buf.getvalue(),
                        file_name="adgen_sdxl.png",
                        mime="image/png"
                    )

                    st.markdown('</div>', unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Görsel üretimi hatası: {e}")

    st.markdown('</div>', unsafe_allow_html=True)


# ---------------------------------------------------
# COMPETITOR SCAN CARD
# ---------------------------------------------------
with st.container():
    st.markdown('<div class="adgen-card">', unsafe_allow_html=True)

    st.markdown(
        f"<div class='field-label'>{L['competitor_scan']}</div>",
        unsafe_allow_html=True
    )

    competitor_name = st.text_input(
        "competitor_name",
        label_visibility="collapsed",
        placeholder=L["competitor_placeholder"]
    )

    btn_comp = st.button("🔍 " + L["btn_scan"])

    if btn_comp:
        if not competitor_name:
            st.warning(L["warning_fill"])
        else:
            with st.spinner(L["comp_scan_spinner"]):
                analysis = scan_competitors(competitor_name, comp_lang)

            st.markdown('<div class="output-box">', unsafe_allow_html=True)
            st.subheader(L["output_competitor"])
            st.write(analysis)
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

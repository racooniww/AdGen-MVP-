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
# ========== LOGO URL (BURAYA RAW LINKİNİ YAPIŞTIR) ==========
# ÖRN: "https://raw.githubusercontent.com/kullanici/AdGen-MVP/main/adgen_logo.png"
# ---------------------------------------------------
LOGO_URL = "BURAYA_RAW_LOGO_URL"

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
        "image_info": "AI görsel üretimi Stability SDXL ile yapılacak.",
        "retry_prompt": "Yeni bir görsel promptu girerek tekrar görsel üretebilirsiniz:"
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
        "image_info": "AI image generation will use Stability SDXL.",
        "retry_prompt": "Enter a new visual prompt to regenerate:"
    }
}

# ---------------------------------------------------
# LANGUAGE SELECTOR
# ---------------------------------------------------
ui_language = st.selectbox("Language / Dil", ["Türkçe", "English"])

L = LANG["tr"] if ui_language == "Türkçe" else LANG["en"]
mode = "tr" if ui_language == "Türkçe" else "en"

# ---------------------------------------------------
# GEMINI CONFIG
# ---------------------------------------------------
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
text_model = genai.GenerativeModel("models/gemini-2.5-flash")

# ---------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------
def inject_custom_css():
    st.markdown("""
        <style>
        .stApp { background: #f5f6fc; font-family: -apple-system, BlinkMacSystemFont; }
        .adgen-header { text-align: center; margin-bottom: 1rem; }
        .adgen-title { font-size: 2rem; font-weight: 800; color: #222; }
        .adgen-subtitle { color: #666; font-size: 1rem; margin-top: -5px; }
        .output-box { background:#fff; padding:1rem; border-radius:10px; border:1px solid #ddd; margin-top:1rem; }
        .stButton>button { border-radius:999px; padding:.5rem 1.2rem; border:1px solid #ddd; background:white; }
        </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# ---------------------------------------------------
# SAFE TEXT EXTRACTION
# ---------------------------------------------------
def extract_text_safe(response):
    if hasattr(response, "text") and response.text:
        return response.text.strip()
    if hasattr(response, "candidates") and response.candidates:
        parts = response.candidates[0].content.parts
        if parts and hasattr(parts[0], "text"):
            return parts[0].text.strip()
    return ""

# ---------------------------------------------------
# TEXT PROMPT GENERATION
# ---------------------------------------------------
def build_ad_prompt(details, audience, platform, tone, mode):
    if mode == "tr":
        return f"""
Sen bir dijital pazarlama uzmanısın.

Ürün Detayları: {details}
Hedef kitle: {audience}
Platform: {platform}
Üslup: {tone}

- 3 başlık
- 2 reklam metni
- slogan
- hashtag seti
"""
    else:
        return f"""
You are a senior digital marketing strategist.

Product Details: {details}
Audience: {audience}
Platform: {platform}
Tone: {tone}

- 3 headlines
- 2 ad copies
- 1 slogan
- hashtags
"""

# ---------------------------------------------------
# VISUAL PROMPT BUILD
# ---------------------------------------------------
def build_visual_prompt(details, audience, platform, tone):
    return f"""
You are an AI advertising visual designer.

Product: {details}
Audience: {audience}
Platform: {platform}
Tone: {tone}

Describe:
- composition
- lighting
- style
- camera angle
- mood
- one final SDXL ready English prompt
"""

# ---------------------------------------------------
# SDXL TRANSLATOR
# ---------------------------------------------------
def translate_to_sdxl(details, audience, platform, tone):
    r = text_model.generate_content(f"""
Convert the following into a clean ENGLISH SDXL prompt:

Product: {details}
Audience: {audience}
Platform: {platform}
Tone: {tone}

Make it studio quality.
""")
    out = extract_text_safe(r)
    return out if len(out) > 10 else f"{details}, product shot, studio light, 4k"

# ---------------------------------------------------
# STABILITY SDXL
# ---------------------------------------------------
STABILITY_API_KEY = st.secrets["STABILITY_API_KEY"]

def generate_sdxl(prompt):
    url = "https://api.stability.ai/v2beta/stable-image/generate/core"

    headers = {
        "Authorization": f"Bearer {STABILITY_API_KEY}",
        "Accept": "image/*"
    }

    files = {
        "prompt": (None, prompt),
        "output_format": (None, "png"),
        "mode": (None, "text-to-image"),
        "aspect_ratio": (None, "1:1")
    }

    r = requests.post(url, headers=headers, files=files)

    if r.status_code != 200:
        raise ValueError(f"Stability API Error: {r.text}")

    return Image.open(BytesIO(r.content))

# ---------------------------------------------------
# COMPETITOR ANALYSIS
# ---------------------------------------------------
def scan_competitors(name, lang="tr"):
    prompt = f"""
You are a competitive intelligence analyst.

Analyze competitor patterns for: {name}

Output:
- competitor brand types
- messaging patterns
- slogans
- angles used in ads
- category trends
- market gaps
- differentiation strategies
"""
    r = text_model.generate_content(prompt)
    return extract_text_safe(r)

# ---------------------------------------------------
# UI – LOGO
# ---------------------------------------------------
if LOGO_URL:
    st.markdown(
        f"""
        <div style="text-align:center; margin-top:10px; margin-bottom:10px;">
            <img src="{LOGO_URL}" width="165">
        </div>
        """,
        unsafe_allow_html=True
    )

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
# MAIN INPUT FIELDS
# ---------------------------------------------------
details = st.text_area(L["product"], height=120)
audience = st.text_input(L["audience"])
platform = st.selectbox(L["platform"], ["Instagram","TikTok","Facebook","LinkedIn"])
tone = st.selectbox(
    L["tone"],
    ["Eğlenceli","Profesyonel","Samimi","İkna Edici"] if mode=="tr"
    else ["Playful","Professional","Friendly","Persuasive"]
)

st.markdown("---")

# BUTTONS
b1, b2, b3 = st.columns(3)
gen_text = b1.button(L["generate_text"])
gen_vp   = b2.button(L["generate_prompt"])
gen_img  = b3.button(L["generate_image"])

# ---------------------------------------------------
# TEXT GENERATION
# ---------------------------------------------------
if gen_text:
    if not details or not audience:
        st.warning(L["warning_fill"])
    else:
        with st.spinner(L["adcopy_spinner"]):
            p = build_ad_prompt(details, audience, platform, tone, mode)
            r = text_model.generate_content(p)
            st.markdown('<div class="output-box">', unsafe_allow_html=True)
            st.write(extract_text_safe(r))
            st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------
# VISUAL PROMPT GENERATION
# ---------------------------------------------------
if gen_vp:
    if not details:
        st.warning(L["warning_fill"])
    else:
        with st.spinner(L["visual_spinner"]):
            p = build_visual_prompt(details, audience, platform, tone)
            r = text_model.generate_content(p)
            st.markdown('<div class="output-box">', unsafe_allow_html=True)
            st.write(extract_text_safe(r))
            st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------
# IMAGE GENERATION + CUSTOM PROMPT FROM USER
# ---------------------------------------------------
if gen_img:
    if not details:
        st.warning(L["warning_fill"])
    else:
        st.info(L["image_info"])

        # 1) Base English prompt
        base_prompt = translate_to_sdxl(details, audience, platform, tone)

        st.subheader("SDXL Prompt")
        st.write(base_prompt)

        # 2) User override prompt
        custom_prompt = st.text_area(L["retry_prompt"], "", height=100)

        final_prompt = custom_prompt if len(custom_prompt.strip()) > 5 else base_prompt

        # 3) Generate Image
        with st.spinner("SDXL generating..."):
            try:
                img = generate_sdxl(final_prompt)

                st.image(img, use_column_width=True)

                buf = BytesIO()
                img.save(buf, format="PNG")
                st.download_button(
                    L["down_img"],
                    buf.getvalue(),
                    file_name="adgen_sdxl.png",
                    mime="image/png"
                )

            except Exception as e:
                st.error(f"Görsel üretimi hatası: {e}")

# ---------------------------------------------------
# COMPETITOR SCAN
# ---------------------------------------------------
st.markdown("---")
st.subheader(L["competitor_scan"])

comp = st.text_input("comp_scan", L["competitor_placeholder"])

if st.button("🔍 " + L["btn_scan"]):
    if not comp:
        st.warning(L["warning_fill"])
    else:
        with st.spinner(L["comp_scan_spinner"]):
            result = scan_competitors(comp, mode)

        st.markdown('<div class="output-box">', unsafe_allow_html=True)
        st.write(result)
        st.markdown('</div>', unsafe_allow_html=True)

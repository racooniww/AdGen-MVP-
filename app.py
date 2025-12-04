import streamlit as st
import google.generativeai as genai
import requests
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
        "image_info": "AI görsel üretimi Stability SDXL ile yapılacak.",
        "extra_prompt_label": "Görseli iyileştirmek için ek yönlendirme (opsiyonel)",
        "extra_prompt_placeholder": "Örn: daha sıcak tonlar, ürüne yakın çekim, arka plan sade..."
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
        "image_info": "AI image generation will use Stability SDXL.",
        "extra_prompt_label": "Extra instructions to refine the image (optional)",
        "extra_prompt_placeholder": "e.g. warmer colors, close-up product shot, minimal background..."
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
st.markdown("""
<style>
.stApp { background: #f3f5fa; }

.header-container {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 14px;
    margin-top: 10px;
}

.header-logo {
    width: 70px;
    height: auto;
    border-radius: 10px;
}

.header-title {
    font-size: 2.3rem;
    font-weight: 800;
    color: #111827;
    margin: 0;
    padding: 0;
}

.header-subtitle {
    text-align: center;
    margin-top: -6px;
    font-size: 1rem;
    color: #4b5563;
}

.gradient-line {
    width: 100%;
    height: 4px;
    margin: 10px 0 25px 0;
    background: linear-gradient(90deg, #ff4d8b, #7a2bff);
    border-radius: 50px;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# HEADER (LOGO + TITLE + SUBTITLE)
# ---------------------------------------------------
st.markdown(f"""
<div class="header-container">
    <img src="https://raw.githubusercontent.com/racooniww/AdGen-MVP-/main/adgen_logo.jpg" class="header-logo">
    <div class="header-title">{L["title"]}</div>
</div>
<div class="header-subtitle">{L["subtitle"]}</div>
<div class="gradient-line"></div>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# SAFE TEXT EXTRACTION
# ---------------------------------------------------
def extract_text_safe(response):
    if hasattr(response, "text") and response.text:
        return response.text.strip()
    if hasattr(response, "candidates") and response.candidates:
        parts = response.candidates[0].content.parts
        if parts and parts[0].text:
            return parts[0].text.strip()
    return ""

# ---------------------------------------------------
# PROMPT BUILDERS
# ---------------------------------------------------
def build_ad_text_prompt(product_details, audience, platform, tone, mode):
    if mode == "tr":
        return f"""
Ürün: {product_details}
Hedef Kitle: {audience}
Platform: {platform}
Üslup: {tone}

- 3 kısa başlık
- 2 reklam metni
- 1 slogan
- 8 hashtag
"""
    if mode == "en":
        return f"""
Product: {product_details}
Audience: {audience}
Platform: {platform}
Tone: {tone}

- 3 headlines
- 2 ad copies
- 1 slogan
- 8 hashtags
"""
    return f"""
(TÜRKÇE VE İNGİLİZCE İKİ DİLDE ÇIKTI VER)

Ürün: {product_details}
Hedef Kitle / Audience: {audience}
Platform: {platform}
Üslup / Tone: {tone}
"""

def build_visual_prompt(product_details, audience, platform, tone, mode):
    return f"""
Describe the advertising visual for:

Product: {product_details}
Audience: {audience}
Platform: {platform}
Tone: {tone}

Include composition, lighting, color palette, angle, and 1 SDXL prompt.
"""

def translate_to_english_for_image(product_details, audience, platform, tone):
    r = text_model.generate_content(
        f"Write an SDXL English image prompt for: {product_details}, audience {audience}, platform {platform}, tone {tone}."
    )
    txt = extract_text_safe(r)
    return txt if txt else f"SDXL product photo of {product_details}."

# ---------------------------------------------------
# STABILITY IMAGE GENERATION
# ---------------------------------------------------
STABILITY_API_KEY = st.secrets["STABILITY_API_KEY"]

def generate_image_stability(prompt):
    url = "https://api.stability.ai/v2beta/stable-image/generate/core"

    headers = {"Authorization": f"Bearer {STABILITY_API_KEY}", "Accept": "image/*"}

    files = {
        "prompt": (None, prompt),
        "mode": (None, "text-to-image"),
        "output_format": (None, "png"),
        "aspect_ratio": (None, "1:1")
    }

    r = requests.post(url, headers=headers, files=files)

    if r.status_code != 200:
        raise ValueError(r.text)

    return Image.open(BytesIO(r.content))

# ---------------------------------------------------
# COMPETITOR ANALYSIS
# ---------------------------------------------------
def scan_competitors(product_name, lang="tr"):
    prompt = f"""
Competitive analysis for: {product_name}

- Market competitors
- Message themes
- Advertising angles
- Tone patterns
- Industry trends
- Market gaps
- Differentiation suggestions
"""
    r = text_model.generate_content(prompt)
    return extract_text_safe(r)

# ---------------------------------------------------
# MAIN UI
# ---------------------------------------------------
with st.container():
    st.markdown('<div class="adgen-card">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"### {L['product']} Detayları")
        product_details = st.text_area(
            label="",
            key="product_details",
            placeholder="Enter product details..." if ui_language != "Türkçe" else "Ürününüzü detaylıca açıklayın...",
            height=150,
            label_visibility="collapsed"
        )

        st.markdown(f"### {L['platform']}")
        platform = st.selectbox(
            label="",
            options=["Instagram", "TikTok", "LinkedIn", "Facebook"],
            key="platform",
            label_visibility="collapsed"
        )

    with col2:
        st.markdown(f"### {L['audience']}")
        audience = st.text_input(
            label="",
            key="audience",
            placeholder="young adults" if ui_language != "Türkçe" else "genç yetişkinler",
            label_visibility="collapsed"
        )

       st.markdown(f"### {L['tone']}")

if ui_language == "Türkçe":
    tone_options = ["Eğlenceli", "Profesyonel", "Samimi", "İkna Edici"]
else:
    tone_options = ["Playful", "Professional", "Friendly", "Persuasive"]

tone = st.selectbox("tone", tone_options)

    st.markdown("---")

    c1, c2, c3 = st.columns(3)
    btn_text = c1.button(L["generate_text"])
    btn_visual = c2.button(L["generate_prompt"])

    # Kullanıcıya gösterilen custom prompt alanı (isim değişti)
    user_custom_prompt = st.text_area(
        label=L["extra_prompt_label"],
        key="custom_sdxl",
        placeholder=L["extra_prompt_placeholder"],
        height=100
    )

    btn_image = c3.button(L["generate_image"])

    # --- AD TEXT ---
    if btn_text:
        with st.spinner(L["adcopy_spinner"]):
            p = build_ad_text_prompt(product_details, audience, platform, tone, output_mode)
            r = text_model.generate_content(p)
            st.write(extract_text_safe(r))

    # --- VISUAL PROMPT ---
    if btn_visual:
        with st.spinner(L["visual_spinner"]):
            p = build_visual_prompt(product_details, audience, platform, tone, output_mode)
            r = text_model.generate_content(p)
            st.write(extract_text_safe(r))

    # --- IMAGE GENERATION ---
    if btn_image:
        with st.spinner("Generating AI Image..."):

            # 1) Her durumda baz SDXL prompt'u oluştur
            base_prompt = translate_to_english_for_image(product_details, audience, platform, tone)

            # 2) Kullanıcı ekstra bir şey yazdıysa bunu baz prompt'un ÜSTÜNE ekle
            if user_custom_prompt and user_custom_prompt.strip():
                final_prompt = (
                    base_prompt
                    + "\n\nRefinement / extra details: "
                    + user_custom_prompt.strip()
                )
            else:
                final_prompt = base_prompt

            img = generate_image_stability(final_prompt)
            st.image(img, use_column_width=True)

            buf = BytesIO()
            img.save(buf, format="PNG")
            st.download_button(L["down_img"], buf.getvalue(), "adgen_sdxl.png")

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------
# COMPETITOR CARD
# ---------------------------------------------------
with st.container():
    st.markdown('<div class="adgen-card">', unsafe_allow_html=True)

    st.markdown(f"### {L['competitor_scan']}")
    competitor_name = st.text_input(
        label="",
        key="competitor_name",
        placeholder=L["competitor_placeholder"],
        label_visibility="collapsed"
    )

    if st.button("🔍 " + L["btn_scan"]):
        with st.spinner(L["comp_scan_spinner"]):
            res = scan_competitors(competitor_name, comp_lang)
            st.write(res)

    st.markdown('</div>', unsafe_allow_html=True)

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
# MULTI-LANGUAGE SYSTEM (TR + EN + DUAL)
# ---------------------------------------------------
LANG = {
    "tr": {
        "title": "AdGen – Yapay Zeka Reklam Üretici",
        "subtitle": "KOBİ'ler ve markalar için metin, görsel ve rakip analizi.",
        "language": "Dil",
        "product": "Ürün / Hizmet",
        "audience": "Hedef Kitle",
        "platform": "Platform",
        "tone": "Üslup",
        "generate_text": "Reklam Metni Üret",
        "generate_prompt": "Görsel Tasarım Promptu",
        "generate_image": "AI Görseli Üret",
        "competitor_scan": "Rakip Analizi",
        "competitor_placeholder": "Rakip analizi için ürün adı...",
        "output_competitor": "Rakip Analizi Sonuçları",
        "warning_fill": "⚠ Lütfen gerekli alanları doldurun.",
        "down_img": "Görseli İndir"
    },
    "en": {
        "title": "AdGen – AI Advertising Generator",
        "subtitle": "Text, visual and competitor intelligence for SMEs and brands.",
        "language": "Language",
        "product": "Product / Service",
        "audience": "Target Audience",
        "platform": "Platform",
        "tone": "Tone",
        "generate_text": "Generate Ad Copy",
        "generate_prompt": "Generate Visual Prompt",
        "generate_image": "Generate AI Image",
        "competitor_scan": "Competitor Scan",
        "competitor_placeholder": "Product name for competitor analysis...",
        "output_competitor": "Competitor Analysis Result",
        "warning_fill": "⚠ Please fill all required fields.",
        "down_img": "Download Image"
    }
}

# ---------------------------------------------------
# LANGUAGE SELECTOR
# ---------------------------------------------------
ui_language = st.selectbox("Language", ["Türkçe", "English", "Dual (TR + EN)"])

if ui_language == "Türkçe":
    L = LANG["tr"]
    output_mode = "tr"
elif ui_language == "English":
    L = LANG["en"]
    output_mode = "en"
else:
    L = LANG["tr"]
    output_mode = "dual"


# ---------------------------------------------------
# GEMINI CONFIG (Your API Key)
# ---------------------------------------------------
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# We will use Gemini Pro (web-browsing enabled)
model = genai.GenerativeModel("models/gemini-pro")


# ---------------------------------------------------
# CUSTOM UI CSS (Modern Clean Design)
# ---------------------------------------------------
def inject_custom_css():
    st.markdown(
        """
        <style>
        .stApp {
            background: #f6f8fc;
            font-family: Inter, -apple-system, BlinkMacSystemFont, sans-serif;
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
            margin-top: -7px;
        }
        .field-label {
            font-size: 0.9rem;
            font-weight: 600;
            color: #374151;
            margin-bottom: 0.25rem;
        }
        .button-row button {
            border-radius: 999px !important;
            padding: 0.55rem 1.2rem !important;
            font-weight: 600;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

inject_custom_css()
# ---------------------------------------------------
# SAFE TEXT EXTRACTOR (Gemini bazen farklı format döndürüyor)
# ---------------------------------------------------
def extract_text_safe(response):
    if hasattr(response, "text") and response.text:
        return response.text.strip()

    # candidates -> parts formatı
    if hasattr(response, "candidates") and response.candidates:
        cand = response.candidates[0]
        if hasattr(cand, "content") and hasattr(cand.content, "parts"):
            if cand.content.parts and hasattr(cand.content.parts[0], "text"):
                txt = cand.content.parts[0].text
                if txt:
                    return txt.strip()

    return ""


# ---------------------------------------------------
# COMPETITOR SEARCH (Gemini Web Browsing)
# ---------------------------------------------------
def competitor_web_search(product_name, output_mode):
    """
    Gemini Pro web browsing kullanarak internetteki rakip marka verilerini toplar.
    """
    query = f"""
    Search the web for competing brands, ads, slogans and marketing messages related to:
    '{product_name}'.

    Return:
    - Top competing brands
    - Example ad slogans found online
    - Common keywords observed in ads
    - Any notable advertising styles
    - Web sources summary

    IMPORTANT:
    - Output MUST be in English only (this is a raw data step).
    """

    response = model.generate_content(query)
    return extract_text_safe(response)


# ---------------------------------------------------
# COMPETITOR ANALYSIS (AI-driven marketing insights)
# ---------------------------------------------------
def competitor_analysis(raw_data, product_name, output_mode):
    """
    Toplanan web verisini dil seçimine göre analiz eder.
    TR / EN / Dual çıktı üretir.
    """

    # ---------------------------------------------------
    # TR Output
    # ---------------------------------------------------
    analysis_tr = f"""
Aşağıdaki web verisine dayanarak kapsamlı bir rakip analizi oluştur:

VERİ:
{raw_data}

ÇIKTIDA ŞUNLAR OLSUN (TÜRKÇE):
1) Rakipler listesi
2) Rakiplerin kullandığı en güçlü 10 slogan
3) En çok geçen reklam kelimeleri
4) Reklam tonu analizi (örnek cümlelerle)
5) Rakiplerin güçlü + zayıf yönleri
6) Pazardaki boşluklar (market gaps)
7) '{product_name}' için 3 farklılaşma stratejisi
"""

    # ---------------------------------------------------
    # EN Output
    # ---------------------------------------------------
    analysis_en = f"""
Based on the following web data, generate a full competitor analysis:

DATA:
{raw_data}

OUTPUT SECTIONS (ENGLISH):
1) List of competitors
2) Top 10 slogans competitors use
3) Most common advertising keywords
4) Tone of ads (with example lines)
5) Strengths + weaknesses of competitors
6) Market gaps
7) 3 differentiation strategies for '{product_name}'
"""

    result_tr = model.generate_content(analysis_tr)
    result_en = model.generate_content(analysis_en)

    txt_tr = extract_text_safe(result_tr)
    txt_en = extract_text_safe(result_en)

    # ---------------------------------------------------
    # OUTPUT MODE HANDLING
    # ---------------------------------------------------
    if output_mode == "tr":
        return f"🇹🇷 **Türkçe Rekabet Analizi**\n\n{txt_tr}"

    elif output_mode == "en":
        return f"🇬🇧 **English Competitor Analysis**\n\n{txt_en}"

    else:
        return f"""
🇹🇷 **Türkçe Rekabet Analizi**  
{txt_tr}

---

🇬🇧 **English Competitor Analysis**  
{txt_en}
"""
# ---------------------------------------------------
# AD TEXT & VISUAL PROMPT HELPERS (MULTILINGUAL)
# ---------------------------------------------------
def build_ad_text_prompt(product, audience, platform, tone, output_mode):
    if output_mode == "tr":
        return f"""
Sen bir dijital pazarlama uzmanısın.

Ürün: {product}
Hedef kitle: {audience}
Platform: {platform}
Üslup: {tone}

Aşağıdaki formatta reklam içeriği oluştur:

- 3 kısa başlık
- 2 farklı reklam metni (A/B testi için)
- Kampanya sloganı
- 8 hashtag
"""
    if output_mode == "en":
        return f"""
You are a senior digital marketing expert.

Product: {product}
Target audience: {audience}
Platform: {platform}
Tone: {tone}

Create the following:

- 3 short headlines
- 2 different ad copies (for A/B testing)
- 1 campaign slogan
- 8 hashtags
"""
    # dual
    return f"""
You are a bilingual senior digital marketing specialist.

Generate TWO VERSIONS of the same ad content:

=========================
🇹🇷 TURKISH VERSION
=========================

Ürün: {product}
Hedef kitle: {audience}
Platform: {platform}
Üslup: {tone}

- 3 kısa başlık
- 2 farklı reklam metni
- Kampanya sloganı
- 8 hashtag

=========================
🇬🇧 ENGLISH VERSION
=========================

Product: {product}
Target audience: {audience}
Platform: {platform}
Tone: {tone}

- 3 short headlines
- 2 different ad copies
- 1 campaign slogan
- 8 hashtags

OUTPUT FORMAT:
Write both languages clearly separated.
Do NOT mix languages.
"""


def build_visual_prompt(product, audience, platform, tone, output_mode):
    if output_mode == "tr":
        return f"""
Sen bir reklam görseli tasarım uzmanısın.

Ürün: {product}
Hedef kitle: {audience}
Platform: {platform}
Üslup: {tone}

Reklam görseli için aşağıdaki başlıklara göre detaylı bir tasarım açıklaması yap:

1) Kompozisyon (ürünün konumu, kadraj)
2) Arka plan (mekan, doku, ortam)
3) Işıklandırma (yumuşak, sert, dramatik vs.)
4) Renk paleti
5) Kamera açısı (yakın plan, üstten, göz hizası vb.)
6) Dilersen Stable Diffusion / SDXL için tek satırlık İngilizce prompt örneği de ver.
"""
    if output_mode == "en":
        return f"""
You are an advertising visual designer.

Product: {product}
Target audience: {audience}
Platform: {platform}
Tone: {tone}

Describe a detailed visual design for an ad under these sections:

1) Composition (where the product is placed)
2) Background (environment, texture, scene)
3) Lighting (soft, dramatic, studio, natural, etc.)
4) Color palette
5) Camera angle (close-up, eye level, top view, etc.)
6) Optionally, provide a single-line SDXL / Stable Diffusion prompt.
"""
    # dual
    return f"""
You are a bilingual advertising visual designer.

Create a visual concept in TWO SECTIONS:

=========================
🇹🇷 TÜRKÇE AÇIKLAMA
=========================

Ürün: {product}
Hedef kitle: {audience}
Platform: {platform}
Üslup: {tone}

1) Kompozisyon
2) Arka plan
3) Işıklandırma
4) Renk paleti
5) Kamera açısı

=========================
🇬🇧 ENGLISH DESCRIPTION
=========================

Product: {product}
Target audience: {audience}
Platform: {platform}
Tone: {tone}

1) Composition
2) Background
3) Lighting
4) Color palette
5) Camera angle
6) One SDXL-style English prompt line.
"""


# ---------------------------------------------------
# (OPSİYONEL) IMAGE GENERATION PLACEHOLDER
# Burada Stability veya başka bir görsel API ile entegrasyon yapılabilir.
# Şimdilik sadece "yakında" mesajı göstereceğiz.
# ---------------------------------------------------


# ---------------------------------------------------
# MAIN UI
# ---------------------------------------------------
# Başlık
st.markdown(
    f"""
    <div class="adgen-header">
        <div class="adgen-title">{L["title"]}</div>
        <div class="adgen-subtitle">{L["subtitle"]}</div>
    </div>
    """,
    unsafe_allow_html=True
)

# Ana kart: Reklam Metni + Görsel Prompt
with st.container():
    st.markdown('<div class="adgen-card">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f'<div class="field-label">{L["product"]}</div>', unsafe_allow_html=True)
        product = st.text_input(
            "product",
            label_visibility="collapsed",
            placeholder="Handmade soap" if ui_language == "English" else "Örn: El yapımı sabun"
        )

        st.markdown(f'<div class="field-label">{L["platform"]}</div>', unsafe_allow_html=True)
        platform = st.selectbox(
            "platform_sel",
            ["Instagram", "TikTok", "LinkedIn", "Facebook"],
            label_visibility="collapsed"
        )

    with col2:
        st.markdown(f'<div class="field-label">{L["audience"]}</div>', unsafe_allow_html=True)
        audience = st.text_input(
            "audience",
            label_visibility="collapsed",
            placeholder="e.g. young adults, coffee lovers"
            if ui_language == "English"
            else "Örn: genç yetişkinler, kahve severler"
        )

        st.markdown(f'<div class="field-label">{L["tone"]}</div>', unsafe_allow_html=True)
        if ui_language == "English":
            tone = st.selectbox(
                "tone",
                ["Playful", "Professional", "Friendly", "Persuasive"],
                label_visibility="collapsed"
            )
        else:
            tone = st.selectbox(
                "tone_tr",
                ["Eğlenceli", "Profesyonel", "Samimi", "İkna Edici"],
                label_visibility="collapsed"
            )

    st.markdown("---")

    # Butonlar
    c1, c2, c3 = st.columns(3)
    with c1:
        btn_text = st.button(L["generate_text"])
    with c2:
        btn_visual = st.button(L["generate_prompt"])
    with c3:
        btn_image = st.button(L["generate_image"])

    # Reklam metni üretimi
    if btn_text:
        if not product or not audience:
            st.warning(L["warning_fill"])
        else:
            with st.spinner("Metin üretiliyor..." if ui_language != "English" else "Generating ad copy..."):
                try:
                    prompt_text = build_ad_text_prompt(product, audience, platform, tone, output_mode)
                    res = model.generate_content(prompt_text)
                    txt = extract_text_safe(res)

                    st.markdown('<div class="output-box">', unsafe_allow_html=True)
                    st.subheader(L["generate_text"])
                    st.write(txt)
                    st.markdown('</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Hata: {e}")

    # Görsel tasarım promptu
    if btn_visual:
        if not product or not audience:
            st.warning(L["warning_fill"])
        else:
            with st.spinner("Görsel tasarım fikri hazırlanıyor..." if ui_language != "English"
                            else "Generating visual design prompt..."):
                try:
                    prompt_vis = build_visual_prompt(product, audience, platform, tone, output_mode)
                    res = model.generate_content(prompt_vis)
                    txt = extract_text_safe(res)

                    st.markdown('<div class="output-box">', unsafe_allow_html=True)
                    st.subheader(L["generate_prompt"])
                    st.write(txt)
                    st.markdown('</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Hata: {e}")

    # Görsel üretimi (şimdilik placeholder)
    if btn_image:
        st.info(
            "Görsel üretim modülü şu an için devre dışı. "
            "Stability / HuggingFace entegrasyonu ile tekrar aktifleştirilebilir."
            if ui_language != "English"
            else "Image generation module is currently disabled. It can be re-enabled with Stability / HuggingFace integration."
        )

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

    product_comp = st.text_input(
        "competitor_product",
        label_visibility="collapsed",
        placeholder=L["competitor_placeholder"]
    )

    btn_comp = st.button("🔍 " + (L["competitor_scan"] if ui_language != "English" else "Scan Competitors"))

    if btn_comp:
        if not product_comp:
            st.warning(L["warning_fill"])
        else:
            with st.spinner("Web'den rakipler taranıyor..." if ui_language != "English"
                            else "Scanning competitors on the web..."):
                try:
                    raw = competitor_web_search(product_comp, output_mode)
                except Exception as e:
                    st.error(f"Web taraması sırasında hata oluştu: {e}")
                    raw = ""

            if not raw:
                st.error("Web sonuçları alınamadı, lütfen daha genel bir ürün adı deneyin."
                         if ui_language != "English"
                         else "Could not retrieve web results, please try a broader product name.")
            else:
                with st.spinner("Rakip analizi hazırlanıyor..." if ui_language != "English"
                                else "Preparing competitor analysis..."):
                    try:
                        comp_result = competitor_analysis(raw, product_comp, output_mode)
                        st.markdown('<div class="output-box">', unsafe_allow_html=True)
                        st.subheader(L["output_competitor"])
                        st.write(comp_result)
                        st.markdown('</div>', unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Analiz sırasında hata oluştu: {e}")

    st.markdown('</div>', unsafe_allow_html=True)

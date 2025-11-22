import streamlit as st
import google.generativeai as genai

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
        "image_info": "Görsel üretim modülü şu an devre dışı. İstenirse Stability / HuggingFace entegrasyonu yeniden eklenebilir."
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
        "image_info": "Image generation module is currently disabled. It can be re-enabled with Stability / HuggingFace integration."
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
    output_mode = "tr"   # metin çıktı dili
    comp_lang = "tr"
elif ui_language == "English":
    L = LANG["en"]
    output_mode = "en"
    comp_lang = "en"
else:
    # UI Türkçe, içerik hem TR hem EN
    L = LANG["tr"]
    output_mode = "dual"
    comp_lang = "tr"   # rakip analizi Türkçe olsun, istersen "en" yapabiliriz

# ---------------------------------------------------
# GEMINI CONFIG
# ---------------------------------------------------
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Tek model: Gemini 2.5 Flash (metin + rekabet analizi için)
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
            if cand.content.parts and hasattr(cand.content.parts[0], "text"):
                txt = cand.content.parts[0].text
                if txt:
                    return txt.strip()

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
- 2 different ad copies (for A/B testing)
- 1 campaign slogan
- 8 hashtags
"""
    # dual (TR + EN)
    return f"""
You are a bilingual senior digital marketing specialist.

Generate TWO versions of the same ad content.

=========================
🇹🇷 TURKISH VERSION
=========================

Ürün: {product}
Hedef kitle: {audience}
Platform: {platform}
Üslup: {tone}

- 3 kısa başlık
- 2 farklı reklam metni
- 1 kampanya sloganı
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

Keep Turkish and English clearly separated.
"""


# ---------------------------------------------------
# VISUAL DESIGN PROMPT BUILDER (TR / EN / DUAL)
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

1) Kompozisyon (ürünün konumu, kadraj)
2) Arka plan (mekan, doku, ortam)
3) Işıklandırma (yumuşak, sert, dramatik vs.)
4) Renk paleti
5) Kamera açısı (yakın plan, üstten, göz hizası vb.)
6) İsteğe bağlı: Stable Diffusion / SDXL için tek satırlık İngilizce prompt örneği.
"""
    if mode == "en":
        return f"""
You are an advertising visual designer.

Product: {product}
Target audience: {audience}
Platform: {platform}
Tone: {tone}

Describe a detailed visual design for an ad:

1) Composition (where the product is placed)
2) Background (environment, texture, scene)
3) Lighting (soft, studio, dramatic, natural)
4) Color palette
5) Camera angle (close-up, eye level, top view)
6) Optional: a single-line SDXL / Stable Diffusion prompt.
"""
    # dual
    return f"""
You are a bilingual advertising visual designer.

Create a visual concept in TWO SECTIONS.

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
# COMPETITOR SCAN (NO RAW URLS, STRATEGIC SUMMARY)
# ---------------------------------------------------
def scan_competitors(product_name, lang="tr"):
    """
    Competitive intelligence using Gemini 2.5 Flash.
    Burada gerçek web bilgisini kullanarak özetleyici / çıkarımsal bir analiz yapmasını istiyoruz.
    """

    if lang == "tr":
        prompt = f"""
Sen bir rekabet analizi ve pazarlama stratejisi uzmanısın.

Görevin:
- İnternetten '{product_name}' ile ilgili markalar, rakipler ve reklam örnekleri hakkında genel bir fikir edinmek
- Web sonuçlarını birebir listelemek yerine, genelleştirilmiş çıkarımlar yaparak özetlemek

ÇIKTI BÖLÜMLERİ (TAMAMI TÜRKÇE OLSUN):

1) Öne çıkan rakip marka türleri
2) Rakiplerin sıklıkla kullandığı slogan ve mesaj temaları
3) Reklamlarda en çok vurgulanan özellikler (örnek cümlelerle)
4) Reklam tonu (samimi, premium, eğlenceli, ciddi vb.) ve örnekler
5) Sektörde fark edilen temel trendler
6) Pazarda görülen boşluklar (market gaps)
7) '{product_name}' için 3 net farklılaşma / konumlandırma önerisi (USP)

URL veya spesifik site ismi verme, özet analiz yap.
"""
    else:
        prompt = f"""
You are a competitive intelligence and marketing strategy expert.

Your task:
- Reason about the web for brands, competitors and ad examples related to '{product_name}'
- Instead of listing raw URLs, provide synthesized insights and patterns

OUTPUT SECTIONS (ENGLISH):

1) Types of key competitor brands
2) Common slogan and message themes competitors use
3) Most emphasized features in ads (with example lines)
4) Overall ad tone (friendly, premium, playful, serious) + examples
5) Major trends observed in the category
6) Market gaps and underserved needs
7) 3 clear differentiation / positioning strategies (USP) for '{product_name}'

Do NOT output raw URLs. Provide a concise but insightful analysis.
"""

    try:
        response = text_model.generate_content(prompt)
        return extract_text_safe(response)
    except Exception as e:
        return f"Competitor scan error: {e}"


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
# MAIN CARD – AD TEXT + VISUAL PROMPT
# ---------------------------------------------------
with st.container():
    st.markdown('<div class="adgen-card">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f'<div class="field-label">{L["product"]}</div>', unsafe_allow_html=True)
        product = st.text_input(
            "product",
            label_visibility="collapsed",
            placeholder="Handmade soap" if ui_language == "English" else "Örn: el yapımı sabun"
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

    c1, c2, c3 = st.columns(3)
    with c1:
        btn_text = st.button(L["generate_text"])
    with c2:
        btn_visual = st.button(L["generate_prompt"])
    with c3:
        btn_image = st.button(L["generate_image"])

    # Ad copy
    if btn_text:
        if not product or not audience:
            st.warning(L["warning_fill"])
        else:
            with st.spinner(L["adcopy_spinner"]):
                try:
                    p = build_ad_text_prompt(product, audience, platform, tone, output_mode)
                    r = text_model.generate_content(p)
                    txt = extract_text_safe(r)
                    st.markdown('<div class="output-box">', unsafe_allow_html=True)
                    st.subheader(L["generate_text"])
                    st.write(txt)
                    st.markdown('</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Hata / Error: {e}")

    # Visual prompt
    if btn_visual:
        if not product or not audience:
            st.warning(L["warning_fill"])
        else:
            with st.spinner(L["visual_spinner"]):
                try:
                    p = build_visual_prompt(product, audience, platform, tone, output_mode)
                    r = text_model.generate_content(p)
                    txt = extract_text_safe(r)
                    st.markdown('<div class="output-box">', unsafe_allow_html=True)
                    st.subheader(L["generate_prompt"])
                    st.write(txt)
                    st.markdown('</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Hata / Error: {e}")

    # Image placeholder
    if btn_image:
        st.info(L["image_info"])

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
                raw = scan_competitors(competitor_name, comp_lang)

            if not raw:
                st.error(
                    "Web sonuçları alınamadı, lütfen daha genel bir ürün / kategori adı deneyin."
                    if comp_lang == "tr"
                    else "Could not retrieve useful insights, please try a broader product/category."
                )
            else:
                st.markdown('<div class="output-box">', unsafe_allow_html=True)
                st.subheader(L["output_competitor"])
                st.write(raw)
                st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

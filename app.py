import streamlit as st
import wikipedia
import requests
import random

# ==========================================
# 1. 配置区域
# ==========================================
PEXELS_API_KEY = "SmnlcdOVoFqWd4dyrh92DsIwtmSUqfgQqKiiDgcsi8xKYxov4HYfEE26"
UNSPLASH_ACCESS_KEY = "WLSYgnTBqCLjqXlQeZe04M5_UVsfJBRzgDOcdAkG2sE"

# ==========================================
# 2. CSS 样式 (对齐、字体、排版)
# ==========================================
def local_css():
    st.markdown("""
    <style>
        /* --- 1. 布局与对齐 --- */
        /* 搜索栏横向对齐微调 */
        div[data-testid="column"] [data-testid="stCheckbox"] { margin-top: 12px; }
        div[data-testid="column"] [data-testid="stRadio"] { margin-top: 8px; }

        /* --- 2. 按钮样式 --- */
        /* 基础胶囊按钮 */
        div[data-testid="column"] .stButton button {
            width: 100%;
            min-height: 45px;
            border-radius: 8px;
            border: 1px solid #f0f0f0;
            background-color: #fff;
            color: #444;
            font-size: 13px;
            font-weight: 500;
            transition: all 0.2s;
        }
        div[data-testid="column"] .stButton button:hover {
            border-color: #002FA7;
            color: #002FA7;
            background-color: #f8faff;
            transform: translateY(-2px);
            box-shadow: 0 2px 8px rgba(0,47,167,0.1);
        }

        /* --- 3. 字体系统 --- */
        .main-title {
            font-family: "PingFang SC", "Helvetica Neue", sans-serif;
            font-size: 3.2em; color: #111; text-align: center; 
            margin-top: -20px; margin-bottom: 0px; font-weight: 900; letter-spacing: -1px;
        }
        .sub-title {
            text-align: center; color: #888; font-size: 0.9em; 
            margin-bottom: 45px; font-weight: 500; letter-spacing: 3px; text-transform: uppercase;
        }
        
        /* 分类标题样式 (强制居中) */
        .category-header {
            text-align: center;
            font-size: 12px;
            color: #999;
            font-weight: 700;
            letter-spacing: 1px;
            margin-bottom: 15px;
            text-transform: uppercase;
            border-bottom: 2px solid #f0f0f0;
            padding-bottom: 8px;
            display: block;
        }

        /* --- 4. 图片瀑布流 --- */
        div[data-testid="stImage"] img {
            height: 450px !important; object-fit: cover !important; 
            border-radius: 8px !important; width: 100% !important;
        }

        /* --- 5. 组件细节 --- */
        /* 克莱因蓝 Radio */
        div[role="radiogroup"] > label > div:first-child { background-color: #f0f2f6; border: 1px solid #dce0e6; }
        div[role="radiogroup"] > label[data-baseweb="radio"] > div:first-child {
            background-color: #002FA7 !important; border-color: #002FA7 !important;
        }
        /* Pinterest 按钮 */
        .pinterest-btn {
            display: inline-block; text-decoration: none; background-color: #E60023;
            color: white !important; padding: 8px 15px; border-radius: 20px;
            font-weight: bold; font-size: 12px; margin-top: 10px; transition: all 0.3s;
        }
        .pinterest-btn:hover { background-color: #ad081b; transform: translateY(-2px); }

        #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. 视觉优化字典 (Soul/Higgsfield 风格库)
# ==========================================
VISUAL_DICT = {
    # --- 🔥 TRENDING ---
    "retro futurism": "retro futurism aesthetic 80s sci-fi neon synthwave chrome",
    "old money": "old money aesthetic fashion luxury ralph lauren style quiet luxury",
    "y2k": "y2k aesthetic fashion 2000s futuristic metallic shiny pink",
    "cottagecore": "cottagecore aesthetic nature flowers vintage dress picnic sunlight",
    "gorpcore": "gorpcore fashion north face arc'teryx outdoor hiking aesthetic",
    "mob wife": "mob wife aesthetic fur coat leopard print sunglasses luxury",

    # --- 👘 FASHION ---
    "kimono": "japanese woman wearing traditional kimono kyoto street portrait",
    "hanfu": "traditional chinese hanfu dress portrait ethereal fairy style",
    "sari": "indian woman wearing colorful saree portrait jewelry",
    "qipao": "woman wearing chinese qipao shanghai vintage style portrait",
    "kilt": "scottish man wearing traditional kilt tartan highlands",
    "flamenco": "spanish flamenco dancer woman red dress motion",

    # --- 🏛️ ARCHITECTURE ---
    "bauhaus": "bauhaus architecture building geometric minimal white",
    "gothic": "gothic cathedral architecture detail spires dark moody",
    "santorini": "santorini greece white houses blue domes aegean sea",
    "brutalist": "brutalist architecture concrete building monumental",
    "pagoda": "asian pagoda temple architecture kyoto red autumn",
    "art deco": "art deco architecture building new york gold detail",

    # --- 🎨 POP CULTURE ---
    "k-pop": "korean idol concert performance fashion stage lighting",
    "cyberpunk": "neon lights tokyo night futuristic rain high contrast",
    "zen": "japanese zen garden rocks moss water meditation peaceful",
    "hollywood": "hollywood sign los angeles sunset vintage cinema aesthetic",
    "bollywood": "bollywood dance scene colorful costume india movie",
    "steampunk": "steampunk fashion machinery gears victorian goggles",

    # --- ✨ NICHE / SOUL / HIGGSFIELD AESTHETICS ---
    "frutiger aero": "frutiger aero aesthetic glossy water bubbles windows xp futuristic 2000s",
    "dreamcore": "dreamcore aesthetic surreal liminal space weird nostalgic eyes",
    "solarpunk": "solarpunk architecture nature green plants futuristic city sunlight",
    "acid pixie": "acid pixie aesthetic fairy grunge neon glitch psychedelic",
    "dark academia": "dark academia aesthetic library books coffee rain vintage fashion",
    "light academia": "light academia aesthetic museum art statues beige sunlight",
    "vaporwave": "vaporwave aesthetic greek statue pink purple neon glitch 80s",
    "liminal space": "liminal space empty hallway fluorescent lights eerie nostalgic",
    "glitch core": "glitch art aesthetic datamosh rgb split digital distortion",
    "bioluminescence": "bioluminescence nature glowing mushrooms forest night blue neon",
    "chromatic": "chromatic aberration prism light rainbow reflection glass photography",
    "knolling": "knolling photography objects organized neatly flat lay overhead"
}

# ==========================================
# 4. 搜图引擎逻辑
# ==========================================
def get_visuals(source, user_query, uhd_mode, per_page=15):
    clean_query = user_query.lower().strip()
    is_optimized = False
    
    if clean_query in VISUAL_DICT:
        search_term = VISUAL_DICT[clean_query]
        is_optimized = True
    else:
        search_term = f"{user_query} aesthetic"

    if source == "Pexels":
        photos, error = _fetch_pexels(search_term, uhd_mode, per_page)
    else:
        photos, error = _fetch_unsplash(search_term, uhd_mode, per_page)
        
    return photos, error, search_term, is_optimized

def _fetch_pexels(query, uhd_mode, per_page):
    headers = {"Authorization": PEXELS_API_KEY}
    url = "https://api.pexels.com/v1/search"
    params = {"query": query, "per_page": per_page, "orientation": "portrait", "locale": "en-US"}
    try:
        res = requests.get(url, headers=headers, params=params)
        if res.status_code == 200:
            raw = res.json().get("photos", [])
            filtered = [p for p in raw if (min(p['width'], p['height']) > 1500)] if uhd_mode else raw
            final = filtered[:9]
            return [{
                "src": p['src']['large2x'], "url": p['url'], 
                "alt": p['alt'] or "Pexels Image", "res": f"{p['width']}x{p['height']}"
            } for p in final], None
        return [], f"Pexels Error: {res.status_code}"
    except Exception as e:
        return [], str(e)

def _fetch_unsplash(query, uhd_mode, per_page):
    headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
    url = "https://api.unsplash.com/search/photos"
    params = {"query": query, "per_page": per_page, "orientation": "portrait"}
    try:
        res = requests.get(url, headers=headers, params=params)
        if res.status_code == 200:
            raw = res.json().get("results", [])
            filtered = [p for p in raw if (min(p['width'], p['height']) > 1500)] if uhd_mode else raw
            final = filtered[:9]
            return [{
                "src": p['urls']['regular'], "url": p['links']['html'], 
                "alt": p['alt_description'] or p['description'] or "Unsplash", "res": f"{p['width']}x{p['height']}"
            } for p in final], None
        elif res.status_code == 403: return [], "⚠️ Unsplash Limit Reached"
        return [], f"Unsplash Error: {res.status_code}"
    except Exception as e:
        return [], str(e)

def get_wiki_summary(query):
    try:
        wikipedia.set_lang("en")
        res = wikipedia.search(query)
        if res:
            page = wikipedia.page(res[0], auto_suggest=False)
            return page.summary[0:600] + "...", page.url, res[0]
        return None, "#", None
    except: return None, "#", None

# ==========================================
# 5. 页面主程序
# ==========================================
st.set_page_config(page_title="Visual Moodboard", page_icon="🎨", layout="wide")
local_css()

st.markdown("<h1 class='main-title'>全球视觉文化 Moodboard</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Global Visual Culture Moodboard</p>", unsafe_allow_html=True)

if 'search_query' not in st.session_state:
    st.session_state.search_query = ""

# --- 1. 核心分类网格 (4列布局) ---
with st.container():
    # 使用 4 列，Trending 放第一个
    c1, c2, c3, c4 = st.columns(4, gap="medium")

    def create_grid(column, title, emoji, items):
        with column:
            # 自定义居中标题
            st.markdown(f"<div class='category-header'>{emoji} {title}</div>", unsafe_allow_html=True)
            # 内部 2x3 布局
            sc1, sc2 = st.columns(2)
            for i, (label, val) in enumerate(items):
                target = sc1 if i % 2 == 0 else sc2
                if target.button(label, key=f"btn_{val}_{i}"):
                    st.session_state.search_query = val
                    st.rerun()

    # 数据定义
    trending = [("Retro Futurism", "retro futurism"), ("Old Money", "old money"), ("Y2K", "y2k"), ("Cottagecore", "cottagecore"), ("Gorpcore", "gorpcore"), ("Mob Wife", "mob wife")]
    fashion = [("Kimono", "kimono"), ("Hanfu", "hanfu"), ("Sari", "sari"), ("Qipao", "qipao"), ("Kilt", "kilt"), ("Flamenco", "flamenco")]
    arch = [("Bauhaus", "bauhaus"), ("Gothic", "gothic"), ("Santorini", "santorini"), ("Brutalist", "brutalist"), ("Pagoda", "pagoda"), ("Art Deco", "art deco")]
    culture = [("K-Pop", "k-pop"), ("Cyberpunk", "cyberpunk"), ("Zen", "zen"), ("Hollywood", "hollywood"), ("Bollywood", "bollywood"), ("Steampunk", "steampunk")]

    create_grid(c1, "TRENDING", "🔥", trending)
    create_grid(c2, "LOCAL FASHION", "👘", fashion)
    create_grid(c3, "ARCHITECTURE", "🏛️", arch)
    create_grid(c4, "POP CULTURE", "🎨", culture)

# --- 2. 灵感探索 (More Button) ---
st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)
with st.expander("✨ Explore Niche Aesthetics (Click to Generate)"):
    st.caption("Curated aesthetic styles inspired by Higgsfield/Soul models.")
    
    # 灵感词云 (Tag Cloud)
    soul_tags =

import streamlit as st
import wikipedia
import requests
import random
from itertools import zip_longest

# ==========================================
# 1. 配置区域
# ==========================================
PEXELS_API_KEY = "SmnlcdOVoFqWd4dyrh92DsIwtmSUqfgQqKiiDgcsi8xKYxov4HYfEE26"
UNSPLASH_ACCESS_KEY = "WLSYgnTBqCLjqXlQeZe04M5_UVsfJBRzgDOcdAkG2sE"

# ==========================================
# 2. CSS 样式
# ==========================================
def local_css():
    st.markdown("""
    <style>
        /* --- 布局与对齐 --- */
        div[data-testid="column"] [data-testid="stCheckbox"] { margin-top: 12px; }

        /* --- 按钮样式 (顶部主分类) --- */
        /* 默认按钮样式，用于顶部的胶囊按钮 */
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

        /* --- 字体系统 --- */
        .main-title {
            font-family: "PingFang SC", "Helvetica Neue", sans-serif;
            font-size: 3.2em; color: #111; text-align: center; 
            margin-top: -20px; margin-bottom: 0px; font-weight: 900; letter-spacing: -1px;
        }
        .sub-title {
            text-align: center; color: #888; font-size: 0.9em; 
            margin-bottom: 30px; font-weight: 500; letter-spacing: 3px; text-transform: uppercase;
        }
        .category-header {
            text-align: center; font-size: 12px; color: #999; font-weight: 700;
            letter-spacing: 1px; margin-bottom: 15px; text-transform: uppercase;
            border-bottom: 2px solid #f0f0f0; padding-bottom: 8px; display: block;
        }

        /* --- 图片瀑布流 --- */
        div[data-testid="stImage"] img {
            height: 450px !important; object-fit: cover !important; 
            border-radius: 8px !important; width: 100% !important;
        }

        /* --- Pinterest 按钮 --- */
        .pinterest-btn {
            display: block; text-align: center; text-decoration: none; background-color: #E60023;
            color: white !important; padding: 10px 0; border-radius: 8px;
            font-weight: bold; font-size: 12px; margin-top: 5px; transition: all 0.3s;
        }
        .pinterest-btn:hover { background-color: #ad081b; transform: translateY(-1px); }

        /* --- 来源标签样式 --- */
        .source-badge {
            font-size: 9px; color: #999; text-transform: uppercase; letter-spacing: 0.5px;
            border: 1px solid #eee; padding: 1px 4px; border-radius: 3px;
        }

        #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. 视觉优化字典
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

    # --- ✨ NICHE TAGS ---
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
# 4. 混合搜图引擎逻辑 (9 Pexels + 9 Unsplash)
# ==========================================
def get_visuals(user_query, uhd_mode):
    clean_query = user_query.lower().strip()
    is_optimized = False
    
    if clean_query in VISUAL_DICT:
        search_term = VISUAL_DICT[clean_query]
        is_optimized = True
    else:
        search_term = f"{user_query} aesthetic"

    # 请求更多图片以确保足够筛选 (比如请求 15 张)
    fetch_limit = 15 
    
    p_photos, p_err = _fetch_pexels(search_term, uhd_mode, fetch_limit)
    u_photos, u_err = _fetch_unsplash(search_term, uhd_mode, fetch_limit)
    
    # 各截取前 9 张 (共 18 张)
    p_final = p_photos[:9]
    u_final = u_photos[:9]
    
    # 交叉合并
    combined_photos = []
    for p, u in zip_longest(p_final, u_final):
        if p: combined_photos.append(p)
        if u: combined_photos.append(u)
        
    error_msg = ""
    if p_err and u_err: error_msg = f"APIs Error: {p_err} | {u_err}"
    elif p_err: error_msg = f"Pexels Warning: {p_err}"
    elif u_err: error_msg = f"Unsplash Warning: {u_err}"
        
    return combined_photos, error_msg, search_term, is_optimized

def _fetch_pexels(query, uhd_mode, limit):
    headers = {"Authorization": PEXELS_API_KEY}
    url = "https://api.pexels.com/v1/search"
    params = {"query": query, "per_page": limit, "orientation": "portrait", "locale": "en-US"}
    try:
        res = requests.get(url, headers=headers, params=params)
        if res.status_code == 200:
            raw = res.json().get("photos", [])
            filtered = [p for p in raw if (min(p['width'], p['height']) > 1500)] if uhd_mode else raw
            return [{
                "src": p['src']['large2x'], "url": p['url'], 
                "alt": p['alt'] or "Pexels", "res": f"{p['width']}x{p['height']}",
                "source": "Pexels"
            } for p in filtered], None
        return [], f"Status {res.status_code}"
    except Exception as e:
        return [], str(e)

def _fetch_unsplash(query, uhd_mode, limit):
    headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
    url = "https://api.unsplash.com/search/photos"
    params = {"query": query, "per_page": limit, "orientation": "portrait"}
    try:
        res = requests.get(url, headers=headers, params=params)
        if res.status_code == 200:
            raw = res.json().get("results", [])
            filtered = [p for p in raw if (min(p['width'], p['height']) > 1500)] if uhd_mode else raw
            return [{
                "src": p['urls']['regular'], "url": p['links']['html'], 
                "alt": p['alt_description'] or p['description']

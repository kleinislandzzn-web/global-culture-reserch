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
            display: block; /* 块级元素确保占满宽度 */
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
def get_visuals(source, user_query, uhd_mode, per_page=15

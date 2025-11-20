import streamlit as st
import wikipedia
import requests
import random
from itertools import zip_longest

# ==========================================
# 0. URL 参数处理
# ==========================================
if "q" in st.query_params:
    param_q = st.query_params["q"]
    if param_q:
        st.session_state.search_query = param_q

# ==========================================
# 1. 配置区域
# ==========================================
PEXELS_API_KEY = "SmnlcdOVoFqWd4dyrh92DsIwtmSUqfgQqKiiDgcsi8xKYxov4HYfEE26"
UNSPLASH_ACCESS_KEY = "WLSYgnTBqCLjqXlQeZe04M5_UVsfJBRzgDOcdAkG2sE"

# ==========================================
# 2. CSS 样式 (对齐终极修正)
# ==========================================
def local_css():
    st.markdown("""
    <style>
        /* --- 布局微调 --- */
        div[data-testid="column"] [data-testid="stCheckbox"] { margin-top: 12px; }

        /* --- 1. 主分类按钮 (完美居中对齐) --- */
        div[data-testid="column"] .stButton button {
            width: 100%;
            height: 48px !important; 
            min-height: 48px !important;
            border-radius: 8px;
            border: 1px solid #f0f0f0;
            background-color: #fff;
            color: #444;
            font-size: 13px;
            font-weight: 500;
            transition: all 0.2s;
            /* 核心对齐代码：Flexbox 双重居中 */
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            /* 防止文字换行 */
            white-space: nowrap; 
            overflow: hidden;
            text-overflow: ellipsis;
            /* 消除默认内边距干扰 */
            padding: 0 10px !important;
            margin: 0 auto !important;
        }
        div[data-testid="column"] .stButton button:hover {
            border-color: #002FA7;
            color: #002FA7;
            background-color: #f8faff;
            transform: translateY(-2px);
            box-shadow: 0 2px 8px rgba(0,47,167,0.1);
        }

        /* --- 2. Tag 纯文本链接样式 --- */
        .tag-link {
            display: inline-block;
            color: #999;
            text-decoration: none !important;
            font-size: 12px;
            font-weight: 500;
            margin-right: 12px;
            margin-bottom: 8px;
            font-family: "Helvetica Neue", sans-serif;
            transition: color 0.2s;
            cursor: pointer;
            border-bottom: none !important;
        }
        .tag-link:hover {
            color: #333;
            opacity: 0.8;
        }
        .tag-container {
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
            margin-top: 10px;
        }

        /* --- 字体与标题 --- */
        .main-title {
            font-family: "PingFang SC", "Helvetica Neue", sans-serif;
            font-size: 3.2em; color: #111; text-align: center; 
            margin-top: -20px; margin-bottom: 0px; font-weight: 900; letter-spacing: -1px;
        }
        .sub-title {
            text-align: center; color: #888; font-size: 0.9em; 
            margin-bottom: 30px; font-weight: 500; letter-spacing: 3px; text-transform: uppercase;
        }
        
        /* 分类标题 (对齐修正) */
        .category-header {
            text-align: center; 
            font-size: 12px; 
            color: #999; 
            font-weight: 700;
            letter-spacing: 1px; 
            margin-bottom: 15px; 
            text-transform: uppercase;
            /* 确保分割线宽度适中且居中 */
            border-bottom: 2px solid #f0f0f0; 
            padding-bottom: 8px; 
            display: block;
            height: 25px; 
            line-height: 16px;
            width: 100%; /* 占满列宽以对齐下方的按钮组 */
        }

        /* --- 图片与组件 --- */
        div[data-testid="stImage"] img {
            height: 450px !important; object-fit: cover !important; 
            border-radius: 8px !important; width: 100% !important;
        }
        .pinterest-btn {
            display: inline-block; text-decoration: none; background-color: #E60023;
            color: white !important; padding: 6px 12px; border-radius: 20px;
            font-weight: bold; font-size: 11px; margin-top: 8px; transition: all 0.3s;
        }
        .pinterest-btn:hover { background-color: #ad081b; transform: translateY(-1px); }
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
# 4. 混合搜图引擎逻辑
# ==========================================
def get_visuals(user_query, uhd_mode):
    clean_query = user_query.lower().strip()
    is_optimized = False
    
    if clean_query in VISUAL_DICT:
        search_term = VISUAL_DICT[clean_query]
        is_optimized = True
    else:
        search_term = f"{user_query} aesthetic"

    fetch_limit = 15 
    
    p_photos, p_err = _fetch_pexels(search_term, uhd_mode, fetch_limit)
    u_photos, u_err = _fetch_unsplash(search_term, uhd_mode, fetch_limit)
    
    p_final = p_photos[:9]
    u_final = u_photos[:9]
    
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
                "alt": p['alt_description'] or p['description'] or "Unsplash", "res": f"{p['width']}x{p['height']}",
                "source": "Unsplash"
            } for p in filtered], None
        elif res.status_code == 403: return [], "Limit Reached"
        return [], f"Status {res.status_code}"
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

# --- 1. 搜索栏与设置 ---
c_sp1, c_search, c_opt, c_sp2 = st.columns([2, 4, 1, 2])

with c_search:
    user_input = st.text_input("Search", value=st.session_state.search_query, placeholder="Type concept...", label_visibility="collapsed")
    if user_input: st.session_state.search_query = user_input

with c_opt:
    uhd_mode = st.checkbox("💎 Ultra HD", value=False)

st.markdown("<br>", unsafe_allow_html=True)

# --- 2. 核心分类网格 (4列布局) ---
with st.container():
    c1, c2, c3, c4 = st.columns(4, gap="medium")

    def create_grid(column, title, emoji, items):
        with column:
            st.markdown(f"<div class='category-header'>{emoji} {title}</div>", unsafe_allow_html=True)
            # 关键修正：增加 gap="small" 使左右按钮列紧凑，视觉上居中对齐标题
            sc1, sc2 = st.columns(2, gap="small")
            for i, (label, val) in enumerate(items):
                target = sc1 if i % 2 == 0 else sc2
                if target.button(label, key=f"btn_{val}_{i}"):
                    st.session_state.search_query = val
                    st.rerun()

    trending = [("🚀 Retro Futurism", "retro futurism"), ("💸 Old Money", "old money"), ("💿 Y2K", "y2k"), ("🏡 Cottagecore", "cottagecore"), ("🧗 Gorpcore", "gorpcore"), ("🐆 Mob Wife", "mob wife")]
    fashion = [("👘 Kimono", "kimono"), ("👗 Hanfu", "hanfu"), ("🧣 Sari", "sari"), ("🎋 Qipao", "qipao"), ("🎼 Kilt", "kilt"), ("💃 Flamenco", "flamenco")]
    arch = [("🏢 Bauhaus", "bauhaus"), ("⛪ Gothic", "gothic"), ("🌊 Santorini", "santorini"), ("🧱 Brutalist", "brutalist"), ("⛩️ Pagoda", "pagoda"), ("🗽 Art Deco", "art deco")]
    culture = [("🎤 K-Pop", "k-pop"), ("🤖 Cyberpunk", "cyberpunk"), ("🌿 Zen", "zen"), ("🎬 Hollywood", "hollywood"), ("💃 Bollywood", "bollywood"), ("⚙️ Steampunk", "steampunk")]

    create_grid(c1, "TRENDING", "🔥", trending)
    create_grid(c2, "LOCAL FASHION", "👘", fashion)
    create_grid(c3, "ARCHITECTURE", "🏛️", arch)
    create_grid(c4, "POP CULTURE", "🎨", culture)

st.markdown("<hr>", unsafe_allow_html=True)

# --- 3. 结果渲染 ---
target_query = st.session_state.search_query if st.session_state.search_query else "Retro Futurism"
is_default = not st.session_state.search_query

if target_query:
    with st.spinner(f"Curating visual mix..."):
        wiki_text, wiki_link, wiki_title = get_wiki_summary(target_query)
        photos, error_msg, optimized_term, is_opt = get_visuals(target_query, uhd_mode)
    
    if is_default:
        st.markdown(f"### 🔥 Trending Now: <span style='color:#002FA7'>{target_query.title()}</span>", unsafe_allow_html=True)
    elif is_opt:
        st.success(f"🎨 **Moodboard Optimized:** '{target_query}' ➔ `{optimized_term}`")
    else:
        st.caption(f"🔍 Result: `{optimized_term}`")

    col_left, col_right = st.columns([1, 2.5])
    
    # --- 左侧信息栏 ---
    with col_left:
        st.markdown("### 📖 Context")
        st.caption(f"Topic: {wiki_title if wiki_title else target_query}")
        if wiki_text:
            st.markdown(f"{wiki_text}")
            st.markdown(f"[👉 Read on Wikipedia]({wiki_link})")
        else:
            st.info("Visual exploration mode.") if is_default else st.warning("No context found.")
            
        st.markdown("---")
        st.markdown("### 📌 External")
        pinterest_url = f"https://www.pinterest.com/search/pins/?q={target_query.replace(' ', '%20')}"
        st.markdown(f"<a href='{pinterest_url}' target='_blank' class='pinterest-btn'>Search on Pinterest ↗</a>", unsafe_allow_html=True)

        # --- ✨ Explore Aesthetics (Link Mode) ---
        st.markdown("---")
        st.markdown("### ✨ Explore Aesthetics")
        
        soul_tags = [
            "🫧 #FrutigerAero", "👁️ #Dreamcore", "☀️ #Solarpunk", "🧚‍♀️ #AcidPixie", 
            "📜 #DarkAcademia", "🗿 #Vaporwave", "🚪 #LiminalSpace", "📺 #GlitchCore",
            "🍄 #Bioluminescence", "🌈 #Chromatic", "📸 #Knolling", "🏛️ #LightAcademia"
        ]
        
        tags_html = "<div class='tag-container'>"
        for tag in soul_tags:
            clean_tag = tag.split("#")[-1] 
            tags_html += f"<a href='/?q={clean_tag}' target='_self' class='tag-link' style='text-decoration:none;'>{tag}</a>"
        tags_html += "</div>"
        
        st.markdown(tags_html, unsafe_allow_html=True)

    # --- 右侧图片 ---
    with col_right:
        st.markdown(f"### 🖼️ Visual Board (Mixed Sources)")
        if error_msg: st.warning(error_msg)
        
        if photos:
            img_cols = st.columns(3)
            for idx, photo in enumerate(photos):
                with img_cols[idx % 3]:
                    st.image(photo['src'], use_container_width=True)
                    st.markdown(f"""
                        <div style="font-size:12px; margin-top:8px; margin-bottom:20px;">
                            <div style="display:flex; justify-content:space-between;">
                                <a href="{photo['url']}" target="_blank" style="color:#333; font-weight:bold; text-decoration:none;">⬇️ Download</a>
                                <div>
                                    <span class="source-badge">Via {photo['source']}</span>
                                    <span style="color:#aaa; background:#f4f4f4; padding:1px 4px; border-radius:3px; font-size:9px; margin-left:4px;">{photo.get('res','HD')}</span>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("No images > 1500px found." if uhd_mode else "No visuals found.")

st.markdown("---")
st.markdown("<div class='footer'>Powered by Streamlit | Pexels & Unsplash<br><strong>© 2025 Leki's Arc Inc.</strong></div>", unsafe_allow_html=True)

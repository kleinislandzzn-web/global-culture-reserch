import streamlit as st
import wikipedia
import requests
import random
from itertools import zip_longest

# ==========================================
# 0. URL 参数处理 & 全局配置
# ==========================================
st.set_page_config(page_title="Visual Moodboard", page_icon="🎨", layout="wide")

if "q" in st.query_params:
    param_q = st.query_params["q"]
    if param_q:
        st.session_state.search_query = param_q

if 'search_query' not in st.session_state:
    st.session_state.search_query = ""

# ==========================================
# 1. 配置区域 (已填入 Key)
# ==========================================
PEXELS_API_KEY = "SmnlcdOVoFqWd4dyrh92DsIwtmSUqfgQqKiiDgcsi8xKYxov4HYfEE26"
UNSPLASH_ACCESS_KEY = "WLSYgnTBqCLjqXlQeZe04M5_UVsfJBRzgDOcdAkG2sE"

# ==========================================
# 2. CSS 样式 (简化版)
# ==========================================
def local_css():
    st.markdown("""
    <style>
        /* 隐藏 Streamlit 默认的一些元素 */
        #MainMenu {visibility: hidden;} footer {visibility: hidden;}

        /* --- 标题与分割线 --- */
        .category-header {
            text-align: center; 
            font-size: 13px; 
            color: #999; 
            font-weight: 700;
            letter-spacing: 1.5px; 
            margin-bottom: 12px; 
            text-transform: uppercase;
            padding-bottom: 8px; 
            border-bottom: 2px solid #f0f0f0; 
        }

        /* --- 按钮样式 --- */
        div[data-testid="column"] .stButton button {
            width: 100% !important;
            height: 45px !important;        
            border-radius: 8px;
            border: 1px solid #eee;
            background-color: #fff;
            color: #555;
            font-size: 13px;
            font-weight: 500;
            transition: all 0.2s;
        }
        div[data-testid="column"] .stButton button:hover {
            border-color: #002FA7;
            color: #002FA7;
            background-color: #f8faff;
        }

        /* --- Tag 链接 --- */
        .tag-link {
            display: inline-block; color: #999; text-decoration: none !important;
            font-size: 12px; margin-right: 12px; margin-bottom: 8px;
            transition: color 0.2s;
        }
        .tag-link:hover { color: #333; }
        
        .main-title {
            font-family: "Helvetica Neue", sans-serif;
            font-size: 3em; color: #111; text-align: center; 
            margin-top: -20px; font-weight: 900; letter-spacing: -1px;
        }
        
        .pinterest-btn {
            display: inline-block; text-decoration: none; background-color: #E60023;
            color: white !important; padding: 6px 12px; border-radius: 20px;
            font-weight: bold; font-size: 11px; margin-top: 8px;
        }
        
        /* 定义图片卡片的响应式高度 */
        .moodboard-img {
            height: 400px;
            width: 100%;
            object-fit: cover;
            display: block;
            transition: transform 0.3s ease;
        }
        
        /* 手机端稍微改矮一点，避免占满整个屏幕 */
        @media only screen and (max-width: 768px) {
            .moodboard-img {
                height: 250px;
            }
        }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. 视觉优化字典
# ==========================================
VISUAL_DICT = {
    "niqab": "niqab clothing", "hijab": "hijab clothing", "abaya": "abaya clothing", "burqa": "burqa clothing",
    "retro futurism": "retro futurism aesthetic 80s sci-fi neon synthwave chrome",
    "old money": "old money aesthetic fashion luxury ralph lauren style quiet luxury",
    "y2k": "y2k aesthetic fashion 2000s futuristic metallic shiny pink",
    "cottagecore": "cottagecore aesthetic nature flowers vintage dress picnic sunlight",
    "gorpcore": "gorpcore fashion north face arc'teryx outdoor hiking aesthetic",
    "mob wife": "mob wife aesthetic fur coat leopard print sunglasses luxury",
    "kimono": "kimono clothing", "hanfu": "hanfu clothing", "sari": "sari clothing",
    "qipao": "qipao clothing", "kilt": "kilt clothing", "flamenco": "flamenco dress clothing",
    "bauhaus": "bauhaus architecture building geometric minimal white",
    "gothic": "gothic cathedral architecture detail spires dark moody",
    "santorini": "santorini greece white houses blue domes aegean sea",
    "brutalist": "brutalist architecture concrete building monumental",
    "pagoda": "asian pagoda temple architecture kyoto red autumn",
    "art deco": "art deco architecture building new york gold detail",
    "k-pop": "korean idol concert performance fashion stage lighting",
    "cyberpunk": "neon lights tokyo night futuristic rain high contrast",
    "zen": "japanese zen garden rocks moss water meditation peaceful",
    "hollywood": "hollywood sign los angeles sunset vintage cinema aesthetic",
    "bollywood": "bollywood dance scene colorful costume india movie",
    "steampunk": "steampunk fashion machinery gears victorian goggles",
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

MODERN_EXCLUDE_LIST = [
    "retro futurism", "cyberpunk", "y2k", "gorpcore", "mob wife", "pop culture",
    "k-pop", "hollywood", "bollywood", "steampunk", "frutiger aero", "dreamcore", 
    "solarpunk", "acid pixie", "vaporwave", "liminal space", "glitch core", 
    "bioluminescence", "chromatic", "knolling", "neon", "tech", "sci-fi"
]

# ==========================================
# 4. 搜图引擎
# ==========================================
@st.cache_data(ttl=3600)
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
        return [], f"Pexels {res.status_code}"
    except Exception as e: return [], str(e)

@st.cache_data(ttl=3600)
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
        return [], f"Unsplash {res.status_code}"
    except Exception as e: return [], str(e)

@st.cache_data(ttl=3600)
def _fetch_aic(query, limit):
    url = "https://api.artic.edu/api/v1/artworks/search"
    params = {"q": query, "limit": limit * 2, "fields": "id,title,image_id,artist_display", "query[term][is_public_domain]": "true"}
    try:
        res = requests.get(url, params=params)
        if res.status_code == 200:
            data = res.json().get("data", [])
            formatted = []
            for item in data:
                img_id = item.get('image_id')
                if img_id:
                    img_url = f"https://www.artic.edu/iiif/2/{img_id}/full/843,/0/default.jpg"
                    formatted.append({
                        "src": img_url, "url": f"https://www.artic.edu/artworks/{item['id']}",
                        "alt": f"{item['title']}", "res": "Museum Art", "source": "Art Institute"
                    })
            return formatted[:limit], None
        return [], f"AIC {res.status_code}"
    except Exception as e: return [], str(e)

@st.cache_data(ttl=3600)
def _fetch_met(query, limit):
    search_url = "https://collectionapi.metmuseum.org/public/collection/v1/search"
    params = {"q": query, "hasImages": "true", "isPublicDomain": "true"}
    try:
        res = requests.get(search_url, params=params)
        if res.status_code == 200:
            object_ids = res.json().get('objectIDs', [])
            if not object_ids: return [], "No IDs"
            target_ids = object_ids[:limit] 
            formatted = []
            for obj_id in target_ids:
                obj_url = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{obj_id}"
                obj_res = requests.get(obj_url)
                if obj_res.status_code == 200:
                    data = obj_res.json()
                    img_url = data.get('primaryImage')
                    if img_url:
                        formatted.append({
                            "src": img_url, "url": data.get('objectURL', '#'),
                            "alt": f"{data.get('title', 'Artwork')}",
                            "res": "The Met", "source": "The Met"
                        })
            return formatted, None
        return [], f"Met Search {res.status_code}"
    except Exception as e: return [], str(e)

@st.cache_data(ttl=3600)
def get_wiki_summary(query):
    try:
        wikipedia.set_lang("en")
        search_results = wikipedia.search(query, results=1)
        if not search_results: return None, "#", None
        target_term = search_results[0]
        try:
            page = wikipedia.page(target_term, auto_suggest=False)
            if not page.summary: return None, "#", None
            return page.summary[0:600] + "...", page.url, page.title
        except: return None, "#", None
    except Exception: return None, "#", None

def get_visuals(user_query, uhd_mode):
    clean_query = user_query.lower().strip()
    is_optimized = False
    is_modern_style = any(term in clean_query for term in MODERN_EXCLUDE_LIST)
    
    if clean_query in VISUAL_DICT:
        search_term = VISUAL_DICT[clean_query]
        museum_term = user_query 
        is_optimized = True
    else:
        search_term = f"{user_query} aesthetic"
        museum_term = user_query

    limit_per_source = 6
    fetch_buffer = 12 
    
    p_photos, p_err = _fetch_pexels(search_term, uhd_mode, fetch_buffer)
    u_photos, u_err = _fetch_unsplash(search_term, uhd_mode, fetch_buffer)
    
    if not is_modern_style:
        a_photos, a_err = _fetch_aic(museum_term, fetch_buffer)
        m_photos, m_err = _fetch_met(museum_term, fetch_buffer)
    else:
        a_photos, a_err = [], None
        m_photos, m_err = [], None
    
    if is_modern_style:
        p_final = p_photos[:9]
        u_final = u_photos[:9]
        a_final = []
        m_final = []
    else:
        p_final = p_photos[:limit_per_source]
        u_final = u_photos[:limit_per_source]
        a_final = a_photos[:limit_per_source]
        m_final = m_photos[:limit_per_source]
    
    combined_photos = []
    for batch in zip_longest(p_final, u_final, a_final, m_final):
        for photo in batch:
            if photo: combined_photos.append(photo)
    
    random.shuffle(combined_photos)
    return combined_photos, "", search_term, is_optimized

# ==========================================
# 5. 页面主程序
# ==========================================
local_css()

st.markdown("<h1 class='main-title'>全球视觉文化 Moodboard</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Global Visual Culture Moodboard</p>", unsafe_allow_html=True)

# --- 1. 搜索栏 ---
c_sp1, c_search, c_opt, c_sp2 = st.columns([2, 4, 1, 2])
with c_search:
    user_input = st.text_input("Search", value=st.session_state.search_query, placeholder="Type concept...", label_visibility="collapsed")
    if user_input: st.session_state.search_query = user_input
with c_opt:
    uhd_mode = st.checkbox("💎 Ultra HD", value=False)

st.markdown("<br>", unsafe_allow_html=True)

# --- 2. 分类网格 ---
with st.container():
    c1, c2, c3, c4 = st.columns(4, gap="medium")
    
    def create_grid(column, title, emoji, items):
        with column:
            st.markdown(f"<div class='category-header'>{emoji} {title}</div>", unsafe_allow_html=True)
            grid_cols = st.columns(2, gap="small") 
            for i, (label, val) in enumerate(items):
                col_idx = 0 if i % 2 == 0 else 1
                with grid_cols[col_idx]:
                    if st.button(label, key=f"btn_{val}_{i}", use_container_width=True):
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
    
    col_left, col_right = st.columns([1, 2.5])
    
    # --- 左栏 ---
    with col_left:
        st.markdown(f"<h3 style='margin-top:0; padding-top:0; line-height:1.2;'>{'🔥 Trending' if is_default else '📖 Context'}</h3>", unsafe_allow_html=True)
        st.caption(f"Topic: {wiki_title if wiki_title else target_query}")
        
        if wiki_text:
            st.markdown(f"{wiki_text}")
            st.markdown(f"[👉 Read on Wikipedia]({wiki_link})")
        else:
            st.info("Visual exploration mode.") if is_default else st.warning("No context found.")
            
        st.markdown("---")
        pinterest_url = f"https://www.pinterest.com/search/pins/?q={target_query.replace(' ', '%20')}"
        st.markdown(f"<a href='{pinterest_url}' target='_blank' class='pinterest-btn'>Search on Pinterest ↗</a>", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### ✨ Explore Aesthetics")
        soul_tags = [
            "🫧 #FrutigerAero", "👁️ #Dreamcore", "☀️ #Solarpunk", "🧚‍♀️ #AcidPixie", 
            "📜 #DarkAcademia", "🗿 #Vaporwave", "🚪 #LiminalSpace", "📺 #GlitchCore"
        ]
        tags_html = "<div class='tag-container'>"
        for tag in soul_tags:
            clean_tag = tag.split("#")[-1] 
            tags_html += f"<a href='/?q={clean_tag}' target='_self' class='tag-link' style='text-decoration:none !important;'>{tag}</a>"
        tags_html += "</div>"
        st.markdown(tags_html, unsafe_allow_html=True)

    # --- 右栏：Images (HTML Card 方案) ---
    with col_right:
        st.markdown(f"<h3 style='margin-top:0; padding-top:0; line-height:1.2;'>🖼️ Visual Board</h3>", unsafe_allow_html=True)
        
        if error_msg and not photos: st.warning(error_msg)
        if photos:
            img_cols = st.columns(3, gap="small")
            for idx, photo in enumerate(photos):
                with img_cols[idx % 3]:
                    # 🔥 HTML Card: 确保图片和文字 100% 对齐 🔥
                    html_card = f"""
                    <div style="width: 100%; margin-bottom: 20px;">
                        <div style="
                            width: 100%; 
                            border-radius: 8px; 
                            overflow: hidden; 
                            background-color: #f0f0f0;
                            margin-bottom: 8px;
                        ">
                            <img src="{photo['src']}" class="moodboard-img">
                        </div>
                        
                        <div style="
                            display: flex; 
                            justify-content: space-between; 
                            align-items: center; 
                            font-family: sans-serif;
                            font-size: 11px;
                        ">
                            <a href="{photo['url']}" target="_blank" style="
                                text-decoration: none; 
                                color: #333; 
                                font-weight: 600;
                                background: #eee;
                                padding: 4px 8px;
                                border-radius: 4px;
                            ">⬇️ Get</a>
                            
                            <span style="
                                color: #888; 
                                text-transform: uppercase; 
                                border: 1px solid #eee; 
                                padding: 3px 6px; 
                                border-radius: 4px;
                            ">
                                {photo['source']}
                            </span>
                        </div>
                    </div>
                    """
                    st.markdown(html_card, unsafe_allow_html=True)
        else:
            st.warning("No images found.")

st.markdown("---")
st.markdown("<div class='footer'>Powered by Streamlit | Pexels, Unsplash, The Met & AIC</div>", unsafe_allow_html=True)

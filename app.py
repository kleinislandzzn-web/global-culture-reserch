import streamlit as st
import wikipedia
import requests
import random

# ==========================================
# 1. 配置区域 (API Keys)
# ==========================================
PEXELS_API_KEY = "SmnlcdOVoFqWd4dyrh92DsIwtmSUqfgQqKiiDgcsi8xKYxov4HYfEE26"
UNSPLASH_ACCESS_KEY = "WLSYgnTBqCLjqXlQeZe04M5_UVsfJBRzgDOcdAkG2sE"

# ==========================================
# 2. CSS 样式 (对齐修复 + 字体升级)
# ==========================================
def local_css():
    st.markdown("""
    <style>
        /* --- 1. 搜索栏横向对齐核心修复 --- */
        
        /* 调整搜索框的高度和圆角，使其更精致 */
        div[data-testid="stTextInput"] div[data-baseweb="input"] {
            border-radius: 8px;
            border-color: #eee;
        }

        /* 强制下压 Checkbox (Ultra HD)，使其与搜索框中心对齐 */
        div[data-testid="column"] [data-testid="stCheckbox"] {
            margin-top: 12px; /* 关键：下移 12px */
        }
        
        /* 强制下压 Radio (图源切换)，使其与搜索框中心对齐 */
        div[data-testid="column"] [data-testid="stRadio"] {
            margin-top: 8px; /* 关键：下移 8px */
        }

        /* --- 2. 克莱因蓝组件风格 --- */
        div[role="radiogroup"] > label > div:first-child {
            background-color: #f0f2f6;
            border: 1px solid #dce0e6;
        }
        div[role="radiogroup"] > label[data-baseweb="radio"] > div:first-child {
            background-color: #002FA7 !important; 
            border-color: #002FA7 !important;
        }
        
        /* --- 3. 图片强制对齐 (瀑布流网格) --- */
        div[data-testid="stImage"] img {
            height: 450px !important; 
            object-fit: cover !important; 
            border-radius: 8px !important;
            width: 100% !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }
        
        /* --- 4. 字体升级 (Typography) --- */
        .main-title {
            /* 使用更现代、更粗的无衬线字体栈 */
            font-family: "PingFang SC", "Heiti SC", "Microsoft YaHei", -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 3.2em; 
            color: #111; 
            text-align: center; 
            margin-top: -20px; 
            margin-bottom: 0px;
            font-weight: 900; /* 极粗 */
            letter-spacing: -1px; /* 紧凑感 */
        }
        
        .sub-title {
            text-align: center; 
            color: #888; 
            font-size: 0.9em; 
            margin-bottom: 45px; 
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            font-weight: 500;
            letter-spacing: 4px; /* 极宽字间距 -> 时尚杂志感 */
            text-transform: uppercase; /* 全大写 */
        }
        
        /* Pinterest 按钮 */
        .pinterest-btn {
            display: inline-block;
            text-decoration: none;
            background-color: #E60023;
            color: white !important;
            padding: 8px 15px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 12px;
            margin-top: 10px;
            transition: all 0.3s;
        }
        .pinterest-btn:hover {
            background-color: #ad081b;
            transform: translateY(-2px);
        }

        /* 预设按钮 */
        div[data-testid="column"] .stButton button {
            width: 100%;
            min-height: 50px;
            border-radius: 25px;
            border: 1px solid #eee;
            background-color: #fff;
            color: #444;
            transition: all 0.3s;
        }
        div[data-testid="column"] .stButton button:hover {
            border-color: #002FA7;
            color: #002FA7;
            background-color: #fff;
            transform: translateY(-2px);
        }

        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. 视觉优化字典
# ==========================================
VISUAL_DICT = {
    # --- Trending ---
    "retro futurism": "retro futurism aesthetic 80s sci-fi neon synthwave chrome",
    "y2k": "y2k aesthetic fashion 2000s futuristic metallic shiny",
    "cottagecore": "cottagecore aesthetic nature flowers vintage dress picnic",
    # --- Fashion ---
    "kimono": "japanese woman wearing traditional kimono kyoto street portrait",
    "hanfu": "traditional chinese hanfu dress portrait ethereal fairy style",
    "sari": "indian woman wearing colorful saree portrait jewelry",
    "qipao": "woman wearing chinese qipao shanghai vintage style portrait",
    "kilt": "scottish man wearing traditional kilt tartan highlands",
    "flamenco": "spanish flamenco dancer woman red dress motion",
    # --- Architecture ---
    "bauhaus": "bauhaus architecture building geometric minimal white",
    "gothic": "gothic cathedral architecture detail spires dark moody",
    "santorini": "santorini greece white houses blue domes aegean sea",
    "brutalist": "brutalist architecture concrete building monumental",
    "pagoda": "asian pagoda temple architecture kyoto red autumn",
    "art deco": "art deco architecture building new york gold detail",
    # --- Culture ---
    "k-pop": "korean idol concert performance fashion stage lighting",
    "kpop": "korean idol concert performance fashion stage lighting",
    "cyberpunk": "neon lights tokyo night futuristic rain high contrast",
    "zen": "japanese zen garden rocks moss water meditation peaceful",
    "bollywood": "bollywood dance scene colorful costume india movie",
    "steampunk": "steampunk fashion machinery gears victorian goggles",
    "hollywood": "hollywood sign los angeles sunset vintage cinema aesthetic"
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
            raw_data = res.json().get("photos", [])
            filtered_data = []
            for p in raw_data:
                if uhd_mode:
                    if min(p['width'], p['height']) > 1500: filtered_data.append(p)
                else:
                    filtered_data.append(p)
            
            final_data = filtered_data[:9]
            return [{
                "src": p['src']['large2x'], 
                "url": p['url'], 
                "alt": p['alt'] or "Pexels Image",
                "res": f"{p['width']}x{p['height']}"
            } for p in final_data], None
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
            raw_data = res.json().get("results", [])
            filtered_data = []
            for p in raw_data:
                if uhd_mode:
                    if min(p['width'], p['height']) > 1500: filtered_data.append(p)
                else:
                    filtered_data.append(p)
            
            final_data = filtered_data[:9]
            return [{
                "src": p['urls']['regular'],
                "url": p['links']['html'],
                "alt": p['alt_description'] or p['description'] or "Unsplash Image",
                "res": f"{p['width']}x{p['height']}"
            } for p in final_data], None
        elif res.status_code == 403:
            return [], "⚠️ Unsplash Limit Reached"
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
    except:
        return None, "#", None

# ==========================================
# 5. 页面主程序
# ==========================================
st.set_page_config(page_title="Visual Moodboard", page_icon="🎨", layout="wide")
local_css()

# --- 标题升级 ---
st.markdown("<h1 class='main-title'>全球视觉文化 Moodboard</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Global Visual Culture Moodboard</p>", unsafe_allow_html=True)

if 'search_query' not in st.session_state:
    st.session_state.search_query = ""

# --- 按钮区域 ---
with st.container():
    col_fashion, col_arch, col_culture = st.columns(3, gap="large")
    def create_grid_buttons(column, title, items):
        with column:
            st.markdown(f"<h3 style='text-align:center; font-size:14px; color:#999; margin-bottom:15px;'>{title}</h3>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            for i, (label, val) in enumerate(items):
                target_col = c1 if i % 2 == 0 else c2
                if target_col.button(label, key=f"btn_{val}_{i}"):
                    st.session_state.search_query = val
                    st.rerun()

    fashion_items = [("👘 Kimono", "Kimono"), ("👗 Hanfu", "Hanfu"), ("🧣 Sari", "Sari"), ("🎋 Qipao", "Qipao"), ("🎼 Kilt", "Kilt"), ("💃 Flamenco", "Flamenco")]
    arch_items = [("🏢 Bauhaus", "Bauhaus"), ("⛪ Gothic", "Gothic"), ("🌊 Santorini", "Santorini"), ("🧱 Brutalist", "Brutalist"), ("⛩️ Pagoda", "Pagoda"), ("🗽 Art Deco", "Art Deco")]
    culture_items = [("🎤 K-Pop", "K-Pop"), ("🤖 Cyberpunk", "Cyberpunk"), ("🌿 Zen", "Zen"), ("🎬 Hollywood", "Hollywood"), ("💃 Bollywood", "Bollywood"), ("⚙️ Steampunk", "Steampunk")]

    create_grid_buttons(col_fashion, "LOCAL FASHION", fashion_items)
    create_grid_buttons(col_arch, "ARCHITECTURE", arch_items)
    create_grid_buttons(col_culture, "POP CULTURE", culture_items)

st.markdown("<br>", unsafe_allow_html=True)

# --- 搜索栏区域 (横向对齐优化) ---
# 布局：3 (Search) : 1 (UHD) : 1 (Source)
c_search, c_opt, c_source = st.columns([3, 1, 1])

with c_search:
    user_input = st.text_input("Search", value=st.session_state.search_query, placeholder="Type to explore...", label_visibility="collapsed")
    if user_input: st.session_state.search_query = user_input

with c_opt:
    # Ultra HD 开关 (CSS 已将其下移对齐)
    uhd_mode = st.checkbox("💎 Ultra HD", value=False)

with c_source:
    # 图源切换 (CSS 已将其下移对齐)
    source = st.radio("Src", ["Pexels", "Unsplash"], horizontal=True, label_visibility="collapsed")

# --- 核心展示逻辑 ---
if not st.session_state.search_query:
    target_query = "Retro Futurism"
    is_default_view = True
else:
    target_query = st.session_state.search_query
    is_default_view = False

if target_query:
    with st.spinner(f"Curating visuals via {source} (UHD: {uhd_mode})..."):
        wiki_text, wiki_link, wiki_title = get_wiki_summary(target_query)
        photos, error_msg, optimized_term, is_opt = get_visuals(source, target_query, uhd_mode)
    
    if is_default_view:
        st.markdown(f"### 🔥 Trending Now: <span style='color:#002FA7'>{target_query}</span>", unsafe_allow_html=True)
    elif is_opt:
        st.success(f"🎨 **Moodboard Optimized:** '{target_query}' ➔ `{optimized_term}`")
    else:
        st.caption(f"🔍 Result for: `{optimized_term}`")

    col_left, col_right = st.columns([1, 2.5])
    
    # Wiki & Pinterest
    with col_left:
        st.markdown("### 📖 Context")
        st.caption(f"Subject: {wiki_title if wiki_title else target_query}")
        if wiki_text:
            st.markdown(f"{wiki_text}")
            st.markdown(f"[👉 Read more on Wikipedia]({wiki_link})")
        else:
            if is_default_view: st.info("Welcome to the Visual Moodboard.")
            else: st.warning("No specific context found.")
            
        st.markdown("---")
        st.markdown("### 📌 External")
        pinterest_url = f"https://www.pinterest.com/search/pins/?q={target_query.replace(' ', '%20')}"
        st.markdown(f"""
            <a href="{pinterest_url}" target="_blank" class="pinterest-btn">
                Search "{target_query}" on Pinterest ↗
            </a>
        """, unsafe_allow_html=True)

    # Images (Bottom Aligned)
    with col_right:
        st.markdown(f"### 🖼️ Visual Board ({source})")
        if error_msg:
            st.error(error_msg)
        elif photos:
            img_cols = st.columns(3)
            for idx, photo in enumerate(photos):
                with img_cols[idx % 3]:
                    # 图像渲染 (CSS强制 450px 高度)
                    st.image(photo['src'], use_container_width=True)
                    
                    raw_alt = photo.get('alt', 'Visual Asset')
                    if not raw_alt: raw_alt = "Untitled"
                    res_info = photo.get('res', 'High Res')
                    
                    st.markdown(f"""
                        <div style="font-size:12px; line-height:1.4; margin-top:8px; margin-bottom:20px;">
                            <div style="display:flex; justify-content:space-between;">
                                <a href="{photo['url']}" target="_blank" style="color:#333; font-weight:600; text-decoration:none;">
                                    ⬇️ Download
                                </a>
                                <span style="color:#aaa; font-size:10px; background:#f0f0f0; padding:2px 6px; border-radius:4px;">
                                    {res_info}
                                </span>
                            </div>
                            <div style="color:#888; font-style:italic; margin-top:4px;">
                                {raw_alt[:25]}...
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            msg = "No images > 1500px found. Try unchecking 'Ultra HD'." if uhd_mode else "No visuals found."
            st.warning(msg)

st.markdown("---")
st.markdown("""
    <div class='footer'>
        Powered by Streamlit | Pexels & Unsplash API<br><br>
        <strong>© 2025 Leki's Arc Inc.</strong>
    </div>
""", unsafe_allow_html=True)

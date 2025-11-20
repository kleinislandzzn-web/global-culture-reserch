import streamlit as st
import wikipedia
import requests

# ==========================================
# 1. 配置区域 (API Keys 已预填)
# ==========================================
PEXELS_API_KEY = "SmnlcdOVoFqWd4dyrh92DsIwtmSUqfgQqKiiDgcsi8xKYxov4HYfEE26"
UNSPLASH_ACCESS_KEY = "WLSYgnTBqCLjqXlQeZe04M5_UVsfJBRzgDOcdAkG2sE"

# ==========================================
# 2. CSS 样式 (Moodboard 风格)
# ==========================================
def local_css():
    st.markdown("""
    <style>
        /* 按钮样式 */
        div[data-testid="column"] .stButton button {
            width: 100%;
            min-height: 60px;
            border-radius: 12px;
            border: 1px solid #f0f0f0;
            background-color: #ffffff;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            transition: all 0.2s;
            font-size: 14px;
            color: #444;
        }
        div[data-testid="column"] .stButton button:hover {
            border-color: #333;
            color: #000;
            background-color: #f9f9f9;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        /* 标题样式 */
        .main-title {
            font-family: "Microsoft YaHei", sans-serif;
            font-size: 3em; 
            color: #111; 
            text-align: center; 
            margin-top: -20px; 
            margin-bottom: 5px; 
            font-weight: 800;
            letter-spacing: -1px;
        }
        .sub-title {
            text-align: center; 
            color: #666; 
            font-size: 1.2em; 
            margin-bottom: 40px; 
            font-family: 'Helvetica Neue', sans-serif;
            font-weight: 300;
            letter-spacing: 1px;
            text-transform: uppercase; 
        }
        /* 底部 */
        .footer {
            text-align: center; 
            color: #aaa; 
            font-size: 12px; 
            margin-top: 80px; 
            padding-bottom: 20px;
        }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. 视觉优化字典
# ==========================================
VISUAL_DICT = {
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
# 4. 搜图引擎逻辑 (⚠️已修复 BUG)
# ==========================================
def get_visuals(source, user_query, per_page=9):
    clean_query = user_query.lower().strip()
    is_optimized = False
    
    # 1. 确定搜索词
    if clean_query in VISUAL_DICT:
        search_term = VISUAL_DICT[clean_query]
        is_optimized = True
    else:
        search_term = f"{user_query} aesthetic"

    # 2. 获取图片 (这里做了修复，先解压 photos 和 error)
    if source == "Pexels":
        photos, error = _fetch_pexels(search_term, per_page)
    else:
        photos, error = _fetch_unsplash(search_term, per_page)
        
    # 3. 返回 4 个独立变量
    return photos, error, search_term, is_optimized

def _fetch_pexels(query, per_page):
    headers = {"Authorization": PEXELS_API_KEY}
    url = "https://api.pexels.com/v1/search"
    params = {"query": query, "per_page": per_page, "orientation": "portrait", "locale": "en-US"}
    try:
        res = requests.get(url, headers=headers, params=params)
        if res.status_code == 200:
            data = res.json().get("photos", [])
            return [{"src": p['src']['large'], "url": p['url'], "alt": p['alt'] or "Pexels Image"} for p in data], None
        return [], f"Pexels Error: {res.status_code}"
    except Exception as e:
        return [], str(e)

def _fetch_unsplash(query, per_page):
    headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
    url = "https://api.unsplash.com/search/photos"
    params = {"query": query, "per_page": per_page, "orientation": "portrait"}
    try:
        res = requests.get(url, headers=headers, params=params)
        if res.status_code == 200:
            data = res.json().get("results", [])
            formatted = []
            for p in data:
                formatted.append({
                    "src": p['urls']['regular'],
                    "url": p['links']['html'],
                    "alt": p['alt_description'] or p['description'] or "Unsplash Image"
                })
            return formatted, None
        elif res.status_code == 403:
            return [], "⚠️ Unsplash Limit Reached (Demo mode limit 50/hr)"
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

# --- 标题区域 ---
st.markdown("<h1 class='main-title'>全球视觉文化 Moodboard</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Global Visual Culture Moodboard</p>", unsafe_allow_html=True)

if 'search_query' not in st.session_state:
    st.session_state.search_query = ""

# --- 按钮区域 ---
with st.container():
    col_fashion, col_arch, col_culture = st.columns(3, gap="large")

    def create_grid_buttons(column, title, items):
        with column:
            st.markdown(f"<h3 style='text-align:center; font-size:1.2em; color:#333;'>{title}</h3>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            for i, (label, val) in enumerate(items):
                target_col = c1 if i % 2 == 0 else c2
                if target_col.button(label, key=f"btn_{val}_{i}"):
                    st.session_state.search_query = val
                    st.rerun()

    fashion_items = [("👘 Kimono", "Kimono"), ("👗 Hanfu", "Hanfu"), ("🧣 Sari", "Sari"), ("🎋 Qipao", "Qipao"), ("🎼 Kilt", "Kilt"), ("💃 Flamenco", "Flamenco")]
    arch_items = [("🏢 Bauhaus", "Bauhaus"), ("⛪ Gothic", "Gothic"), ("🌊 Santorini", "Santorini"), ("🧱 Brutalist", "Brutalist"), ("⛩️ Pagoda", "Pagoda"), ("🗽 Art Deco", "Art Deco")]
    culture_items = [("🎤 K-Pop", "K-Pop"), ("🤖 Cyberpunk", "Cyberpunk"), ("🌿 Zen", "Zen"), ("🎬 Hollywood", "Hollywood"), ("💃 Bollywood", "Bollywood"), ("⚙️ Steampunk", "Steampunk")]

    create_grid_buttons(col_fashion, "👘 Local Fashion", fashion_items)
    create_grid_buttons(col_arch, "🏛️ Architecture", arch_items)
    create_grid_buttons(col_culture, "🎨 Pop Culture", culture_items)

st.markdown("<br>", unsafe_allow_html=True)

# --- 搜索与设置区域 ---
c_search, c_source = st.columns([3, 1])
with c_search:
    query = st.text_input("Search Input", value=st.session_state.search_query, placeholder="Type a concept (e.g. Neon, Temple) to generate moodboard...", label_visibility="collapsed")
with c_source:
    source = st.radio("Visual Engine", ["Pexels", "Unsplash"], horizontal=True, label_visibility="collapsed")
    st.caption(f"Engine: {source}")

# --- 结果展示 ---
if query:
    st.session_state.search_query = query 
    
    with st.spinner(f"Curating visuals from {source}..."):
        wiki_text, wiki_link, wiki_title = get_wiki_summary(query)
        # 调用修复后的 get_visuals，现在它能正确返回4个值了
        photos, error_msg, optimized_term, is_opt = get_visuals(source, query)
    
    if is_opt:
        st.success(f"🎨 **Moodboard Optimized:** '{query}' ➔ `{optimized_term}`")
    else:
        st.caption(f"🔍 Generating moodboard for: `{optimized_term}`")

    col_left, col_right = st.columns([1, 2.5])
    
    with col_left:
        st.markdown("### 📖 Context")
        st.caption(f"Subject: {wiki_title if wiki_title else query}")
        if wiki_text:
            st.markdown(f"{wiki_text}")
            st.markdown(f"[👉 Read more on Wikipedia]({wiki_link})")
        else:
            st.warning("No specific context found.")

    with col_right:
        st.markdown(f"### 🖼️ Visual Board ({source})")
        if error_msg:
            st.error(error_msg)
        elif photos:
            img_cols = st.columns(3)
            for idx, photo in enumerate(photos):
                with img_cols[idx % 3]:
                    st.image(photo['src'], use_container_width=True)
                    raw_alt = photo.get('alt', 'Visual Asset')
                    if not raw_alt: raw_alt = "Untitled"
                    st.markdown(f"""
                        <div style="font-size:12px; line-height:1.4; margin-top:5px;">
                            <div style="color:#888; font-style:italic; height:35px; overflow:hidden;">
                                {raw_alt[:50]}...
                            </div>
                            <a href="{photo['url']}" target="_blank" style="color:#333; font-weight:bold; text-decoration:none; border-bottom:1px solid #ccc;">
                                ⬇️ Save Asset
                            </a>
                        </div>
                        <div style="margin-bottom: 20px;"></div>
                    """, unsafe_allow_html=True)
        else:
            st.warning(f"No visuals found for this moodboard.")

st.markdown("---")
st.markdown("""
    <div class='footer'>
        Powered by Streamlit | Pexels & Unsplash API | Wikipedia<br><br>
        <strong>© 2025 Leki's Arc Inc.</strong>
    </div>
""", unsafe_allow_html=True)

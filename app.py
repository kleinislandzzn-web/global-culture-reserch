import streamlit as st
import wikipedia
import pycountry
import requests

# ==========================================
# 1. 配置区域 (API Key 已填入)
# ==========================================
PEXELS_API_KEY = "SmnlcdOVoFqWd4dyrh92DsIwtmSUqfgQqKiiDgcsi8xKYxov4HYfEE26"

# ==========================================
# 2. 核心字典：视觉翻译 & 多语言界面
# ==========================================

# --- A. 视觉翻译字典 (让搜索更精准，支持中文输入映射) ---
VISUAL_DICT = {
    # 流行文化 & 风格
    "kpop": "korean idol concert performance fashion stage lighting",
    "k-pop": "korean idol concert performance fashion stage lighting",
    "cyberpunk": "neon lights tokyo night futuristic rain high contrast",
    "赛博朋克": "neon lights tokyo night futuristic rain high contrast",
    "steampunk": "steampunk fashion machinery gears victorian style",
    "minimalism": "minimalist white interior design clean lines",
    
    # 服饰 (Fashion)
    "kimono": "japanese woman wearing kimono kyoto street portrait",
    "和服": "japanese woman wearing kimono kyoto street portrait",
    "hanfu": "traditional chinese hanfu dress portrait ethereal",
    "汉服": "traditional chinese hanfu dress portrait ethereal",
    "sari": "indian woman wearing colorful saree portrait",
    "saree": "indian woman wearing colorful saree portrait",
    "qipao": "woman wearing chinese qipao shanghai style portrait",
    "cheongsam": "woman wearing chinese qipao shanghai style portrait",
    
    # 建筑 (Architecture)
    "bauhaus": "bauhaus architecture building geometric white",
    "包豪斯": "bauhaus architecture building geometric white",
    "gothic": "gothic cathedral architecture detail spires",
    "brutalist": "brutalist architecture concrete building",
    "zen garden": "japanese zen garden rocks moss water meditation",
    "santorini": "santorini greece white houses blue dome ocean",
}

# --- B. 界面多语言配置 ---
UI_TEXT = {
    "English": {
        "title": "Global Culture Compass",
        "subtitle": "Explore aesthetics, architecture, and fashion through a local lens.",
        "search_ph": "Search (e.g., Kimono, Cyberpunk, Brutalist)...",
        "searching": "Searching for visual and cultural context...",
        "wiki_title": "📖 Knowledge Base",
        "img_title": "📸 Visual Gallery",
        "no_img": "No relevant high-quality images found.",
        "no_wiki": "No detailed Wikipedia entry found.",
        "download": "Download / License",
        "cat_fashion": "👘 Local Fashion",
        "cat_arch": "🏛️ Architecture",
        "cat_style": "🎨 Aesthetics",
    },
    "中文": {
        "title": "全球本地化文化智库",
        "subtitle": "探索全球视野下的服饰、建筑与审美趋势。",
        "search_ph": "输入关键词 (例如: 和服, 赛博朋克, 包豪斯)...",
        "searching": "正在连接全球数据库进行检索...",
        "wiki_title": "📖 文化百科 (Wiki)",
        "img_title": "📸 视觉灵感 (9-Grid)",
        "no_img": "未找到相关的高清图片。",
        "no_wiki": "暂无详细百科介绍。",
        "download": "下载原图 / 查看许可",
        "cat_fashion": "👘 特色服饰",
        "cat_arch": "🏛️ 地标建筑",
        "cat_style": "🎨 流行风格",
    }
}

# ---------------------------------------------------------
# 3. 工具函数
# ---------------------------------------------------------
def get_pexels_images(user_query, per_page=9):
    """智能搜索图片：先查字典翻译，再调 API"""
    clean_query = user_query.lower().strip()
    
    if clean_query in VISUAL_DICT:
        search_term = VISUAL_DICT[clean_query]
    else:
        search_term = f"{user_query} aesthetic"

    headers = {"Authorization": PEXELS_API_KEY}
    url = "https://api.pexels.com/v1/search"
    params = {
        "query": search_term,
        "per_page": per_page,
        "orientation": "portrait",
        "locale": "en-US"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json().get("photos", []), None, search_term
        return [], f"Error: {response.status_code}", search_term
    except Exception as e:
        return [], str(e), search_term

def get_wiki_summary(query, lang_code):
    """获取 Wiki"""
    try:
        w_lang = "zh" if lang_code == "中文" else "en"
        wikipedia.set_lang(w_lang) 
        
        search_results = wikipedia.search(query)
        if search_results:
            page = wikipedia.page(search_results[0], auto_suggest=False)
            summary = page.summary[0:600] + "..."
            return summary, page.url, search_results[0]
        else:
            if w_lang == "zh":
                wikipedia.set_lang("en")
                search_results = wikipedia.search(query)
                if search_results:
                    page = wikipedia.page(search_results[0], auto_suggest=False)
                    return f"(中文暂缺，显示英文结果) {page.summary[0:600]}...", page.url, search_results[0]
            return None, "#", None
    except:
        return None, "#", None

# ---------------------------------------------------------
# 4. 页面主逻辑
# ---------------------------------------------------------
st.set_page_config(page_title="Global Culture Search", page_icon="🌍", layout="wide")

# --- 侧边栏 ---
with st.sidebar:
    st.header("Settings / 设置")
    lang = st.radio("Language", ["中文", "English"], index=0)
    t = UI_TEXT[lang]

if 'search_query' not in st.session_state:
    st.session_state.search_query = ""

# --- 标题区 ---
st.markdown(f"<h1 style='text-align: center;'>{t['title']}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: grey;'>{t['subtitle']}</p>", unsafe_allow_html=True)

# --- 快捷预设按钮区 ---
with st.container():
    c_p1, c_p2, c_p3 = st.columns(3)
    
    presets_fashion = [("👘", "Kimono/和服", "Kimono"), ("👗", "Hanfu/汉服", "Hanfu"), ("🧣", "Sari/纱丽", "Sari")]
    presets_arch = [("🏯", "Himeji/姬路城", "Himeji Castle"), ("🏛️", "Pantheon/万神殿", "Pantheon"), ("🕌", "Taj Mahal/泰姬陵", "Taj Mahal")]
    presets_style = [("🎤", "K-Pop/韩流", "Kpop"), ("🤖", "Cyberpunk/赛博", "Cyberpunk"), ("🌿", "Zen/禅意", "Zen Garden")]

    def create_buttons(column, title, items):
        with column:
            st.caption(title)
            cols = st.columns(len(items))
            for i, (emoji, label, search_val) in enumerate(items):
                if cols[i].button(f"{emoji}\n{label.split('/')[0] if lang == 'English' else label.split('/')[1]}"):
                    st.session_state.search_query = search_val
                    st.rerun()

    create_buttons(c_p1, t['cat_fashion'], presets_fashion)
    create_buttons(c_p2, t['cat_arch'], presets_arch)
    create_buttons(c_p3, t['cat_style'], presets_style)

st.divider()

# --- 搜索框 ---
query = st.text_input("🔍", value=st.session_state.search_query, placeholder=t['search_ph'], label_visibility="collapsed")

# ---------------------------------------------------------
# 5. 搜索结果展示
# ---------------------------------------------------------
if query:
    st.session_state.search_query = query
    
    with st.spinner(t['searching']):
        wiki_text, wiki_link, wiki_title = get_wiki_summary(query, lang)
        photos, error_msg, real_term = get_pexels_images(query)
    
    col_wiki, col_img = st.columns([1, 2.5])
    
    # --- Wiki ---
    with col_wiki:
        st.markdown(f"### {t['wiki_title']}")
        st.caption(f"Subject: {wiki_title if wiki_title else query}")
        if wiki_text:
            st.info(wiki_text)
            st.markdown(f"[👉 Wikipedia ({lang})]({wiki_link})")
        else:
            st.warning(t['no_wiki'])
        st.markdown("---")
        st.caption(f"Visual Engine Key: `{real_term}`")

    # --- Images ---
    with col_img:
        st.markdown(f"### {t['img_title']}")
        if error_msg:
            st.error(error_msg)
        elif photos:
            img_cols = st.columns(3)
            for idx, photo in enumerate(photos):
                with img_cols[idx % 3]:
                    st.image(photo['src']['large'], use_container_width=True)
                    st.markdown(f"""
                        <div style="text-align:center; font-size:12px; margin-bottom:15px;">
                            <a href="{photo['url']}" target="_blank" style="color:#E67E22; text-decoration:none;">⬇️ {t['download']}</a>
                            <br><span style="color:#999">by {photo['photographer']}</span>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning(t['no_img'])

# ---------------------------------------------------------
# 6. 底部版权信息 (Footer)
# ---------------------------------------------------------
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #888; font-size: 12px;'>
        Powered by Streamlit | Images via Pexels API | Text via Wikipedia<br><br>
        <strong>© 2025 Leki's Arc Inc.</strong>
    </div>
""", unsafe_allow_html=True)

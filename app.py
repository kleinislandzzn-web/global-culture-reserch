import streamlit as st
import wikipedia
import pycountry
import requests

# ==========================================
# 1. 配置区域
# ==========================================
PEXELS_API_KEY = "SmnlcdOVoFqWd4dyrh92DsIwtmSUqfgQqKiiDgcsi8xKYxov4HYfEE26"

# ==========================================
# 2. CSS 样式注入 (关键：实现按钮等宽等高)
# ==========================================
def local_css():
    st.markdown("""
    <style>
        /* 1. 强制按钮占满列宽，并设定最小高度以保持对齐 */
        div[data-testid="column"] .stButton button {
            width: 100%;
            min-height: 80px; /* 设定按钮统一高度 */
            border-radius: 10px;
            border: 1px solid #e0e0e0;
            transition: all 0.3s;
            white-space: pre-wrap; /* 允许文字换行 */
        }
        div[data-testid="column"] .stButton button:hover {
            border-color: #e67e22;
            color: #e67e22;
            background-color: #fff8f0;
        }
        
        /* 2. 调整左上角语言选择器的样式 */
        .lang-select-box {
            margin-bottom: 0px;
        }
        
        /* 3. 标题样式 */
        .main-title {font-size: 2.5em; color: #2c3e50; text-align: center; margin-top: -50px;}
        
        /* 4. 底部版权 */
        .footer {text-align: center; color: #888; font-size: 12px; margin-top: 50px;}
        
        /* 隐藏默认菜单 */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. 核心字典：视觉翻译 & 多语言
# ==========================================
VISUAL_DICT = {
    # 流行文化 & 风格
    "kpop": "korean idol concert performance fashion stage lighting",
    "k-pop": "korean idol concert performance fashion stage lighting",
    "cyberpunk": "neon lights tokyo night futuristic rain high contrast",
    "赛博朋克": "neon lights tokyo night futuristic rain high contrast",
    "zen": "japanese zen garden rocks moss water meditation",
    
    # 服饰 (Fashion)
    "kimono": "japanese woman wearing kimono kyoto street portrait",
    "和服": "japanese woman wearing kimono kyoto street portrait",
    "hanfu": "traditional chinese hanfu dress portrait ethereal",
    "汉服": "traditional chinese hanfu dress portrait ethereal",
    "sari": "indian woman wearing colorful saree portrait",
    
    # 建筑 (Architecture)
    "bauhaus": "bauhaus architecture building geometric white",
    "包豪斯": "bauhaus architecture building geometric white",
    "gothic": "gothic cathedral architecture detail spires",
    "santorini": "santorini greece white houses blue dome ocean",
}

UI_TEXT = {
    "English": {
        "title": "Global Culture Compass",
        "subtitle": "Aesthetics | Architecture | Fashion",
        "search_ph": "Search (e.g., Kimono, Cyberpunk)...",
        "searching": "Analyzing tags and retrieving visuals...",
        "wiki_title": "📖 Context",
        "img_title": "📸 Visual Gallery",
        "no_img": "No relevant high-quality images found.",
        "no_wiki": "No detailed entry found.",
        "download": "Download / License",
        "author_tag": "🏷️ Author's Tag: ",
        "cat_fashion": "👘 Fashion",
        "cat_arch": "🏛️ Architecture",
        "cat_style": "🎨 Culture",
        # 按钮文字 (Emoji + Name)
        "btn_kimono": "👘 Kimono\n(Japan)",
        "btn_hanfu": "👗 Hanfu\n(China)",
        "btn_sari": "🧣 Sari\n(India)",
        "btn_bauhaus": "🏢 Bauhaus\n(Germany)",
        "btn_gothic": "⛪ Gothic\n(Europe)",
        "btn_santorini": "🕌 Santorini\n(Greece)",
        "btn_kpop": "🎤 K-Pop\n(Korea)",
        "btn_cyber": "🤖 Cyberpunk\n(Future)",
        "btn_zen": "🌿 Zen\n(Japan)",
    },
    "中文": {
        "title": "全球本地化文化智库",
        "subtitle": "服饰 · 建筑 · 流行审美",
        "search_ph": "输入关键词 (例如: 和服, 赛博朋克)...",
        "searching": "正在比对图片标签并检索...",
        "wiki_title": "📖 文化百科",
        "img_title": "📸 视觉灵感",
        "no_img": "未找到标签匹配的高清图片。",
        "no_wiki": "暂无详细百科。",
        "download": "下载 / 许可",
        "author_tag": "🏷️ 作者标签: ",
        "cat_fashion": "👘 本地服饰",
        "cat_arch": "🏛️ 特色建筑",
        "cat_style": "🎨 流行文化",
        # 按钮文字
        "btn_kimono": "👘 和服 (Kimono)\n日本",
        "btn_hanfu": "👗 汉服 (Hanfu)\n中国",
        "btn_sari": "🧣 纱丽 (Sari)\n印度",
        "btn_bauhaus": "🏢 包豪斯\n德国",
        "btn_gothic": "⛪ 哥特式\n欧洲",
        "btn_santorini": "🕌 圣托里尼\n希腊",
        "btn_kpop": "🎤 K-Pop\n韩国",
        "btn_cyber": "🤖 赛博朋克\n未来风格",
        "btn_zen": "🌿 禅意 (Zen)\n日本",
    }
}

# ---------------------------------------------------------
# 4. 功能函数
# ---------------------------------------------------------
def get_pexels_images(user_query, per_page=9):
    """
    智能搜索 + 强关联 Tag 验证
    Pexels API 返回的 'alt' 字段通常包含作者打的标签/描述。
    """
    clean_query = user_query.lower().strip()
    
    # 1. 翻译层
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
            photos = response.json().get("photos", [])
            return photos, None, search_term
        return [], f"Error: {response.status_code}", search_term
    except Exception as e:
        return [], str(e), search_term

def get_wiki_summary(query, lang_code):
    try:
        w_lang = "zh" if lang_code == "中文" else "en"
        wikipedia.set_lang(w_lang) 
        search_results = wikipedia.search(query)
        if search_results:
            page = wikipedia.page(search_results[0], auto_suggest=False)
            return page.summary[0:500] + "...", page.url, search_results[0]
        else:
            # 兜底英文
            if w_lang == "zh":
                wikipedia.set_lang("en")
                res = wikipedia.search(query)
                if res:
                    page = wikipedia.page(res[0], auto_suggest=False)
                    return f"(显示英文结果) {page.summary[0:500]}...", page.url, res[0]
            return None, "#", None
    except:
        return None, "#", None

# ---------------------------------------------------------
# 5. 页面主程序
# ---------------------------------------------------------
st.set_page_config(page_title="Global Culture Search", page_icon="🌍", layout="wide")
local_css() # 注入 CSS

# --- A. 顶部布局：左上角语言切换 + 标题 ---
# 使用 columns 将语言切换放在最左边
top_col1, top_col2, top_col3 = st.columns([1, 6, 1])

with top_col1:
    # 语言切换器
    lang = st.selectbox("Language/语言", ["中文", "English"], label_visibility="collapsed")
    t = UI_TEXT[lang]

with top_col2:
    st.markdown(f"<h1 class='main-title'>{t['title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: grey;'>{t['subtitle']}</p>", unsafe_allow_html=True)

# 初始化 Session State
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""

st.markdown("<br>", unsafe_allow_html=True)

# --- B. 核心分类按钮区 (等宽等高布局) ---
# 定义三列
cat_c1, cat_c2, cat_c3 = st.columns(3)

# 1. 服饰类
with cat_c1:
    st.markdown(f"<h3 style='text-align: center;'>{t['cat_fashion']}</h3>", unsafe_allow_html=True)
    # 3个按钮堆叠
    if st.button(t['btn_kimono'], key="btn_kim"): 
        st.session_state.search_query = "Kimono"
        st.rerun()
    if st.button(t['btn_hanfu'], key="btn_han"): 
        st.session_state.search_query = "Hanfu"
        st.rerun()
    if st.button(t['btn_sari'], key="btn_sar"): 
        st.session_state.search_query = "Sari"
        st.rerun()

# 2. 建筑类
with cat_c2:
    st.markdown(f"<h3 style='text-align: center;'>{t['cat_arch']}</h3>", unsafe_allow_html=True)
    if st.button(t['btn_bauhaus'], key="btn_bau"): 
        st.session_state.search_query = "Bauhaus"
        st.rerun()
    if st.button(t['btn_gothic'], key="btn_got"): 
        st.session_state.search_query = "Gothic"
        st.rerun()
    if st.button(t['btn_santorini'], key="btn_san"): 
        st.session_state.search_query = "Santorini"
        st.rerun()

# 3. 文化类
with cat_c3:
    st.markdown(f"<h3 style='text-align: center;'>{t['cat_style']}</h3>", unsafe_allow_html=True)
    if st.button(t['btn_kpop'], key="btn_kpop"): 
        st.session_state.search_query = "Kpop"
        st.rerun()
    if st.button(t['btn_cyber'], key="btn_cyb"): 
        st.session_state.search_query = "Cyberpunk"
        st.rerun()
    if st.button(t['btn_zen'], key="btn_zen"): 
        st.session_state.search_query = "Zen"
        st.rerun()

st.divider()

# --- C. 搜索框 ---
query = st.text_input("Search", value=st.session_state.search_query, placeholder=t['search_ph'], label_visibility="collapsed")

# --- D. 结果展示 ---
if query:
    st.session_state.search_query = query
    
    with st.spinner(t['searching']):
        wiki_text, wiki_link, wiki_title = get_wiki_summary(query, lang)
        photos, error_msg, real_term = get_pexels_images(query)
    
    col_wiki, col_img = st.columns([1, 2.5])
    
    # 左：Wiki
    with col_wiki:
        st.markdown(f"### {t['wiki_title']}")
        st.caption(f"Subject: {wiki_title if wiki_title else query}")
        if wiki_text:
            st.info(wiki_text)
            st.markdown(f"[👉 Wikipedia ({lang})]({wiki_link})")
        else:
            st.warning(t['no_wiki'])

    # 右：图片 (含强关联Tag展示)
    with col_img:
        st.markdown(f"### {t['img_title']}")
        if error_msg:
            st.error(error_msg)
        elif photos:
            img_cols = st.columns(3)
            for idx, photo in enumerate(photos):
                with img_cols[idx % 3]:
                    st.image(photo['src']['large'], use_container_width=True)
                    
                    # 获取作者的原生标签/描述 (ALT text)
                    raw_alt = photo.get('alt', 'No tag provided')
                    
                    # 强关联展示：把 Pexels 作者的 Tag 显示出来
                    st.markdown(f"""
                        <div style="font-size:12px; line-height:1.4;">
                            <div style="margin-bottom:4px; color:#555; font-style:italic;">
                                <b>{t['author_tag']}</b><br>"{raw_alt}"
                            </div>
                            <a href="{photo['url']}" target="_blank" style="color:#E67E22; text-decoration:none; font-weight:bold;">
                                ⬇️ {t['download']}
                            </a>
                        </div>
                        <br>
                    """, unsafe_allow_html=True)
        else:
            st.warning(t['no_img'])

# --- E. 底部 ---
st.markdown("---")
st.markdown("""
    <div class='footer'>
        Powered by Streamlit | Images via Pexels API | Text via Wikipedia<br><br>
        <strong>© 2025 Leki's Arc Inc.</strong>
    </div>
""", unsafe_allow_html=True)

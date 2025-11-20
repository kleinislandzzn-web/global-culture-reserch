import streamlit as st
import wikipedia
import pycountry
import requests

# ==========================================
# 配置区域
# ==========================================
# 这里已经填好了你提供的 Pexels API Key
PEXELS_API_KEY = "SmnlcdOVoFqWd4dyrh92DsIwtmSUqfgQqKiiDgcsi8xKYxov4HYfEE26"

# ---------------------------------------------------------
# 1. 页面配置与CSS样式
# ---------------------------------------------------------
st.set_page_config(page_title="Global Culture Compass", page_icon="🌍", layout="wide")

st.markdown("""
<style>
    .main-title {font-size: 3em; color: #2c3e50; text-align: center; margin-bottom: 0.5em; font-family: 'Helvetica Neue', sans-serif;}
    .sub-text {text-align: center; color: #7f8c8d; margin-bottom: 2em;}
    /* 图片卡片样式 */
    .img-caption {text-align: center; font-size: 0.8em; color: #555; margin-top: 5px;}
    a {text-decoration: none; color: #e67e22; font-weight: bold;}
    a:hover {text-decoration: underline;}
    /* 隐藏 Streamlit 默认菜单让界面更像原生网站 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. 核心逻辑：Pexels 图片搜索
# ---------------------------------------------------------
def get_pexels_images(query, per_page=9):
    """使用 Pexels API 搜索高清图片"""
    headers = {"Authorization": PEXELS_API_KEY}
    url = "https://api.pexels.com/v1/search"
    params = {
        "query": query,
        "per_page": per_page,
        "orientation": "portrait", # 竖屏更适合展示服饰和全身像
        "locale": "en-US" # 强制英文环境搜索更精准
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get("photos", []), None
        elif response.status_code == 401:
            return [], "⚠️ API Key 无效，请检查配置。"
        else:
            return [], f"图片搜索出错 (代码: {response.status_code})"
    except Exception as e:
        return [], str(e)

# ---------------------------------------------------------
# 3. 辅助逻辑：Wiki & Emoji
# ---------------------------------------------------------
def get_country_emoji(query):
    try:
        for country in pycountry.countries:
            if country.name.lower() in query.lower():
                return chr(ord(country.alpha_2[0]) + 127397) + chr(ord(country.alpha_2[1]) + 127397), country.name
    except:
        pass
    return "🌐", "Global"

def get_wiki_summary(query):
    try:
        wikipedia.set_lang("en") 
        search_results = wikipedia.search(query)
        if search_results:
            page = wikipedia.page(search_results[0], auto_suggest=False)
            return page.summary[0:450] + "...", page.url
        else:
            return "暂无详细百科介绍。", "#"
    except:
        return "百科搜索连接超时，建议检查网络或关键词。", "#"

# ---------------------------------------------------------
# 4. UI 主界面
# ---------------------------------------------------------
st.markdown('<h1 class="main-title">🌍 全球审美与文化智库</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">输入关键词，获取本地化服饰、建筑与审美趋势</p>', unsafe_allow_html=True)

# 搜索框
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    query = st.text_input("🔍 请输入英文关键词 (例如: Kimono, Brutalist Architecture, Cyberpunk)", "")

if query:
    st.divider()
    
    # 1. 获取数据
    with st.spinner(f"正在连接全球数据库搜索 '{query}'..."):
        emoji, country_name = get_country_emoji(query)
        wiki_text, wiki_link = get_wiki_summary(query)
        photos, error_msg = get_pexels_images(query)

    # 2. 标题区
    st.subheader(f"{emoji} {country_name} | {query.title()}")
    
    # 3. 布局：左图右文
    c1, c2 = st.columns([2, 1]) 
    
    # --- 左侧：高清美图墙 ---
    with c1:
        st.markdown("### 📸 视觉灵感 (Visuals)")
        if error_msg:
            st.error(error_msg)
        elif photos:
            # 创建 3列 图片网格
            cols = st.columns(3)
            for idx, photo in enumerate(photos):
                col = cols[idx % 3]
                with col:
                    # 展示图片
                    st.image(photo['src']['large'], use_container_width=True)
                    
                    # 获取元数据
                    photographer = photo['photographer']
                    photo_url = photo['url']
                    alt_text = photo['alt']
                    
                    # 图片说明与跳转
                    st.markdown(f"""
                    <div class="img-caption">
                        <span style="color:#888">{alt_text[:30]}...</span><br>
                        <a href="{photo_url}" target="_blank">📥 下载 / 商业许可</a>
                    </div>
                    """, unsafe_allow_html=True)
                    st.write("") # 增加垂直间距
        else:
            st.warning(f"未在 Pexels 图库中找到 '{query}' 相关的高清图片。建议尝试更通用的英文词。")

    # --- 右侧：文化背景 ---
    with c2:
        st.markdown("### 📖 文化背景 (Context)")
        st.info(wiki_text)
        if wiki_link != "#":
            st.markdown(f"[👉 阅读完整 Wikipedia]({wiki_link})")
        
        st.markdown("---")
        st.markdown("### 🏷️ 相关标签")
        tags = [f"#{query.replace(' ', '')}", "#Aesthetics", "#Design", f"#{country_name}"]
        st.write(" ".join(tags))

else:
    # 引导页
    st.markdown("---")
    st.markdown("#### 💡 热门搜索推荐：")
    
    # 创建一些快捷按钮
    but_col1, but_col2, but_col3, but_col4 = st.columns(4)
    if but_col1.button("🇯🇵 Kimono (和服)"):
        st.toast("请在搜索框输入: Kimono")
    if but_col2.button("🇫🇷 Paris Street Style"):
        st.toast("请在搜索框输入: Paris Street Style")
    if but_col3.button("🇪🇸 Gaudi Architecture"):
        st.toast("请在搜索框输入: Gaudi Architecture")
    if but_col4.button("🤖 Cyberpunk"):
        st.toast("请在搜索框输入: Cyberpunk")

    st.caption("数据来源: Wikipedia (知识) & Pexels (视觉)")
# dashboard.py - 量化后台主页 v0.2
import datetime, streamlit as st
from config import DEFAULT_PATH, DEFAULT_ACCOUNT, LINKS, get_footer_text
from trader import get_trader
from premarket import render_premarket_view
from trading import render_trading_view
from postmarket import render_postmarket_view

# 初始化页面
st.set_page_config(
    page_title="Quant Ops Dashboard",
    page_icon="💹",
    layout="wide",
    initial_sidebar_state="expanded",
    # 允许在DataFrame中使用markdown
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# 侧边栏配置
with st.sidebar:
    st.header("⚙️ 连接配置")
    path = st.text_input("安装路径", DEFAULT_PATH)
    account_id = st.text_input("账号", DEFAULT_ACCOUNT)
    if st.button("🔄 重新连接"):
        get_trader.clear()
        st.toast("下次调用将重新连接")

# 页面上半区
top = st.container()
with top:
    tab_pre, tab_live, tab_post = st.tabs(["📈 盘前", "🔄 盘中", "📊 盘后"])

    # 盘前标签页
    with tab_pre:
        render_premarket_view(path, account_id)

    # 盘中标签页
    with tab_live:
        render_trading_view(path, account_id)

    # 盘后标签页
    with tab_post:
        render_postmarket_view(path, account_id)

# 页面下半区 - 功能索引
st.divider()
st.markdown("## 🔗 功能索引 / 快捷入口")

link_cols = st.columns(4)
for col, (label, url) in zip(link_cols, LINKS):
    with col:
        st.page_link(url, label=label, icon="➡️")

# 页脚
st.caption(get_footer_text())

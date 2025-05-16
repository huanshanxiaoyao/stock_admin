# strategies_app.py - 策略配置页面入口
import streamlit as st
from strategies import render_strategy_view
from config import PAGE_CONFIG, get_footer_text

# 初始化页面
st.set_page_config(
    page_title="策略配置",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 渲染策略配置页面
render_strategy_view()

# 页脚
st.caption(get_footer_text())
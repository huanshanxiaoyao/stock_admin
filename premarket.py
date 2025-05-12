# premarket.py - 盘前业务逻辑
import streamlit as st
from trader import get_account_info
from common import run_script

def run_premarket_script(path: str):
    """调用盘前脚本并返回日志与状态"""
    return run_script(path)

def render_premarket_view(path, account_id):
    """渲染盘前视图"""
    row1_col1, row1_col2 = st.columns(2, gap="large")
    row2_col1, row2_col2 = st.columns(2, gap="large")

    # 行 1 • 左：账户信息
    with row1_col1:
        st.subheader("账户当前信息")
        st.dataframe(get_account_info(path, account_id), use_container_width=True)

    # 行 1 • 右：脚本执行 & 日志
    with row1_col2:
        st.subheader("盘前脚本状态")
        script_path = st.text_input("脚本路径", r"C:\scripts\premarket.ps1")
        if st.button("🚀 立即执行"):
            ok, log = run_premarket_script(script_path)
            st.session_state.pre_log = log
            st.session_state.pre_ok = ok

        if "pre_ok" in st.session_state:
            (st.success if st.session_state.pre_ok else st.error)("运行完成")
        st.code(st.session_state.get("pre_log", "（尚未执行）"), height=220)

    # 行 2 • 左：预留模块 1
    with row2_col1:
        st.subheader("行情前瞻（预留）")
        st.info("TODO: 这里可放经济日历、全球指数、因子暴露…")

    # 行 2 • 右：预留模块 2
    with row2_col2:
        st.subheader("预留模块 2")
        st.empty()  # 留空占位，后续自行替换
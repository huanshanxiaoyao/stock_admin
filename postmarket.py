# postmarket.py - 盘后业务逻辑
import streamlit as st
from trader import get_account_info, get_trades

def render_postmarket_view(path, account_id):
    """渲染盘后视图"""
    col_a, col_b = st.columns([1, 2], gap="large")

    with col_a:
        st.subheader("账户当前信息")
        st.dataframe(get_account_info(path, account_id), use_container_width=True)

    with col_b:
        st.subheader("今日成交")
        # 使用真实数据查询
        st.dataframe(get_trades(path, account_id), use_container_width=True)
        
    # 这里可以添加盘后特有的业务逻辑
    # 例如：绩效分析、收益统计等
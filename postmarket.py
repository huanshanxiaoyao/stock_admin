# postmarket.py - 盘后业务逻辑
import streamlit as st
from trader import get_account_info, get_trades
from common import get_xueqiu_link
import os
import json
import pandas as pd
import glob
from datetime import datetime
from postmarket_helper import get_history_trade_from_files

def render_postmarket_view(path, account_id):
    """渲染盘后视图"""
    # 一行一列，依次展示
    st.subheader("总资产走势")

    # 读取所有 account_positions 下的 json 文件（已改为绝对路径）
    data_dir = r"D:\Users\Jack\myqmt_admin\data\account\account_positions"
    files = [f for f in os.listdir(data_dir) if f.endswith(".json") and f[:8].isdigit()]
    files.sort()  # 按日期排序

    records = []
    for fname in files:
        date_str = fname[:8]
        try:
            with open(os.path.join(data_dir, fname), "r", encoding="utf-8") as f:
                data = json.load(f)
            info = data.get("account_info", {})
            total_asset = info.get("总资产")
            market_value = info.get("持仓市值")
            if total_asset is not None and market_value is not None:
                records.append({
                    "date": pd.to_datetime(date_str),
                    "总资产": total_asset,
                    "持仓市值": market_value
                })
        except Exception as e:
            continue

    df = pd.DataFrame(records).set_index("date").sort_index()
    # 补全缺失日期，线性插值
    if not df.empty:
        all_days = pd.date_range(df.index.min(), df.index.max(), freq="D")
        df = df.reindex(all_days)
        df = df.interpolate(method="linear")
        st.line_chart(df[["总资产", "持仓市值"]])
    else:
        st.info("暂无资产数据")

    st.subheader("今日成交")
    # 使用真实数据查询
    trades_df = get_trades(path, account_id)
    
    # 如果存在证券代码列，将其转换为可点击链接
    if not trades_df.empty and '证券代码' in trades_df.columns:
        # 创建一个新的DataFrame用于显示
        display_df = trades_df.copy()
        # 转换证券代码为HTML链接格式
        display_df['证券代码'] = trades_df['证券代码'].apply(
            lambda x: f'<a href="{get_xueqiu_link(x)}" target="_blank">{x}</a>' if pd.notna(x) else ''
        )
        st.write(display_df.to_html(escape=False), unsafe_allow_html=True)
    else:
        st.dataframe(trades_df, use_container_width=True)
        
    # 这里可以添加盘后特有的业务逻辑
    # 例如：绩效分析、收益统计等

    st.subheader("历史成交（不含今日）")

    trades_dir = r"D:\Users\Jack\myqmt_admin\data\account\trades_orders"
    trade_files = sorted(
        glob.glob(os.path.join(trades_dir, "*.json")),
        reverse=True
    )

    # 使用辅助函数获取历史交易记录
    all_trades = get_history_trade_from_files(trade_files)

    # 转为DataFrame并按日期和时间倒序排列
    # 历史成交记录部分
    if all_trades:
        df_trades = pd.DataFrame(all_trades)
        # 如果存在证券代码列，将其转换为可点击链接
        if 'StockCode' in df_trades.columns:
            display_df = df_trades.copy()
            display_df['StockCode'] = df_trades['StockCode'].apply(
                lambda x: f'<a href="{get_xueqiu_link(x)}" target="_blank">{x}</a>' if pd.notna(x) else ''
            )
            st.write(display_df.to_html(escape=False), unsafe_allow_html=True)
        else:
            st.dataframe(df_trades, use_container_width=True)
    else:
        st.info("暂无历史成交记录")
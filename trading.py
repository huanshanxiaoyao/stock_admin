# trading.py - 盘中业务逻辑
import streamlit as st
import pandas as pd
from trader import get_trades

@st.cache_data(ttl=15)  # 15秒缓存，保证数据相对实时
def get_current_trades(path, account_id):
    """获取今日成交"""
    # 直接调用trader.py中的通用函数
    return get_trades(path, account_id)

# 将原有的get_potential_trades函数修改为调用新模块的函数
@st.cache_data(ttl=60)
def get_potential_trades():
    """从日志文件中读取潜在交易机会"""
    from realtime_qmtlog_trigger import read_qmt_log_signals
    signals = read_qmt_log_signals()
        # 转换为DataFrame并返回
    signals_df = pd.DataFrame(signals)
    if signals_df.empty:
        return pd.DataFrame(columns=["信号类型", "证券代码", "详情"])
    return signals_df

def execute_manual_trade(stock_code, trade_type, price, volume, path, account_id):
    """执行手动交易"""
    trader = get_trader(path, account_id)
    
    if trade_type == "买入":
        result = trader.buy_stock(stock_code, volume, price=price, remark='手动触发')
        return result is not None, "买入请求已提交" if result else "买入请求失败"
    else:
        result = trader.sell_stock(stock_code, volume, price=price, remark='手动触发')
        return result is not None, "卖出请求已提交" if result else "卖出请求失败"

def render_trading_view(path, account_id):
    """渲染盘中视图"""
    st.header("🔄 盘中监控")
    
    # 当前委托部分
    st.subheader("当前委托")
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 刷新委托", key="refresh_orders"):
            st.cache_data.clear()
            st.toast("委托数据已刷新")
    
    orders_df = get_current_orders(path, account_id)
    st.dataframe(orders_df, use_container_width=True)
    
    # 添加分隔线
    st.divider()
    
    # 今日成交部分
    st.subheader("今日成交")
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 刷新成交", key="refresh_trades"):
            st.cache_data.clear()
            st.toast("成交数据已刷新")
    
    trades_df = get_current_trades(path, account_id)
    st.dataframe(trades_df, use_container_width=True)
    
    # 添加分隔线
    st.divider()
    
    # 潜在交易机会部分
    st.subheader("潜在交易机会")
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 刷新信号", key="refresh_signals"):
            st.cache_data.clear()
            st.toast("交易信号已刷新")
    
    signals_df = get_potential_trades()
    st.dataframe(
        signals_df,
        use_container_width=True,
        column_config={
            "操作": st.column_config.CheckboxColumn(
                "选择",
                help="选择要执行的交易",
                default=False
            )
        }
    )
    
    # 手动交易表单
    with st.expander("手动触发交易"):
        with st.form("manual_trade_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                stock_code = st.text_input("证券代码", placeholder="例如: 600036")
                trade_type = st.selectbox("交易类型", ["买入", "卖出"])
            
            with col2:
                price = st.number_input("价格", min_value=0.01, step=0.01, value=10.0)
                volume = st.number_input("数量/金额", min_value=100, step=100, value=1000)
            
            submit = st.form_submit_button("执行交易")
            
            if submit:
                success, message = execute_manual_trade(
                    stock_code, trade_type, price, volume, path, account_id
                )
                if success:
                    st.success(message)
                else:
                    st.error(message)


@st.cache_data(ttl=15)  # 15秒缓存，保证数据相对实时
def get_current_orders(path, account_id):
    """获取当前委托订单"""
    from trader import get_orders
    return get_orders(path, account_id)
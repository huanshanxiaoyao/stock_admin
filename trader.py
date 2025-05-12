# trader.py - 交易接口封装
import pandas as pd
import streamlit as st
from mini_trader import MiniTrader

@st.cache_resource(show_spinner="⏳ Connecting…")
def get_trader(path: str, account: str):
    """获取交易接口实例"""
    t = MiniTrader(path, account)
    t.connect()
    return t

@st.cache_data(ttl=30)
def get_account_info(path, account_id):
    """获取账户信息"""
    trader = get_trader(path, account_id)
    account_data = trader.get_account_info()
    
    if account_data:
        return pd.DataFrame({
            "可用资金": [account_data["FreeCash"]],
            "持仓市值": [account_data["MarketValue"]],
            "总资产": [account_data["TotalAsset"]],
            "冻结资金": [account_data["FrozenCash"]]
        }).T.rename(columns={0: "金额(¥)"})
    else:
        # 获取失败时返回空数据
        return pd.DataFrame({"金额(¥)": []})

@st.cache_data(ttl=15)  # 15秒缓存，保证数据相对实时
def get_orders(path, account_id):
    """获取委托订单的通用函数"""
    trader = get_trader(path, account_id)
    orders_df = trader.get_orders()
    
    # 如果返回的是空DataFrame，添加列名
    if orders_df.empty and len(orders_df.columns) == 0:
        return pd.DataFrame(columns=["证券代码", "委托数量", "委托价格", "订单编号", 
                                   "委托策略", "委托状态", "状态描述", "报单时间"])
    
    return orders_df

@st.cache_data(ttl=15)  # 15秒缓存，保证数据相对实时
def get_trades(path, account_id):
    """获取成交信息的通用函数"""
    trader = get_trader(path, account_id)
    trades_df = trader.get_trades()
    
    # 如果返回的是空DataFrame，添加列名并返回
    if trades_df.empty and len(trades_df.columns) == 0:
        return pd.DataFrame(columns=["StockCode", "Volume", "Price", "Value", "TradeType", 
                                   "OrderId", "TradeId", "TradeTime", "Strategy", "Remark"])
    
    # 转换交易类型
    if not trades_df.empty:
        trades_df['TradeType'] = trades_df['TradeType'].map({24: 'sell', 23: 'buy'})
        trades_df = trades_df.rename(columns={
            "StockCode": "证券代码",
            "Volume": "成交数量",
            "Price": "成交价格",
            "Value": "成交金额",
            "TradeType": "交易类型",
            "OrderId": "订单编号",
            "TradeId": "成交编号",
            "TradeTime": "成交时间",
            "Strategy": "策略名称",
            "Remark": "交易备注"
        })
    
    return trades_df

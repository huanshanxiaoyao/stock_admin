import os
import json
import pandas as pd

def get_history_trade_from_files(trade_files):
    """
    从交易文件中获取历史成交记录
    
    Args:
        trade_files: 交易文件路径列表
        
    Returns:
        list: 包含所有标准化交易记录的列表
    """
    all_trades = []
    for file in trade_files:
        date_str = os.path.basename(file)[:8]
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
            trades = data.get("trades", [])
            for trade in trades:
                # 字段名称映射：将中文字段名称转换为英文字段名称
                field_mapping = {
                    "证券代码": "StockCode",
                    "成交数量": "Volume",
                    "成交均价": "Price",
                    "成交金额": "Value",
                    "订单编号": "OrderId",
                    "成交编号": "TradeId",
                    "成交时间": "TradeTime"
                }
                
                # 创建新的交易记录，统一使用英文字段名
                normalized_trade = {}
                
                # 添加日期字段
                normalized_trade["日期"] = date_str
                
                # 处理字段映射
                for key, value in trade.items():
                    if key in field_mapping:
                        # 如果是中文字段名，转换为英文字段名
                        normalized_trade[field_mapping[key]] = value
                    else:
                        # 如果已经是英文字段名或其他字段，保持不变
                        normalized_trade[key] = value
                
                # 处理 TradeType 值：23 -> sell, 24 -> buy
                if "TradeType" in normalized_trade:
                    if normalized_trade["TradeType"] == 23:
                        normalized_trade["TradeType"] = "sell"
                    elif normalized_trade["TradeType"] == 24:
                        normalized_trade["TradeType"] = "buy"
                
                all_trades.append(normalized_trade)
        except Exception as e:
            continue
            
    return all_trades
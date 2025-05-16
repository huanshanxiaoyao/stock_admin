import os
import pandas as pd
import streamlit as st
from collections import deque
import re

def read_qmt_log_signals(log_file=r"D:\Users\Jack\xtquant\logs\main.log", lines_limit=10000):
    """从日志文件中读取潜在交易机会
    
    Args:
        log_file: 日志文件路径
        lines_limit: 读取最后多少行
        
    Returns:
        pd.DataFrame: 包含信号类型、证券代码和详情的DataFrame
    """
    if not os.path.exists(log_file):
        return pd.DataFrame(columns=["信号类型", "证券代码", "详情"])
    
    # 从文件末尾读取最后N行
    def tail(filename, n):
        with open(filename, 'r', encoding='utf-8') as f:
            return deque(f, n)
    
    try:
        lines = tail(log_file, lines_limit)
    except Exception as e:
        st.error(f"读取日志文件失败: {str(e)}")
        return pd.DataFrame(columns=["信号类型", "证券代码", "详情"])
    
    # 解析交易信号
    signals = []
    for line in lines:
        if "触发买入信号" in line or "触发卖出信号" in line:
            # 确定信号类型
            signal_type = "买入" if "触发买入信号" in line else "卖出"
            
            # 查找股票代码（格式：六位数字.两位字母）
            stock_code_match = re.search(r'(\d{6}\.[A-Z]{2})', line)
            if not stock_code_match:
                continue
                
            stock_code = stock_code_match.group(1)
            
            # 提取信号后的详细信息
            detail_start = line.find("信号") + 2
            detail = line[detail_start:].strip()
            
            signals.append({
                "信号类型": signal_type,
                "证券代码": stock_code,
                "详情": detail
            })

    return signals
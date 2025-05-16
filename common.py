# common.py - 公共组件和工具函数
import subprocess
import streamlit as st
from config import PAGE_CONFIG


def run_script(path: str, shell_type="powershell"):
    """通用脚本执行函数"""
    proc = subprocess.run(
        [shell_type, path], capture_output=True,
        text=True, shell=True, timeout=600
    )
    return proc.returncode == 0, proc.stdout + proc.stderr

def render_footer(text):
    """渲染页脚"""
    st.caption(text)


def get_xueqiu_link(stock_code: str) -> str:
    """
    将股票代码转换为雪球网链接
    
    Args:
        stock_code: str, 格式如 "835368.BJ" 或 "000001.SZ"
        
    Returns:
        str: 雪球网链接，如 https://xueqiu.com/S/BJ835368
    """
    code, market = stock_code.split('.')
    if market == 'BJ':
        return f"https://xueqiu.com/S/BJ{code}"
    elif market == 'SZ':
        return f"https://xueqiu.com/S/SZ{code}"
    elif market == 'SH':
        return f"https://xueqiu.com/S/SH{code}"
    else:
        return f"https://xueqiu.com/S/{market}{code}"
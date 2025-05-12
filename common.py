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
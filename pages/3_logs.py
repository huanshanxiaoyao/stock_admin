
# logs_app.py - 日志查询页面
import streamlit as st
import os
import re
import glob
import pandas as pd
from collections import deque
from datetime import datetime, timedelta
from config import get_footer_text

# 初始化页面
st.set_page_config(
    page_title="日志查询",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_log_files_in_date_range(log_base_path, log_type, start_date, end_date):
    """获取指定日期范围内的所有日志文件
    
    Args:
        log_base_path: 日志文件基础路径
        log_type: 日志类型 ('main' 或 'tics')
        start_date: 开始日期
        end_date: 结束日期
        
    Returns:
        list: 日期范围内的日志文件路径列表
    """
    log_files = []
    
    # 获取当前日志文件
    current_log = os.path.join(log_base_path, f"{log_type}.log")
    if os.path.exists(current_log):
        log_files.append(current_log)
    
    # 获取历史日志文件
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y%m%d")
        log_file = os.path.join(log_base_path, f"{log_type}.log.{date_str}")
        if os.path.exists(log_file):
            log_files.append(log_file)
        current_date += timedelta(days=1)
    
    return log_files

def read_log_tail(log_file, lines=200):
    """读取日志文件的最后N行
    
    Args:
        log_file: 日志文件路径
        lines: 要读取的行数
        
    Returns:
        list: 包含日志行的列表
    """
    if not os.path.exists(log_file):
        return []
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            return list(deque(f, lines))
    except Exception as e:
        st.error(f"读取日志文件失败: {str(e)}")
        return []

def read_log_content(log_files, keyword=""):
    """读取多个日志文件的内容并根据关键词过滤
    
    Args:
        log_files: 日志文件路径列表
        keyword: 关键词过滤
        
    Returns:
        list: 包含日志行的列表
    """
    all_lines = []
    
    for log_file in log_files:
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                if keyword:
                    # 如果有关键词，只保留包含关键词的行
                    for line in f:
                        if keyword.lower() in line.lower():
                            all_lines.append(line)
                else:
                    # 如果没有关键词，读取所有行
                    all_lines.extend(f.readlines())
        except Exception as e:
            st.error(f"读取日志文件 {log_file} 失败: {str(e)}")
    
    return all_lines

def parse_log_line(line):
    """解析日志行，提取时间戳和内容
    
    Args:
        line: 日志行文本
        
    Returns:
        tuple: (时间戳, 日志内容)
    """
    # 尝试匹配常见的时间戳格式
    timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})', line)
    if timestamp_match:
        timestamp = timestamp_match.group(1)
        content = line[timestamp_match.end():].strip()
        return timestamp, content
    return "", line.strip()

def filter_logs_by_time(log_lines, start_time=None, end_time=None):
    """根据时间范围过滤日志
    
    Args:
        log_lines: 日志行列表
        start_time: 开始时间
        end_time: 结束时间
        
    Returns:
        list: 过滤后的日志行
    """
    filtered_lines = []
    
    for line in log_lines:
        timestamp, content = parse_log_line(line)
        
        # 时间范围过滤
        if timestamp:
            try:
                log_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                if start_time and log_time < start_time:
                    continue
                if end_time and log_time > end_time:
                    continue
            except:
                pass  # 如果时间解析失败，不进行时间过滤
                
        filtered_lines.append(line)
    
    return filtered_lines

def render_logs_view():
    """渲染日志查询页面"""
    st.title("📋 日志查询")
    
    # 定义日志文件基础路径
    log_base_path = r"D:\Users\Jack\xtquant\logs"
    
    # 创建选项卡
    tab1, tab2 = st.tabs(["主日志 (main.log)", "行情日志 (tick.log)"])
    
    # 主日志选项卡
    with tab1:
        st.subheader("主日志查询")
        
        # 查询参数
        col1, col2, col3 = st.columns(3)
        with col1:
            keyword = st.text_input("关键词过滤", key="main_keyword")
        with col2:
            start_date = st.date_input("开始日期", key="main_start_date")
            start_time = datetime.combine(start_date, datetime.min.time())
        with col3:
            end_date = st.date_input("结束日期", key="main_end_date")
            end_time = datetime.combine(end_date, datetime.max.time())
        
        # 刷新按钮
        col1, col2 = st.columns([3, 1])
        with col2:
            refresh = st.button("🔄 刷新日志", key="refresh_main")
        
        # 获取日期范围内的所有日志文件
        log_files = get_log_files_in_date_range(log_base_path, "main", start_date, end_date)
        
        if not log_files:
            st.warning(f"在指定日期范围内未找到日志文件")
        else:
            # 根据是否有关键词决定读取方式
            if keyword:
                # 有关键词，进行全文搜索
                with st.spinner(f"正在搜索 {len(log_files)} 个日志文件..."):
                    log_lines = read_log_content(log_files, keyword)
                    filtered_lines = filter_logs_by_time(log_lines, start_time, end_time)
                
                if filtered_lines:
                    st.code("".join(filtered_lines), language="text")
                    st.info(f"找到 {len(filtered_lines)} 条匹配记录，来自 {len(log_files)} 个日志文件")
                else:
                    st.warning(f"未找到包含关键词 '{keyword}' 的日志记录")
            else:
                # 没有关键词，只读取最新的200行
                if len(log_files) > 0:
                    # 只读取当前日志文件的末尾
                    current_log = log_files[0]  # 当前日志文件应该是第一个
                    log_lines = read_log_tail(current_log, 200)
                    filtered_lines = filter_logs_by_time(log_lines, start_time, end_time)
                    
                    if filtered_lines:
                        st.code("".join(filtered_lines), language="text")
                        st.info(f"显示最新 {len(filtered_lines)} 行日志")
                    else:
                        st.warning("在指定时间范围内没有日志记录")
            
            # 导出功能（仅当有数据时显示）
            if 'filtered_lines' in locals() and filtered_lines:
                if st.download_button(
                    "📥 导出筛选结果", 
                    "".join(filtered_lines), 
                    file_name=f"main_log_export_{start_date.strftime('%Y%m%d')}-{end_date.strftime('%Y%m%d')}.txt",
                    mime="text/plain"
                ):
                    st.success("日志导出成功！")
    
    # 行情日志选项卡
    with tab2:
        st.subheader("行情日志查询")
        
        # 查询参数
        col1, col2, col3 = st.columns(3)
        with col1:
            keyword = st.text_input("关键词过滤", key="tick_keyword")
        with col2:
            start_date = st.date_input("开始日期", key="tick_start_date")
            start_time = datetime.combine(start_date, datetime.min.time())
        with col3:
            end_date = st.date_input("结束日期", key="tick_end_date")
            end_time = datetime.combine(end_date, datetime.max.time())
        
        # 刷新按钮
        col1, col2 = st.columns([3, 1])
        with col2:
            refresh = st.button("🔄 刷新日志", key="refresh_tick")
        
        # 获取日期范围内的所有日志文件
        log_files = get_log_files_in_date_range(log_base_path, "tick", start_date, end_date)
        
        if not log_files:
            st.warning(f"在指定日期范围内未找到日志文件")
        else:
            # 根据是否有关键词决定读取方式
            if keyword:
                # 有关键词，进行全文搜索
                with st.spinner(f"正在搜索 {len(log_files)} 个日志文件..."):
                    log_lines = read_log_content(log_files, keyword)
                    filtered_lines = filter_logs_by_time(log_lines, start_time, end_time)
                
                if filtered_lines:
                    st.code("".join(filtered_lines), language="text")
                    st.info(f"找到 {len(filtered_lines)} 条匹配记录，来自 {len(log_files)} 个日志文件")
                else:
                    st.warning(f"未找到包含关键词 '{keyword}' 的日志记录")
            else:
                # 没有关键词，只读取最新的200行
                if len(log_files) > 0:
                    # 只读取当前日志文件的末尾
                    current_log = log_files[0]  # 当前日志文件应该是第一个
                    log_lines = read_log_tail(current_log, 200)
                    filtered_lines = filter_logs_by_time(log_lines, start_time, end_time)
                    
                    if filtered_lines:
                        st.code("".join(filtered_lines), language="text")
                        st.info(f"显示最新 {len(filtered_lines)} 行日志")
                    else:
                        st.warning("在指定时间范围内没有日志记录")
            
            # 导出功能（仅当有数据时显示）
            if 'filtered_lines' in locals() and filtered_lines:
                if st.download_button(
                    "📥 导出筛选结果", 
                    "".join(filtered_lines), 
                    file_name=f"tick_log_export_{start_date.strftime('%Y%m%d')}-{end_date.strftime('%Y%m%d')}.txt",
                    mime="text/plain"
                ):
                    st.success("日志导出成功！")

# 渲染日志查询页面
render_logs_view()

# 页脚
st.caption(get_footer_text())
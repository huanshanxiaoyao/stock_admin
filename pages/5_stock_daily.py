# 股票分钟级K线图展示
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

# 添加上级目录到路径中，以便导入stock_common_utils
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))
from stock_common_utils.data_manager import DataManager

# 创建DataManager实例
data_manager = DataManager()

# 页面配置
st.set_page_config(
    page_title="股票分钟级K线图",
    page_icon="📊",
    layout="wide"
)

# 页面标题
st.title("📊 股票分钟级K线图")

# 创建输入表单
with st.form("stock_data_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        stock_code = st.text_input("股票代码", placeholder="例如: 836077.BJ", value="836077.BJ")
    
    with col2:
        date_input = st.text_input("交易日期", placeholder="例如: 20250513", 
                                  value=datetime.now().strftime("%Y%m%d"))
    
    submit_button = st.form_submit_button("获取K线图")

# 当用户提交表单时
if submit_button or ('stock_code' in st.session_state and 'date_input' in st.session_state):
    # 保存当前输入到session_state
    if submit_button:
        st.session_state['stock_code'] = stock_code
        st.session_state['date_input'] = date_input
    
    # 使用session_state中的值
    stock_code = st.session_state['stock_code']
    date_input = st.session_state['date_input']
    
    try:
        # 显示加载状态
        with st.spinner(f"正在获取 {stock_code} 在 {date_input} 的分钟级数据..."):
            # 调用data_manager中的接口获取分钟级数据
            print(f"stock_code: {stock_code}, date_input: {date_input}")
            minute_data = data_manager.get_minutes_data(['open', 'high', 'low', 'close', 'volume'], [stock_code], date_input, date_input)
            print(f"minute_data: {minute_data}")
            
            if minute_data is not None and all(not df.empty for df in minute_data.values()):
                # 数据处理：将字典中的各个DataFrame合并成一个
                # 假设所有DataFrame具有相同的索引
                combined_data = pd.DataFrame()
                for key, df in minute_data.items():
                    # 转置DataFrame使股票代码成为列
                    transposed = df.T
                    # 重命名列为数据类型
                    combined_data[key] = transposed.iloc[:, 0]  # 假设只有一个股票代码
                
                # 处理时间索引格式：从20250514093000转换为0930
                if not combined_data.empty:
                    # 创建新的时间索引
                    new_index = []
                    for time_str in combined_data.index:
                        # 提取时分部分（第9-12位）
                        time_only = str(time_str)[8:12]
                        new_index.append(time_only)
                    
                    # 更新DataFrame的索引
                    combined_data.index = new_index
                    
                    # 对索引进行排序，确保时间顺序正确
                    combined_data = combined_data.sort_index()
                
                # 确保数据包含必要的列
                required_columns = ['open', 'high', 'low', 'close', 'volume']
                missing_columns = [col for col in required_columns if col not in combined_data.columns]
                
                if missing_columns:
                    st.error(f"数据缺少必要的列: {', '.join(missing_columns)}")
                else:
                    # 创建K线图，使用更健壮的方式处理数据
                    try:
                        # 尝试创建K线图
                        fig = go.Figure(data=[go.Candlestick(
                            x=combined_data.index,
                            open=combined_data['open'],
                            high=combined_data['high'],
                            low=combined_data['low'],
                            close=combined_data['close'],
                            name='K线'
                        )])
                        
                        # 添加成交量图表
                        fig.add_trace(go.Bar(
                            x=combined_data.index,
                            y=combined_data['volume'],
                            name='成交量',
                            marker_color='rgba(0, 0, 255, 0.5)',
                            yaxis='y2'
                        ))
                        
                        # 设置图表布局
                        fig.update_layout(
                            title=f'{stock_code} - {date_input} 分钟K线图',
                            yaxis_title='价格',
                            yaxis2=dict(
                                title='成交量',
                                overlaying='y',
                                side='right'
                            ),
                            xaxis_rangeslider_visible=False,
                            height=600,
                            hovermode='x unified',
                            # 设置X轴为分类轴，不保留缺失的类别
                            xaxis=dict(
                                type='category',
                                categoryorder='array',
                                categoryarray=sorted(combined_data.index)
                            )
                        )
                        
                        # 显示图表
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # 显示原始数据表格
                        with st.expander("查看原始数据"):
                            # 使用更安全的方式显示数据
                            if isinstance(minute_data, dict):
                                # 如果是字典，显示每个键的数据
                                for key, value in minute_data.items():
                                    st.subheader(f"{key}")
                                    if isinstance(value, pd.DataFrame):
                                        st.dataframe(value, use_container_width=True)
                                    else:
                                        st.write(value)
                            else:
                                st.dataframe(minute_data, use_container_width=True)
                    except Exception as e:
                        st.error(f"创建图表时发生错误: {str(e)}")
                        st.write("原始数据结构:")
                        st.write(minute_data)
            else:
                st.warning(f"未找到 {stock_code} 在 {date_input} 的分钟级数据")
                data_manager.download_data_async([stock_code], '1m', date_input)
    
    except Exception as e:
        st.error(f"获取数据时发生错误: {str(e)}")
        st.info("请确保stock_common_utils/data_manager.py中包含get_minute_data函数，并且能够正确获取分钟级数据")

# 添加使用说明
with st.expander("使用说明"):
    st.markdown("""
    ### 使用说明
    
    1. 在**股票代码**输入框中输入要查询的股票代码，格式如：836077.BJ
    2. 在**交易日期**输入框中输入要查询的日期，格式如：20250513
    3. 点击**获取K线图**按钮获取数据并显示K线图
    
    ### 注意事项
    
    - 确保输入的股票代码格式正确，包含市场后缀（如.BJ、.SH、.SZ等）
    - 日期格式为8位数字，如20250513表示2025年5月13日
    - 如果指定日期为非交易日或数据不存在，将无法获取数据
    """)
import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

# 添加上级目录到路径中，以便导入stock_common_utils
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))
from stock_common_utils.data_manager import DataManager
from stock_common_utils.stock_code_config import *
from stock_common_utils.date_utils import get_last_trading_day

# 页面标题
st.title("北交所股票排行榜")

# 初始化数据管理器
data_manager = DataManager()

# 日期选择器
selected_date = st.date_input("选择日期", datetime.now().date() - pd.Timedelta(days=1))

# 股票集合选择
stock_sets = {
    "BJ_50": "北交所50指数成分股",
    "BJ_ALL": "北交所全部股票",
    "SH_50": "上证50指数成分股",
}
selected_stock_set = st.selectbox("选择股票集合", options=list(stock_sets.keys()), format_func=lambda x: stock_sets[x])

# 获取选定日期的股票数据
@st.cache_data
def get_stock_data(date, stock_set):
    try:
        # 根据选择的股票集合获取相应的股票代码列表
        if stock_set == "BJ_ALL":
            stock_codes = BJ_ALL
        elif stock_set == "BJ_50":
            stock_codes = BJ50
        elif stock_set == "SH_50":
            stock_codes = SH50
        else:
            stock_codes = BJ_ALL
            
       
        date_str = date.strftime("%Y%m%d")
        
        # 获取当天股票数据
        required_columns = ['code', 'open', 'close', 'high', 'low', 'volume', 'amount']
        stock_data_dict = data_manager.get_local_daily_data(required_columns, stock_codes, date_str)
        
        # 检查是否所有股票都有数据
        missing_data_codes = []
        for code in stock_codes:
            if code not in stock_data_dict or stock_data_dict[code].empty:
                missing_data_codes.append(code)
            elif 'close' not in stock_data_dict[code].columns or stock_data_dict[code]['close'].isnull().all():
                missing_data_codes.append(code)
        
        # 如果有缺失数据，触发下载
        if missing_data_codes:
            st.warning(f"正在下载缺失的股票数据，共 {len(missing_data_codes)} 只股票，请稍后重试...")
            print(f"Missing codes: {missing_data_codes}")
            # 下载数据，使用当天日期前30天作为开始日期
            start_date = (datetime.strptime(date_str, "%Y%m%d") - pd.Timedelta(days=3)).strftime("%Y%m%d")
            data_manager.download_data_async(missing_data_codes, 'daily', start_date, date_str)
            return pd.DataFrame()  # 返回空DataFrame，提示用户稍后重试
        
        # 获取前一个交易日
        last_tradedate = get_last_trading_day(date_str)
        
        # 获取前一个交易日的数据，用于计算涨跌幅
        last_day_data_dict = data_manager.get_local_daily_data(['code', 'close'], stock_codes, last_tradedate)
        #print(f"前一交易日数据: {last_day_data_dict}")
        
        # 将字典格式转换为单个DataFrame
        result_df = pd.DataFrame()
        for code, df in stock_data_dict.items():
            if not df.empty:
                # 确保日期索引是字符串格式
                date_idx = df.index[0]
                if isinstance(date_idx, str) or isinstance(date_idx, int):
                    # 创建单行数据
                    row_data = df.loc[date_idx].copy() if date_idx in df.index else pd.Series()
                    if not row_data.empty:
                        # 添加股票代码
                        row_data['code'] = code
                        # 如果没有name列，添加一个空的name列
                        if 'name' not in row_data:
                            row_data['name'] = code.split('.')[0]
                        
                        # 获取前一个交易日的收盘价
                        if code in last_day_data_dict and not last_day_data_dict[code].empty:
                            last_idx = last_day_data_dict[code].index[0]
                            if last_idx in last_day_data_dict[code].index:
                                row_data['pre_close'] = last_day_data_dict[code].loc[last_idx, 'close']
                                #print(f"close: {row_data['close']}, pre_close: {row_data['pre_close']}")
                        
                        # 将行数据添加到结果DataFrame
                        result_df = pd.concat([result_df, pd.DataFrame([row_data])])
        
        # 重置索引
        if not result_df.empty:
            result_df = result_df.reset_index(drop=True)
            
            # 确保数据包含必要的列
            for col in required_columns:
                if col not in result_df.columns:
                    if col == 'pre_close':
                        # 如果没有pre_close列，使用前一天的收盘价
                        result_df['pre_close'] = result_df['close']
                    else:
                        st.error(f"数据中缺少必要的列: {col}")
                        return pd.DataFrame()
            
            # 计算涨跌幅
            result_df['change_pct'] = (result_df['close'] - result_df['pre_close']) / result_df['pre_close'] * 100
            
            # 将NaN值替换为0
            result_df = result_df.fillna(0)
            
            # 确保所有数值列都是数值类型
            numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'amount', 'pre_close', 'change_pct']
            for col in numeric_cols:
                if col in result_df.columns:
                    result_df[col] = pd.to_numeric(result_df[col], errors='coerce').fillna(0)
        
        return result_df
    except Exception as e:
        st.error(f"获取数据时出错: {str(e)}")
        return pd.DataFrame()

# 获取数据
df = get_stock_data(selected_date, selected_stock_set)

if df.empty:
    st.warning(f"未找到 {selected_date} 的股票数据，请选择其他日期。")
else:
    # 创建三个标签页，分别展示涨跌幅、成交量和成交额排行榜
    tab1, tab2, tab3 = st.tabs(["涨跌幅排行", "成交量排行", "成交额排行"])
    
    # 涨跌幅排行榜
    with tab1:
        st.subheader("涨跌幅排行榜")
        
        # 按涨跌幅排序
        df_change = df.sort_values(by='change_pct', ascending=False).reset_index(drop=True)
        
        # 默认显示前20
        show_all = st.checkbox("显示全部", key="show_all_change")
        if show_all:
            st.dataframe(df_change[['code', 'name', 'close', 'change_pct', 'volume', 'amount']].style.format({
                'change_pct': '{:.2f}%',
                'volume': '{:,.0f}',
                'amount': '{:,.2f}'
            }))
        else:
            st.dataframe(df_change.head(20)[['code', 'name', 'close', 'change_pct', 'volume', 'amount']].style.format({
                'change_pct': '{:.2f}%',
                'volume': '{:,.0f}',
                'amount': '{:,.2f}'
            }))
    
    # 成交量排行榜
    with tab2:
        st.subheader("成交量排行")
        
        # 按成交量排序
        df_volume = df.sort_values(by='volume', ascending=False).reset_index(drop=True)
        
        # 默认显示前20
        show_all = st.checkbox("显示全部", key="show_all_volume")
        if show_all:
            st.dataframe(df_volume[['code', 'name', 'close', 'change_pct', 'volume', 'amount']].style.format({
                'change_pct': '{:.2f}%',
                'volume': '{:,.0f}',
                'amount': '{:,.2f}'
            }))
        else:
            st.dataframe(df_volume.head(20)[['code', 'name', 'close', 'change_pct', 'volume', 'amount']].style.format({
                'change_pct': '{:.2f}%',
                'volume': '{:,.0f}',
                'amount': '{:,.2f}'
            }))
    
    # 成交额排行榜
    with tab3:
        st.subheader("成交额排行")
        
        # 按成交额排序
        df_amount = df.sort_values(by='amount', ascending=False).reset_index(drop=True)
        
        # 默认显示前20
        show_all = st.checkbox("显示全部", key="show_all_amount")
        if show_all:
            st.dataframe(df_amount[['code', 'name', 'close', 'change_pct', 'volume', 'amount']].style.format({
                'change_pct': '{:.2f}%',
                'volume': '{:,.0f}',
                'amount': '{:,.2f}'
            }))
        else:
            st.dataframe(df_amount.head(20)[['code', 'name', 'close', 'change_pct', 'volume', 'amount']].style.format({
                'change_pct': '{:.2f}%',
                'volume': '{:,.0f}',
                'amount': '{:,.2f}'
            }))


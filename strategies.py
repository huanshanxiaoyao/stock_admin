# strategies.py - 策略配置页面
import os
import sys
import streamlit as st
import pandas as pd
import importlib.util
from config import DEFAULT_PATH, DEFAULT_ACCOUNT

def load_strategy_params():
    """
    从 ../xtquant/strategy/strategy_params.py 加载策略参数
    """
    try:
        # 构建策略参数文件的路径
        strategy_params_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                           "xtquant", "strategy", "strategy_params.py")
        
        if not os.path.exists(strategy_params_path):
            return None, f"策略参数文件不存在: {strategy_params_path}"
        
        # 添加模块所在目录到系统路径
        module_dir = os.path.dirname(strategy_params_path)
        parent_dir = os.path.dirname(module_dir)  # 获取上级目录
        
        # 保存原始路径以便后续恢复
        original_path = sys.path.copy()
        
        # 添加目录到系统路径
        sys.path.insert(0, module_dir)
        sys.path.insert(0, parent_dir)  # 添加上级目录
        
        # 动态加载模块
        spec = importlib.util.spec_from_file_location("strategy_params", strategy_params_path)
        strategy_params = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(strategy_params)
        
        # 使用完后恢复原始路径
        sys.path = original_path
        
        # 获取所有策略参数
        params = {}
        for attr_name in dir(strategy_params):
            # 跳过私有属性和内置属性
            if attr_name.startswith('__') or attr_name.startswith('_'):
                continue
            
            attr_value = getattr(strategy_params, attr_name)
            # 只获取字典类型的属性，这些通常是策略参数
            if isinstance(attr_value, dict):
                params[attr_name] = attr_value
        
        return params, None
    except Exception as e:
        return None, f"加载策略参数时出错: {str(e)}"

def render_strategy_view():
    """渲染策略配置页面"""
    st.title("策略配置")
    
    # 加载策略参数
    params, error = load_strategy_params()
    
    if error:
        st.error(error)
        return
    
    if not params:
        st.warning("未找到任何策略参数")
        return
    
    # 创建策略选择器
    strategy_names = list(params.keys())
    selected_strategy = st.selectbox("选择策略参数", strategy_names)
    
    if selected_strategy:
        st.subheader(f"{selected_strategy} 参数配置")
        
        # 获取选定策略的参数
        strategy_params = params[selected_strategy]
        
        # 将参数转换为DataFrame以便展示
        param_data = []
        for param_name, param_value in strategy_params.items():
            param_type = type(param_value).__name__
            param_data.append({
                "参数名": param_name,
                "参数值": str(param_value),
                "类型": param_type
            })
        
        param_df = pd.DataFrame(param_data)
        st.dataframe(param_df, use_container_width=True)
        
        # 显示原始参数字典
        with st.expander("查看原始参数字典"):
            st.code(str(strategy_params))
        
        st.info("注意：当前仅支持查看策略参数，不支持修改。")

if __name__ == "__main__":
    st.set_page_config(
        page_title="策略配置",
        page_icon="⚙️",
        layout="wide"
    )
    render_strategy_view()
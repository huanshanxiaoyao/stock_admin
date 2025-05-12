# config.py - 系统配置信息
import datetime

# 默认配置
DEFAULT_PATH = r"D:\Apps\ZJ_QMT3\userdata_mini"
DEFAULT_ACCOUNT = "6681802088"

# 页面配置
PAGE_CONFIG = {
    "page_title": "Quant Ops Dashboard",
    "page_icon": "💹",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

# 链接配置
LINKS = [
    ("回测管理", "http://localhost:8501/backtest"),
    ("日志查询", "http://localhost:8501/logs"),
    ("策略配置", "http://localhost:8501/strategies"),
    ("系统设置", "http://localhost:8501/settings"),
]

# 版权信息
def get_footer_text():
    return f"© {datetime.date.today().year} Quant Team | Last refresh : {datetime.datetime.now():%H:%M:%S}"
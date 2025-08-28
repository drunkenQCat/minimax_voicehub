import streamlit as st

import pandas as pd


def load_excel_data(file_path: str) -> pd.DataFrame:
    """加载Excel文件数据"""
    try:
        # 读取Excel文件
        df = pd.read_excel(file_path, engine="openpyxl")
        return df
    except Exception as e:
        st.error(f"加载Excel文件失败: {str(e)}")
        return pd.DataFrame()

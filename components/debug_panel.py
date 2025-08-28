import streamlit as st
import pandas as pd
from pydantic import BaseModel


def display_debug_panel():
    """在 Streamlit 应用中显示一个用于调试的、可折叠的会话状态面板。"""
    if not st.session_state.get("debug_mode", False):
        return

    st.markdown("##### 🐞 Debug Panel")

    # 添加筛选输入框
    filter_text = st.text_input(
        "筛选 Session State 参数", key="debug_panel_filter"
    ).lower()

    # 创建一个可供st.json使用的字典副本
    state_dict = {}
    for key, value in st.session_state.items():
        # 应用筛选
        if filter_text and type(key) is str and filter_text not in key.lower():
            continue

        # 对特殊对象进行处理，以便能够被json序列化
        if isinstance(value, pd.DataFrame):
            state_dict[key] = f"DataFrame with {len(value)} rows"
        elif hasattr(value, "__dict__"):
            if isinstance(value, BaseModel):
                try:
                    state_dict[key] = value.model_dump()
                except Exception:
                    state_dict[key] = (
                        f"Pydantic model of type {type(value).__name__}, could not be serialized"
                    )
            else:
                try:
                    # 排除内置或大型属性
                    simple_dict = {
                        k: v
                        for k, v in value.__dict__.items()
                        if not k.startswith("_") and not isinstance(v, (pd.DataFrame))
                    }
                    state_dict[key] = (
                        simple_dict
                        if simple_dict
                        else f"Object of type {type(value).__name__}"
                    )
                except Exception:
                    state_dict[key] = (
                        f"Object of type {type(value).__name__}, not serializable"
                    )
        else:
            state_dict[key] = value

    st.json(state_dict, expanded=True)
    st.markdown("---")


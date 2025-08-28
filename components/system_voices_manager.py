import streamlit as st


from minimax_speech.tts_models import Voice


from components.voice_manager import VoiceManager


class APIVoice:
    def __init__(self, voice_id, name, description=[]):
        self.value = voice_id
        self.name = name
        self.description = description


def render_system_voices_manager(voice_manager: VoiceManager):
    def update_selected_voice():
        """更新选中的音色"""
        voice_id = st.session_state.get("selected_system_voice_option", "")
        voice_manager.current_voice = (
            st.session_state.voice_options[voice_id] if voice_id else ""
        )

    st.subheader("🎭 系统音色测试")

    # 初始化session_state中的系统音色
    if "system_voices" not in st.session_state:
        st.session_state.system_voices = list(Voice)
        st.session_state.api_system_voices = []

    # 获取基础系统音色（枚举中的）
    base_system_voices = list(Voice)

    # 合并基础音色和API获取的音色

    with st.spinner("正在获取系统音色..."):
        # 使用新的 get_voices 方法获取系统音色，内置缓存机制
        api_system_voices_data = voice_manager.get_voices(voice_type="system")

        if not api_system_voices_data:
            st.warning("未获取到系统音色")
            # even if it fails, we should ensure the list is empty
            st.session_state.api_system_voices = []
            api_voices = []
        else:
            # 创建API音色对象
            api_voices: list[APIVoice] = []
            for voice_info in api_system_voices_data:
                # 创建一个类似Voice枚举的对象
                api_voice = APIVoice(
                    voice_id=voice_info.voice_id,
                    name=voice_info.voice_name or voice_info.voice_id,
                    description=voice_info.description or "",
                )
                api_voices.append(api_voice)

            # 更新session_state
            if "api_system_voices" not in st.session_state or len(
                st.session_state.api_system_voices
            ) != len(api_voices):
                st.success(f"成功获取 {len(api_voices)} 个系统音色")
            st.session_state.api_system_voices = api_voices
    # 添加获取API系统音色的按钮
    col_search, col_clear_search = st.columns([2, 1])

    with col_search:
        # 搜索框
        search_term = st.text_input(
            "🔍 搜索音色",
            placeholder="输入音色名称或描述进行搜索...",
            help="支持按音色ID、名称或描述搜索，搜索结果会显示在下拉菜单中",
            key="search_term",
        )

    with col_clear_search:
        if search_term:
            if st.button("🗑️ 清除搜索", help="清除搜索条件，显示所有音色"):
                # 清除搜索状态
                if "search_term" in st.session_state:
                    del st.session_state.search_term
                st.rerun()

    # 过滤音色
    filtered_voices: list[Voice | APIVoice] = []
    if search_term:
        search_lower = search_term.lower()  # 提前转换大小写避免重复计算

        for voice in base_system_voices:
            # 检查主要属性
            matches_value = search_lower in voice.value.lower()
            matches_name = search_lower in voice.name.lower()

            # 任一条件匹配则包含
            if matches_value or matches_name:
                filtered_voices.append(voice)
        for voice in api_voices:
            # 只检查第一个描述（根据原逻辑）
            # 检查主要属性
            matches_value = search_lower in voice.value.lower()
            matches_name = search_lower in voice.name.lower()
            if matches_value or matches_name:
                # 任一条件匹配则包含
                filtered_voices.append(voice)

    else:
        filtered_voices.extend(base_system_voices)
        filtered_voices.extend(st.session_state.api_system_voices)
    # 显示当前音色来源和搜索状态
    if search_term:
        if filtered_voices:
            st.success(
                f"🔍 搜索 '{search_term}' 找到 {len(filtered_voices)} 个匹配音色 ↓ 请在下拉菜单中选择"
            )
        else:
            st.warning(f"🔍 搜索 '{search_term}' 没有找到匹配的音色")
    else:
        if st.session_state.api_system_voices:
            st.info(
                f"📊 当前显示 {len(base_system_voices)} 个音色（基础 {len(base_system_voices)} + API {len(st.session_state.api_system_voices)}）"
            )
        else:
            st.info(f"📊 当前显示 {len(base_system_voices)} 个基础音色")

    if not filtered_voices:
        st.info("没有找到匹配的音色")
    # 选择音色
    voice_options = {}
    for voice in filtered_voices:
        display_name = f"{voice.value} ({voice.name})"
        voice_options[display_name] = voice.value
    if voice_options:
        st.session_state.voice_options = voice_options

    # 根据搜索结果调整下拉菜单的提示
    if search_term and filtered_voices:
        selectbox_label = f"🎯 选择系统音色 (找到 {len(filtered_voices)} 个匹配结果)"
        selectbox_help = (
            f"搜索结果：'{search_term}' 匹配到 {len(filtered_voices)} 个音色"
        )
    elif search_term and not filtered_voices:
        selectbox_label = "❌ 选择系统音色 (无匹配结果)"
        selectbox_help = f"搜索 '{search_term}' 没有找到匹配的音色"
    else:
        selectbox_label = "选择系统音色"
        selectbox_help = "选择要测试的系统音色"

    st.selectbox(
        selectbox_label,
        options=list(voice_options.keys()),
        help=selectbox_help,
        on_change=update_selected_voice,
        key="selected_system_voice_option",
    )
    if search_term and filtered_voices:
        update_selected_voice()

"""
MiniMax 音色管理器核心类
"""

import os
import streamlit as st
from minimax_speech import MiniMaxSpeech, SystemVoice
from minimax_speech.voice_query_models import VoiceCloning
from minimax_speech.tts_models import T2AResponse


class VoiceManager:
    """音色管理器"""

    client: MiniMaxSpeech
    cloned_voices_cache: list[VoiceCloning] | None
    cloned_voices_cache_time: int
    system_voices_cache: list[SystemVoice] | None
    system_voices_cache_time: int
    current_voice: str = ""

    def __init__(self) -> None:
        api_key = os.getenv("MINIMAX_API_KEY", "")
        group_id = os.getenv("MINIMAX_GROUP_ID", "")
        self.cloned_voices_cache = None
        self.cloned_voices_cache_time = 0
        self.system_voices_cache = None
        self.system_voices_cache_time = 0
        self.init_client(api_key, group_id)
        # 初始化 session_state 中的确认状态
        if "confirm_delete_id" not in st.session_state:
            st.session_state.confirm_delete_id = None

    def init_client(self, api_key: str, group_id: str):
        """初始化客户端"""
        try:
            self.client = MiniMaxSpeech(api_key=api_key, group_id=group_id)
            return True
        except Exception as e:
            st.error(f"初始化客户端失败: {str(e)}")
            return False

    def get_voices(self, voice_type: str = "clone", force_refresh: bool = False):
        """
        获取音色列表
        :param voice_type: 'clone' 或 'system'
        :param force_refresh: 是否强制刷新
        """
        current_time = int(st.session_state.get("current_time", 0))

        if voice_type == "clone":
            cache = self.cloned_voices_cache
            cache_time = self.cloned_voices_cache_time
            # 5分钟缓存
            is_cache_valid = cache is not None and (current_time - cache_time) <= 300

            if not force_refresh and is_cache_valid:
                # 如果没有必要刷新，就跳过
                return self.cloned_voices_cache
            try:
                st.toast("正在获取克隆音色列表...")
                self.cloned_voices_cache = self.client.get_cloned_voices()
                self.cloned_voices_cache_time = current_time
                if self.cloned_voices_cache is not None:
                    self.current_voice = self.cloned_voices_cache[0].voice_id
            except Exception as e:
                st.error(f"获取克隆音色列表失败: {str(e)}")
                self.cloned_voices_cache = None
            return self.cloned_voices_cache

        elif voice_type == "system":
            cache = self.system_voices_cache
            cache_time = self.system_voices_cache_time
            # 5分钟缓存
            is_cache_valid = cache is not None and (current_time - cache_time) <= 300

            if not force_refresh and is_cache_valid:
                # 如果没有必要刷新，就跳过
                return self.system_voices_cache
            try:
                st.toast("正在获取系统音色列表...")
                self.system_voices_cache = self.client.get_system_voices()
                self.system_voices_cache_time = current_time
                if self.system_voices_cache is not None:
                    self.current_voice = self.system_voices_cache[0].voice_id
            except Exception as e:
                st.error(f"获取系统音色列表失败: {str(e)}")
                self.system_voices_cache = None
            return self.system_voices_cache

        return None

    def delete_voice(self, voice_id: str):
        """删除音色"""
        try:
            result = self.client.voice_delete(voice_id)
            if result.base_resp.is_success:
                st.success(f"成功删除音色: {voice_id}")
                # 刷新缓存
                self.get_voices(force_refresh=True)
                return True
            else:
                st.error(f"删除音色失败: {result.base_resp.error_type}")
                return False
        except Exception as e:
            st.error(f"删除音色时发生错误: {str(e)}")
            return False

    def clone_voice(self, file_id: int, voice_id: str, **kwargs):
        """克隆音色"""
        try:
            print(file_id)
            print(voice_id)
            print(kwargs)
            result = self.client.voice_clone_simple(
                file_id=file_id, voice_id=voice_id, **kwargs
            )
            if result.base_resp.is_success:
                st.success(f"成功克隆音色: {voice_id}")
                # 刷新缓存
                self.get_voices(force_refresh=True)
                return True
            else:
                st.error(f"克隆音色失败: {result.base_resp.error_type}")
                return False
        except Exception as e:
            st.error(f"克隆音色时发生错误: {str(e)}")
            return False

    def test_voice(self, voice_id: str, text: str, **kwargs) -> T2AResponse | None:
        """测试音色"""
        try:
            result = self.client.text_to_speech_simple(
                text=text, voice_id=voice_id, **kwargs
            )
            if result.base_resp.is_success:
                return result
            else:
                st.error(f"生成测试音频失败: {result.base_resp.error_type}")
                return None
        except Exception as e:
            st.error(f"生成测试音频时发生错误: {str(e)}")
            return None

import streamlit as st
from bilix.sites.bilibili import api
from bilix.sites.bilibili import DownloaderBilibili
from httpx import AsyncClient
import asyncio
import sys


if 'win32' in sys.platform:
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


@st.dialog('设置 SESSDATA')
def set_sess_data():
    sess_data = st.text_input('请输入 SESSDATA', value=st.session_state.sess_data)
    if st.button('保存'):
        st.session_state.sess_data = sess_data
        st.success('保存成功')


def on_input_change():
    st.session_state.search_query = st.session_state.user_input


async def download_video():
    video_url = st.session_state.search_query
    if not video_url:
        st.error('视频链接不能为空')
        return None
    sess_data = None
    if st.session_state.sess_data:
        sess_data = st.session_state.sess_data
    d = DownloaderBilibili(sess_data=sess_data)
    with st.spinner('下载中...', show_time=True):
        await d.get_video(url=video_url)
        await d.aclose()
    st.session_state.is_downloading = False
    st.success('下载完成')


async def get_video_info():
    video_url = st.session_state.search_query
    if not video_url:
        st.error('视频链接不能为空')
        return None
    client = AsyncClient(**api.dft_client_settings)
    if st.session_state.sess_data:
        client.cookies.set('SESSDATA', st.session_state.sess_data)
    return await api.get_video_info(client=client, url=video_url)


# 页面配置
st.set_page_config(
    page_title='B站视频下载',
    page_icon='😎'
)

# 初始化 session state
if 'search_query' not in st.session_state:
    st.session_state.search_query = ''
if 'video_info' not in st.session_state:
    st.session_state.video_info = st.container
if 'sess_data' not in st.session_state:
    st.session_state.sess_data = ''
if 'is_downloading' not in st.session_state:
    st.session_state.is_downloading = False
if 'video_data' not in st.session_state:
    st.session_state.video_data = None
st.title('😎 B站视频下载')
col1, col2, col3 = st.columns(3, vertical_alignment='bottom')
col3.button('⚙️', on_click=set_sess_data)
col1.text_input(
    '请输入B站视频链接',
    value=st.session_state.search_query,
    placeholder='https://www.bilibili.com/video/BV1aDf8Y4Es8',
    key='user_input',
    disabled=st.session_state.is_downloading,
    on_change=on_input_change)
if col2.button('获取视频信息', use_container_width=True, disabled=st.session_state.is_downloading):
    st.session_state.video_data = asyncio.run(get_video_info())
if st.session_state.video_data:
    data = st.session_state.video_data
    video_info_container = st.session_state.video_info
    img_url = f'https://wsrv.nl/?url={data.img_url}&w=300&h=300'
    with video_info_container():
        col1, col2 = st.columns(2)
        col1.image(img_url)
        col2.text(data.title)
        if data.desc:
            col2.text(data.desc)
        if col2.button('下载', disabled=st.session_state.is_downloading):
            st.session_state.is_downloading = True
            asyncio.run(download_video())
st.markdown('---')
st.markdown(
    """
    <div style='text-align: center'>
    
    🌟 关注我 | Follow Me 🌟
    
    👨‍💻 [GitHub](https://github.com/liuyuhe666) 
    📝 [个人博客](https://liuyuhe666.github.io)
    </div>
    """,
    unsafe_allow_html=True)

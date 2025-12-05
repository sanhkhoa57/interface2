import streamlit as st
import base64
import os

# cấu hình
LOCAL_WEBP_FILE = "utsuro.webp" 

# ảnh nền Anime mẫu (fallback nếu không tìm thấy file local)
DEFAULT_ANIME_BG_URL = "https://images.unsplash.com/photo-1626245648558-f542a2592790?q=80&w=2574&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"

def get_base64_of_file(path):
    """Đọc file và mã hóa thành chuỗi Base64"""
    try:
        with open(path, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode()
            return f"data:image/webp;base64,{encoded_string}"
    except FileNotFoundError:
        st.error(f"Lỗi: Không tìm thấy file ảnh nền tại đường dẫn: {path}. Đang sử dụng ảnh mặc định từ web.")
        return None

def set_background_image(image_file_path: str = LOCAL_WEBP_FILE):
    """
    Hàm chèn CSS tùy chỉnh để đặt ảnh nền cho ứng dụng Streamlit.
    Ưu tiên sử dụng file local Base64, nếu không có sẽ dùng URL mặc định.
    """
    
    # xác định nguồn ảnh
    final_image_source = None
    
    if os.path.exists(image_file_path):
        final_image_source = get_base64_of_file(image_file_path)
    
    if not final_image_source:
        final_image_source = DEFAULT_ANIME_BG_URL

    # CSS cho toàn bộ trang+ Shine Sweep + Glow Pulse
    page_container_css = f"""
    @keyframes shine {{
        0%, 50%, 100% {{
            background-position: -200% center, center;
        }}
        25% {{
            background-position: 200% center, center;
        }}
    }}
    
    @keyframes glowPulse {{
        0%, 50%, 100% {{
            filter: brightness(1) drop-shadow(0 0 0px transparent);
        }}
        60% {{
            filter: brightness(1.04) drop-shadow(0 0 15px rgba(174, 224, 215, 0.4));
        }}
        70% {{
            filter: brightness(1.08) drop-shadow(0 0 30px rgba(174, 224, 215, 0.6));
        }}
        80% {{
            filter: brightness(1.04) drop-shadow(0 0 15px rgba(174, 224, 215, 0.4));
        }}
        90% {{
            filter: brightness(1) drop-shadow(0 0 0px transparent);
        }}
    }}
    
    [data-testid="stAppViewContainer"] {{
        background-image: 
            linear-gradient(
                110deg,
                transparent 30%,
                rgba(255, 255, 255, 0) 40%,
                rgba(255, 255, 255, 0.5) 50%,
                rgba(255, 255, 255, 0) 60%,
                transparent 70%
            ),
            url("{final_image_source}");
        background-size: 200% 100%, contain;
        background-color: #AEE0D7;
        background-position: -200% center, center;
        background-repeat: no-repeat, no-repeat;
        background-attachment: scroll, fixed;
        animation: shine 12s ease-in-out infinite, glowPulse 12s ease-in-out infinite;
    }}
    """
    
    # CSS cho các thành phần khác (để tăng độ tương phản)
    component_css = """
    /* Import font anime style */
    @import url('https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@400;500;700;800&display=swap');
    
    /* Làm cho Sidebar trong suốt và tối màu nhẹ */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(255, 250, 245, 0.95) 0%, rgba(244, 239, 234, 0.95) 100%);
        border-right: 2px solid rgba(174, 224, 215, 0.4); 
        box-shadow: 2px 0 10px rgba(0, 0, 0, 0.05);
        font-family: 'M PLUS Rounded 1c', sans-serif;
    }
    
    /* Header trong Sidebar */
    [data-testid="stSidebar"] h2 {
        color: #1A5F7A !important;
        font-weight: 800 !important;
        text-shadow: none !important;
    }
    
    /* Text trong sidebar */
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: #2C3E50 !important;
        text-shadow: none !important;
        font-weight: 500 !important;
    }
    
    /* Info box trong sidebar */
    [data-testid="stSidebar"] [data-testid="stAlert"] {
        background: linear-gradient(135deg, rgba(174, 224, 215, 0.3) 0%, rgba(120, 200, 190, 0.2) 100%) !important;
        border: 2px solid rgba(174, 224, 215, 0.6) !important;
        border-radius: 12px !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stAlert"] p {
        color: #1A5F7A !important;
        font-weight: 700 !important;
        text-shadow: none !important;
    }

    /* Làm cho Header trong suốt */
    [data-testid="stHeader"] {
        background-color: rgba(0, 0, 0, 0.0);
    }
    
    /* Làm cho các Widget đầu vào đẹp hơn */
    .stSelectbox, .stTextInput, .stRadio > label, [data-testid="stTextInput"] > div:nth-child(2) > div {
        background-color: rgba(255, 255, 255, 0.85); 
        border: 1px solid rgba(174, 224, 215, 0.5);
        border-radius: 10px;
        padding: 8px;
        transition: all 0.3s ease;
    }
    
    .stSelectbox:hover, .stTextInput:hover {
        background-color: rgba(255, 255, 255, 0.95);
        border-color: rgba(120, 200, 190, 0.7);
        box-shadow: 0 2px 8px rgba(120, 200, 190, 0.2);
    }
    
    /* Tăng độ tương phản cho tiêu đề và chữ */
    h1, h2, h3, h4, .stMarkdown, .stText, .stButton > button, .stRadio, label {
        color: #FFFFFF !important; 
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.9), 
                     0 0 8px rgba(0, 0, 0, 0.7);
        font-weight: 600;
    }
    
    h1 {
        color: #FFFFFF !important;
        font-size: 2.5rem !important;
        text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.95), 
                     0 0 12px rgba(0, 0, 0, 0.8);
    }
    
    /* Tùy chỉnh khung st.success/st.info để làm khung hiển thị AI */
    [data-testid="stAlert"] {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.97) 0%, rgba(250, 252, 255, 0.97) 100%);
        border: 2px solid rgba(174, 224, 215, 0.6);
        border-radius: 15px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12), 
                    0 0 0 1px rgba(255, 255, 255, 0.5) inset;
        padding: 20px;
        backdrop-filter: blur(10px);
    }

    /* Màu chữ bên trong khung Alert */
    [data-testid="stAlert"] p, 
    [data-testid="stAlert"] li,
    [data-testid="stAlert"] h1, 
    [data-testid="stAlert"] h2, 
    [data-testid="stAlert"] h3,
    [data-testid="stAlert"] strong {
        color: #2C3E50 !important;
        text-shadow: none !important;
        line-height: 1.6;
    }
    
    /* Đổi màu icon */
    [data-testid="stAlert"] svg {
        fill: #1A5F7A !important;
    }
    
    /* Tạo khung nền cho ô Metric */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(174, 224, 215, 0.3) 100%);
        border: 2px solid rgba(174, 224, 215, 0.5);
        border-radius: 12px;
        padding: 15px 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        width: fit-content;
        transition: transform 0.2s ease;
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
    }

    /* Màu chữ Metric */
    [data-testid="stMetricLabel"] {
        color: #1A5F7A !important; 
        font-weight: 700;
        font-size: 0.9rem;
    }

    [data-testid="stMetricValue"] {
        color: #2C3E50 !important;
        font-weight: 800;
        font-size: 1.8rem;
    }
    
    /* Tạo khung nền cho Spinner */
    [data-testid="stSpinner"] {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(174, 224, 215, 0.3) 100%);
        border: 2px solid rgba(174, 224, 215, 0.6);
        border-radius: 12px;
        padding: 12px 25px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        width: fit-content;
    }

    /* Màu chữ Spinner */
    [data-testid="stSpinner"] p, 
    [data-testid="stSpinner"] div {
        color: #1A5F7A !important;
        font-weight: 600;
        text-shadow: none !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #78C8BE 0%, #5AACA3 100%);
        color: white !important;
        border: none;
        border-radius: 10px;
        padding: 10px 24px;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(120, 200, 190, 0.3);
        transition: all 0.3s ease;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2) !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #5AACA3 0%, #4A9C93 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(120, 200, 190, 0.4);
    }
    
    /* STYLE CHO ẢNH (st.image) - Style giống Spinner */
    [data-testid="stImage"] img {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(174, 224, 215, 0.3) 100%);
        border: 2px solid rgba(174, 224, 215, 0.6);
        border-radius: 12px;
        padding: 10px; 
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        transition: transform 0.3s ease;
    }

    [data-testid="stImage"] img:hover {
        transform: scale(1.01);
        box-shadow: 0 6px 16px rgba(174, 224, 215, 0.4);
    }
    
    /* Biến các lựa chọn Radio thành dạng thẻ (Card) */
    div[role="radiogroup"] > label {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(240, 250, 255, 0.8) 100%);
        border: 1px solid rgba(174, 224, 215, 0.6);
        border-radius: 10px;
        padding: 10px 15px;
        margin-bottom: 8px;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }

    div[role="radiogroup"] > label:hover {
        background: rgba(255, 255, 255, 1);
        border-color: #1A5F7A;
        transform: translateX(5px);
        box-shadow: 0 4px 8px rgba(174, 224, 215, 0.4);
    }

    div[role="radiogroup"] label p {
        color: #1A5F7A !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
    }
    
    div[role="radiogroup"] div[data-testid="stMarkdownContainer"] {
        padding-left: 0px;
    }
    """
    
    full_css = f"<style>{page_container_css}{component_css}</style>"
    st.markdown(full_css, unsafe_allow_html=True)
    
    # Ẩn Streamlit footer
    hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """
    st.markdown(hide_st_style, unsafe_allow_html=True)

# thêm gif
def add_corner_gif():
    """Thêm GIF nhỏ ở góc phải trên"""
    gif_html = """
    <style>
    .corner-gif {
        position: fixed;
        top: 20px;
        right: 20px;
        width: 100px;
        height: 100px;
        z-index: 9999;
        border-radius: 50%;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        transition: transform 0.3s ease;
        pointer-events: auto;
    }
    .corner-gif:hover {
        transform: scale(1.15) rotate(5deg);
    }
    </style>
    <img src="https://s3.getstickerpack.com/storage/uploads/sticker-pack/genshin-stickers-set-44/sticker_1.png?9fea17fd7eb9063146bb3e6c6cc33beb" class="corner-gif" alt="cute gif">
    """
=======
import streamlit as st
import base64
import os

# cấu hình
LOCAL_WEBP_FILE = "utsuro.webp" 

# ảnh nền Anime mẫu (fallback nếu không tìm thấy file local)
DEFAULT_ANIME_BG_URL = "https://images.unsplash.com/photo-1626245648558-f542a2592790?q=80&w=2574&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"

def get_base64_of_file(path):
    """Đọc file và mã hóa thành chuỗi Base64"""
    try:
        with open(path, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode()
            return f"data:image/webp;base64,{encoded_string}"
    except FileNotFoundError:
        st.error(f"Lỗi: Không tìm thấy file ảnh nền tại đường dẫn: {path}. Đang sử dụng ảnh mặc định từ web.")
        return None

def set_background_image(image_file_path: str = LOCAL_WEBP_FILE):
    """
    Hàm chèn CSS tùy chỉnh để đặt ảnh nền cho ứng dụng Streamlit.
    Ưu tiên sử dụng file local Base64, nếu không có sẽ dùng URL mặc định.
    """
    
    # xác định nguồn ảnh
    final_image_source = None
    
    if os.path.exists(image_file_path):
        final_image_source = get_base64_of_file(image_file_path)
    
    if not final_image_source:
        final_image_source = DEFAULT_ANIME_BG_URL

    # CSS cho toàn bộ trang+ Shine Sweep + Glow Pulse
    page_container_css = f"""
    @keyframes shine {{
        0%, 50%, 100% {{
            background-position: -200% center, center;
        }}
        25% {{
            background-position: 200% center, center;
        }}
    }}
    
    @keyframes glowPulse {{
        0%, 50%, 100% {{
            filter: brightness(1) drop-shadow(0 0 0px transparent);
        }}
        60% {{
            filter: brightness(1.04) drop-shadow(0 0 15px rgba(174, 224, 215, 0.4));
        }}
        70% {{
            filter: brightness(1.08) drop-shadow(0 0 30px rgba(174, 224, 215, 0.6));
        }}
        80% {{
            filter: brightness(1.04) drop-shadow(0 0 15px rgba(174, 224, 215, 0.4));
        }}
        90% {{
            filter: brightness(1) drop-shadow(0 0 0px transparent);
        }}
    }}
    
    [data-testid="stAppViewContainer"] {{
        background-image: 
            linear-gradient(
                110deg,
                transparent 30%,
                rgba(255, 255, 255, 0) 40%,
                rgba(255, 255, 255, 0.5) 50%,
                rgba(255, 255, 255, 0) 60%,
                transparent 70%
            ),
            url("{final_image_source}");
        background-size: 200% 100%, contain;
        background-color: #AEE0D7;
        background-position: -200% center, center;
        background-repeat: no-repeat, no-repeat;
        background-attachment: scroll, fixed;
        animation: shine 12s ease-in-out infinite, glowPulse 12s ease-in-out infinite;
    }}
    """
    
    # CSS cho các thành phần khác (để tăng độ tương phản)
    component_css = """
    /* Import font anime style */
    @import url('https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@400;500;700;800&display=swap');
    
    /* Làm cho Sidebar trong suốt và tối màu nhẹ */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(255, 250, 245, 0.95) 0%, rgba(244, 239, 234, 0.95) 100%);
        border-right: 2px solid rgba(174, 224, 215, 0.4); 
        box-shadow: 2px 0 10px rgba(0, 0, 0, 0.05);
        font-family: 'M PLUS Rounded 1c', sans-serif;
    }
    
    /* Header trong Sidebar */
    [data-testid="stSidebar"] h2 {
        color: #1A5F7A !important;
        font-weight: 800 !important;
        text-shadow: none !important;
    }
    
    /* Text trong sidebar */
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: #2C3E50 !important;
        text-shadow: none !important;
        font-weight: 500 !important;
    }
    
    /* Info box trong sidebar */
    [data-testid="stSidebar"] [data-testid="stAlert"] {
        background: linear-gradient(135deg, rgba(174, 224, 215, 0.3) 0%, rgba(120, 200, 190, 0.2) 100%) !important;
        border: 2px solid rgba(174, 224, 215, 0.6) !important;
        border-radius: 12px !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stAlert"] p {
        color: #1A5F7A !important;
        font-weight: 700 !important;
        text-shadow: none !important;
    }

    /* Làm cho Header trong suốt */
    [data-testid="stHeader"] {
        background-color: rgba(0, 0, 0, 0.0);
    }
    
    /* Làm cho các Widget đầu vào đẹp hơn */
    .stSelectbox, .stTextInput, .stRadio > label, [data-testid="stTextInput"] > div:nth-child(2) > div {
        background-color: rgba(255, 255, 255, 0.85); 
        border: 1px solid rgba(174, 224, 215, 0.5);
        border-radius: 10px;
        padding: 8px;
        transition: all 0.3s ease;
    }
    
    .stSelectbox:hover, .stTextInput:hover {
        background-color: rgba(255, 255, 255, 0.95);
        border-color: rgba(120, 200, 190, 0.7);
        box-shadow: 0 2px 8px rgba(120, 200, 190, 0.2);
    }
    
    /* Tăng độ tương phản cho tiêu đề và chữ */
    h1, h2, h3, h4, .stMarkdown, .stText, .stButton > button, .stRadio, label {
        color: #FFFFFF !important; 
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.9), 
                     0 0 8px rgba(0, 0, 0, 0.7);
        font-weight: 600;
    }
    
    h1 {
        color: #FFFFFF !important;
        font-size: 2.5rem !important;
        text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.95), 
                     0 0 12px rgba(0, 0, 0, 0.8);
    }
    
    /* Tùy chỉnh khung st.success/st.info để làm khung hiển thị AI */
    [data-testid="stAlert"] {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.97) 0%, rgba(250, 252, 255, 0.97) 100%);
        border: 2px solid rgba(174, 224, 215, 0.6);
        border-radius: 15px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12), 
                    0 0 0 1px rgba(255, 255, 255, 0.5) inset;
        padding: 20px;
        backdrop-filter: blur(10px);
    }

    /* Màu chữ bên trong khung Alert */
    [data-testid="stAlert"] p, 
    [data-testid="stAlert"] li,
    [data-testid="stAlert"] h1, 
    [data-testid="stAlert"] h2, 
    [data-testid="stAlert"] h3,
    [data-testid="stAlert"] strong {
        color: #2C3E50 !important;
        text-shadow: none !important;
        line-height: 1.6;
    }
    
    /* Đổi màu icon */
    [data-testid="stAlert"] svg {
        fill: #1A5F7A !important;
    }
    
    /* Tạo khung nền cho ô Metric */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(174, 224, 215, 0.3) 100%);
        border: 2px solid rgba(174, 224, 215, 0.5);
        border-radius: 12px;
        padding: 15px 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        width: fit-content;
        transition: transform 0.2s ease;
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
    }

    /* Màu chữ Metric */
    [data-testid="stMetricLabel"] {
        color: #1A5F7A !important; 
        font-weight: 700;
        font-size: 0.9rem;
    }

    [data-testid="stMetricValue"] {
        color: #2C3E50 !important;
        font-weight: 800;
        font-size: 1.8rem;
    }
    
    /* Tạo khung nền cho Spinner */
    [data-testid="stSpinner"] {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(174, 224, 215, 0.3) 100%);
        border: 2px solid rgba(174, 224, 215, 0.6);
        border-radius: 12px;
        padding: 12px 25px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        width: fit-content;
    }

    /* Màu chữ Spinner */
    [data-testid="stSpinner"] p, 
    [data-testid="stSpinner"] div {
        color: #1A5F7A !important;
        font-weight: 600;
        text-shadow: none !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #78C8BE 0%, #5AACA3 100%);
        color: white !important;
        border: none;
        border-radius: 10px;
        padding: 10px 24px;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(120, 200, 190, 0.3);
        transition: all 0.3s ease;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2) !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #5AACA3 0%, #4A9C93 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(120, 200, 190, 0.4);
    }
    
    /* STYLE CHO ẢNH (st.image) - Style giống Spinner */
    [data-testid="stImage"] img {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(174, 224, 215, 0.3) 100%);
        border: 2px solid rgba(174, 224, 215, 0.6);
        border-radius: 12px;
        padding: 10px; 
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        transition: transform 0.3s ease;
    }

    [data-testid="stImage"] img:hover {
        transform: scale(1.01);
        box-shadow: 0 6px 16px rgba(174, 224, 215, 0.4);
    }
    
    /* Biến các lựa chọn Radio thành dạng thẻ (Card) */
    div[role="radiogroup"] > label {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(240, 250, 255, 0.8) 100%);
        border: 1px solid rgba(174, 224, 215, 0.6);
        border-radius: 10px;
        padding: 10px 15px;
        margin-bottom: 8px;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }

    div[role="radiogroup"] > label:hover {
        background: rgba(255, 255, 255, 1);
        border-color: #1A5F7A;
        transform: translateX(5px);
        box-shadow: 0 4px 8px rgba(174, 224, 215, 0.4);
    }

    div[role="radiogroup"] label p {
        color: #1A5F7A !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
    }
    
    div[role="radiogroup"] div[data-testid="stMarkdownContainer"] {
        padding-left: 0px;
    }
    """
    
    full_css = f"<style>{page_container_css}{component_css}</style>"
    st.markdown(full_css, unsafe_allow_html=True)
    
    # Ẩn Streamlit footer
    hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """
    st.markdown(hide_st_style, unsafe_allow_html=True)

# thêm gif
def add_corner_gif():
    """Thêm GIF nhỏ ở góc phải trên"""
    gif_html = """
    <style>
    .corner-gif {
        position: fixed;
        top: 20px;
        right: 20px;
        width: 100px;
        height: 100px;
        z-index: 9999;
        border-radius: 50%;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        transition: transform 0.3s ease;
        pointer-events: auto;
    }
    .corner-gif:hover {
        transform: scale(1.15) rotate(5deg);
    }
    </style>
    <img src="https://s3.getstickerpack.com/storage/uploads/sticker-pack/genshin-stickers-set-44/sticker_1.png?9fea17fd7eb9063146bb3e6c6cc33beb" class="corner-gif" alt="cute gif">
    """
>>>>>>> eb80681a56c9ad3134888de4191995202dbdce75
    st.markdown(gif_html, unsafe_allow_html=True)

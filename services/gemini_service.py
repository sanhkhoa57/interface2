import google.generativeai as genai
import os
import streamlit as st # IMPORT STREAMLIT
from dotenv import load_dotenv

# Code API function
@st.cache_resource #@st.cache_resource để đảm bảo Key chỉ được gọi 1 lần duy nhất
def initialize_gemini():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key or api_key.startswith("DÁN_KEY"):
        st.error("LỖI CẤU HÌNH: Vui lòng dán API Key vào file .env")
        return None
    
    try:
        # Thêm .strip() để xóa hết khoảng trắng thừa
        cleaned_key = api_key.strip()
        genai.configure(api_key=cleaned_key)
        return genai.GenerativeModel('gemini-2.5-flash-lite')
    except Exception as e:
        # Nếu lỗi API
        st.error(f"LỖI CẤU HÌNH: Key API không hợp lệ. Hãy tạo Key mới.")
        print(f"LỖI CẤU HÌNH CHI TIẾT: {e}")
        return None

model = initialize_gemini()


# Code Computer Vision:
def ai_vision_detect(image_data):
    """ Nhìn ảnh và đoán tên nhân vật. """
    if not model:
        return "ERROR: Key chưa được cấu hình."
        
    prompt = "Look at this anime character. Tell me ONLY their full canonical name. If not sure, return 'Unknown'."
    try:
        response = model.generate_content([prompt, image_data])
        return response.text.strip()
    except Exception as e:
        return "Unknown"
# Code Texting:
def ai_analyze_profile(char_info):
    """ Phân tích thông tin và viết báo cáo. """
    if not model:
        return "ERROR: Key chưa được cấu hình."
    if not isinstance(char_info, dict):
        return "Lỗi Dữ liệu: Jikan không trả về hồ sơ hợp lệ cho nhân vật này. Vui lòng thử tên khác."
        
    # Lấy thông tin an toàn (Nếu không có key 'about' thì dùng chuỗi rỗng)
    # Dùng .get(key, default) để không bị lỗi nếu key không tồn tại
    about_text = char_info.get('about', 'Không có tiểu sử chi tiết.')
    name_text = char_info.get('name', 'Nhân vật này')
    prompt = f"""
    Dựa vào thông tin tiếng Anh: "{char_info['about']}".
    Hãy đóng vai một Otaku chuyên nghiệp, viết hồ sơ phân tích nhân vật {char_info['name']} bằng tiếng Việt:
    
    1. **Tiểu sử vắn tắt**: (Kể lại quá khứ hoặc xuất thân một cách lôi cuốn).
    2. **Phim tham gia**: (Giới thiệu bộ Anime gốc và vai trò của nhân vật trong đó).
    3. **Sức mạnh & Kỹ năng**: (Phân tích điểm mạnh, chiêu thức đặc biệt).
    4. **Đánh giá cá nhân**: (Tại sao nhân vật này lại được yêu thích/hoặc bị ghét).
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Xin lỗi, AI đang bị lỗi kết nối/timeout: {e}"
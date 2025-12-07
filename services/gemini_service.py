import google.generativeai as genai
import os
import streamlit as st # IMPORT STREAMLIT
from dotenv import load_dotenv
from PIL import Image  # ← THÊM DÒNG NÀY
import requests  # ← THÊM DÒNG NÀY
from io import BytesIO  # ← THÊM DÒNG NÀY

# Code API function
@st.cache_resource #@st.cache_resource để đảm bảo Key chỉ được gọi 1 lần duy nhất
def initialize_gemini():
    load_dotenv()
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        api_key = None
    
    if not api_key:
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
def generate_custom_avatar(avatar_config, face_reference=None):
    """
    Tạo avatar anime sử dụng Pollinations.AI API (MIỄN PHÍ - KHÔNG CẦN KEY)
    
    Args:
        avatar_config: Dict chứa toàn bộ config
        face_reference: PIL Image của user (optional)
    
    Returns:
        PIL Image hoặc None
    """
    
    # Build prompt từ config
    prompt_parts = []
    
    # Art style
    art_style_prompts = {
        "Anime style chuẩn": "anime style",
        "Chibi siêu cute": "chibi cute kawaii",
        "Makoto Shinkai style": "makoto shinkai style",
        "Studio Ghibli style": "studio ghibli style",
        "Manga đen trắng": "manga monochrome",
        "Watercolor mềm mại": "watercolor anime",
        "Kyoto Animation style": "kyoto animation style",
        "Vtuber style": "vtuber style",
        "Webtoon style": "webtoon style"
    }
    prompt_parts.append(art_style_prompts.get(avatar_config["art_style"], "anime"))
    
    # Character
    gender_map = {"Nữ": "1girl", "Nam": "1boy", "Non-binary": "androgynous person"}
    prompt_parts.append(gender_map[avatar_config['gender']])
    
    # Hair
    prompt_parts.append(f"{avatar_config['hair_color']} {avatar_config['hair_style']}")
    
    # Eyes
    prompt_parts.append(f"{avatar_config['eye_color']} eyes")
    
    # Outfit
    prompt_parts.append(f"wearing {avatar_config['outfit_type']}")
    
    # Expression
    expression_map = {
        "Mặc định/Bình thường": "neutral",
        "Cười tươi rói": "smiling",
        "Cười ngượng đỏ mặt": "blushing shy",
        "Ngầu lạnh lùng": "cool",
        "Buồn lo lắng": "sad",
        "Giận dữ tsundere": "angry tsundere",
        "Wink một mắt": "winking",
        "Shocked/Ngạc nhiên": "surprised",
        "Tự tin badass": "confident"
    }
    prompt_parts.append(expression_map[avatar_config["expression"]])
    
    # Background
    bg_map = {
        "Trong suốt (PNG)": "white background",
        "Lớp học Nhật Bản": "classroom",
        "Sân thượng trường học": "rooftop",
        "Vườn hoa anh đào": "cherry blossoms",
        "Thành phố về đêm": "city night",
        "Bãi biển hoàng hôn": "beach sunset",
        "Rừng huyền bí": "forest",
        "Phòng ngủ cute": "bedroom",
        "Phố Shibuya đông người": "shibuya",
        "Trạm tàu điện": "train station",
        "Công viên mùa thu": "autumn park",
        "Cầu thang Your Name": "stairs sunset",
        "Không gian ảo cyberpunk": "cyberpunk"
    }
    prompt_parts.append(bg_map.get(avatar_config["background"], "simple background"))
    
    # Final prompt - NGẮN GỌN
    full_prompt = ", ".join(prompt_parts) + ", high quality, detailed"
    
    st.info(f"🎨 Đang tạo avatar với prompt: {full_prompt[:100]}...")
    
    try:
        import urllib.parse
        
        # Encode prompt
        encoded_prompt = urllib.parse.quote(full_prompt)
        
        # ✅ POLLINATIONS API - CHÍNH XÁC 100%
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        
        # Parameters
        params = {
            "width": 512,
            "height": 768,
            "model": "flux",  # flux model tốt cho anime
            "nologo": "true",
            "enhance": "true"
        }
        
        # Build full URL
        param_str = "&".join([f"{k}={v}" for k, v in params.items()])
        full_url = f"{url}?{param_str}"
        
        st.info("⏳ Đang gửi request đến Pollinations.AI...")
        
        # GET request
        response = requests.get(full_url, timeout=90)
        
        if response.status_code == 200:
            # Kiểm tra content type
            content_type = response.headers.get('content-type', '')
            
            if 'image' in content_type:
                image = Image.open(BytesIO(response.content))
                st.success("✅ Tạo avatar thành công!")
                return image
            else:
                st.error(f"❌ Response không phải ảnh. Content-Type: {content_type}")
                st.error(f"Response: {response.text[:200]}")
                return None
        else:
            st.error(f"❌ Lỗi API: {response.status_code}")
            st.error(f"Response: {response.text[:200]}")
            return None
            
    except requests.exceptions.Timeout:
        st.error("⏰ Timeout! Server mất quá lâu để xử lý.")
        st.info("💡 Thử giảm độ phức tạp hoặc chọn style đơn giản hơn")
        return None
        
    except Exception as e:
        st.error(f"❌ Lỗi: {str(e)}")
        st.info("💡 Debug info:")
        st.code(f"URL: {full_url}")
        return None
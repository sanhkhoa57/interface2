import streamlit as st
from PIL import Image
# Gọi file css
from styles_css import set_background_image, add_corner_gif
# Gọi các thư mục ở services
from services.jikan_service import get_character_data, get_one_character_data
from services.gemini_service import ai_vision_detect, ai_analyze_profile

# cấu hình
chitoge_icon = Image.open("itooklogo.jpg")
st.set_page_config(page_title="ITook Library", page_icon=chitoge_icon, layout="wide")
set_background_image("utsuro.webp")
add_corner_gif()
st.title("ITOOK LIBRARY - Find Your Characters ")
st.markdown("---")

# sidebar
with st.sidebar:
    st.header("Which tool?")
    mode = st.radio("Tell me what you need", ["Texting", "Uploading"])
    st.info("A-I-T Model - Tứ Đại Bổ Ích")

# logic code
character_name = None
run_analysis = False

# CHẾ ĐỘ 1: NHẬP TÊN
if mode == "Texting":
    search_query = st.text_input("Enter the character name  (Ex: Tanjirou, Edogawa Conan,...):")
    
    # hộp chọn (Dropdown)
    if search_query:
        # gọi hàm lấy danh sách 10 người
        results = get_character_data(search_query)
        
        if results:
            # tạo danh sách tên để hiện trong menu
            menu_options = [f"{char['name']} (ID: {char['mal_id']})" for char in results]
            
            # tiện Hộp Chọn
            selected_option = st.selectbox("Tìm thấy nhiều kết quả, bạn chọn ai?", menu_options)
            
            # nút bấm Phân tích
            if st.button("Phân tích nhân vật này"):
                # Lấy lại thông tin người được chọn
                index = menu_options.index(selected_option)
                info = results[index] # Đây là dữ liệu chuẩn của người bạn chọn
                
                # AI phân tích
                with st.spinner(f"Đang tải hồ sơ của {info['name']}..."):
                    ai_text = ai_analyze_profile(info)
                    
                    # hiển thị kết quả 
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.image(info['images']['jpg']['image_url'], use_container_width=True)
                        st.metric("Yêu thích", info['favorites'])
                    with col2:
                        st.header(info['name'])
                        st.success(ai_text, icon="🐱")
        else:
            st.warning("Không tìm thấy nhân vật nào!")
# CHẾ ĐỘ 2: UPLOAD ẢNH (VISION)
elif mode == "Uploading":
    uploaded_file = st.file_uploader("Chọn ảnh nhân vật...", type=["jpg", "png", "jpeg"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Ảnh đã tải lên", width=300)
        
        if st.button("Quét ảnh & Phân tích"):
            
            # BƯỚC 1: NHẬN DẠNG TÊN (VISION)
            with st.spinner("AI đang nhận diện khuôn mặt..."):
                detected_name = ai_vision_detect(image)
                
            if detected_name and detected_name != "Unknown":
                st.success(f"AI phát hiện đây là: **{detected_name}**")
                
                # BƯỚC 2: LẤY DỮ LIỆU TỪ JIKAN 
                with st.spinner(f"Đang tìm kiếm hồ sơ của {detected_name}..."):
                    # hàm get_character_data trả về Dictionary của 1 người (Đúng cho mục đích này)
                    info = get_one_character_data(detected_name) 
                
                if info:
                    # BƯỚC 3: GỌI AI PHÂN TÍCH VÀ HIỂN THỊ 
                    ai_text = ai_analyze_profile(info)
                    
                    # ĐOẠN HIỂN THỊ KẾT QUẢ 
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.image(info['images']['jpg']['image_url'], use_container_width=True) 
                        st.metric("Lượt yêu thích", info['favorites'])
                        st.caption(f"Nguồn: MyAnimeList")
                    with col2:
                        st.header(info['name'])
                        st.write(f"**Tên tiếng Nhật:** {info.get('name_kanji', 'N/A')}")
                        st.markdown("### 📝 Báo cáo phân tích từ AI")
                        st.success(ai_text, icon="📝")
                        
                else:
                    # nếu Jikan không tìm thấy data của tên mà AI đoán ra
                    st.warning(f"Jikan không tìm thấy data chi tiết cho tên '{detected_name}'. Vui lòng thử lại với tên đầy đủ.")
            else:
                st.error("AI không nhận diện được nhân vật này. Thử ảnh khác xem!")


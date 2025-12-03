import streamlit as st
from PIL import Image
# Gọi các thư mục ở services
from services.jikan_service import get_character_data, get_one_character_data
from services.gemini_service import ai_vision_detect, ai_analyze_profile

# --- CẤU HÌNH TRANG ---
chitoge_icon = Image.open("itooklogo.jpg")
st.set_page_config(page_title="Itook Library", page_icon=chitoge_icon, layout="wide")

st.title("ITOOK LIBRARY - Find Your Characters ")
st.markdown("---")

# --- SIDEBAR (THANH BÊN) ---
with st.sidebar:
    st.header("Choose a tool")
    mode = st.radio("Bạn muốn tìm bằng cách nào?", ["Texting", "Uploading"])
    st.info("Project 2 - Tứ Đại Bổ Ích")

# --- LOGIC CHÍNH ---
character_name = None
run_analysis = False

# CHẾ ĐỘ 1: NHẬP TÊN
if mode == "Texting":
    search_query = st.text_input("Nhập tên nhân vật (VD: Sakura):")
    
    # Logic Hộp chọn (Dropdown)
    if search_query:
        # Gọi hàm lấy danh sách 10 người
        results = get_character_data(search_query)
        
        if results:
            # Tạo danh sách tên để hiện trong menu
            menu_options = [f"{char['name']} (ID: {char['mal_id']})" for char in results]
            
            # Hiện Hộp Chọn
            selected_option = st.selectbox("Tìm thấy nhiều kết quả, bạn chọn ai?", menu_options)
            
            # Nút bấm Phân tích
            if st.button("Phân tích nhân vật này"):
                # Lấy lại thông tin người được chọn
                index = menu_options.index(selected_option)
                info = results[index] # Đây là dữ liệu chuẩn của người bạn chọn
                
                # --- GỌI AI PHÂN TÍCH ---
                with st.spinner(f"Đang tải hồ sơ của {info['name']}..."):
                    ai_text = ai_analyze_profile(info)
                    
                    # Hiển thị kết quả ngay tại đây
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.image(info['images']['jpg']['image_url'], use_container_width=True)
                        st.metric("Yêu thích", info['favorites'])
                    with col2:
                        st.header(info['name'])
                        st.markdown(ai_text)
        else:
            st.warning("Không tìm thấy nhân vật nào!")
# CHẾ ĐỘ 2: UPLOAD ẢNH (VISION)
elif mode == "Uploading":
    uploaded_file = st.file_uploader("Chọn ảnh nhân vật...", type=["jpg", "png", "jpeg"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Ảnh đã tải lên", width=300)
        
        if st.button("Quét ảnh & Phân tích"):
            
            # --- BƯỚC 1: NHẬN DẠNG TÊN (VISION) ---
            with st.spinner("AI đang nhận diện khuôn mặt..."):
                detected_name = ai_vision_detect(image)
                
            if detected_name and detected_name != "Unknown":
                st.success(f"AI phát hiện đây là: **{detected_name}**")
                
                # --- BƯỚC 2: LẤY DỮ LIỆU TỪ JIKAN ---
                with st.spinner(f"Đang tìm kiếm hồ sơ của {detected_name}..."):
                    # Hàm get_character_data trả về Dictionary của 1 người (Đúng cho mục đích này)
                    info = get_one_character_data(detected_name) 
                
                if info:
                    # --- BƯỚC 3: GỌI AI PHÂN TÍCH VÀ HIỂN THỊ ---
                    ai_text = ai_analyze_profile(info)
                    
                    # *********** ĐOẠN HIỂN THỊ KẾT QUẢ ĐÃ THIẾT KẾ ĐÚNG ************
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        # Streamlit đã tự sửa use_column_width thành use_container_width
                        st.image(info['images']['jpg']['image_url'], use_container_width=True) 
                        st.metric("Lượt yêu thích", info['favorites'])
                        st.caption(f"Nguồn: MyAnimeList")
                    with col2:
                        st.header(info['name'])
                        st.write(f"**Tên tiếng Nhật:** {info.get('name_kanji', 'N/A')}")
                        st.markdown("### 📝 Báo cáo phân tích từ AI")
                        st.markdown(ai_text)
                    # ************************************************************
                        
                else:
                    # Nếu Jikan không tìm thấy data của tên mà AI đoán ra
                    st.warning(f"Jikan không tìm thấy data chi tiết cho tên '{detected_name}'. Vui lòng thử lại với tên đầy đủ.")
            else:
                st.error("AI không nhận diện được nhân vật này. Thử ảnh khác xem!")


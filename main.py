import streamlit as st
from PIL import Image
import requests 
from services.genre_service import get_genre_map 
# gọi file css
from styles_css import set_background_image, add_corner_gif
# gọi các thư mục ở services
from services.jikan_service import get_character_data, get_one_character_data
from services.gemini_service import ai_vision_detect, ai_analyze_profile

# xử lý phần delay khi vào web bằng html
st.markdown("""
<style>
    /* Overlay che phủ toàn màn hình */
    .loading-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: rgba(0, 0, 0, 0.9);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        z-index: 99999;
        animation: fadeOutOverlay 0.5s ease-out 2.5s forwards;
    }
    
    .loading-content {
        text-align: center;
    }
    
    .loading-title {
        font-size: 2rem;
        font-weight: bold;
        color: white;
        margin-bottom: 30px;
    }
    
    /* Progress bar container */
    .progress-container {
        width: 400px;
        height: 8px;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        overflow: hidden;
        margin-bottom: 15px;
    }
    
    /* Progress bar fill */
    .progress-bar {
        height: 100%;
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        border-radius: 10px;
        animation: loadProgress 2s ease-out forwards;
        box-shadow: 0 0 10px rgba(79, 172, 254, 0.5);
    }
    
    @keyframes loadProgress {
        0% { width: 0%; }
        100% { width: 100%; }
    }
    
    /* Percentage text */
    .progress-text {
        color: white;
        font-size: 1.2rem;
        animation: countUp 2s ease-out forwards;
    }
    
    @keyframes fadeOutOverlay {
        to {
            opacity: 0;
            visibility: hidden;
            pointer-events: none;
        }
    }
    
    /* Content mờ khi đang load */
    .main, .stApp > header, [data-testid="stSidebar"] {
        opacity: 0.3;
        filter: blur(5px);
        animation: clearContent 1s ease-in-out 2.2s forwards;
    }
    
    @keyframes clearContent {
        to {
            opacity: 1;
            filter: blur(0px);
        }
    }
    
</style>

<div class="loading-overlay">
    <div class="loading-content">
        <div class="loading-title">-- WHO IS YOUR WAIFU? --</div>
        <div class="progress-container">
            <div class="progress-bar"></div>
        </div>
        <div class="progress-text" id="progress-text">Loading... 0%</div>
    </div>
</div>

<script>
    // Đếm từ 0% đến 100%
    let progress = 0;
    const interval = setInterval(() => {
        progress += 2;
        if (progress > 100) progress = 100;
        document.getElementById('progress-text').innerText = `Loading... ${progress}%`;
        if (progress >= 100) clearInterval(interval);
    }, 40);
</script>
""", unsafe_allow_html=True)
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
    mode = st.radio("Tell me what you need", ["Texting", "Uploading", "Genre"])
    st.info("A-I-T Model - Tứ Đại Bổ Ích")

# logic code
character_name = None
run_analysis = False

# CHẾ ĐỘ 1: NHẬP TÊN
if mode == "Texting":
    search_query = st.text_input("Enter the character name  (E.g: Tanjirou, Edogawa Conan,...):")
    
    # hộp chọn (Dropdown)
    if search_query:
        # gọi hàm lấy danh sách 10 người
        results = get_character_data(search_query)
        
        if results:
            # tạo danh sách tên để hiện trong menu
            menu_options = [f"{char['name']} (ID: {char['mal_id']})" for char in results]
            
            # tiện Hộp Chọn
            selected_option = st.selectbox("Multiple results found. Select one:", menu_options)
            
            # nút bấm Phân tích
            if st.button("Analyze this character"):
                # Lấy lại thông tin người được chọn
                index = menu_options.index(selected_option)
                info = results[index] # Đây là dữ liệu chuẩn của người bạn chọn
                
                # AI phân tích
                with st.spinner(f"Loading the profile of {info['name']}..."):
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
    uploaded_file = st.file_uploader("Choose a Character Image...", type=["jpg", "png", "jpeg"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", width=300)
        
        if st.button("Image Scanning & Analysis"):
            
            # BƯỚC 1: NHẬN DẠNG TÊN (VISION)
            with st.spinner("AI is identifying the face..."):
                detected_name = ai_vision_detect(image)
                
            if detected_name and detected_name != "Unknown":
                st.success(f"AI detected this as”: **{detected_name}**")
                
                # BƯỚC 2: LẤY DỮ LIỆU TỪ JIKAN 
                with st.spinner(f"Searching for the profile of… {detected_name}..."):
                    # hàm get_character_data trả về Dictionary của 1 người 
                    info = get_one_character_data(detected_name) 
                
                if info:
                    # BƯỚC 3: GỌI AI PHÂN TÍCH VÀ HIỂN THỊ 
                    ai_text = ai_analyze_profile(info)
                    
                    # ĐOẠN HIỂN THỊ KẾT QUẢ 
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.image(info['images']['jpg']['image_url'], use_container_width=True) 
                        st.metric("Favorites", info['favorites'])
                        st.caption(f"Cre: MyAnimeList")
                    with col2:
                        st.header(info['name'])
                        st.write(f"**Japanese name:** {info.get('name_kanji', 'N/A')}")
                        st.markdown("### 📝 AI Analysis Report")
                        st.success(ai_text, icon="📝")
                        
                else:
                    # nếu Jikan không tìm thấy data của tên mà AI đoán ra
                    st.warning(f"Jikan không tìm thấy data chi tiết cho tên '{detected_name}'. Vui lòng thử lại với tên đầy đủ.")
            else:
                st.error("AI couldn’t identify this character. Try a different image!")
elif mode == "Genre":
    st.subheader("🎭 Search Anime/Manga by Genre")
    
    # chọn type
    content_type = st.selectbox(
        "📖 Content type:",
        options=["anime", "manga"]
    )
    
    # toad genre map tương ứng với content_type
    with st.spinner(f"Loading genre list {content_type}..."):
        genre_map = get_genre_map(content_type)  # <--- TRUYỀN content_type VÀO
    
    if not genre_map:
        st.error(f"⚠️ Unable to load the genre list {content_type} from Jikan API!")
    else:
        # tạo danh sách genres từ API (ID: Name)
        genre_options = {v: k for k, v in genre_map.items()}  # {Name: ID}
        genre_names = sorted(genre_options.keys())
        
        selected_genre_names = st.multiselect(
            "📚 Choose genres (Genres):",
            options=genre_names,
            help="Select one or more genres to search"
        )
        
        # chuyển thể loại thành id
        selected_genre_ids = [genre_options[name] for name in selected_genre_names]
        
        # time-ordering
        order_by = st.selectbox(
            "📅 Sort by:",
            options=["Newest", "Oldest", "Most Popular"],
            help="Sort results by release date or score"
        )
        
        # nút 
        if st.button("🔍 Searching"):
            if not selected_genre_ids:
                st.warning("⚠️ Choose at lease one genre")
            else:
                # tạo URL 
                genre_params = ",".join(map(str, selected_genre_ids))
                
                # xác định order_by và sort
                if order_by == "Newest":
                    order_param = "start_date"
                    sort_param = "desc"
                elif order_by == "Oldest":
                    order_param = "start_date"
                    sort_param = "asc"
                else:  # điểm cao nhất
                    order_param = "score"
                    sort_param = "desc"
                
                url = f"https://api.jikan.moe/v4/{content_type}?genres={genre_params}&order_by={order_param}&sort={sort_param}&limit=10"
                
                st.write(f"**Searching with...:**")
                st.write(f"- Genre: {', '.join(selected_genre_names)}")
                st.write(f"- Type: {content_type.capitalize()}")
                st.write(f"- Sort by: {order_by}")
                
                # gọi API tìm kiếm
                try:
                    response = requests.get(url)
                    
                    if response.status_code == 200:
                        data = response.json()
                        results = data.get('data', [])
                        
                        if results:
                            st.success(f"✅ Found {len(results)} results!")
                            
                            # hiển thị kết quả
                            for item in results:
                                with st.expander(f"📺 {item.get('title', 'N/A')}"):
                                    col1, col2 = st.columns([1, 3])
                                    
                                    with col1:
                                        img_url = item.get('images', {}).get('jpg', {}).get('image_url')
                                        if img_url:
                                            st.image(img_url, use_container_width=True)
                                    
                                    with col2:
                                        st.write(f"**Name:** {item.get('title_japanese', 'N/A')}")
                                        st.write(f"**Score:** {item.get('score', 'N/A')} ⭐")
                                        
                                        # hiển thị năm phát hành
                                        aired = item.get('aired', {}) if content_type == "anime" else item.get('published', {})
                                        if aired:
                                            from_date = aired.get('from', 'N/A')
                                            if from_date and from_date != 'N/A':
                                                year = from_date.split('-')[0]
                                                st.write(f"**Release year:** {year}")
                                        
                                        # hiển thị số tập (anime) hoặc số chương (manga)
                                        if content_type == "anime":
                                            st.write(f"**Episodes:** {item.get('episodes', 'N/A')}")
                                        else:
                                            st.write(f"**Chapters:** {item.get('chapters', 'N/A')}")
                                            st.write(f"**Volumes:** {item.get('volumes', 'N/A')}")
                                        
                                        # hiển thị genres
                                        genres = item.get('genres', [])
                                        if genres:
                                            genre_list = [g['name'] for g in genres]
                                            st.write(f"**Genre:** {', '.join(genre_list)}")
                                        
                                        # Synopsis
                                        synopsis = item.get('synopsis', 'Không có mô tả')
                                        if synopsis and len(synopsis) > 200:
                                            synopsis = synopsis[:200] + "..."
                                        st.write(f"**Summary:** {synopsis}")
                                        
                                        # Link
                                        st.markdown(f"[🔗 Xem trên MyAnimeList]({item.get('url', '#')})")
                        else:
                            st.warning("No matching results found.")
                    else:
                        st.error(f"Lỗi API: {response.status_code}")
                        
                except Exception as e:
                    st.error(f"Lỗi kết nối: {e}")

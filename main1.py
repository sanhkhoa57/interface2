import streamlit as st
from PIL import Image
import requests 
from datetime import datetime
from services.genre_service import get_genre_map 
from styles_css import set_background_image, add_corner_gif
from services.jikan_service import get_character_data, get_one_character_data
from services.gemini_service import ai_vision_detect, ai_analyze_profile

# Delay loading animation
st.markdown("""
<style>
    .loading-overlay {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background: rgba(0, 0, 0, 0.9); display: flex; flex-direction: column;
        justify-content: center; align-items: center; z-index: 99999;
        animation: fadeOutOverlay 0.5s ease-out 2.5s forwards;
    }
    .loading-content { text-align: center; }
    .loading-title { font-size: 2rem; font-weight: bold; color: white; margin-bottom: 30px; }
    .progress-container { width: 400px; height: 8px; background: rgba(255, 255, 255, 0.2);
        border-radius: 10px; overflow: hidden; margin-bottom: 15px; }
    .progress-bar { height: 100%; background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        border-radius: 10px; animation: loadProgress 2s ease-out forwards;
        box-shadow: 0 0 10px rgba(79, 172, 254, 0.5); }
    @keyframes loadProgress { 0% { width: 0%; } 100% { width: 100%; } }
    .progress-text { color: white; font-size: 1.2rem; animation: countUp 2s ease-out forwards; }
    @keyframes fadeOutOverlay { to { opacity: 0; visibility: hidden; pointer-events: none; } }
    .main, .stApp > header, [data-testid="stSidebar"] {
        opacity: 0.3; filter: blur(5px); animation: clearContent 1s ease-in-out 2.2s forwards; }
    @keyframes clearContent { to { opacity: 1; filter: blur(0px); } }
</style>
<div class="loading-overlay">
    <div class="loading-content">
        <div class="loading-title">-- WHO IS YOUR WAIFU? --</div>
        <div class="progress-container"><div class="progress-bar"></div></div>
        <div class="progress-text" id="progress-text">Loading... 0%</div>
    </div>
</div>
<script>
    let progress = 0;
    const interval = setInterval(() => {
        progress += 2;
        if (progress > 100) progress = 100;
        document.getElementById('progress-text').innerText = `Loading... ${progress}%`;
        if (progress >= 100) clearInterval(interval);
    }, 40);
</script>
""", unsafe_allow_html=True)

# Configuration
chitoge_icon = Image.open("itooklogo.jpg")
st.set_page_config(page_title="ITook Library", page_icon=chitoge_icon, layout="wide")

# Session State
if 'favorites' not in st.session_state:
    st.session_state.favorites = {'characters': []}
if 'search_history' not in st.session_state:
    st.session_state.search_history = []
# Thêm state để lưu kết quả AI analysis
if 'current_analysis' not in st.session_state:
    st.session_state.current_analysis = None

set_background_image("utsuro.webp")
add_corner_gif()
st.title("ITOOK LIBRARY - Find Your Characters ")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("Which tool?")
    mode = st.radio("Tell me what you need", ["Texting", "Uploading", "Genre", "Avatar Creator", "Favorite", "History"])
    st.info("A-I-T Model - Tứ Đại Bổ Ách")

# MODE 1: TEXTING
if mode == "Texting":
    search_query = st.text_input("Enter the character name  (E.g: Tanjirou, Edogawa Conan,...):")
    
    if search_query:
        results = get_character_data(search_query)
        
        if results:
            menu_options = [f"{char['name']} (ID: {char['mal_id']})" for char in results]
            selected_option = st.selectbox("Multiple results found. Select one:", menu_options)
            
            if st.button("Analyze this character"):
                index = menu_options.index(selected_option)
                info = results[index]
                
                # Add to history
                st.session_state.search_history.append({
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'type': 'Text_Search',
                    'query': search_query,
                    'result': info['name']
                })
                
                with st.spinner(f"Loading the profile of {info['name']}..."):
                    ai_text = ai_analyze_profile(info)
                    
                    # Lưu vào session state để giữ lại sau khi thêm favorite
                    st.session_state.current_analysis = {
                        'info': info,
                        'ai_text': ai_text,
                        'mode': 'texting'
                    }
            
            # Hiển thị kết quả nếu đã có analysis
            if st.session_state.current_analysis and st.session_state.current_analysis.get('mode') == 'texting':
                info = st.session_state.current_analysis['info']
                ai_text = st.session_state.current_analysis['ai_text']
                
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(info['images']['jpg']['image_url'], use_container_width=True)
                    st.metric("Yêu thích", info['favorites'])
                    
                    # Check nếu đã có trong favorites
                    char_exists = any(c['id'] == info['mal_id'] for c in st.session_state.favorites['characters'])
                    
                    if not char_exists:
                        if st.button("❤️ Add to Favorites", key=f"add_fav_text_{info['mal_id']}", use_container_width=True):
                            st.session_state.favorites['characters'].append({
                                'id': info['mal_id'],
                                'name': info['name'],
                                'image': info['images']['jpg']['image_url'],
                                'favorites': info['favorites']
                            })
                            st.success("✅ Added to Favorites!")
                            # KHÔNG dùng st.rerun() nữa!
                    else:
                        st.info("✅ Already in Favorites")
                
                with col2:
                    st.header(info['name'])
                    st.success(ai_text, icon="🐱")
        else:
            st.warning("Không tìm thấy nhân vật nào!")

# MODE 2: UPLOADING
elif mode == "Uploading":
    uploaded_file = st.file_uploader("Choose a Character Image...", type=["jpg", "png", "jpeg"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", width=300)
        
        if st.button("Image Scanning & Analysis"):
            with st.spinner("AI is identifying the face..."):
                detected_name = ai_vision_detect(image)
            
            # Add to history
            st.session_state.search_history.append({
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'type': 'Image_Upload',
                'query': f"Image Upload",
                'result': detected_name
            })
                
            if detected_name and detected_name != "Unknown":
                st.success(f"AI detected this as: **{detected_name}**")
                
                with st.spinner(f"Searching for the profile of {detected_name}..."):
                    info = get_one_character_data(detected_name)
                
                if info:
                    ai_text = ai_analyze_profile(info)
                    
                    # Lưu vào session state
                    st.session_state.current_analysis = {
                        'info': info,
                        'ai_text': ai_text,
                        'mode': 'uploading'
                    }
                else:
                    st.warning(f"Jikan không tìm thấy data chi tiết cho tên '{detected_name}'.")
            else:
                st.error("AI couldn't identify this character. Try a different image!")
        
        # Hiển thị kết quả nếu đã có analysis
        if st.session_state.current_analysis and st.session_state.current_analysis.get('mode') == 'uploading':
            info = st.session_state.current_analysis['info']
            ai_text = st.session_state.current_analysis['ai_text']
            
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(info['images']['jpg']['image_url'], use_container_width=True)
                st.metric("Favorites", info['favorites'])
                st.caption(f"Cre: MyAnimeList")
                
                # Check nếu đã có trong favorites
                char_exists = any(c['id'] == info['mal_id'] for c in st.session_state.favorites['characters'])
                
                if not char_exists:
                    if st.button("❤️ Add to Favorites", key=f"add_fav_upload_{info['mal_id']}", use_container_width=True):
                        st.session_state.favorites['characters'].append({
                            'id': info['mal_id'],
                            'name': info['name'],
                            'image': info['images']['jpg']['image_url'],
                            'favorites': info['favorites']
                        })
                        st.success("✅ Added to Favorites!")
                        # KHÔNG dùng st.rerun() nữa!
                else:
                    st.info("✅ Already in Favorites")
            
            with col2:
                st.header(info['name'])
                st.write(f"**Japanese name:** {info.get('name_kanji', 'N/A')}")
                st.markdown("### 📝 AI Analysis Report")
                st.success(ai_text, icon="📄")

# MODE 3: GENRE
elif mode == "Genre":
    st.subheader("🎭 Search Anime/Manga by Genre")
    
    content_type = st.selectbox("📖 Content type:", options=["anime", "manga"])
    
    with st.spinner(f"Loading genre list {content_type}..."):
        genre_map = get_genre_map(content_type)
    
    if not genre_map:
        st.error(f"⚠️ Unable to load the genre list {content_type} from Jikan API!")
    else:
        excluded_genres = ["Hentai", "Ecchi"]
        genre_map = {k: v for k, v in genre_map.items() if v not in excluded_genres}
        genre_options = {v: k for k, v in genre_map.items()}
        genre_names = sorted(genre_options.keys())
        
        selected_genre_names = st.multiselect("📚 Choose genres:", options=genre_names)
        selected_genre_ids = [genre_options[name] for name in selected_genre_names]
        order_by = st.selectbox("📅 Sort by:", options=["Newest", "Oldest", "Most Popular"])
        
        if st.button("🔍 Searching"):
            if not selected_genre_ids:
                st.warning("⚠️ Choose at least one genre")
            else:
                genre_params = ",".join(map(str, selected_genre_ids))
                
                if order_by == "Newest":
                    order_param, sort_param = "start_date", "desc"
                elif order_by == "Oldest":
                    order_param, sort_param = "start_date", "asc"
                else:
                    order_param, sort_param = "score", "desc"
                
                url = f"https://api.jikan.moe/v4/{content_type}?genres={genre_params}&order_by={order_param}&sort={sort_param}&limit=10"
                
                try:
                    response = requests.get(url)
                    if response.status_code == 200:
                        data = response.json()
                        results = data.get('data', [])
                        
                        if results:
                            st.success(f"✅ Found {len(results)} results!")
                            
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
                                        synopsis = item.get('synopsis', 'Không có mô tả')
                                        if synopsis and len(synopsis) > 200:
                                            synopsis = synopsis[:200] + "..."
                                        st.write(f"**Summary:** {synopsis}")
                                        st.markdown(f"[🔗 View on MyAnimeList]({item.get('url', '#')})")
                        else:
                            st.warning("No matching results found.")
                except Exception as e:
                    st.error(f"Lỗi kết nối: {e}")

# MODE 4: AVATAR CREATOR
elif mode == "Avatar Creator":
    st.subheader("🎨 Create Your Anime Avatar")
    st.markdown("**Tạo phiên bản anime của bạn với đầy đủ customization!**")
    
    # Upload ảnh
    st.markdown("### 📸 Bước 1: Upload ảnh của bạn (Optional)")
    uploaded_face = st.file_uploader(
        "Upload ảnh mặt để AI học features của bạn (hoặc bỏ qua để tạo random)",
        type=["jpg", "png", "jpeg"],
        help="Ảnh chân dung rõ mặt sẽ cho kết quả tốt hơn"
    )
    
    if uploaded_face:
        face_img = Image.open(uploaded_face)
        col_preview, _ = st.columns([1, 3])
        with col_preview:
            st.image(face_img, caption="Ảnh của bạn", width=200)
    
    st.markdown("---")
    
    # CUSTOMIZATION SECTION
    st.markdown("### ✨ Bước 2: Customize Your Character")
    
    # Row 1: Gender + Age
    col1, col2 = st.columns(2)
    with col1:
        gender = st.selectbox(
            "👤 Giới tính:",
            ["Nữ", "Nam", "Non-binary"]
        )
    with col2:
        age_group = st.selectbox(
            "🎂 Độ tuổi:",
            ["Trẻ em (8-12)", "Thiếu niên (13-17)", "Thanh niên (18-25)", "Trưởng thành (25+)"]
        )
    
    # Row 2: Hair Style + Color
    col3, col4 = st.columns(2)
    with col3:
        hair_style = st.selectbox(
            "💇 Kiểu tóc:",
            [
                "Tóc dài thẳng",
                "Tóc dài xoăn", 
                "Tóc ngắn bob",
                "Tóc đuôi ngựa (ponytail)",
                "Tóc bím đôi (twin tails)",
                "Tóc ngắn tomboy",
                "Tóc dài buộc cao",
                "Tóc mohawk",
                "Tóc ngắn messy",
                "Tóc dài với mái"
            ]
        )
    with col4:
        hair_color = st.selectbox(
            "🎨 Màu tóc:",
            [
                "Đen tự nhiên",
                "Nâu",
                "Vàng bạch kim",
                "Hồng pastel",
                "Xanh dương",
                "Tím lavender",
                "Đỏ cherry",
                "Xanh lá mint",
                "Bạc/Trắng",
                "Gradient (2 màu)"
            ]
        )
    
    # Row 3: Eye Style + Color
    col5, col6 = st.columns(2)
    with col5:
        eye_style = st.selectbox(
            "👁️ Kiểu mắt:",
            [
                "Mắt to tròn (cute)",
                "Mắt hạnh nhân",
                "Mắt cáo (fox eyes)",
                "Mắt buồn (droopy)",
                "Mắt sắc lạnh",
                "Mắt sanpaku (3 white)",
                "Heterochromia (2 màu khác nhau)"
            ]
        )
    with col6:
        eye_color = st.selectbox(
            "🌈 Màu mắt:",
            [
                "Nâu",
                "Đen",
                "Xanh dương",
                "Xanh lá",
                "Tím",
                "Đỏ",
                "Vàng/Gold",
                "Hồng",
                "Heterochromia (mỗi mắt 1 màu)"
            ]
        )
    
    st.markdown("---")
    
    # OUTFIT SECTION
    st.markdown("### 👗 Bước 3: Chọn Outfit")
    
    col7, col8 = st.columns(2)
    with col7:
        outfit_type = st.selectbox(
            "👔 Loại trang phục:",
            [
                "Đồng phục học sinh Nhật (sailor)",
                "Đồng phục học sinh hiện đại",
                "Kimono truyền thống",
                "Yukata (kimono mùa hè)",
                "Maid outfit",
                "Gothic Lolita",
                "Casual hiện đại (áo hoodie)",
                "Váy công chúa",
                "Armor chiến binh",
                "Ninja outfit",
                "Idol costume",
                "Witch/Wizard robe",
                "Cyberpunk style",
                "Streetwear Harajuku"
            ]
        )
    
    with col8:
        outfit_color = st.selectbox(
            "🎨 Màu outfit chủ đạo:",
            [
                "Trắng tinh khôi",
                "Đen huyền bí",
                "Xanh navy",
                "Đỏ rực rỡ",
                "Hồng pastel",
                "Tím royal",
                "Vàng gold",
                "Xanh lá emerald",
                "Mix nhiều màu"
            ]
        )
    
    # ACCESSORIES
    st.markdown("### 🎀 Bước 4: Phụ kiện (Chọn nhiều)")
    
    accessories = st.multiselect(
        "Chọn phụ kiện:",
        [
            "Không có phụ kiện",
            "Kính mát",
            "Kính cận trong suốt",
            "Nơ tóc to",
            "Băng đô tai mèo",
            "Mũ beret",
            "Mũ phù thủy",
            "Tai nghe",
            "Choker cổ",
            "Vòng cổ hoa",
            "Hoa cài tóc",
            "Mũ rơm",
            "Găng tay dài",
            "Cánh thiên thần",
            "Cánh ác quỷ",
            "Kiếm/Vũ khí",
            "Sách phép thuật",
            "Thú cưng mini",
            "Khăn quàng cổ dài"
        ],
        default=["Không có phụ kiện"]
    )
    
    st.markdown("---")
    
    # SCENE & STYLE
    st.markdown("### 🌆 Bước 5: Background & Art Style")
    
    col9, col10 = st.columns(2)
    with col9:
        background = st.selectbox(
            "🖼️ Background:",
            [
                "Trong suốt (PNG)",
                "Lớp học Nhật Bản",
                "Sân thượng trường học",
                "Vườn hoa anh đào",
                "Thành phố về đêm",
                "Bãi biển hoàng hôn",
                "Rừng huyền bí",
                "Phòng ngủ cute",
                "Phố Shibuya đông người",
                "Trạm tàu điện",
                "Công viên mùa thu",
                "Cầu thang Your Name",
                "Không gian ảo cyberpunk"
            ]
        )
    
    with col10:
        art_style_avatar = st.selectbox(
            "🎨 Phong cách vẽ:",
            [
                "Anime style chuẩn",
                "Chibi siêu cute",
                "Makoto Shinkai style",
                "Studio Ghibli style",
                "Manga đen trắng",
                "Watercolor mềm mại",
                "Kyoto Animation style",
                "Vtuber style",
                "Webtoon style"
            ]
        )
    
    # Expression
    expression = st.selectbox(
        "😊 Biểu cảm:",
        [
            "Mặc định/Bình thường",
            "Cười tươi rói",
            "Cười ngượng đỏ mặt",
            "Ngầu lạnh lùng",
            "Buồn lo lắng",
            "Giận dữ tsundere",
            "Wink một mắt",
            "Shocked/Ngạc nhiên",
            "Tự tin badass"
        ]
    )
    
    st.markdown("---")
    
    # GENERATE BUTTON
    if st.button("✨ TẠO AVATAR CỦA TÔI", type="primary", use_container_width=True):
        
        with st.spinner("🎨 AI đang vẽ avatar của bạn... (30-60 giây)"):
            try:
                # Import hàm mới
                from services.gemini_service import generate_custom_avatar
                
                # Tạo dictionary chứa toàn bộ customization
                avatar_config = {
                    "gender": gender,
                    "age_group": age_group,
                    "hair_style": hair_style,
                    "hair_color": hair_color,
                    "eye_style": eye_style,
                    "eye_color": eye_color,
                    "outfit_type": outfit_type,
                    "outfit_color": outfit_color,
                    "accessories": accessories,
                    "background": background,
                    "art_style": art_style_avatar,
                    "expression": expression
                }
                
                # Gọi hàm generate
                if uploaded_face:
                    result_avatar = generate_custom_avatar(avatar_config, face_reference=face_img)
                else:
                    result_avatar = generate_custom_avatar(avatar_config)
                
                if result_avatar:
                    st.success("✅ Hoàn thành! Đây là avatar anime của bạn:")
                    
                    # Hiển thị ảnh
                    col_result1, col_result2 = st.columns([2, 1])
                    with col_result1:
                        st.image(result_avatar, use_container_width=True)
                    
                    with col_result2:
                        st.markdown("### 📋 Thông tin Avatar:")
                        st.write(f"👤 **Giới tính:** {gender}")
                        st.write(f"💇 **Tóc:** {hair_style} - {hair_color}")
                        st.write(f"👁️ **Mắt:** {eye_style} - {eye_color}")
                        st.write(f"👗 **Outfit:** {outfit_type}")
                        st.write(f"🎨 **Style:** {art_style_avatar}")
                        
                        if len(accessories) > 1 or accessories[0] != "Không có phụ kiện":
                            acc_list = [a for a in accessories if a != "Không có phụ kiện"]
                            st.write(f"🎀 **Phụ kiện:** {', '.join(acc_list)}")
                    
                    # Nút download
                    import io
                    buf = io.BytesIO()
                    result_avatar.save(buf, format="PNG")
                    byte_im = buf.getvalue()
                    
                    st.download_button(
                        label="💾 Tải avatar về",
                        data=byte_im,
                        file_name="my_anime_avatar.png",
                        mime="image/png",
                        use_container_width=True
                    )
                    
                    # Nút tạo lại
                    if st.button("🔄 Tạo lại với setting khác"):
                        st.rerun()
                        
                else:
                    st.error("❌ Có lỗi xảy ra. Vui lòng thử lại!")
                    
            except Exception as e:
                st.error(f"❌ Lỗi: {str(e)}")
                st.info("💡 Thử giảm bớt phụ kiện hoặc chọn background đơn giản hơn.")                  


# MODE 5: FAVORITE
elif mode == "Favorite":
    # Clear current_analysis khi vào tab Favorite
    st.session_state.current_analysis = None
    
    st.header("❤️ Your Favorite Characters")
    st.markdown("---")

    fav_chars = st.session_state.favorites.get('characters', [])

    if not fav_chars:
        st.info("You haven't added any characters to your favorites yet. Go find your waifu!")
    else:
        st.success(f"You have {len(fav_chars)} favorite characters!")
        
        cols = st.columns(4, gap="large")
        for idx, char in enumerate(fav_chars):
            with cols[idx % 4]:
                st.image(char['image'], use_container_width=True, caption=char['name'])
                st.write(f"**{char['name']}**")
                st.write(f"⭐ {char['favorites']} Favorites")
                
                if st.button("🗑️ Remove", key=f"remove_fav_{char['id']}", use_container_width=True):
                    st.session_state.favorites['characters'] = [
                        c for c in st.session_state.favorites['characters'] if c['id'] != char['id']
                    ]
                    st.rerun()
    
    st.markdown("---")
    st.markdown(f"**Total Favorites:** {len(fav_chars)}")

# MODE 6: HISTORY
elif mode == "History":
    # Clear current_analysis khi vào tab History
    st.session_state.current_analysis = None
    
    st.header("📜 Search History")
    st.markdown("---")

    history = st.session_state.search_history

    if not history:
        st.info("No search history yet.")
    else:
        st.markdown(f"**Total entries:** {len(history)}")
        
        if st.button("🗑️ Clear History", type="secondary"):
            st.session_state.search_history = []
            st.rerun()

        st.markdown("---")

        for entry in reversed(history):
            with st.expander(f"[{entry['timestamp']}] - **{entry['type'].upper().replace('_', ' ')}**"):
                st.write(f"**Query:** `{entry['query']}`")
                if entry.get('result'):
                    st.write(f"**Result:** {entry['result']}")
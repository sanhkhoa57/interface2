import requests

# Cache để tránh gọi API nhiều lần
_anime_genre_cache = None
_manga_genre_cache = None

def get_genre_map(content_type="anime"):
    """
    Lấy ánh xạ ID -> Tên thể loại từ Jikan API.
    Sử dụng cache để tối ưu performance.
    
    Args:
        content_type: "anime" hoặc "manga"
    
    Returns:
        dict: {mal_id: name} hoặc {} nếu lỗi
    """
    global _anime_genre_cache, _manga_genre_cache
    
    # Kiểm tra cache theo loại
    if content_type == "anime":
        if _anime_genre_cache is not None:
            return _anime_genre_cache
    elif content_type == "manga":
        if _manga_genre_cache is not None:
            return _manga_genre_cache
    
    # URL thay đổi theo content_type
    url = f"https://api.jikan.moe/v4/genres/{content_type}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            genres = data["data"]
            
            # Tạo mapping
            genre_map = {g["mal_id"]: g["name"] for g in genres}
            
            # Lưu vào cache tương ứng
            if content_type == "anime":
                _anime_genre_cache = genre_map
            elif content_type == "manga":
                _manga_genre_cache = genre_map
            
            return genre_map
        else:
            print(f"Lỗi API genres {content_type}: {response.status_code}")
            return {}
    except Exception as e:
        print(f"Lỗi kết nối genres {content_type}: {e}")
        return {}


def get_genre_names(genre_ids, content_type="anime"):
    """
    Chuyển đổi list ID thành list tên thể loại.
    
    Args:
        genre_ids: List các dict có key 'mal_id', ví dụ: [{'mal_id': 1}, {'mal_id': 2}]
        content_type: "anime" hoặc "manga"
    
    Returns:
        list: Danh sách tên thể loại
    """
    genre_map = get_genre_map(content_type)
    
    if not genre_map:
        return ["N/A"]
    
    # Trích xuất tên từ IDs
    names = []
    for item in genre_ids:
        genre_id = item.get('mal_id')
        if genre_id in genre_map:
            names.append(genre_map[genre_id])
    
    return names if names else ["N/A"]
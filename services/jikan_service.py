import requests

def get_character_data(name):
    """
    Hàm này tìm kiếm nhân vật trên MyAnimeList thông qua Jikan API.
    Input: Tên nhân vật (String)
    Output: Dictionary chứa thông tin hoặc None
    """
    # Lấy 10 kết quả thay vì 1
    url = f"https://api.jikan.moe/v4/characters?q={name}&limit=10"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # trả 1 loạt kết quả
            return response.json()['data']
    except Exception as e:
        print(f"Lỗi Jikan: {e}")
    return []
# --- HÀM 2: DÀNH CHO CHẾ ĐỘ UPLOADING (CHỈ CẦN 1 NGƯỜI) ---
def get_one_character_data(name):
    """
    Chỉ lấy thông tin chi tiết của 1 nhân vật duy nhất.
    Trả về Dictionary (Từ điển) duy nhất.
    """
    url = f"https://api.jikan.moe/v4/characters?q={name}&limit=1"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()['data']
            if data:
                return data[0] # <<--- Lấy đúng phần tử [0]
    except Exception as e:
        print(f"Lỗi kết nối Jikan: {e}")
    return None
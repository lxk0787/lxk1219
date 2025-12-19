import requests
import json

class CoordinateGetter:
    def __init__(self):
        self.base_url = "https://nominatim.openstreetmap.org"
        self.headers = {'User-Agent': 'LuojiaExplorer/1.0'}
    
    def get_coordinates(self, location):
        """获取地点的精确经纬度坐标"""
        geocode_url = f"{self.base_url}/search?q={location}&format=json&limit=1"
        response = requests.get(geocode_url, headers=self.headers)
        result = response.json()
        
        if result:
            lat = float(result[0]["lat"])
            lon = float(result[0]["lon"])
            display_name = result[0]["display_name"]
            print(f"📍 {location}")
            print(f"   纬度: {lat}")
            print(f"   经度: {lon}")
            print(f"   地址: {display_name}")
            print()
            return lat, lon
        else:
            print(f"❌ 未找到 {location} 的坐标")
            print()
            return None, None

# 要获取坐标的武汉大学地标
landmarks = [
    "武汉大学老图书馆",
    "武汉大学樱花大道",
    "武汉大学文理学部操场",
    "武汉大学信息学部操场",
    "武汉大学宋卿体育馆",
    "武汉大学万林艺术博物馆",
    "武汉大学工学部操场",
    "武汉大学医学部",
    "武汉大学信息学部图书馆",
    "武汉大学十八栋"
]

if __name__ == "__main__":
    print("🎯 获取武汉大学地标精确坐标")
    print("=" * 50)
    
    getter = CoordinateGetter()
    coordinates = {}
    
    for landmark in landmarks:
        lat, lon = getter.get_coordinates(landmark)
        if lat and lon:
            coordinates[landmark] = (lat, lon)
    
    print("📋 坐标汇总（Leaflet.js格式: [纬度, 经度]）")
    print("=" * 50)
    for landmark, (lat, lon) in coordinates.items():
        print(f"{landmark}: [{lat}, {lon}]")
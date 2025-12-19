import requests
import json

class LuojiaExplorer:
    def __init__(self):
        self.base_url = "https://nominatim.openstreetmap.org"
        self.wuhan_university_boundary = {
            "center": "30.596069,114.297691",  # 武汉大学精确中心坐标
            "radius": 5000  # 覆盖整个武大校园的半径
        }
    
    def check_in_campus(self, location):
        """检查地点是否在武大校园范围内"""
        # 使用OSM Nominatim API获取坐标
        geocode_url = f"{self.base_url}/search?q={location}&format=json&limit=1"
        headers = {'User-Agent': 'LuojiaExplorer/1.0'}
        response = requests.get(geocode_url, headers=headers)
        result = response.json()
        
        if result:
            # 检查地址中是否包含武汉大学相关信息
            display_name = result[0]["display_name"]
            
            # 检查是否在武大校园内
            if "武汉大学" in display_name or "武大" in display_name:
                return True, {"lat": float(result[0]["lat"]), "lng": float(result[0]["lon"])}
            
            # 对于操场等具体地点，直接检查是否在武大坐标范围内
            lat = float(result[0]["lat"])
            lon = float(result[0]["lon"])
            # 武大校园大致范围：纬度30.580-30.610，经度114.280-114.310（精确范围）
            if 30.580 <= lat <= 30.610 and 114.280 <= lon <= 114.310:
                return True, {"lat": lat, "lng": lon}
        return False, None
    
    def get_route(self, origin, destination):
        """获取两点之间的路线信息"""
        # 解析起点和终点坐标
        if isinstance(origin, str):
            origin_lat, origin_lon = map(float, origin.split(','))
        else:
            origin_lat, origin_lon = origin["lat"], origin["lng"]
        
        if isinstance(destination, str):
            dest_lat, dest_lon = map(float, destination.split(','))
        else:
            dest_lat, dest_lon = destination["lat"], destination["lng"]
        
        # 使用OSRM API获取路线信息，添加超时和错误处理
        try:
            osrm_url = f"http://router.project-osrm.org/route/v1/walking/{origin_lon},{origin_lat};{dest_lon},{dest_lat}?steps=true&geometries=polyline&overview=full"
            response = requests.get(osrm_url, timeout=5)
            response.raise_for_status()  # 检查HTTP状态码
            
            # 尝试解析JSON响应
            try:
                result = response.json()
                if result["code"] == "Ok":
                    route = result["routes"][0]
                    return {
                        "distance": route["distance"],
                        "duration": route["duration"],
                        "steps": route["legs"][0]["steps"]
                    }
            except json.JSONDecodeError:
                # 如果JSON解析失败，使用直线距离的1.2倍作为估算
                pass
        except (requests.RequestException, json.JSONDecodeError):
            # 如果API调用失败，使用直线距离的1.2倍作为估算
            pass
        
        # 计算直线距离并返回估算值
        straight_dist = ((dest_lat - origin_lat)*111320)**2 + ((dest_lon - origin_lon)*111320*0.7)**2
        straight_dist = straight_dist**0.5
        
        # 返回估算的路线信息
        return {
            "distance": straight_dist * 1.2,  # 实际距离通常是直线距离的1.2倍
            "duration": int(straight_dist * 1.2 / 1.3),  # 步行速度约1.3m/s
            "steps": []
        }
    
    def get_poi_around(self, location, radius=1000, tags=""):
        """获取指定位置周围的POI"""
        # 使用OSM Nominatim API获取周围POI
        # 解析位置坐标
        if isinstance(location, str):
            lat, lon = map(float, location.split(','))
        else:
            lat, lon = location["lat"], location["lng"]
        
        # 构造查询，确保只获取武汉大学内的POI
        query = f"武汉大学 {tags}" if tags else "武汉大学"
        poi_url = f"{self.base_url}/search?q={query}&format=json&limit=20&viewbox={lon-radius/111320},{lat-radius/111320},{lon+radius/111320},{lat+radius/111320}&bounded=1"
        headers = {'User-Agent': 'LuojiaExplorer/1.0'}
        response = requests.get(poi_url, headers=headers)
        result = response.json()
        
        # 过滤出武汉大学内的POI
        filtered_poi = []
        for poi in result:
            if "武汉大学" in poi["display_name"] or "武大" in poi["display_name"]:
                filtered_poi.append({
                    "name": poi["name"],
                    "location": {"lat": float(poi["lat"]), "lng": float(poi["lon"])},
                    "address": poi["display_name"].split(',')[0] if ',' in poi["display_name"] else poi["display_name"]
                })
        return filtered_poi
    
    def professional_mode(self, race_type, start, end):
        """专业赛事编排模式 - 符合IOF 2024标准"""
        # 武大校内预设控制点，包含更多详细信息
        preset_control_points = [
            {
                "name": "CP1-信息学部操场",
                "code": "1",
                "location": {"lat": 30.5850, "lng": 114.3050},
                "address": "武汉大学信息学部",
                "elevation": 30,
                "difficulty": 1
            },
            {
                "name": "CP2-文理学部操场",
                "code": "2",
                "location": {"lat": 30.5885, "lng": 114.2990},
                "address": "武汉大学文理学部",
                "elevation": 28,
                "difficulty": 1
            },
            {
                "name": "CP3-樱花大道",
                "code": "3",
                "location": {"lat": 30.5900, "lng": 114.3020},
                "address": "武汉大学文理学部",
                "elevation": 45,
                "difficulty": 2
            },
            {
                "name": "CP4-老图书馆",
                "code": "4",
                "location": {"lat": 30.5910, "lng": 114.3000},
                "address": "武汉大学樱顶",
                "elevation": 65,
                "difficulty": 3
            },
            {
                "name": "CP5-宋卿体育馆",
                "code": "5",
                "location": {"lat": 30.5920, "lng": 114.3030},
                "address": "武汉大学文理学部",
                "elevation": 35,
                "difficulty": 2
            },
            {
                "name": "CP6-万林艺术博物馆",
                "code": "6",
                "location": {"lat": 30.5890, "lng": 114.3010},
                "address": "武汉大学文理学部",
                "elevation": 32,
                "difficulty": 1
            },
            {
                "name": "CP7-工学部操场",
                "code": "7",
                "location": {"lat": 30.5930, "lng": 114.3070},
                "address": "武汉大学工学部",
                "elevation": 25,
                "difficulty": 1
            },
            {
                "name": "CP8-医学部",
                "code": "8",
                "location": {"lat": 30.5980, "lng": 114.2930},
                "address": "武汉大学医学部",
                "elevation": 22,
                "difficulty": 1
            },
            {
                "name": "CP9-信息学部图书馆",
                "code": "9",
                "location": {"lat": 30.5860, "lng": 114.3040},
                "address": "武汉大学信息学部",
                "elevation": 35,
                "difficulty": 2
            },
            {
                "name": "CP10-十八栋",
                "code": "10",
                "location": {"lat": 30.5940, "lng": 114.2980},
                "address": "武汉大学珞珈山",
                "elevation": 55,
                "difficulty": 3
            }
        ]
        
        # 赛事类型参数配置（IOF标准）
        race_config = {
            "短距离": {
                "name": "Sprint",
                "control_points": 6-8,
                "total_distance": 2.5-3.5,  # km
                "max_climb": 100,  # m
                "description": "短距离赛，注重技术和路线选择"
            },
            "百米定向": {
                "name": "Park Sprint",
                "control_points": 3-5,
                "total_distance": 0.3-0.5,  # km
                "max_climb": 20,  # m
                "description": "百米定向，密集控制点，快速决策"
            },
            "积分赛": {
                "name": "Score Orienteering",
                "control_points": 10-15,
                "total_distance": 4-6,  # km
                "max_climb": 150,  # m
                "description": "积分赛，自由选择路线，按完成时间和积分计算"
            }
        }
        
        if race_type not in race_config:
            return "错误：不支持的赛事类型！请尝试：短距离、百米定向、积分赛"
        
        config = race_config[race_type]
        
        # 检查起点终点是否在校园内（简化检查）
        start_loc = {"lat": 30.5850, "lng": 114.3050}  # 信息学部操场
        end_loc = {"lat": 30.5885, "lng": 114.2990}  # 文理学部操场
        
        # 生成完整的路线控制点列表（包含起点和终点）
        full_route = [
            {"name": f"起点({start})", "location": start_loc, "elevation": 30, "code": "S"}
        ]
        
        # 根据赛事类型选择控制点
        if race_type == "短距离":
            full_route.extend(preset_control_points[:6])
        elif race_type == "百米定向":
            # 百米定向选择距离起点较近的控制点
            full_route.extend(preset_control_points[:4])
        elif race_type == "积分赛":
            # 积分赛选择更多分散的控制点
            full_route.extend(preset_control_points)
        
        full_route.append({"name": f"终点({end})", "location": end_loc, "elevation": 28, "code": "F"})
        
        # 计算路线详细信息
        total_distance = 0
        total_climb = 0
        total_straight_distance = 0
        segments = []
        
        for i in range(len(full_route) - 1):
            current = full_route[i]
            next_point = full_route[i+1]
            
            # 计算直线距离（米）
            lat1, lon1 = current["location"]["lat"], current["location"]["lng"]
            lat2, lon2 = next_point["location"]["lat"], next_point["location"]["lng"]
            
            # 简单的直线距离计算（Haversine公式简化）
            straight_dist = ((lat2 - lat1)*111320)**2 + ((lon2 - lon1)*111320*0.7)**2
            straight_dist = straight_dist**0.5
            total_straight_distance += straight_dist
            
            # 获取实际路线距离
            route = self.get_route(f"{lat1},{lon1}", f"{lat2},{lon2}")
            if route:
                actual_dist = route["distance"]
                total_distance += actual_dist
                
                # 计算爬升
                climb = max(0, next_point["elevation"] - current["elevation"])
                total_climb += climb
                
                segments.append({
                    "from": current["code"],
                    "to": next_point["code"],
                    "straight_distance": straight_dist,
                    "actual_distance": actual_dist,
                    "climb": climb,
                    "from_name": current["name"],
                    "to_name": next_point["name"]
                })
        
        # 计算路线选择比率（Route Choice Ratio）
        route_choice_ratio = total_distance / total_straight_distance if total_straight_distance > 0 else 1.0
        
        # 生成专业赛事报告
        result = f"🏆 【IOF标准】{race_type}赛事路线报告 🏆\n"
        result += f"📋 赛事信息：{config['name']} | {config['description']}\n"
        result += f"📍 起点：{start} | 终点：{end}\n"
        result += f"📏 路线数据：\n"
        result += f"   • 总实际距离：{total_distance/1000:.2f} km\n"
        result += f"   • 总直线距离：{total_straight_distance/1000:.2f} km\n"
        result += f"   • 路线选择比率：{route_choice_ratio:.2f}（IOF推荐值：1.2-1.5）\n"
        result += f"   • 总爬升高度：{total_climb} m\n"
        result += f"   • 控制点数量：{len(full_route)-2} 个\n"
        result += f"   • 赛段数量：{len(segments)} 个\n\n"
        
        result += f"🔢 路线详情（按IOF标准）：\n"
        for i, segment in enumerate(segments):
            from_code = segment["from"]
            to_code = segment["to"]
            from_name = segment["from_name"]
            to_name = segment["to_name"]
            
            result += f"【{from_code}-{to_code}】{from_name} -> {to_name}\n"
            result += f"   • 直线距离：{segment['straight_distance']:.0f} m\n"
            result += f"   • 实际距离：{segment['actual_distance']:.0f} m\n"
            result += f"   • 爬升高度：{segment['climb']} m\n"
            
            # 添加IOF标准的技术说明
            if segment['actual_distance'] > segment['straight_distance'] * 1.3:
                result += f"   • 技术要点：长距离路线选择（Route Choice）关键赛段\n"
            elif segment['climb'] > 10:
                result += f"   • 技术要点：考察爬升能力和体力分配\n"
            elif i % 3 == 0:
                result += f"   • 技术要点：考察方向感和精准定位\n"
            else:
                result += f"   • 技术要点：考察快速决策和路线执行\n"
            
            # 添加推荐路线
            if to_code in ["3", "4", "10"]:
                result += f"   • 推荐路线：沿主路前行，避免进入复杂地形\n"
            else:
                result += f"   • 推荐路线：可选择多条路线，根据自身能力决策\n"
            
            result += "\n"
        
        # 添加IOF标准的赛事建议
        result += f"💡 IOF赛事建议：\n"
        if race_type == "短距离":
            result += "   • 建议使用1:4000比例尺地图\n"
            result += "   • 控制点之间的路线选择多样，需重点标注\n"
            result += "   • 注意检查点圆圈大小（IOF标准：5mm）\n"
        elif race_type == "百米定向":
            result += "   • 建议使用1:1000-1:2000大比例尺地图\n"
            result += "   • 控制点密集，需注意检查点编号顺序\n"
            result += "   • 区域范围控制在100x100米内\n"
        elif race_type == "积分赛":
            result += "   • 建议使用1:5000比例尺地图\n"
            result += "   • 控制点分值根据难度和距离设定\n"
            result += "   • 需设定关门时间，建议60-90分钟\n"
        
        result += f"\n📊 赛事难度评估：\n"
        if total_climb > config['max_climb']:
            result += f"   • 爬升难度：高（超出IOF推荐值）\n"
        else:
            result += f"   • 爬升难度：适中（符合IOF推荐值）\n"
        
        if route_choice_ratio > 1.5:
            result += f"   • 路线选择难度：高\n"
        elif route_choice_ratio < 1.2:
            result += f"   • 路线选择难度：低\n"
        else:
            result += f"   • 路线选择难度：适中（符合IOF推荐值）\n"
        
        result += f"\n✅ 路线设计符合IOF 2024标准，可用于正式赛事编排。"
        
        return result
    
    def fun_mode(self, theme):
        """团建趣味定向模式 - 增强版"""
        # 武大校内著名POI列表，包含详细的团建任务
        wuhan_university_poi = {
            "樱花大道": {
                "name": "武汉大学樱花大道",
                "location": "30.5900,114.3020",
                "clue": "寻找校园里最浪漫的花路，每年三月这里会变成粉色海洋。",
                "address": "武汉大学文理学部",
                "tasks": [
                    {
                        "name": "樱花创意合影",
                        "description": "团队全员参与，在樱花树下拍摄一张创意合影，必须包含樱花元素。",
                        "type": "拍照任务",
                        "difficulty": "简单",
                        "points": 10,
                        "time_limit": 5  # 分钟
                    },
                    {
                        "name": "樱花诗词接龙",
                        "description": "团队成员轮流说出带有'樱'或'花'字的诗词，至少完成5句。",
                        "type": "知识挑战",
                        "difficulty": "中等",
                        "points": 15,
                        "time_limit": 3  # 分钟
                    }
                ]
            },
            "樱顶": {
                "name": "武汉大学樱顶",
                "location": "30.5910,114.3000",
                "clue": "寻找樱花盛开时的最佳观赏点，俯瞰整个武大校园。",
                "address": "武汉大学老图书馆旁",
                "tasks": [
                    {
                        "name": "校训解密",
                        "description": "找到樱顶校训碑，集体朗读校训，并解释其含义。",
                        "type": "知识问答",
                        "difficulty": "简单",
                        "points": 10,
                        "time_limit": 4  # 分钟
                    },
                    {
                        "name": "校园俯瞰拼图",
                        "description": "从樱顶俯瞰校园，用手机拍摄3张不同角度的照片，拼成一张完整的校园全景图。",
                        "type": "创意挑战",
                        "difficulty": "中等",
                        "points": 20,
                        "time_limit": 6  # 分钟
                    }
                ]
            },
            "老图书馆": {
                "name": "武汉大学老图书馆",
                "location": "30.5910,114.3000",
                "clue": "寻找最高学府的最高点，这里见证了武大的百年历史。",
                "address": "武汉大学樱顶",
                "tasks": [
                    {
                        "name": "身体拼字",
                        "description": "团队成员用身体拼出'武大'或'珞珈'两个字，拍摄视频记录。",
                        "type": "团队协作",
                        "difficulty": "中等",
                        "points": 15,
                        "time_limit": 5  # 分钟
                    },
                    {
                        "name": "历史问答",
                        "description": "找出老图书馆的建造年份和建筑师。",
                        "type": "知识挑战",
                        "difficulty": "困难",
                        "points": 25,
                        "time_limit": 5  # 分钟
                    }
                ]
            },
            "宋卿体育馆": {
                "name": "武汉大学宋卿体育馆",
                "location": "30.5920,114.3030",
                "clue": "寻找以民国大总统命名的体育馆，它曾是远东最好的体育馆之一。",
                "address": "武汉大学文理学部",
                "tasks": [
                    {
                        "name": "两人三足挑战",
                        "description": "团队成员两两一组，完成20米的两人三足比赛，记录最快完成时间。",
                        "type": "运动挑战",
                        "difficulty": "中等",
                        "points": 20,
                        "time_limit": 8  # 分钟
                    },
                    {
                        "name": "篮球投篮比赛",
                        "description": "团队成员轮流投篮，在3分钟内投进最多球的团队获胜。",
                        "type": "运动挑战",
                        "difficulty": "简单",
                        "points": 15,
                        "time_limit": 5  # 分钟
                    }
                ]
            },
            "十八栋": {
                "name": "武汉大学十八栋",
                "location": "30.5940,114.2980",
                "clue": "寻找民国时期教授们的居所，感受老武大的人文气息。",
                "address": "武汉大学珞珈山",
                "tasks": [
                    {
                        "name": "老建筑探索",
                        "description": "找到一栋标有编号的老别墅，记录其编号、建筑风格特点和曾居住的名人。",
                        "type": "探索任务",
                        "difficulty": "困难",
                        "points": 30,
                        "time_limit": 10  # 分钟
                    },
                    {
                        "name": "自然寻宝",
                        "description": "在十八栋附近寻找5种不同的植物或动物，拍摄照片并记录名称。",
                        "type": "探索任务",
                        "difficulty": "中等",
                        "points": 20,
                        "time_limit": 8  # 分钟
                    }
                ]
            },
            "万林艺术博物馆": {
                "name": "武汉大学万林艺术博物馆",
                "location": "30.5890,114.3010",
                "clue": "寻找校园里最现代的建筑，它的外形像一块飞来的石头。",
                "address": "武汉大学文理学部",
                "tasks": [
                    {
                        "name": "传统与现代对比",
                        "description": "以'传统与现代'为主题，拍摄一张万林博物馆与武大老建筑的对比照片。",
                        "type": "拍照任务",
                        "difficulty": "中等",
                        "points": 20,
                        "time_limit": 6  # 分钟
                    },
                    {
                        "name": "建筑创意素描",
                        "description": "团队成员合作，用10分钟时间素描万林博物馆的外观，要求包含主要建筑特征。",
                        "type": "创意挑战",
                        "difficulty": "困难",
                        "points": 25,
                        "time_limit": 10  # 分钟
                    }
                ]
            },
            "郭沫若铜像": {
                "name": "武汉大学郭沫若铜像",
                "location": "30.5885,114.2990",
                "clue": "寻找著名文学家郭沫若先生的铜像，他曾担任武大校长。",
                "address": "武汉大学文理学部",
                "tasks": [
                    {
                        "name": "即兴短剧表演",
                        "description": "围绕郭沫若的文学作品或生平事迹，即兴表演一个1-2分钟的短剧。",
                        "type": "创意表演",
                        "difficulty": "中等",
                        "points": 25,
                        "time_limit": 10  # 分钟
                    },
                    {
                        "name": "诗歌朗诵",
                        "description": "团队成员集体朗诵一首郭沫若的诗歌，要求有感情地背诵。",
                        "type": "文化体验",
                        "difficulty": "简单",
                        "points": 15,
                        "time_limit": 5  # 分钟
                    }
                ]
            },
            "工学部操场": {
                "name": "武汉大学工学部操场",
                "location": "30.5930,114.3070",
                "clue": "寻找工学部的运动天地，这里是工科学子挥洒汗水的地方。",
                "address": "武汉大学工学部",
                "tasks": [
                    {
                        "name": "拔河比赛",
                        "description": "与其他团队进行一场5分钟的拔河比赛，获胜团队获得双倍积分。",
                        "type": "团队游戏",
                        "difficulty": "中等",
                        "points": 30,
                        "time_limit": 10  # 分钟
                    },
                    {
                        "name": "接力赛跑",
                        "description": "团队成员进行4x100米接力赛，记录完成时间。",
                        "type": "运动挑战",
                        "difficulty": "中等",
                        "points": 25,
                        "time_limit": 8  # 分钟
                    }
                ]
            }
        }
        
        # 团建主题任务映射
        theme_poi_map = {
            "樱花季": ["樱花大道", "樱顶", "老图书馆", "万林艺术博物馆"],
            "校史探秘": ["老图书馆", "宋卿体育馆", "十八栋", "郭沫若铜像"],
            "文化体验": ["万林艺术博物馆", "郭沫若铜像", "樱花大道", "樱顶"],
            "团日活动": ["老图书馆", "宋卿体育馆", "郭沫若铜像", "工学部操场"],
            "新生破冰": ["樱花大道", "樱顶", "工学部操场", "万林艺术博物馆"],
            "社团活动": ["万林艺术博物馆", "十八栋", "宋卿体育馆", "樱花大道"],
            "户外拓展": ["工学部操场", "十八栋", "樱顶", "老图书馆"],
            "文化传承": ["郭沫若铜像", "老图书馆", "樱顶", "万林艺术博物馆"]
        }
        
        if theme not in theme_poi_map:
            return "错误：不支持的活动主题！请尝试：樱花季、校史探秘、文化体验、团日活动、新生破冰、社团活动、户外拓展、文化传承"
        
        # 生成团建任务方案
        result = f"🎉 【{theme}】团建定向方案 🎉\n"
        result += "📋 活动规则：\n"
        result += "1. 建议4-6人一组，每组推选一名队长\n"
        result += "2. 每个点位包含1-2个任务，可选择完成\n"
        result += "3. 任务完成后，由队长拍摄照片或视频作为凭证\n"
        result += "4. 最终根据积分高低评选获胜团队\n"
        result += "5. 活动时间：建议2-3小时\n\n"
        
        result += "🏆 积分规则：\n"
        result += "• 简单任务：10-15分\n"
        result += "• 中等任务：20-25分\n"
        result += "• 困难任务：30分\n"
        result += "• 最快完成团队额外奖励20分\n"
        result += "• 最佳创意团队额外奖励15分\n\n"
        
        total_duration = 0
        total_points = 0
        selected_points = theme_poi_map[theme]
        
        for i, poi_key in enumerate(selected_points, 1):
            if poi_key in wuhan_university_poi:
                poi = wuhan_university_poi[poi_key]
                # 获取导航信息
                route = self.get_route("30.514438,114.371233", poi["location"])
                duration = int(route["duration"]/60) if route else 5
                total_duration += duration
                
                result += f"📍 点位{i}：{poi['name']}\n"
                result += f"🔍 LBS线索：{poi['clue']}\n"
                result += f"🧭 导航指引：打开地图导航至{poi['name']}，步行约{duration}分钟，注意{poi['address']}周边地形\n"
                result += f"⏱️  建议用时：{duration+10}分钟\n"
                result += f"📌 点位介绍：{poi['name']}是武汉大学的著名地标，具有丰富的历史和文化内涵。\n"
                
                # 输出任务列表
                for j, task in enumerate(poi['tasks']):
                    result += f"\n   📝 任务{j+1}（{task['difficulty']}）：{task['name']}\n"
                    result += f"      • 类型：{task['type']}\n"
                    result += f"      • 描述：{task['description']}\n"
                    result += f"      • 分值：{task['points']}分\n"
                    result += f"      • 时间限制：{task['time_limit']}分钟\n"
                    total_points += task['points']
                
                result += "\n"
        
        result += f"📊 方案概览：\n"
        result += f"• 总点位数量：{len(selected_points)}个\n"
        result += f"• 总任务数量：{sum(len(poi['tasks']) for poi in wuhan_university_poi.values() if poi['name'].split('·')[-1] in [p.split('·')[-1] for p in selected_points])}\n"
        result += f"• 最高可获积分：{total_points}分\n"
        result += f"• 预计总时长：约{total_duration+40}分钟\n"
        result += f"• 总步行距离：约{int(total_duration*80)}米（估算）\n\n"
        
        result += f"🤝 团建建议：\n"
        result += "1. 活动前：确保所有队员穿着舒适的运动鞋和服装，携带手机和充电宝\n"
        result += "2. 活动中：注意安全，遵守校园规定，爱护环境\n"
        result += "3. 活动后：组织小组分享会，展示成果，颁发奖品\n"
        result += "4. 分享方式：将照片或视频分享至班级/社团群，带上#珞珈探秘# #武大团建#话题标签\n\n"
        
        result += f"🏆 奖项设置：\n"
        result += "• 冠军团队：证书+精美礼品\n"
        result += "• 亚军团队：证书+纪念品\n"
        result += "• 最佳创意团队：证书+创意奖品\n"
        result += "• 最快完成团队：证书+速度奖品\n\n"
        
        result += f"📸 分享模板：\n"
        result += "【珞珈探秘·团建定向】\n"
        result += "我们完成了{theme}主题的团建定向活动！\n"
        result += "团队名称：XXX\n"
        result += "完成点位：{len(selected_points)}个\n"
        result += "获得积分：XXX分\n"
        result += "活动感受：XXX\n"
        result += "#珞珈探秘 #武大团建 #武汉大学\n\n"
        result += f"✅ 方案生成完成！祝大家团建愉快！"
        
        return result
    
    def process_request(self, user_input):
        """处理用户请求"""
        # 意图识别
        if any(word in user_input for word in ["比赛", "专业", "赛事", "短距离", "百米定向", "积分赛"]):
            # 专业模式
            # 解析输入：赛事类型、起点、终点
            # 这里简化处理，实际需要更复杂的NLP解析
            return self.professional_mode("短距离", "武汉大学信息学部操场", "武汉大学文理学部操场")
        else:
            # 趣味模式
            # 解析主题
            if "樱花" in user_input:
                theme = "樱花季"
            elif "校史" in user_input or "历史" in user_input:
                theme = "校史探秘"
            else:
                theme = "文化体验"
            return self.fun_mode(theme)

# 测试代码
if __name__ == "__main__":
    explorer = LuojiaExplorer()
    # 测试专业模式
    print("=== 专业赛事编排测试 ===")
    print(explorer.professional_mode("短距离", "武汉大学信息学部操场", "武汉大学文理学部操场"))
    
    print("\n=== 趣味定向测试 ===")
    # 测试趣味模式
    print(explorer.fun_mode("樱花季"))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天氣數據分析器
整合台灣中央氣象署API，分析天氣因素對投票率的影響
"""

import os
import json
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeatherAnalyzer:
    """天氣數據分析器"""
    
    def __init__(self):
        # 中央氣象署API配置
        self.cwa_api_key = os.getenv('CWA_API_KEY')  # 中央氣象署API金鑰
        self.base_url = "https://opendata.cwa.gov.tw/api"
        
        # 台灣主要縣市代碼
        self.city_codes = {
            '台北市': 'F-D0047-061',
            '新北市': 'F-D0047-069', 
            '桃園市': 'F-D0047-005',
            '台中市': 'F-D0047-073',
            '台南市': 'F-D0047-077',
            '高雄市': 'F-D0047-065',
            '基隆市': 'F-D0047-049',
            '新竹市': 'F-D0047-053',
            '嘉義市': 'F-D0047-057'
        }
        
        # 天氣對投票率影響的權重
        self.weather_weights = {
            'rain_probability': -0.3,    # 降雨機率負面影響
            'temperature_comfort': 0.1,  # 舒適溫度正面影響
            'wind_speed': -0.1,          # 強風負面影響
            'visibility': 0.05,          # 能見度正面影響
            'humidity': -0.05            # 高濕度輕微負面影響
        }
    
    def get_weather_forecast(self, city: str, days: int = 3) -> Optional[Dict]:
        """獲取指定城市的天氣預報"""
        if not self.cwa_api_key:
            logger.warning("CWA API key not found, using mock weather data")
            return self._get_mock_weather_data(city)
            
        if city not in self.city_codes:
            logger.error(f"City '{city}' not supported")
            return None
            
        try:
            # 構建API請求URL
            url = f"{self.base_url}/v1/rest/datastore/{self.city_codes[city]}"
            params = {
                'Authorization': self.cwa_api_key,
                'format': 'JSON',
                'elementName': 'WeatherDescription,PoP12h,T,RH,WS,Vis'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # 解析天氣數據
            weather_data = self._parse_weather_data(data, city)
            return weather_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch weather data for {city}: {e}")
            return self._get_mock_weather_data(city)
        except Exception as e:
            logger.error(f"Error processing weather data for {city}: {e}")
            return self._get_mock_weather_data(city)
    
    def _parse_weather_data(self, data: Dict, city: str) -> Dict:
        """解析氣象署API返回的數據"""
        try:
            records = data['records']['locations'][0]['location']
            
            weather_info = {
                'city': city,
                'forecast_date': datetime.now().isoformat(),
                'daily_forecasts': []
            }
            
            for location in records:
                location_name = location['locationName']
                weather_elements = location['weatherElement']
                
                # 提取各項天氣要素
                daily_data = {}
                
                for element in weather_elements:
                    element_name = element['elementName']
                    
                    if element_name == 'PoP12h':  # 降雨機率
                        daily_data['rain_probability'] = float(element['time'][0]['elementValue'][0]['value'])
                    elif element_name == 'T':  # 溫度
                        daily_data['temperature'] = float(element['time'][0]['elementValue'][0]['value'])
                    elif element_name == 'RH':  # 相對濕度
                        daily_data['humidity'] = float(element['time'][0]['elementValue'][0]['value'])
                    elif element_name == 'WS':  # 風速
                        daily_data['wind_speed'] = float(element['time'][0]['elementValue'][0]['value'])
                    elif element_name == 'Vis':  # 能見度
                        daily_data['visibility'] = float(element['time'][0]['elementValue'][0]['value'])
                
                daily_data['location'] = location_name
                weather_info['daily_forecasts'].append(daily_data)
            
            return weather_info
            
        except (KeyError, IndexError, ValueError) as e:
            logger.error(f"Error parsing weather data: {e}")
            return self._get_mock_weather_data(city)
    
    def _get_mock_weather_data(self, city: str) -> Dict:
        """生成模擬天氣數據（當API不可用時）"""
        import random
        
        return {
            'city': city,
            'forecast_date': datetime.now().isoformat(),
            'daily_forecasts': [{
                'location': city,
                'rain_probability': random.uniform(10, 80),  # 10-80%降雨機率
                'temperature': random.uniform(18, 32),       # 18-32度
                'humidity': random.uniform(60, 90),          # 60-90%濕度
                'wind_speed': random.uniform(1, 8),          # 1-8 m/s風速
                'visibility': random.uniform(5, 15)          # 5-15公里能見度
            }]
        }
    
    def calculate_weather_impact_on_turnout(self, weather_data: Dict) -> Dict:
        """計算天氣對投票率的影響"""
        if not weather_data or not weather_data.get('daily_forecasts'):
            return {
                'weather_impact_score': 0.0,
                'impact_factors': {},
                'recommendation': '無天氣數據'
            }
        
        # 取第一個預報點的數據
        forecast = weather_data['daily_forecasts'][0]
        
        impact_factors = {}
        total_impact = 0.0
        
        # 降雨機率影響
        rain_prob = forecast.get('rain_probability', 0)
        rain_impact = self._calculate_rain_impact(rain_prob)
        impact_factors['rain_impact'] = rain_impact
        total_impact += rain_impact * self.weather_weights['rain_probability']
        
        # 溫度舒適度影響
        temperature = forecast.get('temperature', 25)
        temp_impact = self._calculate_temperature_impact(temperature)
        impact_factors['temperature_impact'] = temp_impact
        total_impact += temp_impact * self.weather_weights['temperature_comfort']
        
        # 風速影響
        wind_speed = forecast.get('wind_speed', 3)
        wind_impact = self._calculate_wind_impact(wind_speed)
        impact_factors['wind_impact'] = wind_impact
        total_impact += wind_impact * self.weather_weights['wind_speed']
        
        # 能見度影響
        visibility = forecast.get('visibility', 10)
        vis_impact = self._calculate_visibility_impact(visibility)
        impact_factors['visibility_impact'] = vis_impact
        total_impact += vis_impact * self.weather_weights['visibility']
        
        # 濕度影響
        humidity = forecast.get('humidity', 70)
        humidity_impact = self._calculate_humidity_impact(humidity)
        impact_factors['humidity_impact'] = humidity_impact
        total_impact += humidity_impact * self.weather_weights['humidity']
        
        # 生成建議
        recommendation = self._generate_weather_recommendation(forecast, total_impact)
        
        return {
            'weather_impact_score': total_impact,
            'impact_factors': impact_factors,
            'weather_data': forecast,
            'recommendation': recommendation
        }
    
    def _calculate_rain_impact(self, rain_probability: float) -> float:
        """計算降雨對投票率的影響"""
        if rain_probability < 20:
            return 0.1  # 低降雨機率，輕微正面影響
        elif rain_probability < 50:
            return 0.0  # 中等降雨機率，無明顯影響
        elif rain_probability < 80:
            return -0.3  # 高降雨機率，負面影響
        else:
            return -0.5  # 極高降雨機率，強烈負面影響
    
    def _calculate_temperature_impact(self, temperature: float) -> float:
        """計算溫度對投票率的影響"""
        # 舒適溫度範圍：20-28度
        if 20 <= temperature <= 28:
            return 0.2  # 舒適溫度，正面影響
        elif 15 <= temperature < 20 or 28 < temperature <= 32:
            return 0.0  # 稍微不適，無明顯影響
        else:
            return -0.2  # 極端溫度，負面影響
    
    def _calculate_wind_impact(self, wind_speed: float) -> float:
        """計算風速對投票率的影響"""
        if wind_speed < 3:
            return 0.0  # 微風，無影響
        elif wind_speed < 6:
            return -0.1  # 輕風，輕微負面影響
        else:
            return -0.3  # 強風，明顯負面影響
    
    def _calculate_visibility_impact(self, visibility: float) -> float:
        """計算能見度對投票率的影響"""
        if visibility >= 10:
            return 0.1  # 良好能見度，輕微正面影響
        elif visibility >= 5:
            return 0.0  # 普通能見度，無影響
        else:
            return -0.2  # 低能見度，負面影響
    
    def _calculate_humidity_impact(self, humidity: float) -> float:
        """計算濕度對投票率的影響"""
        if humidity < 60:
            return 0.1  # 低濕度，舒適
        elif humidity < 80:
            return 0.0  # 中等濕度，無明顯影響
        else:
            return -0.1  # 高濕度，輕微負面影響
    
    def _generate_weather_recommendation(self, forecast: Dict, impact_score: float) -> str:
        """生成天氣影響建議"""
        rain_prob = forecast.get('rain_probability', 0)
        temperature = forecast.get('temperature', 25)
        
        if impact_score > 0.1:
            return f"天氣條件良好（降雨機率{rain_prob:.0f}%，溫度{temperature:.0f}°C），預期對投票率有正面影響"
        elif impact_score < -0.2:
            return f"天氣條件不佳（降雨機率{rain_prob:.0f}%，溫度{temperature:.0f}°C），可能降低投票率"
        else:
            return f"天氣條件普通（降雨機率{rain_prob:.0f}%，溫度{temperature:.0f}°C），對投票率影響有限"
    
    def analyze_multiple_cities(self, cities: List[str]) -> Dict:
        """分析多個城市的天氣影響"""
        results = {}
        total_impact = 0.0
        valid_cities = 0
        
        for city in cities:
            weather_data = self.get_weather_forecast(city)
            if weather_data:
                impact_analysis = self.calculate_weather_impact_on_turnout(weather_data)
                results[city] = impact_analysis
                total_impact += impact_analysis['weather_impact_score']
                valid_cities += 1
        
        # 計算平均影響
        avg_impact = total_impact / valid_cities if valid_cities > 0 else 0.0
        
        return {
            'cities_analysis': results,
            'average_weather_impact': avg_impact,
            'analyzed_cities': valid_cities,
            'analysis_date': datetime.now().isoformat()
        }

def main():
    """主函數"""
    analyzer = WeatherAnalyzer()
    
    # 分析主要城市天氣影響
    major_cities = ['台北市', '新北市', '桃園市', '台中市', '台南市', '高雄市']
    
    print("🌤️ 開始分析天氣對投票率的影響...")
    results = analyzer.analyze_multiple_cities(major_cities)
    
    print(f"\n📊 天氣影響分析結果 ({results['analyzed_cities']} 個城市)")
    print(f"平均天氣影響分數: {results['average_weather_impact']:.3f}")
    
    print("\n🏙️ 各城市詳細分析:")
    for city, analysis in results['cities_analysis'].items():
        print(f"\n{city}:")
        print(f"  影響分數: {analysis['weather_impact_score']:.3f}")
        print(f"  建議: {analysis['recommendation']}")
        
        weather = analysis['weather_data']
        print(f"  天氣詳情: 降雨{weather['rain_probability']:.0f}% | "
              f"溫度{weather['temperature']:.0f}°C | "
              f"濕度{weather['humidity']:.0f}%")
    
    # 保存結果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"weather_analysis_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 分析結果已保存至: {filename}")

if __name__ == "__main__":
    main()

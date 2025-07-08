#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台灣罷免預測 - 歷史驗證模組
使用過去選舉數據驗證模型準確性
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List, Tuple
import logging
from sklearn.metrics import mean_absolute_percentage_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HistoricalValidator:
    """歷史驗證器"""
    
    def __init__(self):
        """初始化歷史驗證器"""
        self.historical_data = self.load_historical_data()
        self.validation_results = {}
        
    def load_historical_data(self) -> Dict:
        """載入歷史選舉數據"""
        historical_data = {
            "presidential_elections": [
                {
                    "year": 2016,
                    "type": "總統選舉",
                    "national_turnout": 0.661,
                    "regional_turnout": {
                        "北部": 0.703,
                        "中部": 0.659,
                        "南部": 0.631,
                        "東部": 0.642
                    },
                    "age_group_turnout": {
                        "18-35": 0.58,
                        "36-55": 0.72,
                        "56+": 0.68
                    },
                    "weather_conditions": {
                        "temperature": 18.5,
                        "rainfall": 2.3,
                        "weather_score": 0.75
                    },
                    "economic_indicators": {
                        "unemployment_rate": 3.92,
                        "gdp_growth": 1.48,
                        "inflation_rate": 1.39
                    }
                },
                {
                    "year": 2020,
                    "type": "總統選舉",
                    "national_turnout": 0.748,
                    "regional_turnout": {
                        "北部": 0.782,
                        "中部": 0.744,
                        "南部": 0.731,
                        "東部": 0.715
                    },
                    "age_group_turnout": {
                        "18-35": 0.69,
                        "36-55": 0.81,
                        "56+": 0.74
                    },
                    "weather_conditions": {
                        "temperature": 22.1,
                        "rainfall": 0.8,
                        "weather_score": 0.85
                    },
                    "economic_indicators": {
                        "unemployment_rate": 3.73,
                        "gdp_growth": 3.11,
                        "inflation_rate": -0.23
                    }
                }
            ],
            "recall_elections": [
                {
                    "year": 2020,
                    "target": "韓國瑜",
                    "location": "高雄市",
                    "region": "南部",
                    "turnout": 0.421,
                    "result": "通過",
                    "agree_rate": 0.939,
                    "weather_conditions": {
                        "temperature": 28.3,
                        "rainfall": 15.2,
                        "weather_score": 0.65
                    },
                    "political_climate": {
                        "media_coverage": 0.95,
                        "social_media_activity": 0.88,
                        "controversy_level": 0.92
                    },
                    "economic_factors": {
                        "local_unemployment": 3.8,
                        "satisfaction_rating": 0.32
                    }
                },
                {
                    "year": 2021,
                    "target": "陳柏惟",
                    "location": "台中市第二選區",
                    "region": "中部",
                    "turnout": 0.257,
                    "result": "通過",
                    "agree_rate": 0.773,
                    "weather_conditions": {
                        "temperature": 25.1,
                        "rainfall": 3.5,
                        "weather_score": 0.78
                    },
                    "political_climate": {
                        "media_coverage": 0.72,
                        "social_media_activity": 0.65,
                        "controversy_level": 0.68
                    },
                    "economic_factors": {
                        "local_unemployment": 3.5,
                        "satisfaction_rating": 0.45
                    }
                },
                {
                    "year": 2022,
                    "target": "林昶佐",
                    "location": "台北市第八選區",
                    "region": "北部",
                    "turnout": 0.171,
                    "result": "未通過",
                    "agree_rate": 0.503,
                    "weather_conditions": {
                        "temperature": 16.8,
                        "rainfall": 8.7,
                        "weather_score": 0.68
                    },
                    "political_climate": {
                        "media_coverage": 0.58,
                        "social_media_activity": 0.52,
                        "controversy_level": 0.48
                    },
                    "economic_factors": {
                        "local_unemployment": 2.9,
                        "satisfaction_rating": 0.58
                    }
                }
            ]
        }
        
        return historical_data
    
    def calculate_mece_prediction(self, election_data: Dict) -> float:
        """使用MECE模型計算歷史選舉的預測值"""
        
        # 投票意願計算
        if election_data.get('type') == '總統選舉':
            # 總統選舉的投票意願較高
            base_intention = 0.75
        else:
            # 罷免選舉的投票意願較低
            base_intention = 0.35
        
        # 根據爭議程度調整
        if 'political_climate' in election_data:
            controversy_factor = election_data['political_climate'].get('controversy_level', 0.5)
            base_intention *= (0.8 + 0.4 * controversy_factor)
        
        # 外部環境計算
        weather_score = election_data.get('weather_conditions', {}).get('weather_score', 0.75)
        
        if 'political_climate' in election_data:
            media_factor = election_data['political_climate'].get('media_coverage', 0.6)
        else:
            media_factor = 0.6
        
        # 經濟因素
        if 'economic_factors' in election_data:
            economic_factor = 1 - election_data['economic_factors'].get('local_unemployment', 3.5) / 10
        else:
            economic_factor = 0.65
        
        external_environment = (weather_score + media_factor + economic_factor) / 3
        
        # MECE預測
        prediction = base_intention * external_environment
        
        return prediction
    
    def validate_model_accuracy(self) -> Dict:
        """驗證模型準確性"""
        logger.info("開始模型準確性驗證...")
        
        actual_values = []
        predicted_values = []
        election_info = []
        
        # 驗證總統選舉
        for election in self.historical_data['presidential_elections']:
            actual = election['national_turnout']
            predicted = self.calculate_mece_prediction(election)
            
            actual_values.append(actual)
            predicted_values.append(predicted)
            election_info.append(f"{election['year']}總統選舉")
        
        # 驗證罷免選舉
        for election in self.historical_data['recall_elections']:
            actual = election['turnout']
            predicted = self.calculate_mece_prediction(election)
            
            actual_values.append(actual)
            predicted_values.append(predicted)
            election_info.append(f"{election['year']}{election['target']}罷免")
        
        # 計算驗證指標
        mape = mean_absolute_percentage_error(actual_values, predicted_values)
        r2 = r2_score(actual_values, predicted_values)
        
        # 計算平均絕對誤差
        mae = np.mean(np.abs(np.array(actual_values) - np.array(predicted_values)))
        
        validation_results = {
            'mape': float(mape),
            'r2_score': float(r2),
            'mae': float(mae),
            'sample_size': int(len(actual_values)),
            'detailed_results': [
                {
                    'election': info,
                    'actual': float(actual),
                    'predicted': float(predicted),
                    'error': float(abs(actual - predicted)),
                    'percentage_error': float(abs(actual - predicted) / actual * 100)
                }
                for info, actual, predicted in zip(election_info, actual_values, predicted_values)
            ]
        }
        
        self.validation_results = validation_results
        logger.info(f"驗證完成 - MAPE: {mape:.3f}, R²: {r2:.3f}")
        
        return validation_results
    
    def regional_validation(self) -> Dict:
        """地區驗證分析"""
        logger.info("開始地區驗證分析...")
        
        regional_results = {}
        
        for election in self.historical_data['presidential_elections']:
            year = election['year']
            regional_results[f'{year}總統選舉'] = {}
            
            for region, actual_turnout in election['regional_turnout'].items():
                # 根據地區特性調整預測
                base_prediction = self.calculate_mece_prediction(election)
                
                # 地區調整因子
                regional_factors = {
                    '北部': 1.1,   # 政治中心，投票率較高
                    '中部': 0.95,  # 傳統地區，投票率中等
                    '南部': 1.05,  # 政治傳統，投票率較高
                    '東部': 0.85   # 人口較少，投票率較低
                }
                
                regional_prediction = base_prediction * regional_factors.get(region, 1.0)
                error = abs(actual_turnout - regional_prediction)
                
                regional_results[f'{year}總統選舉'][region] = {
                    'actual': float(actual_turnout),
                    'predicted': float(regional_prediction),
                    'error': float(error),
                    'percentage_error': float(error / actual_turnout * 100)
                }
        
        return regional_results
    
    def age_group_validation(self) -> Dict:
        """年齡層驗證分析"""
        logger.info("開始年齡層驗證分析...")
        
        age_results = {}
        
        for election in self.historical_data['presidential_elections']:
            year = election['year']
            age_results[f'{year}總統選舉'] = {}
            
            for age_group, actual_turnout in election['age_group_turnout'].items():
                # 根據年齡層特性調整預測
                base_prediction = self.calculate_mece_prediction(election)
                
                # 年齡層調整因子
                age_factors = {
                    '18-35': 0.85,  # 年輕人投票率較低
                    '36-55': 1.15,  # 中年人投票率最高
                    '56+': 1.0      # 長者投票率中等
                }
                
                age_prediction = base_prediction * age_factors.get(age_group, 1.0)
                error = abs(actual_turnout - age_prediction)
                
                age_results[f'{year}總統選舉'][age_group] = {
                    'actual': float(actual_turnout),
                    'predicted': float(age_prediction),
                    'error': float(error),
                    'percentage_error': float(error / actual_turnout * 100)
                }
        
        return age_results
    
    def temporal_stability_analysis(self) -> Dict:
        """時間穩定性分析"""
        logger.info("開始時間穩定性分析...")
        
        # 分析模型在不同時期的表現
        temporal_results = {
            'trend_analysis': {},
            'stability_metrics': {}
        }
        
        # 按年份排序
        all_elections = []
        
        for election in self.historical_data['presidential_elections']:
            all_elections.append({
                'year': election['year'],
                'type': '總統選舉',
                'actual': election['national_turnout'],
                'predicted': self.calculate_mece_prediction(election)
            })
        
        for election in self.historical_data['recall_elections']:
            all_elections.append({
                'year': election['year'],
                'type': '罷免選舉',
                'actual': election['turnout'],
                'predicted': self.calculate_mece_prediction(election)
            })
        
        all_elections.sort(key=lambda x: x['year'])
        
        # 計算時間趨勢
        years = [e['year'] for e in all_elections]
        errors = [abs(e['actual'] - e['predicted']) for e in all_elections]
        
        # 計算穩定性指標
        error_std = np.std(errors)
        error_mean = np.mean(errors)
        stability_coefficient = 1 - (error_std / error_mean) if error_mean > 0 else 0
        
        temporal_results['stability_metrics'] = {
            'error_standard_deviation': float(error_std),
            'error_mean': float(error_mean),
            'stability_coefficient': float(stability_coefficient),
            'temporal_consistency': bool(stability_coefficient > 0.8)
        }
        
        temporal_results['trend_analysis'] = all_elections
        
        return temporal_results
    
    def generate_validation_report(self) -> Dict:
        """生成完整驗證報告"""
        logger.info("生成驗證報告...")
        
        # 執行所有驗證
        accuracy_results = self.validate_model_accuracy()
        regional_results = self.regional_validation()
        age_results = self.age_group_validation()
        temporal_results = self.temporal_stability_analysis()
        
        # 綜合評估
        overall_assessment = {
            'model_grade': self.calculate_model_grade(accuracy_results),
            'strengths': self.identify_strengths(accuracy_results, regional_results, age_results),
            'weaknesses': self.identify_weaknesses(accuracy_results, regional_results, age_results),
            'recommendations': self.generate_recommendations(accuracy_results, regional_results, age_results)
        }
        
        validation_report = {
            'timestamp': datetime.now().isoformat(),
            'overall_assessment': overall_assessment,
            'accuracy_validation': accuracy_results,
            'regional_validation': regional_results,
            'age_group_validation': age_results,
            'temporal_stability': temporal_results
        }
        
        # 保存報告
        self.save_validation_report(validation_report)
        
        return validation_report
    
    def calculate_model_grade(self, accuracy_results: Dict) -> str:
        """計算模型等級"""
        mape = accuracy_results['mape']
        r2 = accuracy_results['r2_score']
        
        if mape < 0.1 and r2 > 0.9:
            return "A+ (優秀)"
        elif mape < 0.15 and r2 > 0.85:
            return "A (良好)"
        elif mape < 0.2 and r2 > 0.8:
            return "B+ (尚可)"
        elif mape < 0.25 and r2 > 0.7:
            return "B (需改進)"
        else:
            return "C (待優化)"
    
    def identify_strengths(self, accuracy_results: Dict, regional_results: Dict, age_results: Dict) -> List[str]:
        """識別模型優勢"""
        strengths = []
        
        if accuracy_results['mape'] < 0.1:
            strengths.append("整體預測準確度高")
        
        if accuracy_results['r2_score'] > 0.85:
            strengths.append("模型解釋力強")
        
        # 檢查地區預測表現
        regional_errors = []
        for election, regions in regional_results.items():
            for region, data in regions.items():
                regional_errors.append(data['percentage_error'])
        
        if np.mean(regional_errors) < 15:
            strengths.append("地區預測表現良好")
        
        return strengths
    
    def identify_weaknesses(self, accuracy_results: Dict, regional_results: Dict, age_results: Dict) -> List[str]:
        """識別模型弱點"""
        weaknesses = []
        
        if accuracy_results['mape'] > 0.15:
            weaknesses.append("整體預測誤差偏高")
        
        # 檢查樣本數量
        if accuracy_results['sample_size'] < 10:
            weaknesses.append("歷史數據樣本不足")
        
        return weaknesses
    
    def generate_recommendations(self, accuracy_results: Dict, regional_results: Dict, age_results: Dict) -> List[str]:
        """生成改進建議"""
        recommendations = []
        
        if accuracy_results['mape'] > 0.1:
            recommendations.append("增加更多歷史數據進行訓練")
            recommendations.append("優化MECE模型參數")
        
        recommendations.append("定期更新模型權重")
        recommendations.append("增加實時校準機制")
        
        return recommendations
    
    def save_validation_report(self, report: Dict):
        """保存驗證報告"""
        os.makedirs('reports', exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f'reports/validation_report_{timestamp}.json'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"驗證報告已保存到: {report_file}")

def main():
    """主要執行函數"""
    validator = HistoricalValidator()
    
    # 生成完整驗證報告
    report = validator.generate_validation_report()
    
    # 顯示關鍵結果
    print("=== 模型驗證結果 ===")
    print(f"模型等級: {report['overall_assessment']['model_grade']}")
    print(f"MAPE: {report['accuracy_validation']['mape']:.3f}")
    print(f"R²: {report['accuracy_validation']['r2_score']:.3f}")
    print(f"平均絕對誤差: {report['accuracy_validation']['mae']:.3f}")
    
    print("\n=== 模型優勢 ===")
    for strength in report['overall_assessment']['strengths']:
        print(f"✅ {strength}")
    
    print("\n=== 改進建議 ===")
    for recommendation in report['overall_assessment']['recommendations']:
        print(f"💡 {recommendation}")

if __name__ == "__main__":
    main()

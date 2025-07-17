#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
數據來源驗證和標註系統
Data Source Validator and Annotation System

確保所有數據都明確標註來源，區分真實數據和模擬數據
"""

import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataSourceValidator:
    """數據來源驗證器"""
    
    def __init__(self):
        self.data_sources = {
            'real_sources': [
                'PTT論壇爬蟲',
                'Dcard API',
                '中央氣象署API',
                '聯合新聞網',
                '中時新聞網',
                '自由時報',
                '中選會開放數據',
                '內政部統計',
                '政大選研中心',
                '中研院數據'
            ],
            'simulated_sources': [
                '模擬數據',
                '隨機生成',
                '統計模型',
                '歷史推估'
            ]
        }
        
        self.validation_log = []
    
    def validate_data_source(self, data: Dict) -> Dict:
        """驗證數據來源並添加標註"""
        validated_data = data.copy()
        
        # 檢查是否已有數據來源標註
        if 'data_source' not in data:
            validated_data['data_source'] = '⚠️ 未標註數據來源 (Unknown Source)'
            validated_data['is_simulated'] = True
            validated_data['validation_warning'] = '數據來源未明確標註'
        
        # 檢查是否為模擬數據
        if 'is_simulated' not in data:
            # 根據數據來源判斷
            source = validated_data.get('data_source', '')
            if any(sim_source in source for sim_source in self.data_sources['simulated_sources']):
                validated_data['is_simulated'] = True
            else:
                validated_data['is_simulated'] = False
        
        # 添加驗證時間戳
        validated_data['validation_timestamp'] = datetime.now().isoformat()
        
        # 記錄驗證日誌
        self._log_validation(validated_data)
        
        return validated_data
    
    def _log_validation(self, data: Dict):
        """記錄驗證日誌"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'data_source': data.get('data_source', 'Unknown'),
            'is_simulated': data.get('is_simulated', True),
            'has_warning': 'validation_warning' in data
        }
        self.validation_log.append(log_entry)
    
    def generate_data_source_report(self) -> Dict:
        """生成數據來源報告"""
        if not self.validation_log:
            return {
                'total_validations': 0,
                'real_data_count': 0,
                'simulated_data_count': 0,
                'warning_count': 0,
                'report_timestamp': datetime.now().isoformat()
            }
        
        total = len(self.validation_log)
        real_count = sum(1 for log in self.validation_log if not log['is_simulated'])
        simulated_count = sum(1 for log in self.validation_log if log['is_simulated'])
        warning_count = sum(1 for log in self.validation_log if log['has_warning'])
        
        return {
            'total_validations': total,
            'real_data_count': real_count,
            'simulated_data_count': simulated_count,
            'warning_count': warning_count,
            'real_data_percentage': (real_count / total) * 100 if total > 0 else 0,
            'simulated_data_percentage': (simulated_count / total) * 100 if total > 0 else 0,
            'data_quality_score': (real_count / total) * 100 if total > 0 else 0,
            'report_timestamp': datetime.now().isoformat(),
            'source_breakdown': self._get_source_breakdown()
        }
    
    def _get_source_breakdown(self) -> Dict:
        """獲取數據來源分解"""
        source_counts = {}
        for log in self.validation_log:
            source = log['data_source']
            if source in source_counts:
                source_counts[source] += 1
            else:
                source_counts[source] = 1
        
        return source_counts
    
    def annotate_mece_data(self, mece_data: pd.DataFrame) -> pd.DataFrame:
        """為MECE數據添加來源標註"""
        annotated_data = mece_data.copy()
        
        # 添加數據來源列
        annotated_data['data_source'] = '📊 統計推估數據 (Statistical Estimation)'
        annotated_data['is_simulated'] = True
        annotated_data['source_type'] = 'statistical_model'
        annotated_data['reference_basis'] = '基於歷史案例和學術研究'
        
        # 為不同維度添加具體參考來源
        for idx, row in annotated_data.iterrows():
            dimension = row['dimension']
            category = row['category']
            
            if dimension == '政治立場':
                annotated_data.at[idx, 'reference_source'] = '韓國瑜罷免案分析 + TVBS民調'
            elif dimension == '年齡層':
                annotated_data.at[idx, 'reference_source'] = '台灣民主基金會民調 + 山水民調'
            elif dimension == '地區':
                annotated_data.at[idx, 'reference_source'] = '內政部統計 + 歷年選舉結果'
            elif dimension == '教育程度':
                annotated_data.at[idx, 'reference_source'] = '台灣社會變遷調查 + 中研院研究'
            elif dimension == '職業':
                annotated_data.at[idx, 'reference_source'] = '勞動部統計 + 政治參與調查'
            else:
                annotated_data.at[idx, 'reference_source'] = '綜合統計資料'
        
        return annotated_data
    
    def create_data_transparency_report(self, all_data: Dict) -> str:
        """創建數據透明度報告"""
        report = []
        report.append("# 🔍 台灣罷免預測系統 - 數據透明度報告")
        report.append(f"**生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # 數據來源概覽
        report.append("## 📊 數據來源概覽")
        report.append("")
        
        real_sources = []
        simulated_sources = []
        
        for key, data in all_data.items():
            if isinstance(data, dict):
                is_simulated = data.get('is_simulated', True)
                source = data.get('data_source', '未知來源')
                
                if is_simulated:
                    simulated_sources.append(f"- **{key}**: {source}")
                else:
                    real_sources.append(f"- **{key}**: {source}")
        
        report.append("### ✅ 真實數據來源")
        if real_sources:
            report.extend(real_sources)
        else:
            report.append("- 目前無真實數據來源")
        report.append("")
        
        report.append("### ⚠️ 模擬數據來源")
        if simulated_sources:
            report.extend(simulated_sources)
        else:
            report.append("- 目前無模擬數據")
        report.append("")
        
        # 數據品質評估
        total_sources = len(real_sources) + len(simulated_sources)
        if total_sources > 0:
            real_percentage = (len(real_sources) / total_sources) * 100
            report.append("## 📈 數據品質評估")
            report.append("")
            report.append(f"- **總數據源數量**: {total_sources}")
            report.append(f"- **真實數據比例**: {real_percentage:.1f}%")
            report.append(f"- **模擬數據比例**: {100-real_percentage:.1f}%")
            report.append("")
            
            if real_percentage >= 70:
                quality_level = "🟢 高品質"
            elif real_percentage >= 40:
                quality_level = "🟡 中等品質"
            else:
                quality_level = "🔴 需要改善"
            
            report.append(f"- **數據品質等級**: {quality_level}")
        
        # 改善建議
        report.append("")
        report.append("## 💡 數據品質改善建議")
        report.append("")
        report.append("1. **增加真實數據來源**: 申請更多官方API金鑰")
        report.append("2. **提升爬蟲穩定性**: 改善網站爬蟲的錯誤處理")
        report.append("3. **數據驗證機制**: 建立多源數據交叉驗證")
        report.append("4. **即時監控**: 建立數據來源健康度監控")
        report.append("")
        
        # 免責聲明
        report.append("## ⚠️ 免責聲明")
        report.append("")
        report.append("- 本系統僅供學術研究和教育用途")
        report.append("- 模擬數據僅用於系統展示，不代表真實情況")
        report.append("- 預測結果不構成任何政治建議或投資指導")
        report.append("- 使用者應理性看待預測結果，並結合多元資訊來源")
        
        return "\n".join(report)

def validate_all_system_data():
    """驗證系統中所有數據的來源"""
    validator = DataSourceValidator()
    
    # 示例：驗證各種數據源
    sample_data = {
        'ptt_sentiment': {
            'positive_ratio': 0.35,
            'data_source': '✅ PTT論壇爬蟲 (Real PTT Crawler)',
            'is_simulated': False
        },
        'weather_data': {
            'temperature': 25.5,
            'data_source': '⚠️ 模擬天氣數據 (Simulated Weather)',
            'is_simulated': True
        },
        'news_sentiment': {
            'positive_ratio': 0.42,
            # 缺少數據來源標註
        }
    }
    
    validated_results = {}
    for key, data in sample_data.items():
        validated_results[key] = validator.validate_data_source(data)
    
    # 生成報告
    report = validator.generate_data_source_report()
    transparency_report = validator.create_data_transparency_report(validated_results)
    
    return {
        'validated_data': validated_results,
        'validation_report': report,
        'transparency_report': transparency_report
    }

if __name__ == "__main__":
    # 執行數據驗證
    results = validate_all_system_data()
    
    print("=== 數據驗證報告 ===")
    print(json.dumps(results['validation_report'], ensure_ascii=False, indent=2))
    
    print("\n=== 數據透明度報告 ===")
    print(results['transparency_report'])

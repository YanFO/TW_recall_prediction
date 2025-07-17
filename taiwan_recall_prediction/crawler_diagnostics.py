#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬蟲診斷工具
Crawler Diagnostics Tool

診斷PTT、Dcard等爬蟲不可用的具體原因並提供解決方案
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CrawlerDiagnostics:
    """爬蟲診斷類"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        self.test_results = {}
    
    def diagnose_ptt_crawler(self, candidate_name="羅智強"):
        """診斷PTT爬蟲問題"""
        print("🔍 診斷PTT爬蟲...")
        
        try:
            # 測試PTT網站連接
            ptt_url = "https://www.ptt.cc/"
            response = requests.get(ptt_url, headers=self.headers, timeout=10)
            
            print(f"PTT主站連接狀態: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ PTT主站可以正常訪問")
                
                # 測試搜尋功能
                search_url = f"https://www.ptt.cc/bbs/search?q={candidate_name}"
                search_response = requests.get(search_url, headers=self.headers, timeout=10)
                
                print(f"PTT搜尋頁面狀態: {search_response.status_code}")
                
                if search_response.status_code == 200:
                    soup = BeautifulSoup(search_response.text, 'html.parser')
                    
                    # 檢查是否需要年齡驗證
                    if "over18" in search_response.text or "滿18歲" in search_response.text:
                        print("⚠️ PTT需要年齡驗證 - 這是主要問題！")
                        print("解決方案: 需要先通過年齡驗證頁面")
                        return self._test_ptt_with_age_verification(candidate_name)
                    
                    # 檢查搜尋結果
                    posts = soup.find_all('div', class_='r-ent')
                    print(f"找到文章數量: {len(posts)}")
                    
                    if len(posts) > 0:
                        print("✅ PTT搜尋功能正常")
                        return {
                            'status': 'success',
                            'posts_found': len(posts),
                            'issue': None
                        }
                    else:
                        print("⚠️ 沒有找到相關文章")
                        return {
                            'status': 'no_data',
                            'posts_found': 0,
                            'issue': '搜尋結果為空'
                        }
                else:
                    print(f"❌ PTT搜尋頁面無法訪問: {search_response.status_code}")
                    return {
                        'status': 'search_failed',
                        'posts_found': 0,
                        'issue': f'搜尋頁面HTTP {search_response.status_code}'
                    }
            else:
                print(f"❌ PTT主站無法訪問: {response.status_code}")
                return {
                    'status': 'connection_failed',
                    'posts_found': 0,
                    'issue': f'主站HTTP {response.status_code}'
                }
                
        except Exception as e:
            print(f"❌ PTT爬蟲錯誤: {e}")
            return {
                'status': 'error',
                'posts_found': 0,
                'issue': str(e)
            }
    
    def _test_ptt_with_age_verification(self, candidate_name):
        """測試PTT年齡驗證解決方案"""
        print("🔧 嘗試解決PTT年齡驗證問題...")
        
        try:
            # 創建session來保持cookies
            session = requests.Session()
            session.headers.update(self.headers)
            
            # 先訪問年齡驗證頁面
            over18_url = "https://www.ptt.cc/ask/over18"
            response = session.get(over18_url, timeout=10)
            
            if response.status_code == 200:
                # 提交年齡驗證
                verify_data = {
                    'from': '/bbs/Gossiping/index.html',
                    'yes': 'yes'
                }
                
                verify_response = session.post(over18_url, data=verify_data, timeout=10)
                
                if verify_response.status_code == 200:
                    print("✅ 年齡驗證通過")
                    
                    # 現在嘗試搜尋
                    search_url = f"https://www.ptt.cc/bbs/search?q={candidate_name}"
                    search_response = session.get(search_url, timeout=10)
                    
                    if search_response.status_code == 200:
                        soup = BeautifulSoup(search_response.text, 'html.parser')
                        posts = soup.find_all('div', class_='r-ent')
                        
                        print(f"✅ 年齡驗證後找到文章數量: {len(posts)}")
                        
                        return {
                            'status': 'success_with_verification',
                            'posts_found': len(posts),
                            'issue': None,
                            'solution': '需要年齡驗證'
                        }
                    
        except Exception as e:
            print(f"❌ 年齡驗證解決方案失敗: {e}")
        
        return {
            'status': 'verification_failed',
            'posts_found': 0,
            'issue': '年齡驗證失敗',
            'solution': '需要手動處理年齡驗證'
        }
    
    def diagnose_dcard_crawler(self, candidate_name="羅智強"):
        """診斷Dcard爬蟲問題"""
        print("🔍 診斷Dcard爬蟲...")
        
        try:
            # 測試Dcard API
            api_url = "https://www.dcard.tw/service/api/v2/posts/search"
            
            params = {
                'query': candidate_name,
                'limit': 10
            }
            
            response = requests.get(api_url, headers=self.headers, params=params, timeout=10)
            
            print(f"Dcard API狀態: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ Dcard API正常，找到文章數量: {len(data)}")
                    
                    return {
                        'status': 'success',
                        'posts_found': len(data),
                        'issue': None
                    }
                    
                except json.JSONDecodeError:
                    print("⚠️ Dcard API返回非JSON格式")
                    return {
                        'status': 'json_error',
                        'posts_found': 0,
                        'issue': 'API返回格式錯誤'
                    }
            
            elif response.status_code == 429:
                print("⚠️ Dcard API請求頻率限制")
                return {
                    'status': 'rate_limited',
                    'posts_found': 0,
                    'issue': 'API請求頻率過高',
                    'solution': '需要降低請求頻率或使用代理'
                }
            
            else:
                print(f"❌ Dcard API錯誤: {response.status_code}")
                return {
                    'status': 'api_error',
                    'posts_found': 0,
                    'issue': f'API HTTP {response.status_code}'
                }
                
        except Exception as e:
            print(f"❌ Dcard爬蟲錯誤: {e}")
            return {
                'status': 'error',
                'posts_found': 0,
                'issue': str(e)
            }
    
    def diagnose_news_crawler(self, candidate_name="羅智強"):
        """診斷新聞爬蟲問題"""
        print("🔍 診斷新聞爬蟲...")
        
        news_sources = [
            ("聯合新聞網", f"https://udn.com/search/result/2/{candidate_name}"),
            ("中時新聞網", f"https://www.chinatimes.com/search/{candidate_name}"),
            ("自由時報", f"https://search.ltn.com.tw/list?keyword={candidate_name}")
        ]
        
        results = {}
        
        for source_name, url in news_sources:
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # 簡單檢查是否有內容
                    if len(soup.text) > 1000:  # 基本內容檢查
                        print(f"✅ {source_name} 可以正常訪問")
                        results[source_name] = {
                            'status': 'success',
                            'issue': None
                        }
                    else:
                        print(f"⚠️ {source_name} 內容異常")
                        results[source_name] = {
                            'status': 'content_error',
                            'issue': '頁面內容異常'
                        }
                else:
                    print(f"❌ {source_name} HTTP錯誤: {response.status_code}")
                    results[source_name] = {
                        'status': 'http_error',
                        'issue': f'HTTP {response.status_code}'
                    }
                    
            except Exception as e:
                print(f"❌ {source_name} 錯誤: {e}")
                results[source_name] = {
                    'status': 'error',
                    'issue': str(e)
                }
        
        return results
    
    def generate_diagnostic_report(self):
        """生成診斷報告"""
        print("\n" + "="*50)
        print("📋 爬蟲診斷報告")
        print("="*50)
        
        candidate_name = "羅智強"
        
        # 診斷PTT
        ptt_result = self.diagnose_ptt_crawler(candidate_name)
        print(f"\n🔍 PTT診斷結果:")
        print(f"   狀態: {ptt_result['status']}")
        print(f"   找到文章: {ptt_result['posts_found']}")
        if ptt_result['issue']:
            print(f"   問題: {ptt_result['issue']}")
        if 'solution' in ptt_result:
            print(f"   解決方案: {ptt_result['solution']}")
        
        # 診斷Dcard
        dcard_result = self.diagnose_dcard_crawler(candidate_name)
        print(f"\n🔍 Dcard診斷結果:")
        print(f"   狀態: {dcard_result['status']}")
        print(f"   找到文章: {dcard_result['posts_found']}")
        if dcard_result['issue']:
            print(f"   問題: {dcard_result['issue']}")
        if 'solution' in dcard_result:
            print(f"   解決方案: {dcard_result['solution']}")
        
        # 診斷新聞
        news_results = self.diagnose_news_crawler(candidate_name)
        print(f"\n🔍 新聞爬蟲診斷結果:")
        for source, result in news_results.items():
            print(f"   {source}: {result['status']}")
            if result['issue']:
                print(f"      問題: {result['issue']}")
        
        # 總結和建議
        print(f"\n💡 總結和建議:")
        
        if ptt_result['status'] in ['success', 'success_with_verification']:
            print("   ✅ PTT爬蟲可以修復")
        else:
            print("   ❌ PTT爬蟲需要進一步處理")
        
        if dcard_result['status'] == 'success':
            print("   ✅ Dcard爬蟲正常")
        else:
            print("   ❌ Dcard爬蟲需要修復")
        
        working_news = sum(1 for result in news_results.values() if result['status'] == 'success')
        print(f"   📰 新聞爬蟲: {working_news}/{len(news_results)} 個來源正常")
        
        return {
            'ptt': ptt_result,
            'dcard': dcard_result,
            'news': news_results,
            'timestamp': datetime.now().isoformat()
        }

if __name__ == "__main__":
    diagnostics = CrawlerDiagnostics()
    report = diagnostics.generate_diagnostic_report()
    
    # 保存診斷報告
    with open('crawler_diagnostic_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 診斷報告已保存到: crawler_diagnostic_report.json")

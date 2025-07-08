#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修復dashboard.py中的智能引號
"""

def fix_smart_quotes():
    """修復智能引號"""
    print('開始修復智能引號...')
    
    # 讀取文件
    with open('dashboard.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 計算修復前的智能引號數量
    import re
    smart_quotes_count = len(re.findall(r'[""'']', content))
    print(f'修復前智能引號數量: {smart_quotes_count}')
    
    # 替換所有智能引號
    content = content.replace('"', '"')  # 左智能雙引號
    content = content.replace('"', '"')  # 右智能雙引號
    content = content.replace(''', "'")  # 左智能單引號
    content = content.replace(''', "'")  # 右智能單引號
    
    # 計算修復後的智能引號數量
    remaining_count = len(re.findall(r'[""'']', content))
    print(f'修復後剩餘智能引號數量: {remaining_count}')
    
    # 寫回文件
    with open('dashboard.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f'✅ 成功修復 {smart_quotes_count - remaining_count} 個智能引號')
    
    # 驗證語法
    try:
        import ast
        ast.parse(content)
        print('✅ 語法檢查通過')
        return True
    except Exception as e:
        print(f'❌ 語法檢查失敗: {e}')
        return False

if __name__ == "__main__":
    success = fix_smart_quotes()
    if success:
        print('🎉 智能引號修復完成，文件語法正確！')
    else:
        print('❌ 修復失敗，請檢查文件')

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Method definition content extractor using javalang
"""

import javalang
from utils import read_file_with_encoding


def extract_method_content(file_path: str, method_name: str):
    """特定メソッドの内容を完全抽出"""
    try:
        content = read_file_with_encoding(file_path)
        tree = javalang.parse.parse(content)
        lines = content.split('\n')
        
        for _, node in tree.filter(javalang.tree.MethodDeclaration):
            if node.name == method_name:
                result = {
                    'method_name': node.name,
                    'file_path': file_path,
                    'line_start': node.position.line if hasattr(node, 'position') and node.position else 0,
                    'return_type': node.return_type.name if node.return_type else 'void',
                    'modifiers': [str(m) for m in node.modifiers] if node.modifiers else [],
                    'parameters': [],
                    'throws': [],
                    'annotations': [],
                    'javadoc': None,
                    'body_source': None,
                    'method_calls_inside': [],
                    'local_variables': []
                }
                
                # パラメータ詳細
                if node.parameters:
                    for param in node.parameters:
                        param_info = {
                            'name': param.name,
                            'type': param.type.name if hasattr(param.type, 'name') else str(param.type),
                            'modifiers': [str(m) for m in param.modifiers] if param.modifiers else []
                        }
                        result['parameters'].append(param_info)
                
                # throws句
                if hasattr(node, 'throws') and node.throws:
                    result['throws'] = [str(t) for t in node.throws]
                
                # アノテーション
                if hasattr(node, 'annotations') and node.annotations:
                    for ann in node.annotations:
                        result['annotations'].append({
                            'name': ann.name,
                            'element': str(ann.element) if hasattr(ann, 'element') and ann.element else None
                        })
                
                # メソッドボディのソースコード抽出
                if hasattr(node, 'position') and node.position:
                    start_line = node.position.line - 1  # 0-based
                    
                    # メソッド終了行を推定（簡易版）
                    brace_count = 0
                    end_line = start_line
                    in_method = False
                    
                    for i in range(start_line, len(lines)):
                        line = lines[i]
                        if '{' in line:
                            brace_count += line.count('{')
                            in_method = True
                        if '}' in line:
                            brace_count -= line.count('}')
                            if in_method and brace_count == 0:
                                end_line = i
                                break
                    
                    # ソースコード抽出
                    method_source_lines = lines[start_line:end_line + 1]
                    result['body_source'] = '\n'.join(method_source_lines)
                    result['line_end'] = end_line + 1  # 1-based
                
                # メソッド内のメソッド呼び出しを抽出
                if node.body:
                    method_calls = []
                    # node.bodyからメソッド呼び出しを抽出（簡易版）
                    try:
                        for _, call_node in tree.filter(javalang.tree.MethodInvocation):
                            # メソッド内にあるかチェック（簡易版）
                            call_info = {
                                'method': call_node.member,
                                'qualifier': None
                            }
                            
                            if hasattr(call_node, 'qualifier') and call_node.qualifier:
                                if hasattr(call_node.qualifier, 'name'):
                                    call_info['qualifier'] = call_node.qualifier.name
                            
                            method_calls.append(call_info)
                    except:
                        pass
                    
                    result['method_calls_inside'] = method_calls[:5]  # 最初の5個のみ
                
                # ローカル変数は簡略化
                result['local_variables'] = []  # 今回は省略
                
                return result
        
        return None
    
    except Exception as e:
        print(f"メソッド内容抽出エラー: {e}")
        return None


def display_method_details(method_info):
    """メソッド詳細情報を見やすく表示"""
    if not method_info:
        print("メソッドが見つかりませんでした")
        return
    
    print(f"🔍 メソッド詳細: {method_info['method_name']}")
    print(f"📄 ファイル: {method_info['file_path']}")
    print(f"📍 行番号: {method_info['line_start']}-{method_info.get('line_end', '?')}")
    print(f"🔧 修飾子: {', '.join(method_info['modifiers'])}")
    print(f"↩️  戻り値: {method_info['return_type']}")
    
    # パラメータ
    if method_info['parameters']:
        print("📥 パラメータ:")
        for param in method_info['parameters']:
            print(f"   - {param['type']} {param['name']}")
    
    # アノテーション
    if method_info['annotations']:
        print("🏷️  アノテーション:")
        for ann in method_info['annotations']:
            print(f"   - @{ann['name']}")
    
    # throws句
    if method_info['throws']:
        print(f"⚠️  例外: {', '.join(method_info['throws'])}")
    
    # メソッド内のメソッド呼び出し
    if method_info['method_calls_inside']:
        print("📞 内部メソッド呼び出し:")
        for call in method_info['method_calls_inside']:
            qualifier = call['qualifier'] or '?'
            print(f"   - {qualifier}.{call['method']}()")
    
    # ローカル変数
    if method_info['local_variables']:
        print("📦 ローカル変数:")
        for var in method_info['local_variables']:
            print(f"   - {var['type']} {var['name']}")
    
    # ソースコード
    if method_info['body_source']:
        print("\n💻 ソースコード:")
        print("=" * 50)
        print(method_info['body_source'])
        print("=" * 50)


if __name__ == "__main__":
    # テスト
    file_path = "test_java_src/com/example/util/DataAccessUtil.java"
    method_name = "checkUserExists"
    
    method_info = extract_method_content(file_path, method_name)
    display_method_details(method_info)
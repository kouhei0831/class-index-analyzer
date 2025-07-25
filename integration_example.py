#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
メイン解析システムと依存関係グラフの統合例
"""

from main import extract_method_calls
from method_finder import find_method_definition_in_project
from method_detail_extractor import extract_method_content
from dependency_graph import create_dependency_graph, analyze_graph_metrics, find_critical_methods, generate_dependency_report
from utils import read_file_with_encoding


def analyze_project_dependencies(file_path: str, class_indexer):
    """プロジェクト全体の依存関係を分析"""
    
    print(f"🔍 プロジェクト依存関係分析: {file_path}")
    
    # Step 1: ファイル内のメソッド呼び出しを抽出
    content = read_file_with_encoding(file_path)
    method_calls = extract_method_calls(content, [])
    
    # メソッド名セットを作成
    used_methods = set()
    for call in method_calls:
        method_name = call.get('method', '')
        if method_name and method_name != 'constructor':
            used_methods.add(method_name)
    
    print(f"   📋 使用メソッド: {len(used_methods)}種類")
    
    # Step 2: 各メソッドの定義を検索
    method_definitions = {}
    method_call_relations = {}
    
    for method_name in list(used_methods)[:10]:  # 最初の10個を詳細分析
        # 定義を検索
        definitions = find_method_definition_in_project(method_name, class_indexer)
        
        if definitions:
            # 最初の定義を使用
            first_def = definitions[0]
            method_key = f"{first_def['class_name']}.{method_name}"
            method_definitions[method_key] = first_def
            
            # メソッドの詳細内容を取得
            detail = extract_method_content(first_def['file_path'], method_name)
            if detail and detail.get('method_calls_inside'):
                # 内部で呼び出すメソッドを記録
                internal_calls = []
                for call in detail['method_calls_inside']:
                    if call['method'] != method_name:  # 自己再帰を除外
                        internal_calls.append(call['method'])
                
                method_call_relations[method_key] = internal_calls
    
    print(f"   📖 定義発見: {len(method_definitions)}個")
    
    # Step 3: 依存関係グラフを作成
    G = create_dependency_graph(method_definitions, method_call_relations)
    
    # Step 4: 分析実行
    metrics = analyze_graph_metrics(G)
    critical = find_critical_methods(G)
    
    # Step 5: レポート生成
    generate_dependency_report(G, metrics, critical)
    
    return G, metrics, critical


if __name__ == "__main__":
    print("🧪 統合依存関係分析のテスト")
    
    # 実際のファイルでテスト
    test_file = "test_java_src/com/example/util/DataAccessUtil.java"
    
    # クラスインデックスを簡易作成
    class MockIndexer:
        def __init__(self):
            self.class_index = {}
    
    mock_indexer = MockIndexer()
    
    try:
        G, metrics, critical = analyze_project_dependencies(test_file, mock_indexer)
        print("✅ 統合分析完了")
    except Exception as e:
        print(f"❌ エラー: {e}")
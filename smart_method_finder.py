#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart method finder using import context
"""

def find_method_definition_with_imports(method_name: str, imports: list, class_indexer):
    """
    importコンテキストを使ったスマートなメソッド定義検索
    
    Args:
        method_name: 検索対象のメソッド名
        imports: 起点ファイルのimport文リスト
        class_indexer: マルチソースクラスインデックス
    """
    candidates = []
    
    # Step 1: importされたクラス名を抽出
    imported_classes = []
    for import_statement in imports:
        if import_statement.startswith('java.'):
            continue  # JDK標準ライブラリは除外
        
        # com.example.mapper.UserEntityManager → UserEntityManager
        class_name = import_statement.split('.')[-1]
        imported_classes.append({
            'class_name': class_name,
            'full_name': import_statement
        })
    
    # Step 2: importされたクラスからのみメソッドを検索
    for imported_class in imported_classes:
        class_name = imported_class['class_name']
        
        # クラス情報を取得
        class_info = class_indexer.get_class_info(class_name)
        if class_info and hasattr(class_info, 'methods') and class_info.methods:
            
            # メソッドが存在するかチェック
            if method_name in class_info.methods:
                method_info = class_info.methods[method_name]
                
                candidate = {
                    'method_name': method_name,
                    'class_name': class_name,
                    'full_class_name': imported_class['full_name'],
                    'file_path': class_info.file_path,
                    'return_type': method_info.return_type,
                    'parameters': method_info.parameters,
                    'confidence': 'HIGH'  # importされているので高信頼度
                }
                candidates.append(candidate)
    
    # Step 3: 結果の整理
    return candidates


def extract_method_source_from_file(file_path: str, method_name: str):
    """ファイルから特定メソッドのソースコードを抽出"""
    try:
        from utils import read_file_with_encoding
        import javalang
        
        content = read_file_with_encoding(file_path)
        tree = javalang.parse.parse(content)
        lines = content.split('\n')
        
        for _, node in tree.filter(javalang.tree.MethodDeclaration):
            if node.name == method_name:
                # メソッドの開始・終了行を特定
                start_line = node.position.line - 1 if hasattr(node, 'position') and node.position else 0
                
                # 簡易的な終了行推定
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
                source_lines = lines[start_line:end_line + 1]
                return {
                    'source_code': '\n'.join(source_lines),
                    'start_line': start_line + 1,
                    'end_line': end_line + 1,
                    'return_type': node.return_type.name if node.return_type else 'void',
                    'parameters': [{'name': p.name, 'type': p.type.name if hasattr(p.type, 'name') else str(p.type)} 
                                  for p in node.parameters] if node.parameters else [],
                    'modifiers': [str(m) for m in node.modifiers] if node.modifiers else []
                }
        
        return None
    
    except Exception as e:
        return None


def display_method_definition(method_name: str, candidates: list, show_source: bool = False):
    """メソッド定義の結果を表示"""
    
    if not candidates:
        print(f"❌ メソッド定義未発見: {method_name}()")
        return
    
    if len(candidates) == 1:
        candidate = candidates[0]
        print(f"🎯 メソッド定義を一意に特定:")
        print(f"   📍 {candidate['class_name']}.{method_name}()")
        print(f"   📄 ファイル: {candidate['file_path']}")
        print(f"   ↩️  戻り値: {candidate['return_type']}")
        print(f"   📥 パラメータ: {len(candidate['parameters'])}個")
        
        if show_source:
            # ソースコードを表示
            source_info = extract_method_source_from_file(candidate['file_path'], method_name)
            if source_info:
                print(f"   📍 行番号: {source_info['start_line']}-{source_info['end_line']}")
                print("\n💻 ソースコード:")
                print("=" * 50)
                print(source_info['source_code'])
                print("=" * 50)
        
    else:
        print(f"⚠️  複数のメソッド定義候補: {len(candidates)}個")
        for i, candidate in enumerate(candidates, 1):
            print(f"   {i}. {candidate['class_name']}.{method_name}()")
            print(f"      📄 {candidate['file_path']}")
            print(f"      ↩️  {candidate['return_type']}")


def batch_find_method_definitions(method_names: list, imports: list, class_indexer, show_source: bool = False):
    """複数メソッドの定義を一括検索"""
    
    print(f"🔍 一括メソッド定義検索: {len(method_names)}個のメソッド")
    print(f"📥 検索範囲: import済み{len([imp for imp in imports if not imp.startswith('java.')])}クラス")
    print()
    
    results = {}
    
    for method_name in method_names:
        print(f"🔎 {method_name}()を検索中...")
        candidates = find_method_definition_with_imports(method_name, imports, class_indexer)
        results[method_name] = candidates
        
        display_method_definition(method_name, candidates, show_source)
        print()
    
    # サマリー
    found_count = len([name for name, candidates in results.items() if candidates])
    unique_count = len([name for name, candidates in results.items() if len(candidates) == 1])
    
    print(f"📊 検索結果サマリー:")
    print(f"   発見: {found_count}/{len(method_names)}個")
    print(f"   一意特定: {unique_count}/{len(method_names)}個")
    print(f"   特定率: {unique_count/len(method_names)*100:.1f}%")
    
    return results


def demonstrate_smart_search():
    """スマート検索のデモンストレーション"""
    
    # サンプルデータ
    sample_imports = [
        'com.example.mapper.UserEntityManager',
        'com.example.ormapper.UserORMapper', 
        'com.example.entity.UserEntity',
        'java.util.List',
        'java.util.Map'
    ]
    
    sample_method_name = 'find'
    
    print("🧪 スマートメソッド検索デモ")
    print("=" * 50)
    
    print(f"📋 検索メソッド: {sample_method_name}")
    print(f"📥 importコンテキスト:")
    for imp in sample_imports:
        print(f"   - {imp}")
    
    print("\n従来の検索:")
    print(f"   全プロジェクトから'{sample_method_name}'を検索")
    print(f"   → 数十個の候補がヒット（曖昧）")
    
    print("\nスマート検索:")
    print(f"   importされた5クラスからのみ'{sample_method_name}'を検索")
    print(f"   → UserEntityManager.find(), UserORMapper.find() のみヒット")
    print(f"   → 大幅に絞り込み成功！")


if __name__ == "__main__":
    demonstrate_smart_search()
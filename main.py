#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Class Index Analyzer - Main Entry Point
クラスインデックスを活用した高度な解析ツール
"""

import argparse
import os
import sys
import json
from pathlib import Path
from datetime import datetime

# クラスインデックス機能
from class_indexer import MultiSourceClassIndexer
from utils import load_settings_and_resolve_paths


def main():
    """メイン実行関数"""
    print("🚀 特定Javaファイルから再帰的探索した特化クラスインデックス")
    print("=" * 60)
    
    # コマンドライン引数の解析
    args = parse_arguments()
    
    try:
        # Javaファイルの検証
        if not args.java_file.endswith('.java'):
            raise Exception("Javaファイル（.java）を指定してください")
        
        if not os.path.exists(args.java_file):
            raise Exception(f"ファイルが見つかりません: {args.java_file}")
        
        # ファイル名からクラス名を推定
        file_name = os.path.basename(args.java_file)
        class_name = file_name.replace('.java', '')
        
        print(f"\n📄 起点Javaファイル: {args.java_file}")
        print(f"🎯 起点クラス名: {class_name}")
        print(f"📏 最大探索深度: {args.max_depth}")
        
        # Step 1: 基本クラスインデックス構築
        print("\n📚 Step 1: 基本クラスインデックス構築")
        base_indexer = build_base_class_index(args)
        
        # Step 2: 特化クラスインデックス構築
        print("\n🔍 Step 2: 特化クラスインデックス構築")
        specialized_index = build_specialized_index(base_indexer, class_name, args.max_depth, args.show_method_source)
        
        # Step 3: 結果表示
        print("\n📊 Step 3: 結果表示")
        display_specialized_index(specialized_index)
        
        print("\n✅ 特化インデックス構築完了")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  処理が中断されました")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        sys.exit(1)


def parse_arguments():
    """コマンドライン引数の解析"""
    parser = argparse.ArgumentParser(
        description="特定Javaファイルから再帰的に探索した特化クラスインデックス",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 特定のJavaファイルから再帰的インデックス構築
  python main.py DataAccessUtil.java --settings test_settings.json
  
  # メソッド定義の詳細検索（ソースコード表示）
  python main.py DataAccessUtil.java --settings test_settings.json --show-method-source
        """
    )
    
    parser.add_argument(
        'java_file',
        help='解析対象のJavaファイル'
    )
    
    parser.add_argument(
        '--settings',
        required=True,
        help='設定ファイルパス'
    )
    
    parser.add_argument(
        '--max-depth',
        type=int,
        default=5,
        help='再帰探索の最大深度（デフォルト: 5）'
    )
    
    parser.add_argument(
        '--show-method-source',
        action='store_true',
        help='メソッド定義のソースコードも表示'
    )
    
    return parser.parse_args()


def build_base_class_index(args) -> MultiSourceClassIndexer:
    """クラスインデックスを構築"""
    
    # 設定ファイルから複数ソースパスを取得
    source_paths = []
    
    if args.settings and os.path.exists(args.settings):
        print(f"📄 設定ファイル読み込み: {args.settings}")
        
        try:
            resolved_source_paths, jar_paths = load_settings_and_resolve_paths(args.settings)
            
            if resolved_source_paths:
                source_paths = resolved_source_paths
                print(f"📁 設定ファイルから{len(source_paths)}個のソースパス解決済み")
                for path in source_paths:
                    print(f"   ✅ {path}")
            else:
                print("⚠️  設定ファイルからソースパスを取得できませんでした")
            
        except Exception as e:
            print(f"⚠️  設定ファイル読み込みエラー: {e}")
            pass
    elif args.settings:
        print(f"❌ 設定ファイルが見つかりません: {args.settings}")
        pass  # 設定ファイルが見つからない場合はフォールバックを使用
    
    # フォールバック：Javaファイルの親ディレクトリを使用
    if not source_paths:
        parent_dir = os.path.dirname(args.java_file)
        if parent_dir:
            source_paths = [parent_dir]
            print(f"📁 Javaファイルの親ディレクトリを使用: {parent_dir}")
        else:
            source_paths = ['.']
            print(f"📁 現在のディレクトリを使用")
    
    # クラスインデックス構築
    print("🔨 クラスインデックス構築開始...")
    
    indexer = MultiSourceClassIndexer()
    
    # キャッシュ設定（デフォルトで有効）
    indexer.cache_enabled = True
    
    # 存在するソースパスのみフィルタ
    valid_source_paths = []
    for source_path in source_paths:
        if os.path.exists(source_path):
            valid_source_paths.append(source_path)
            print(f"   📦 有効なソースパス: {source_path}")
        else:
            print(f"⚠️  ソースパスが存在しません: {source_path}")
    
    if not valid_source_paths:
        raise Exception("有効なソースパスが見つかりませんでした")
    
    # クラスインデックス構築（一括）
    print("   🔨 インデックス構築実行中...")
    indexer.class_index = indexer.build_class_index(valid_source_paths)
    
    total_classes = len(indexer.class_index)
    print(f"✅ クラスインデックス構築完了: {total_classes}クラス登録")
    
    return indexer


def build_specialized_index(base_indexer: MultiSourceClassIndexer, start_class: str, max_depth: int, show_method_source: bool = False) -> dict:
    """特定クラスから再帰的に探索した特化インデックスを構築（メソッド単位）"""
    
    specialized_index = {}
    visited_methods = set()  # メソッド単位の訪問管理
    
    print(f"   🎯 起点クラス: {start_class}")
    print(f"   🔄 メソッド単位の再帰的探索開始...")
    
    # 起点クラスのファイル情報を取得
    start_class_info = base_indexer.get_class_info(start_class)
    if not start_class_info:
        print(f"   ❌ 起点クラスが見つかりません: {start_class}")
        return specialized_index
    
    # 起点ファイルの全メソッドを探索対象とする
    _build_recursive_from_start_file(base_indexer, start_class_info, 0, max_depth, visited_methods, specialized_index, show_method_source)
    
    print(f"   📦 特化インデックス構築完了: {len(specialized_index)}クラス")
    
    return specialized_index


def _build_recursive_from_start_file(base_indexer: MultiSourceClassIndexer, start_class_info, current_depth: int, max_depth: int, visited_methods: set, specialized_index: dict, show_method_source: bool = False):
    """起点ファイルの全メソッドから再帰的探索を開始"""
    
    if current_depth >= max_depth:
        return
    
    # 起点クラスを特化インデックスに追加
    start_class = start_class_info.class_name
    if start_class not in specialized_index:
        specialized_index[start_class] = {
            'class_name': start_class_info.class_name,
            'file_path': start_class_info.file_path,
            'package_name': start_class_info.package_name,
            'methods': dict(start_class_info.methods) if start_class_info.methods else {},
            'imports': list(start_class_info.imports) if start_class_info.imports else [],
            'depth': current_depth,
            'used_methods': [],  # 起点ファイルでは全メソッドが対象
            'dependencies': []
        }
    
    print(f"   {'  ' * current_depth}├─ {start_class} (深度: {current_depth}) [起点ファイル - 全メソッド探査]")
    
    # 起点ファイルの内容を解析
    try:
        from utils import read_file_with_encoding
        file_content = read_file_with_encoding(start_class_info.file_path)
        
        # ファイル全体からメソッド呼び出しを抽出
        method_calls = extract_method_calls(file_content, start_class_info.imports)
        
        # メソッド名のリストを作成（重複除去）
        method_names = set()
        for call in method_calls:
            method_name = call.get('method', '')
            if method_name and method_name != 'constructor':
                method_names.add(method_name)
        
        print(f"   {'  ' * current_depth}  📋 使用メソッド名: {len(method_names)}種類")
        sorted_methods = sorted(method_names)[:10]  # 最初の10個をアルファベット順
        print(f"   {'  ' * current_depth}    {', '.join(sorted_methods)}")
        if len(method_names) > 10:
            print(f"   {'  ' * current_depth}    ... 他{len(method_names) - 10}個")
        
        # 🆕 メソッド定義検索オプション
        if len(method_names) <= 25:  # 詳細検索実行
            from smart_method_finder import batch_find_method_definitions
            print(f"   {'  ' * current_depth}  🔍 メソッド定義検索を実行中...")
            results = batch_find_method_definitions(list(method_names), start_class_info.imports, base_indexer, show_method_source)
            
            # 一意特定できたメソッドの数を表示
            unique_count = len([name for name, candidates in results.items() if len(candidates) == 1])
            if unique_count > 0:
                print(f"   {'  ' * current_depth}  ✅ {unique_count}/{len(method_names)}個のメソッド定義を一意特定")
        
        resolved_calls = resolve_method_calls(base_indexer, method_calls, start_class_info.imports)
        
        # 解決できた依存関係を探索
        for call in resolved_calls:
            if call.get('resolved', False):
                target_class_name = call['target_class']
                target_method_name = call['target_method']
                method_key = f"{target_class_name}.{target_method_name}"
                
                # 既に訪問済みのメソッドはスキップ
                if method_key in visited_methods:
                    continue
                
                visited_methods.add(method_key)
                specialized_index[start_class]['dependencies'].append(method_key)
                
                # 依存メソッドを再帰的に探索
                _build_recursive_from_specific_method(base_indexer, target_class_name, target_method_name, current_depth + 1, max_depth, visited_methods, specialized_index)
    
    except Exception as e:
        print(f"   {'  ' * current_depth}  ⚠️ ファイル読み込みエラー: {e}")


def _build_recursive_from_specific_method(base_indexer: MultiSourceClassIndexer, target_class: str, target_method: str, current_depth: int, max_depth: int, visited_methods: set, specialized_index: dict):
    """特定メソッドから再帰的に依存関係を探索"""
    
    if current_depth >= max_depth:
        return
    
    # クラス情報を取得
    class_info = base_indexer.get_class_info(target_class)
    if not class_info:
        return
    
    # 特化インデックスにクラスを追加（初回のみ）
    if target_class not in specialized_index:
        specialized_index[target_class] = {
            'class_name': class_info.class_name,
            'file_path': class_info.file_path,
            'package_name': class_info.package_name,
            'methods': dict(class_info.methods) if class_info.methods else {},
            'imports': list(class_info.imports) if class_info.imports else [],
            'depth': current_depth,
            'used_methods': [],  # 使用されたメソッドのみ記録
            'dependencies': []
        }
    
    # 使用メソッドを記録
    if target_method not in specialized_index[target_class]['used_methods']:
        specialized_index[target_class]['used_methods'].append(target_method)
    
    print(f"   {'  ' * current_depth}├─ {target_class}.{target_method}() (深度: {current_depth})")
    
    # 特定メソッドの内容のみを解析
    try:
        from utils import read_file_with_encoding
        file_content = read_file_with_encoding(class_info.file_path)
        
        # 特定メソッド内からのみメソッド呼び出しを抽出
        method_calls = extract_method_calls_from_specific_method(file_content, target_method, class_info.imports)
        resolved_calls = resolve_method_calls(base_indexer, method_calls, class_info.imports)
        
        # 解決できた依存関係を再帰的に探索
        for call in resolved_calls:
            if call.get('resolved', False):
                next_class = call['target_class']
                next_method = call['target_method']
                method_key = f"{next_class}.{next_method}"
                
                # 循環参照チェック
                if method_key in visited_methods:
                    continue
                
                visited_methods.add(method_key)
                specialized_index[target_class]['dependencies'].append(method_key)
                
                # 再帰的に探索
                _build_recursive_from_specific_method(base_indexer, next_class, next_method, current_depth + 1, max_depth, visited_methods, specialized_index)
    
    except Exception as e:
        print(f"   {'  ' * current_depth}  ⚠️ メソッド解析エラー: {e}")


def display_specialized_index(specialized_index: dict):
    """特化インデックスの内容を表示（メソッド単位版）"""
    
    if not specialized_index:
        print("   ⚠️ 特化インデックスが空です")
        return
    
    print(f"   📦 特化インデックス内容: {len(specialized_index)}クラス")
    print()
    
    # 深度順にソート
    sorted_classes = sorted(specialized_index.items(), key=lambda x: x[1]['depth'])
    
    for class_name, info in sorted_classes:
        indent = "   " + "  " * info['depth']
        print(f"{indent}📍 {class_name} (深度: {info['depth']})")
        print(f"{indent}   📄 {info['file_path']}")
        print(f"{indent}   📦 {info['package_name']}")
        
        # 使用メソッド表示（起点ファイルは全メソッド、依存ファイルは使用メソッドのみ）
        if info['depth'] == 0:
            print(f"{indent}   🔧 全メソッド: {len(info['methods'])}個")
        else:
            used_methods = info.get('used_methods', [])
            print(f"{indent}   🎯 使用メソッド: {len(used_methods)}個 ({', '.join(used_methods)})")
        
        print(f"{indent}   📥 インポート: {len(info['imports'])}個")
        
        if info['dependencies']:
            print(f"{indent}   🔗 メソッド依存: {len(info['dependencies'])}個")
            # 依存メソッドをクラス別にグループ化して表示
            dep_by_class = {}
            for dep in info['dependencies']:
                if '.' in dep:
                    cls, method = dep.split('.', 1)
                    if cls not in dep_by_class:
                        dep_by_class[cls] = []
                    dep_by_class[cls].append(method)
            
            for dep_class, methods in dep_by_class.items():
                print(f"{indent}     → {dep_class}: {', '.join(methods)}")
        
        print()
    
    # サマリー
    depth_counts = {}
    method_counts = {}
    for info in specialized_index.values():
        depth = info['depth']
        depth_counts[depth] = depth_counts.get(depth, 0) + 1
        
        if depth == 0:
            method_counts[depth] = len(info['methods'])  # 起点は全メソッド
        else:
            method_counts[depth] = method_counts.get(depth, 0) + len(info.get('used_methods', []))
    
    print("   📊 深度別クラス数:")
    for depth in sorted(depth_counts.keys()):
        method_count = method_counts.get(depth, 0)
        if depth == 0:
            print(f"     深度 {depth}: {depth_counts[depth]}クラス ({method_count}メソッド - 起点)")
        else:
            print(f"     深度 {depth}: {depth_counts[depth]}クラス ({method_count}使用メソッド)")


# ここから下は既存のメソッド抽出・解決関数を再利用


def extract_method_calls_from_specific_method(file_content: str, target_method: str, imports: list) -> list:
    """特定メソッド内からのみメソッド呼び出しを抽出"""
    import re
    
    # Step 1: 特定メソッドの範囲を特定
    method_body = extract_method_body(file_content, target_method)
    if not method_body:
        return []
    
    # Step 2: そのメソッド内のメソッド呼び出しを抽出
    return extract_method_calls(method_body, imports)


def extract_method_body(file_content: str, method_name: str) -> str:
    """特定メソッドのボディ部分を抽出"""
    import re
    
    # メソッド定義の開始を探す
    # パターン: public/private/static などのキーワードに続くメソッド名
    method_pattern = rf'(public|private|protected|static|\s)+.*?\b{re.escape(method_name)}\s*\([^)]*\)\s*\{{'
    
    lines = file_content.split('\n')
    method_start_line = -1
    
    # メソッド開始行を見つける
    for i, line in enumerate(lines):
        if re.search(method_pattern, line):
            method_start_line = i
            break
    
    if method_start_line == -1:
        return ""
    
    # 中括弧のバランスを取ってメソッド終了を見つける
    brace_count = 0
    method_end_line = -1
    started = False
    
    for i in range(method_start_line, len(lines)):
        line = lines[i]
        
        # 文字列リテラル内の中括弧は無視（簡易版）
        line_without_strings = re.sub(r'"[^"]*"', '""', line)
        
        for char in line_without_strings:
            if char == '{':
                brace_count += 1
                started = True
            elif char == '}':
                brace_count -= 1
                
                if started and brace_count == 0:
                    method_end_line = i
                    break
        
        if method_end_line != -1:
            break
    
    if method_end_line == -1:
        return ""
    
    # メソッドボディを抽出
    method_lines = lines[method_start_line:method_end_line + 1]
    return '\n'.join(method_lines)


def extract_method_calls(file_content: str, imports: list) -> list:
    """javalangを使ってファイル内容からメソッド呼び出しを抽出"""
    import javalang
    
    method_calls = []
    
    try:
        # JavaコードをASTに変換
        tree = javalang.parse.parse(file_content)
        
        # ASTを走査してメソッド呼び出しを抽出
        for _, node in tree.filter(javalang.tree.MethodInvocation):
            if hasattr(node, 'qualifier') and node.qualifier:
                # object.method() 形式
                obj_name = None
                
                # 様々な修飾子のタイプを処理
                if hasattr(node.qualifier, 'name'):
                    # 単純な変数参照: userEntityManager.find()
                    obj_name = node.qualifier.name
                elif hasattr(node.qualifier, 'member'):
                    # フィールドアクセス: this.manager.find()
                    obj_name = node.qualifier.member
                elif hasattr(node.qualifier, 'type'):
                    # 型参照: ClassName.staticMethod()
                    if hasattr(node.qualifier.type, 'name'):
                        obj_name = node.qualifier.type.name
                
                if obj_name:
                    method_name = node.member
                    method_calls.append({
                        'type': 'instance_call',
                        'object': obj_name,
                        'method': method_name,
                        'pattern': f"{obj_name}.{method_name}()"
                    })
                else:
                    # 解析できない修飾子の場合
                    method_name = node.member
                    method_calls.append({
                        'type': 'unknown_call',
                        'method': method_name,
                        'pattern': f"?.{method_name}()",
                        'qualifier': str(type(node.qualifier))
                    })
            else:
                # 直接メソッド呼び出し this.method() or method()
                method_name = node.member
                method_calls.append({
                    'type': 'local_call',
                    'method': method_name,
                    'pattern': f"{method_name}()"
                })
        
        # コンストラクタ呼び出しを抽出
        for _, node in tree.filter(javalang.tree.ClassCreator):
            class_name = node.type.name
            method_calls.append({
                'type': 'constructor_call',
                'class': class_name,
                'method': 'constructor',
                'pattern': f"new {class_name}()"
            })
    
    except Exception as e:
        print(f"      ⚠️ javalang解析エラー、フォールバック実行: {e}")
        # フォールバック：正規表現ベース
        return extract_method_calls_regex_fallback(file_content, imports)
    
    return method_calls


def extract_method_calls_regex_fallback(file_content: str, imports: list) -> list:
    """正規表現ベースのフォールバック実装"""
    import re
    
    method_calls = []
    
    # パターン1: object.method() 形式
    pattern1 = re.compile(r'(\w+)\.(\w+)\s*\(')
    matches1 = pattern1.findall(file_content)
    
    for obj_name, method_name in matches1:
        method_calls.append({
            'type': 'instance_call',
            'object': obj_name,
            'method': method_name,
            'pattern': f"{obj_name}.{method_name}()"
        })
    
    # パターン2: new ClassName() 形式
    pattern2 = re.compile(r'new\s+(\w+)\s*\(')
    matches2 = pattern2.findall(file_content)
    
    for class_name in matches2:
        method_calls.append({
            'type': 'constructor_call',
            'class': class_name,
            'method': 'constructor',
            'pattern': f"new {class_name}()"
        })
    
    return method_calls


def resolve_method_calls(indexer: MultiSourceClassIndexer, method_calls: list, imports: list) -> list:
    """メソッド呼び出しをクラスインデックスで解決"""
    
    resolved = []
    
    for call in method_calls:
        if call['type'] == 'constructor_call':
            # コンストラクタ呼び出しの解決
            class_name = call['class']
            
            # インポートから完全クラス名を探す
            full_class_name = None
            for imp in imports:
                if imp.endswith('.' + class_name):
                    full_class_name = imp
                    break
            
            if not full_class_name:
                full_class_name = class_name
            
            # クラス情報を取得
            target_class_info = indexer.get_class_info(class_name)
            if target_class_info:
                resolved.append({
                    'call_pattern': call['pattern'],
                    'target_class': class_name,
                    'target_method': 'constructor',
                    'target_file': target_class_info.file_path,
                    'target_package': target_class_info.package_name,
                    'resolved': True
                })
            else:
                resolved.append({
                    'call_pattern': call['pattern'],
                    'target_class': class_name,
                    'resolved': False
                })
        
        elif call['type'] == 'instance_call':
            # インスタンスメソッド呼び出しの解決
            obj_name = call['object']
            method_name = call['method']
            
            # オブジェクト名からクラス名を推測（簡易版）
            guessed_class = guess_class_from_object_name(obj_name, imports)
            
            if guessed_class:
                target_class_info = indexer.get_class_info(guessed_class)
                if target_class_info and method_name in target_class_info.methods:
                    resolved.append({
                        'call_pattern': call['pattern'],
                        'target_class': guessed_class,
                        'target_method': method_name,
                        'target_file': target_class_info.file_path,
                        'target_package': target_class_info.package_name,
                        'resolved': True
                    })
                else:
                    resolved.append({
                        'call_pattern': call['pattern'],
                        'target_class': guessed_class,
                        'target_method': method_name,
                        'resolved': False
                    })
            else:
                resolved.append({
                    'call_pattern': call['pattern'],
                    'resolved': False
                })
    
    return resolved


def guess_class_from_object_name(obj_name: str, imports: list) -> str:
    """オブジェクト名からクラス名を推測"""
    
    # よくあるパターン: userEntityManager → UserEntityManager
    if 'entitymanager' in obj_name.lower():
        for imp in imports:
            if 'EntityManager' in imp:
                return imp.split('.')[-1]
    
    if 'ormapper' in obj_name.lower():
        for imp in imports:
            if 'ORMapper' in imp:
                return imp.split('.')[-1]
    
    if 'service' in obj_name.lower():
        for imp in imports:
            if 'Service' in imp:
                return imp.split('.')[-1]
    
    # その他のパターンも追加可能
    return None


def display_dependency_trace(resolved_calls: list):
    """依存関係追跡結果を表示"""
    
    resolved_count = len([call for call in resolved_calls if call.get('resolved', False)])
    total_count = len(resolved_calls)
    
    print(f"   📊 解決結果: {resolved_count}/{total_count} 個のメソッド呼び出しを解決")
    print()
    
    if resolved_count > 0:
        print("   ✅ 解決済み依存関係:")
        for call in resolved_calls:
            if call.get('resolved', False):
                print(f"      📞 {call['call_pattern']}")
                print(f"         → {call['target_class']}.{call['target_method']}")
                print(f"         📄 {call['target_file']}")
                print()
    
    unresolved_calls = [call for call in resolved_calls if not call.get('resolved', False)]
    if unresolved_calls:
        print("   ⚠️  未解決の呼び出し:")
        for call in unresolved_calls:
            print(f"      ❓ {call['call_pattern']}")
        print()
    

if __name__ == "__main__":
    main()
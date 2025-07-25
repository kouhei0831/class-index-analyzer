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
    print("🚀 Class Index Analyzer - Advanced Java Code Analysis Tool")
    print("=" * 70)
    
    # コマンドライン引数の解析
    args = parse_arguments()
    
    try:
        # targetが.javaファイルの場合、そのファイルから解析対象を決定
        if args.target and args.target.endswith('.java'):
            # ファイル名からクラス名を推定
            file_name = os.path.basename(args.target)
            class_name = file_name.replace('.java', '')
            print(f"\n📄 Javaファイル指定: {args.target}")
            print(f"🎯 推定クラス名: {class_name}")
            
            # クラス名で解析を実行
            if not args.trace_dependencies and not getattr(args, 'class') and not args.method:
                # 何も指定されていない場合は、そのクラスの依存関係を追跡
                args.trace_dependencies = class_name
        
        # Step 1: クラスインデックス構築
        print("\n📚 Step 1: クラスインデックス構築")
        class_indexer = build_class_index(args)
        
        # Step 2: インデックス情報の表示・分析
        print("\n🔍 Step 2: クラスインデックス分析")
        analyze_class_index(class_indexer, args)
        
        print("\n✅ 解析完了")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  解析が中断されました")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 予期しないエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def parse_arguments():
    """コマンドライン引数の解析"""
    parser = argparse.ArgumentParser(
        description="Class Index Analyzer - クラスインデックスを活用した解析ツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 特定のJavaファイルを解析
  python main.py UserService.java --settings test_settings.json
  
  # 設定ファイルのみで解析  
  python main.py --settings .vscode/settings.json
  
  # ディレクトリを解析
  python main.py /path/to/java/src --settings .vscode/settings.json
  
  # 特定クラスの詳細情報表示
  python main.py --settings .vscode/settings.json --class EventEntity
  
  # 特定Javaファイルの依存関係を追跡
  python main.py DataAccessUtil.java --settings test_settings.json
        """
    )
    
    parser.add_argument(
        'target',
        nargs='?',
        help='解析対象のJavaファイルまたはディレクトリ'
    )
    
    parser.add_argument(
        '--settings',
        help='設定ファイルパス（複数ソースパス指定用）'
    )
    
    parser.add_argument(
        '--class',
        help='特定クラスの詳細情報を表示'
    )
    
    parser.add_argument(
        '--method',
        help='特定メソッド名を含むクラスを検索'
    )
    
    parser.add_argument(
        '--inheritance',
        help='特定クラスの継承関係を分析'
    )
    
    parser.add_argument(
        '--output', 
        default='output',
        help='出力ディレクトリ (デフォルト: output)'
    )
    
    parser.add_argument(
        '--no-cache',
        action='store_true',
        help='クラスインデックスキャッシュを使用しない'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='詳細ログを出力'
    )
    
    parser.add_argument(
        '--show-all-methods',
        action='store_true',
        help='クラスの全メソッドを表示（--classと組み合わせて使用）'
    )
    
    parser.add_argument(
        '--show-all-imports',
        action='store_true',
        help='クラスの全インポートを表示（--classと組み合わせて使用）'
    )
    
    parser.add_argument(
        '--trace-dependencies',
        help='特定クラス.メソッドの依存関係を追跡解析（例: DataAccessUtil.checkUserExists）'
    )
    
    parser.add_argument(
        '--max-depth',
        type=int,
        default=3,
        help='依存関係追跡の最大深度（デフォルト: 3）'
    )
    
    
    return parser.parse_args()


def build_class_index(args) -> MultiSourceClassIndexer:
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
            if args.target:
                print("   → コマンドライン指定の解析対象を使用")
    elif args.settings:
        print(f"❌ 設定ファイルが見つかりません: {args.settings}")
        if not args.target:
            raise Exception("設定ファイルが見つからず、解析対象も指定されていません")
    
    # フォールバック：コマンドライン引数のtargetを使用
    if not source_paths:
        if not args.target:
            raise Exception("解析対象のソースパスが指定されていません。--settingsまたはtargetを指定してください")
        # targetがディレクトリの場合はそのまま使用
        if os.path.isdir(args.target):
            source_paths = [args.target]
            print(f"📁 コマンドライン指定ディレクトリを使用: {args.target}")
        else:
            # ファイルの場合は親ディレクトリを使用
            parent_dir = os.path.dirname(args.target)
            if parent_dir:
                source_paths = [parent_dir]
                print(f"📁 ファイルの親ディレクトリを使用: {parent_dir}")
            else:
                raise Exception(f"ファイル {args.target} の親ディレクトリが特定できません")
    
    # クラスインデックス構築
    print("🔨 クラスインデックス構築開始...")
    
    indexer = MultiSourceClassIndexer()
    
    # キャッシュ設定
    use_cache = not args.no_cache
    indexer.cache_enabled = use_cache
    
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


def analyze_class_index(indexer: MultiSourceClassIndexer, args):
    """クラスインデックスの分析・活用"""
    
    # 基本統計情報の表示
    print("\n📊 クラスインデックス統計:")
    
    # クラス数統計
    unique_classes = set()
    for key, class_info in indexer.class_index.items():
        if '@' not in key:  # 基本キーのみカウント
            unique_classes.add(class_info.class_name)
    
    print(f"   📦 総クラス数: {len(unique_classes)}")
    
    # ソースパス別統計
    source_path_stats = {}
    for key, class_info in indexer.class_index.items():
        if '@' in key and class_info.source_path:
            source_path = class_info.source_path
            if source_path not in source_path_stats:
                source_path_stats[source_path] = 0
            source_path_stats[source_path] += 1
    
    print(f"   📁 ソースパス別クラス数:")
    for source_path, count in source_path_stats.items():
        print(f"      - {source_path}: {count}クラス")
    
    # 特定クラスの詳細表示
    if getattr(args, 'class'):
        print(f"\n🔍 クラス詳細情報: {getattr(args, 'class')}")
        display_class_details(indexer, getattr(args, 'class'), args.show_all_methods, args.show_all_imports)
    
    # メソッド検索
    if args.method:
        print(f"\n🔍 メソッド検索: {args.method}")
        search_methods(indexer, args.method)
    
    # 継承関係分析
    if args.inheritance:
        print(f"\n🔍 継承関係分析: {args.inheritance}")
        analyze_inheritance(indexer, args.inheritance)
    
    # 依存関係追跡
    if args.trace_dependencies:
        print(f"\n🔍 依存関係追跡: {args.trace_dependencies}")
        print(f"📏 最大深度: {args.max_depth}")
        trace_method_dependencies_recursive(indexer, args.trace_dependencies, args.max_depth)
    


def display_class_details(indexer: MultiSourceClassIndexer, class_name: str, show_all_methods: bool = False, show_all_imports: bool = False):
    """特定クラスの詳細情報を表示"""
    
    # クラス検索
    class_info = indexer.get_class_info(class_name)
    
    if not class_info:
        print(f"   ⚠️  クラス '{class_name}' が見つかりませんでした")
        return
    
    print(f"   📄 ファイル: {class_info.file_path}")
    print(f"   📦 パッケージ: {class_info.package_name}")
    print(f"   📁 ソースパス: {class_info.source_path}")
    
    # メソッド一覧
    if class_info.methods:
        print(f"   🔧 メソッド数: {len(class_info.methods)}")
        print("   📋 メソッド一覧:")
        
        if show_all_methods:
            # 全メソッドを表示
            for method_name, method_info in class_info.methods.items():
                params = ', '.join(method_info.parameters)
                print(f"      - {method_info.return_type} {method_name}({params})")
        else:
            # 最初の10個のみ表示
            for method_name, method_info in list(class_info.methods.items())[:10]:
                params = ', '.join(method_info.parameters)
                print(f"      - {method_info.return_type} {method_name}({params})")
            
            if len(class_info.methods) > 10:
                print(f"      ... 他 {len(class_info.methods) - 10} メソッド（--show-all-methodsで全表示）")
    
    # インポート一覧
    if class_info.imports:
        print(f"   📥 インポート数: {len(class_info.imports)}")
        print("   📋 主要インポート:")
        for imp in class_info.imports[:5]:
            print(f"      - {imp}")
        
        if len(class_info.imports) > 5:
            print(f"      ... 他 {len(class_info.imports) - 5} インポート")


def search_methods(indexer: MultiSourceClassIndexer, method_pattern: str):
    """メソッド名でクラスを検索"""
    
    found_classes = []
    method_pattern_lower = method_pattern.lower()
    
    for key, class_info in indexer.class_index.items():
        if '@' in key:  # ソース特定版はスキップ
            continue
            
        for method_name in class_info.methods:
            if method_pattern_lower in method_name.lower():
                found_classes.append((class_info, method_name))
                break
    
    if found_classes:
        print(f"   📋 '{method_pattern}' を含むメソッドを持つクラス: {len(found_classes)}個")
        for class_info, method_name in found_classes[:10]:
            print(f"      - {class_info.class_name}.{method_name}() ({class_info.file_path})")
        
        if len(found_classes) > 10:
            print(f"      ... 他 {len(found_classes) - 10} クラス")
    else:
        print(f"   ⚠️  '{method_pattern}' を含むメソッドが見つかりませんでした")


def analyze_inheritance(indexer: MultiSourceClassIndexer, base_class: str):
    """継承関係の分析（簡易版）"""
    
    print(f"   ℹ️  継承関係の分析は将来的に実装予定です")
    print(f"   📋 現在のクラスインデックスには継承情報が含まれていません")


def trace_method_dependencies_recursive(indexer: MultiSourceClassIndexer, target_spec: str, max_depth: int = 3):
    """特定メソッドの依存関係を再帰的に追跡"""
    
    visited = set()  # 循環参照回避
    dependency_tree = {}  # 依存関係ツリー
    
    print(f"   🌳 再帰的依存関係解析開始...")
    
    # 再帰的に依存関係を追跡
    trace_recursive(indexer, target_spec, 0, max_depth, visited, dependency_tree)
    
    # 結果を表示
    display_dependency_tree(dependency_tree, max_depth)


def trace_recursive(indexer: MultiSourceClassIndexer, target_spec: str, current_depth: int, max_depth: int, visited: set, dependency_tree: dict) -> dict:
    """再帰的に依存関係を追跡する内部関数"""
    
    if current_depth >= max_depth:
        return {}
    
    if target_spec in visited:
        return {"circular_reference": True}
    
    visited.add(target_spec)
    
    # Step 1: クラス.メソッド形式の解析
    if '.' in target_spec:
        class_name, method_name = target_spec.split('.', 1)
    else:
        class_name = target_spec
        method_name = None
    
    # Step 2: クラス情報取得
    class_info = indexer.get_class_info(class_name)
    if not class_info:
        return {"error": f"クラス '{class_name}' が見つかりません"}
    
    if method_name and method_name not in class_info.methods:
        return {"error": f"メソッド '{method_name}' が見つかりません"}
    
    # Step 3: ファイル内容を詳細解析
    try:
        with open(class_info.file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
    except Exception as e:
        return {"error": f"ファイル読み込みエラー: {e}"}
    
    # Step 4: メソッド呼び出しパターンを抽出
    if method_name:
        method_calls = extract_method_calls_from_specific_method(file_content, method_name, class_info.imports)
    else:
        method_calls = extract_method_calls(file_content, class_info.imports)
    
    # Step 5: 呼び出し先をクラスインデックスで解決
    resolved_calls = resolve_method_calls(indexer, method_calls, class_info.imports)
    
    # Step 6: 依存関係ツリーを構築
    current_node = {
        "target": target_spec,
        "class_name": class_name,
        "method_name": method_name,
        "file_path": class_info.file_path,
        "depth": current_depth,
        "dependencies": {},
        "resolved_calls": resolved_calls
    }
    
    # Step 7: 解決できた依存関係を再帰的に追跡
    for call in resolved_calls:
        if call.get('resolved', False):
            target_class = call['target_class']  
            target_method = call['target_method']
            next_target = f"{target_class}.{target_method}" if target_method != 'constructor' else target_class
            
            # 再帰的に追跡
            if next_target not in visited:
                child_deps = trace_recursive(indexer, next_target, current_depth + 1, max_depth, visited.copy(), dependency_tree)
                if child_deps:
                    current_node["dependencies"][next_target] = child_deps
    
    visited.remove(target_spec)
    dependency_tree[target_spec] = current_node
    return current_node


def display_dependency_tree(dependency_tree: dict, max_depth: int):
    """依存関係ツリーを表示"""
    
    if not dependency_tree:
        print("   ⚠️  依存関係が見つかりませんでした")
        return
    
    print(f"   🌳 依存関係ツリー（最大深度: {max_depth}）:")
    print()
    
    # ルートノードから表示
    for root_target, root_node in dependency_tree.items():
        if root_node.get('depth', 0) == 0:
            display_tree_node(root_node, 0, set())
            break


def display_tree_node(node: dict, indent_level: int, shown_nodes: set):
    """ツリーノードを再帰的に表示"""
    
    if node.get("error"):
        print("   " + "  " * indent_level + f"❌ {node['error']}")
        return
    
    if node.get("circular_reference"):
        print("   " + "  " * indent_level + f"🔄 循環参照")
        return
    
    target = node.get("target", "Unknown")
    file_path = node.get("file_path", "")
    depth = node.get("depth", 0)
    
    # 表示用のインデント
    indent = "   " + "  " * indent_level
    
    if indent_level == 0:
        print(f"{indent}📍 {target} (深度: {depth})")
    else:
        print(f"{indent}├─ {target} (深度: {depth})")
    
    if file_path:
        print(f"{indent}   📄 {file_path}")
    
    # 解決できた呼び出しを表示
    resolved_calls = node.get("resolved_calls", [])
    resolved_count = len([call for call in resolved_calls if call.get('resolved', False)])
    total_count = len(resolved_calls)
    
    if total_count > 0:
        print(f"{indent}   📊 メソッド呼び出し: {resolved_count}/{total_count} 解決")
    
    # 依存関係を再帰的に表示
    dependencies = node.get("dependencies", {})
    if dependencies:
        print(f"{indent}   🔗 依存関係 ({len(dependencies)}個):")
        for dep_target, dep_node in dependencies.items():
            if dep_target not in shown_nodes:
                shown_nodes.add(dep_target)
                display_tree_node(dep_node, indent_level + 1, shown_nodes)
            else:
                print(f"{indent}     ├─ {dep_target} (既に表示済み)")
    
    print()


def trace_method_dependencies(indexer: MultiSourceClassIndexer, target_spec: str):
    """特定メソッドの依存関係を詳細追跡"""
    
    # Step 1: クラス.メソッド形式の解析
    if '.' in target_spec:
        class_name, method_name = target_spec.split('.', 1)
    else:
        class_name = target_spec
        method_name = None
    
    # Step 2: クラス情報取得
    class_info = indexer.get_class_info(class_name)
    if not class_info:
        print(f"   ⚠️  クラス '{class_name}' が見つかりませんでした")
        return
    
    print(f"   📄 解析対象: {class_info.file_path}")
    print(f"   📦 パッケージ: {class_info.package_name}")
    
    if method_name:
        if method_name not in class_info.methods:
            print(f"   ⚠️  メソッド '{method_name}' が見つかりませんでした")
            return
        print(f"   🎯 対象メソッド: {method_name}")
    else:
        print(f"   🎯 対象: クラス全体")
    
    # Step 3: ファイル内容を詳細解析
    try:
        with open(class_info.file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        print(f"   🔍 メソッド呼び出し解析開始...")
        
        # Step 4: メソッド呼び出しパターンを抽出（特定メソッド内のみ）
        if method_name:
            method_calls = extract_method_calls_from_specific_method(file_content, method_name, class_info.imports)
        else:
            method_calls = extract_method_calls(file_content, class_info.imports)
        
        if method_calls:
            print(f"   📋 発見されたメソッド呼び出し: {len(method_calls)}個")
            
            # Step 5: 呼び出し先をクラスインデックスで解決
            resolved_calls = resolve_method_calls(indexer, method_calls, class_info.imports)
            
            # Step 6: 結果表示
            display_dependency_trace(resolved_calls)
        else:
            print(f"   ⚠️  メソッド呼び出しが見つかりませんでした")
            
    except Exception as e:
        print(f"   ❌ ファイル解析エラー: {e}")


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
    """ファイル内容からメソッド呼び出しを抽出"""
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
            'method': class_name,
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
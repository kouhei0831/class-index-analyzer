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
  # 基本的な解析
  python main.py /path/to/java/src
  
  # 設定ファイル指定（複数ソースパス対応）
  python main.py /path/to/java/src --settings .vscode/settings.json
  
  # 特定クラスの詳細情報表示
  python main.py /path/to/java/src --class EventEntity
  
  # メソッド検索
  python main.py /path/to/java/src --method insert
  
  # 継承関係の分析
  python main.py /path/to/java/src --inheritance BaseClass
  
  # キャッシュ無効化
  python main.py /path/to/java/src --no-cache
        """
    )
    
    parser.add_argument(
        'directory',
        help='解析対象のJavaソースディレクトリ'
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
            print("   → デフォルトのディレクトリ指定を使用")
    
    # フォールバック：コマンドライン引数のディレクトリを使用
    if not source_paths:
        source_paths = [args.directory]
        print(f"📁 コマンドライン指定ディレクトリを使用: {args.directory}")
    
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
    if args.class:
        print(f"\n🔍 クラス詳細情報: {args.class}")
        display_class_details(indexer, args.class)
    
    # メソッド検索
    if args.method:
        print(f"\n🔍 メソッド検索: {args.method}")
        search_methods(indexer, args.method)
    
    # 継承関係分析
    if args.inheritance:
        print(f"\n🔍 継承関係分析: {args.inheritance}")
        analyze_inheritance(indexer, args.inheritance)


def display_class_details(indexer: MultiSourceClassIndexer, class_name: str):
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
        for method_name, method_info in list(class_info.methods.items())[:10]:
            params = ', '.join(method_info.parameters)
            print(f"      - {method_info.return_type} {method_name}({params})")
        
        if len(class_info.methods) > 10:
            print(f"      ... 他 {len(class_info.methods) - 10} メソッド")
    
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
    

if __name__ == "__main__":
    main()
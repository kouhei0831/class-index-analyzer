#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Class indexer for Smart Entity CRUD Analyzer
複数ソースパス対応版
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, List
from collections import defaultdict

from models import ClassInfo, MethodInfo
from utils import (
    read_file_with_encoding, 
    get_source_identifier,
    extract_package_and_class_name,
    extract_method_signatures,
    extract_imports,
    find_java_files
)


class MultiSourceClassIndexer:
    """
    複数ソースパス対応クラスインデックス構築
    
    重要な設計考慮点：
    1. 同じクラス名が複数ソースパスに存在する可能性
    2. ソースパス毎にクラスを区別して管理
    3. インデックスキーにソース識別子を含める
    """
    
    def __init__(self, cache_enabled: bool = True):
        self.source_paths = []  # 解決済み絶対パスリスト
        self.cache_enabled = cache_enabled
        self.cache_file = "multi_source_class_index_cache.json"
        
    def build_class_index(self, source_paths: List[str]) -> Dict[str, ClassInfo]:
        """
        複数ソースパスからクラスインデックスを構築
        
        戻り値のキー形式：
        - "ClassName" : 最初に見つかったクラス（後方互換性）
        - "ClassName@aios_cas:src" : ソースパス特定版
        - "full.package.ClassName" : 完全クラス名版
        - "full.package.ClassName@aios_cas:src" : 完全クラス名+ソース特定版
        """
        self.source_paths = source_paths
        
        # キャッシュチェック
        if self.cache_enabled and self._is_cache_valid(source_paths):
            print("🚀 キャッシュからクラスインデックスを読み込み中...")
            return self._load_from_cache()
        
        all_classes = {}
        
        print(f"🏗️  複数ソースパス対応クラスインデックス構築開始")
        print(f"📁 対象ソースパス: {len(source_paths)}個")
        
        # ソースパス別統計
        source_stats = {}
        
        for source_path in source_paths:
            source_identifier = get_source_identifier(source_path, source_paths)
            source_stats[source_identifier] = 0
            
            print(f"   🔍 解析中: {source_identifier} ({source_path})")
            
            if not Path(source_path).exists():
                print(f"   ⚠️  ソースパス未発見: {source_path}")
                continue
            
            # Java ファイルを検索
            java_files = find_java_files(source_path)
            print(f"   📄 Javaファイル: {len(java_files)}個")
            
            for java_file in java_files:
                try:
                    class_info = self._extract_class_info(java_file, source_path, source_identifier)
                    if class_info:
                        # 複数のキーでインデックス登録
                        self._register_class_info(all_classes, class_info)
                        source_stats[source_identifier] += 1
                        
                except Exception as e:
                    print(f"   ⚠️  ファイル解析エラー {Path(java_file).name}: {e}")
                    continue
        
        # 統計出力
        total_classes = len([k for k in all_classes.keys() if '@' not in k and '.' not in k])  # 基本クラス名のみカウント
        print(f"🏛️  クラスインデックス構築完了:")
        print(f"   📦 総クラス数: {total_classes}個")
        
        for source_id, count in source_stats.items():
            print(f"   📦 {source_id}: {count}個のクラス")
        
        print(f"   🔑 総インデックスキー数: {len(all_classes)}個")
        
        # キャッシュに保存
        if self.cache_enabled:
            self._save_to_cache(all_classes, source_paths)
        
        return all_classes
    
    def _extract_class_info(self, file_path: str, source_path: str, source_identifier: str) -> ClassInfo:
        """
        Javaファイルからクラス情報を抽出
        """
        try:
            content = read_file_with_encoding(file_path)
            
            # パッケージ名・クラス名を抽出
            package_name, class_name = extract_package_and_class_name(content)
            
            if not class_name:
                return None
            
            # 完全クラス名を構築
            full_class_name = f"{package_name}.{class_name}" if package_name else class_name
            
            # メソッドシグネチャを抽出
            method_signatures = extract_method_signatures(content)
            methods = {}
            
            for method_sig in method_signatures:
                method_info = MethodInfo(
                    file_path=file_path,
                    class_name=class_name,
                    method_name=method_sig['method_name'],
                    return_type=method_sig['return_type'],
                    parameters=[],  # 簡略版では未実装
                    source_path=source_identifier
                )
                methods[method_sig['method_name']] = method_info
            
            # import文を抽出
            imports = extract_imports(content)
            
            return ClassInfo(
                class_name=class_name,
                full_class_name=full_class_name,
                file_path=file_path,
                source_path=source_identifier,
                package_name=package_name,
                methods=methods,
                imports=imports
            )
            
        except Exception as e:
            print(f"⚠️  クラス情報抽出エラー {Path(file_path).name}: {e}")
            return None
    
    def _register_class_info(self, all_classes: Dict[str, ClassInfo], class_info: ClassInfo):
        """
        クラス情報を複数のキーで登録
        複数ソースパス対応のため、衝突回避が重要
        """
        # 1. 基本クラス名（最初に見つかったもの優先）
        if class_info.class_name not in all_classes:
            all_classes[class_info.class_name] = class_info
        
        # 2. クラス名@ソース識別子（ソースパス特定版）
        source_specific_key = f"{class_info.class_name}@{class_info.source_path}"
        all_classes[source_specific_key] = class_info
        
        # 3. 完全クラス名（最初に見つかったもの優先）
        if class_info.full_class_name not in all_classes:
            all_classes[class_info.full_class_name] = class_info
        
        # 4. 完全クラス名@ソース識別子（完全特定版）
        full_source_specific_key = f"{class_info.full_class_name}@{class_info.source_path}"
        all_classes[full_source_specific_key] = class_info
    
    def search_class(self, all_classes: Dict[str, ClassInfo], class_name: str, 
                    preferred_source: str = None) -> ClassInfo:
        """
        クラス検索（複数ソースパス対応）
        
        検索順序:
        1. preferred_sourceが指定されている場合、そのソース優先
        2. 完全クラス名での検索
        3. 基本クラス名での検索
        """
        # 1. ソース特定検索
        if preferred_source:
            source_specific_key = f"{class_name}@{preferred_source}"
            if source_specific_key in all_classes:
                return all_classes[source_specific_key]
        
        # 2. 完全クラス名検索
        if class_name in all_classes and '.' in class_name:
            return all_classes[class_name]
        
        # 3. 基本クラス名検索
        if class_name in all_classes:
            return all_classes[class_name]
        
        return None
    
    def debug_print_index(self, all_classes: Dict[str, ClassInfo], max_entries: int = 10):
        """デバッグ用：インデックス内容を出力"""
        print(f"\n🔍 クラスインデックス内容（最初の{max_entries}件）:")
        
        count = 0
        for key, class_info in all_classes.items():
            if count >= max_entries:
                break
            print(f"   🔑 {key} → {class_info.full_class_name} ({class_info.source_path})")
            count += 1
        
        if len(all_classes) > max_entries:
            print(f"   ... 他{len(all_classes) - max_entries}件")
    
    def _is_cache_valid(self, source_paths: List[str]) -> bool:
        """キャッシュが有効かどうかを判定"""
        if not os.path.exists(self.cache_file):
            return False
        
        try:
            cache_mtime = os.path.getmtime(self.cache_file)
            
            # ソースファイルの最新更新時刻をチェック
            latest_source_mtime = 0
            for source_path in source_paths:
                if not Path(source_path).exists():
                    continue
                    
                for root, dirs, files in os.walk(source_path):
                    for file in files:
                        if file.endswith('.java'):
                            file_path = os.path.join(root, file)
                            file_mtime = os.path.getmtime(file_path)
                            latest_source_mtime = max(latest_source_mtime, file_mtime)
            
            # キャッシュがソースファイルより新しければ有効
            is_valid = cache_mtime > latest_source_mtime
            if is_valid:
                print(f"✅ キャッシュが最新です (キャッシュ: {time.ctime(cache_mtime)})")
            else:
                print(f"⚠️  キャッシュが古いです - 再構築します")
            
            return is_valid
            
        except Exception as e:
            print(f"⚠️  キャッシュ有効性確認エラー: {e}")
            return False
    
    def _save_to_cache(self, all_classes: Dict[str, ClassInfo], source_paths: List[str]):
        """クラスインデックスをキャッシュに保存"""
        try:
            cache_data = {
                'metadata': {
                    'created_at': time.time(),
                    'source_paths': source_paths,
                    'total_classes': len([k for k in all_classes.keys() if '@' not in k and '.' not in k])
                },
                'classes': {}
            }
            
            for class_key, class_info in all_classes.items():
                # メソッド情報をシリアライズ
                methods_data = {}
                for method_name, method_info in class_info.methods.items():
                    methods_data[method_name] = {
                        'file_path': method_info.file_path,
                        'class_name': method_info.class_name,
                        'method_name': method_info.method_name,
                        'return_type': method_info.return_type,
                        'parameters': method_info.parameters,
                        'source_path': method_info.source_path
                    }
                
                # クラス情報をシリアライズ
                cache_data['classes'][class_key] = {
                    'class_name': class_info.class_name,
                    'full_class_name': class_info.full_class_name,
                    'file_path': class_info.file_path,
                    'source_path': class_info.source_path,
                    'package_name': class_info.package_name,
                    'methods': methods_data,
                    'imports': class_info.imports
                }
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ クラスインデックスをキャッシュに保存: {self.cache_file}")
            
        except Exception as e:
            print(f"⚠️  キャッシュ保存エラー: {e}")
    
    def _load_from_cache(self) -> Dict[str, ClassInfo]:
        """キャッシュからクラスインデックスを読み込み"""
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            all_classes = {}
            metadata = cache_data.get('metadata', {})
            
            print(f"📦 キャッシュメタデータ:")
            print(f"   🕒 作成日時: {time.ctime(metadata.get('created_at', 0))}")
            print(f"   📁 ソースパス数: {len(metadata.get('source_paths', []))}")
            print(f"   📦 総クラス数: {metadata.get('total_classes', 0)}")
            
            for class_key, class_data in cache_data.get('classes', {}).items():
                # メソッド情報を復元
                methods = {}
                for method_name, method_data in class_data.get('methods', {}).items():
                    methods[method_name] = MethodInfo(
                        file_path=method_data['file_path'],
                        class_name=method_data['class_name'],
                        method_name=method_data['method_name'],
                        return_type=method_data['return_type'],
                        parameters=method_data['parameters'],
                        source_path=method_data['source_path']
                    )
                
                # クラス情報を復元
                class_info = ClassInfo(
                    class_name=class_data['class_name'],
                    full_class_name=class_data['full_class_name'],
                    file_path=class_data['file_path'],
                    source_path=class_data['source_path'],
                    package_name=class_data['package_name'],
                    methods=methods,
                    imports=class_data['imports']
                )
                
                all_classes[class_key] = class_info
            
            print(f"✅ キャッシュからクラスインデックスを読み込み完了: {len(all_classes)}個のキー")
            return all_classes
            
        except Exception as e:
            print(f"❌ キャッシュ読み込みエラー: {e}")
            return {}
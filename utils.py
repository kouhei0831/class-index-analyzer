#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utility functions for Smart Entity CRUD Analyzer
"""

import os
import json
import glob
from pathlib import Path
from typing import List, Dict, Tuple


def read_file_with_encoding(file_path: str) -> str:
    """複数のエンコーディングでファイルを読み込み"""
    encodings = ['utf-8', 'shift_jis', 'cp932', 'euc-jp', 'iso-2022-jp', 'latin-1']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    
    # 最後の手段：エラーを無視して読み込み
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()


def load_settings_and_resolve_paths(settings_path: str) -> Tuple[List[str], List[str]]:
    """
    settings.jsonを読み込んで絶対パスに解決する
    複数ソースパス対応版
    """
    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        
        source_paths = settings.get('java.project.sourcePaths', [])
        referenced_libraries = settings.get('java.project.referencedLibraries', [])
        
        # settings.jsonの親ディレクトリをベースパスとする
        settings_dir = Path(settings_path).parent
        if settings_dir.name == '.vscode':
            base_dir = settings_dir.parent
        else:
            base_dir = settings_dir
            
        print(f"📁 設定ファイルベースディレクトリ: {base_dir}")
        
        # ソースパスを絶対パスに変換
        absolute_source_paths = []
        for source_path in source_paths:
            if os.path.isabs(source_path):
                abs_path = source_path
            else:
                abs_path = str((base_dir / source_path).resolve())
            
            if Path(abs_path).exists():
                absolute_source_paths.append(abs_path)
                print(f"✅ ソースパス: {source_path} → {abs_path}")
            else:
                print(f"⚠️  ソースパス未発見: {source_path} → {abs_path}")
        
        # JARライブラリパスを絶対パスに変換（glob展開）
        absolute_jar_paths = []
        for lib_pattern in referenced_libraries:
            if os.path.isabs(lib_pattern):
                pattern = lib_pattern
            else:
                pattern = str(base_dir / lib_pattern)
            
            # glob展開
            expanded_jars = glob.glob(pattern, recursive=True)
            for jar_path in expanded_jars:
                if Path(jar_path).exists() and jar_path.endswith('.jar'):
                    absolute_jar_paths.append(jar_path)
                    
        print(f"📦 解決ソースパス: {len(absolute_source_paths)}個")
        print(f"📚 解決JARライブラリ: {len(absolute_jar_paths)}個")
        
        return absolute_source_paths, absolute_jar_paths
        
    except Exception as e:
        print(f"❌ settings.json読み込みエラー: {e}")
        return [], []


def get_source_identifier(file_path: str, source_paths: List[str]) -> str:
    """
    ファイルパスからどのソースパス由来かを識別
    重要：複数ソースパスで同名クラスが存在する場合の区別に使用
    """
    file_path_abs = str(Path(file_path).resolve())
    
    for i, source_path in enumerate(source_paths):
        source_path_abs = str(Path(source_path).resolve())
        if file_path_abs.startswith(source_path_abs):
            # ソースパス名から識別子を生成
            source_name = Path(source_path).parts[-2] if len(Path(source_path).parts) >= 2 else Path(source_path).name
            return f"{source_name}:{Path(source_path).name}"  # 例: "aios_cas:src", "cfw_cas:src"
    
    return "unknown"


def find_java_files(directory: str) -> List[str]:
    """ディレクトリからJavaファイルを再帰検索"""
    java_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.java'):
                java_files.append(os.path.join(root, file))
    return java_files


def extract_package_and_class_name(content: str) -> Tuple[str, str]:
    """
    ファイル内容からパッケージ名とクラス名を抽出
    """
    import re
    
    # パッケージ名を抽出
    package_match = re.search(r'package\s+([\w.]+)\s*;', content)
    package_name = package_match.group(1) if package_match else ""
    
    # クラス名を抽出（複数クラスある場合は最初の公開クラス）
    class_match = re.search(r'(?:public\s+)?(?:class|interface)\s+(\w+)', content)
    class_name = class_match.group(1) if class_match else ""
    
    return package_name, class_name


def extract_method_signatures(content: str) -> List[Dict[str, str]]:
    """
    ファイル内容からメソッドシグネチャを抽出
    複数ソースパス対応：重複メソッドの区別のため詳細情報を保持
    """
    import re
    
    methods = []
    
    # メソッドパターン（interface対応含む）
    patterns = [
        r'(?:public|private|protected)?\s*(?:static\s+)?(?:final\s+)?(\w+(?:<[^>]*>)?)\s+(\w+)\s*\([^)]*\)\s*(?:throws\s+[\w\s,]+)?\s*[{;]',
        r'(?:public|private|protected)?\s*(?:abstract\s+)?(\w+(?:<[^>]*>)?)\s+(\w+)\s*\([^)]*\)\s*(?:throws\s+[\w\s,]+)?\s*;'
    ]
    
    detected_methods = set()
    
    for pattern in patterns:
        for match in re.finditer(pattern, content):
            return_type = match.group(1)
            method_name = match.group(2)
            
            # 重複チェック & フィルタリング
            if (method_name not in detected_methods and 
                method_name not in ['getClass', 'hashCode', 'equals', 'toString'] and
                return_type not in ['if', 'for', 'while', 'switch', 'try', 'catch', 'return']):
                
                detected_methods.add(method_name)
                methods.append({
                    'method_name': method_name,
                    'return_type': return_type,
                    'signature': match.group(0).strip()
                })
    
    return methods


def extract_imports(content: str) -> List[str]:
    """import文を抽出"""
    import re
    
    imports = []
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('import ') and not line.startswith('import static'):
            import_match = re.search(r'import\s+([\w.]+)\s*;', line)
            if import_match and not import_match.group(1).endswith('*'):
                imports.append(import_match.group(1))
    
    return imports
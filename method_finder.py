#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Method definition finder using javalang
"""

import javalang
from utils import read_file_with_encoding
from typing import List, Dict


def find_method_definitions_in_file(file_path: str) -> List[Dict]:
    """単一ファイル内のメソッド定義を検索"""
    try:
        content = read_file_with_encoding(file_path)
        tree = javalang.parse.parse(content)
        
        methods = []
        for _, node in tree.filter(javalang.tree.MethodDeclaration):
            methods.append({
                'name': node.name,
                'file_path': file_path,
                'return_type': node.return_type.name if node.return_type else 'void',
                'parameters': [p.type.name for p in node.parameters] if node.parameters else [],
                'modifiers': [str(m) for m in node.modifiers] if node.modifiers else [],
                'line_number': node.position.line if hasattr(node, 'position') and node.position else 0
            })
        
        return methods
    
    except Exception as e:
        print(f"メソッド定義解析エラー: {file_path} - {e}")
        return []


def find_method_definition_in_project(method_name: str, class_indexer) -> List[Dict]:
    """プロジェクト内でメソッド定義を検索"""
    results = []
    
    # クラスインデックス内の全ファイルを検索
    for class_info in class_indexer.class_index.values():
        if hasattr(class_info, 'methods') and method_name in class_info.methods:
            method_info = class_info.methods[method_name]
            results.append({
                'method_name': method_name,
                'class_name': class_info.class_name,
                'file_path': class_info.file_path,
                'package_name': class_info.package_name,
                'return_type': method_info.return_type,
                'parameters': method_info.parameters
            })
    
    return results


def find_field_definitions_in_file(file_path: str) -> List[Dict]:
    """ファイル内のフィールド定義を検索（型推論用）"""
    try:
        content = read_file_with_encoding(file_path)
        tree = javalang.parse.parse(content)
        
        fields = []
        for _, node in tree.filter(javalang.tree.FieldDeclaration):
            field_type = node.type.name if hasattr(node.type, 'name') else str(node.type)
            
            for declarator in node.declarators:
                fields.append({
                    'name': declarator.name,
                    'type': field_type,
                    'file_path': file_path,
                    'modifiers': [str(m) for m in node.modifiers] if node.modifiers else []
                })
        
        return fields
    
    except Exception as e:
        print(f"フィールド定義解析エラー: {file_path} - {e}")
        return []


if __name__ == "__main__":
    # テスト用
    test_file = "test_java_src/com/example/util/DataAccessUtil.java"
    methods = find_method_definitions_in_file(test_file)
    
    print(f"メソッド定義: {len(methods)}個")
    for method in methods[:5]:
        print(f"  - {method['name']}(): {method['return_type']}")
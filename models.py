#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data models for Smart Entity CRUD Analyzer
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class CrudType(Enum):
    """CRUD操作の種別"""
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE" 
    DELETE = "DELETE"


@dataclass
class ClassInfo:
    """クラス情報"""
    class_name: str                    # クラス名 (EventEntity)
    full_class_name: str               # 完全クラス名 (jp.co.ana.fmc.cfw.domain.event.entity.EventEntity)
    file_path: str                     # ファイルパス
    source_path: str                   # ソースパス (aios_cas/src or cfw_cas/src)
    package_name: str                  # パッケージ名
    methods: Dict[str, 'MethodInfo']   # メソッド一覧
    imports: List[str]                 # import文一覧
    
    def __post_init__(self):
        """ソースパス情報の正規化"""
        if self.source_path:
            # ソースパスを正規化（末尾のスラッシュを統一）
            self.source_path = self.source_path.rstrip('/')


@dataclass
class MethodInfo:
    """メソッド情報"""
    file_path: str
    class_name: str
    method_name: str
    return_type: str
    parameters: List[str]
    source_path: str                   # 追加：どのソースパス由来か


@dataclass
class EntityInfo:
    """エンティティ情報"""
    class_name: str                    # クラス名
    full_class_name: str               # 完全クラス名  
    file_path: str                     # ファイルパス
    source_path: str                   # ソースパス識別子
    package_name: str                  # パッケージ名
    table_name: Optional[str] = None   # テーブル名
    fields: List[str] = None           # フィールド一覧
    
    def __post_init__(self):
        if self.fields is None:
            self.fields = []
        # ソースパスを正規化
        if self.source_path:
            self.source_path = self.source_path.rstrip('/')


@dataclass
class EntityCrudOperation:
    """エンティティCRUD操作情報"""
    entity_class: str
    crud_type: CrudType
    method_name: str
    file_path: str
    confidence: float
    evidence: str
    call_chain: List[str] = None
    
    def __post_init__(self):
        if self.call_chain is None:
            self.call_chain = []


# Entity中心型システム用の新しいデータ構造

@dataclass
class CodeLocation:
    """コードの位置情報"""
    file_path: str
    line_number: int
    line_content: str
    context: str = ""


@dataclass
class EntityUsage:
    """Entity使用箇所の情報"""
    entity_name: str
    usage_type: str  # variable_declaration, instantiation, method_parameter, etc.
    location: CodeLocation
    

@dataclass
class MethodCall:
    """メソッド呼び出し情報"""
    method_name: str
    class_name: str
    location: CodeLocation
    variable_name: str = ""
    parameter_count: int = 0


@dataclass
class MethodDefinition:
    """メソッド定義情報"""
    class_name: str
    method_name: str
    file_path: str
    method_body: str
    line_number: int = 0
    is_ormapper: bool = False
    has_implementation: bool = True


@dataclass
class MethodChain:
    """メソッドチェーンの追跡結果"""
    start_location: CodeLocation
    chain_steps: List[MethodCall] = field(default_factory=list)
    final_destination: Optional[MethodDefinition] = None
    reached_ormapper: bool = False
    pattern_type: str = ""  # "EntityManager→ORMapper", "Direct ORMapper", "EntityCollection→Control→EntityManager→ORMapper"
    fallback_operations: List['CRUDOperation'] = field(default_factory=list)  # フォールバック用CRUD操作
    
    def is_complete(self) -> bool:
        """チェーンが完全に追跡できたか"""
        return self.reached_ormapper and self.final_destination is not None
    
    def has_fallback_operations(self) -> bool:
        """フォールバック操作があるか"""
        return len(self.fallback_operations) > 0


@dataclass  
class CRUDOperation:
    """CRUD操作情報"""
    operation_type: str  # CREATE, READ, UPDATE, DELETE
    method_name: str
    sql_pattern: Optional[str] = None
    confidence: float = 0.0
    source_location: Optional[CodeLocation] = None
    evidence: str = ""


@dataclass
class EntityAnalysisResult:
    """単一Entityの解析結果"""
    name: str
    package: str = ""
    usage_locations: List[EntityUsage] = field(default_factory=list)
    create_operations: List[CRUDOperation] = field(default_factory=list)
    read_operations: List[CRUDOperation] = field(default_factory=list)
    update_operations: List[CRUDOperation] = field(default_factory=list)
    delete_operations: List[CRUDOperation] = field(default_factory=list)
    method_chains: List[MethodChain] = field(default_factory=list)
    no_pattern_detected: bool = False  # EntityManager/ORMapper/EntityCollection未検出フラグ
    analysis_failed: bool = False  # 判定不可能フラグ
    
    def add_operations(self, operations: List[CRUDOperation]):
        """CRUD操作を追加（Entity レベルで重複除去）"""
        for op in operations:
            # 同じメソッド名の操作が既に存在するかチェック
            existing_ops = self._get_operations_by_type(op.operation_type)
            is_duplicate = any(existing_op.method_name == op.method_name for existing_op in existing_ops)
            
            if not is_duplicate:
                if op.operation_type == "CREATE":
                    self.create_operations.append(op)
                elif op.operation_type == "READ":
                    self.read_operations.append(op)
                elif op.operation_type == "UPDATE":
                    self.update_operations.append(op)
                elif op.operation_type == "DELETE":
                    self.delete_operations.append(op)
    
    def _get_operations_by_type(self, operation_type: str) -> List[CRUDOperation]:
        """指定タイプの操作リストを取得"""
        if operation_type == "CREATE":
            return self.create_operations
        elif operation_type == "READ":
            return self.read_operations
        elif operation_type == "UPDATE":
            return self.update_operations
        elif operation_type == "DELETE":
            return self.delete_operations
        return []
    
    def calculate_confidence(self) -> float:
        """信頼度計算（ORMapperまで到達できた割合）"""
        if not self.method_chains:
            return 0.0
        
        complete_chains = sum(1 for chain in self.method_chains if chain.is_complete())
        return complete_chains / len(self.method_chains)
    
    def get_total_operations(self) -> int:
        """総CRUD操作数"""
        return (len(self.create_operations) + len(self.read_operations) + 
                len(self.update_operations) + len(self.delete_operations))
    
    def has_full_crud(self) -> bool:
        """完全CRUD実装判定"""
        return (len(self.create_operations) > 0 and len(self.read_operations) > 0 and
                len(self.update_operations) > 0 and len(self.delete_operations) > 0)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Method dependency graph creator using networkx
"""

import networkx as nx
import matplotlib.pyplot as plt
from typing import Dict, List
import json


def create_dependency_graph(method_definitions: Dict, method_calls: Dict):
    """
    メソッドの依存関係グラフを作成
    
    Args:
        method_definitions: {method_name: {class_name, file_path, ...}}
        method_calls: {caller_method: [called_method1, called_method2, ...]}
    """
    G = nx.DiGraph()
    
    # ノード追加（メソッド定義）
    for method_name, info in method_definitions.items():
        G.add_node(method_name, **info)
    
    # エッジ追加（メソッド呼び出し関係）
    for caller, called_methods in method_calls.items():
        for called in called_methods:
            if called in method_definitions:  # 定義が存在する場合のみ
                G.add_edge(caller, called)
    
    return G


def analyze_graph_metrics(G):
    """グラフの基本メトリクスを分析"""
    metrics = {
        'total_nodes': G.number_of_nodes(),
        'total_edges': G.number_of_edges(),
        'density': nx.density(G),
        'is_connected': nx.is_weakly_connected(G),
        'strongly_connected_components': len(list(nx.strongly_connected_components(G))),
        'cycles': list(nx.simple_cycles(G))[:5],  # 最初の5個のサイクル
        'in_degree_centrality': dict(sorted(nx.in_degree_centrality(G).items(), 
                                          key=lambda x: x[1], reverse=True)[:10]),
        'out_degree_centrality': dict(sorted(nx.out_degree_centrality(G).items(), 
                                           key=lambda x: x[1], reverse=True)[:10]),
        'pagerank': dict(sorted(nx.pagerank(G).items(), 
                               key=lambda x: x[1], reverse=True)[:10])
    }
    return metrics


def find_critical_methods(G):
    """重要なメソッドを特定"""
    critical = {
        'most_called': [],      # 最も呼ばれるメソッド
        'most_calling': [],     # 最も多くを呼ぶメソッド
        'bridge_methods': [],   # ブリッジ的なメソッド
        'leaf_methods': [],     # 末端メソッド
        'root_methods': []      # 起点メソッド
    }
    
    # 入次数が高い（最も呼ばれる）
    in_degrees = dict(G.in_degree())
    critical['most_called'] = sorted(in_degrees.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # 出次数が高い（最も多くを呼ぶ）
    out_degrees = dict(G.out_degree())
    critical['most_calling'] = sorted(out_degrees.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # 末端メソッド（出次数0）
    critical['leaf_methods'] = [node for node, out_deg in out_degrees.items() if out_deg == 0]
    
    # 起点メソッド（入次数0）
    critical['root_methods'] = [node for node, in_deg in in_degrees.items() if in_deg == 0]
    
    # PageRankで重要度測定
    pagerank = nx.pagerank(G)
    critical['bridge_methods'] = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return critical


def visualize_dependency_graph(G, output_file="dependency_graph.png", layout="spring"):
    """依存関係グラフを可視化"""
    plt.figure(figsize=(15, 10))
    
    # レイアウト選択
    if layout == "spring":
        pos = nx.spring_layout(G, k=1, iterations=50)
    elif layout == "circular":
        pos = nx.circular_layout(G)
    elif layout == "hierarchical":
        pos = nx.nx_agraph.graphviz_layout(G, prog='dot')
    else:
        pos = nx.random_layout(G)
    
    # ノードの色づけ（入次数に基づく）
    in_degrees = dict(G.in_degree())
    node_colors = [in_degrees.get(node, 0) for node in G.nodes()]
    
    # ノードサイズ（PageRankに基づく）
    pagerank = nx.pagerank(G)
    node_sizes = [pagerank.get(node, 0) * 3000 + 100 for node in G.nodes()]
    
    # グラフ描画
    nx.draw(G, pos, 
            node_color=node_colors, 
            node_size=node_sizes,
            cmap=plt.cm.viridis,
            with_labels=True, 
            font_size=8,
            font_weight='bold',
            arrows=True,
            arrowsize=20,
            edge_color='gray',
            alpha=0.7)
    
    plt.title("Method Dependency Graph", size=16)
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"グラフを保存しました: {output_file}")


def generate_dependency_report(G, metrics, critical):
    """依存関係レポートを生成"""
    print("=" * 60)
    print("🕸️  メソッド依存関係グラフ分析レポート")
    print("=" * 60)
    
    print(f"\n📊 基本統計:")
    print(f"   総メソッド数: {metrics['total_nodes']}")
    print(f"   総依存関係数: {metrics['total_edges']}")
    print(f"   密度: {metrics['density']:.3f}")
    print(f"   弱連結: {'Yes' if metrics['is_connected'] else 'No'}")
    print(f"   強連結成分数: {metrics['strongly_connected_components']}")
    
    if metrics['cycles']:
        print(f"\n🔄 循環依存:")
        for i, cycle in enumerate(metrics['cycles'], 1):
            cycle_str = " → ".join(cycle + [cycle[0]])
            print(f"   {i}. {cycle_str}")
    
    print(f"\n🎯 最も呼ばれるメソッド (Top 5):")
    for method, count in critical['most_called']:
        print(f"   - {method}: {count}回")
    
    print(f"\n📞 最も多くを呼ぶメソッド (Top 5):")
    for method, count in critical['most_calling']:
        print(f"   - {method}: {count}個")
    
    print(f"\n⭐ 重要度の高いメソッド (PageRank):")
    for method, score in critical['bridge_methods']:
        print(f"   - {method}: {score:.3f}")
    
    if critical['root_methods']:
        print(f"\n🌱 起点メソッド ({len(critical['root_methods'])}個):")
        for method in critical['root_methods'][:10]:
            print(f"   - {method}")
    
    if critical['leaf_methods']:
        print(f"\n🍃 末端メソッド ({len(critical['leaf_methods'])}個):")
        for method in critical['leaf_methods'][:10]:
            print(f"   - {method}")


def export_graph_data(G, filename="dependency_graph.json"):
    """グラフデータをJSONで出力"""
    data = {
        'nodes': [
            {
                'id': node,
                'in_degree': G.in_degree(node),
                'out_degree': G.out_degree(node),
                **G.nodes[node]
            }
            for node in G.nodes()
        ],
        'edges': [
            {
                'source': edge[0],
                'target': edge[1]
            }
            for edge in G.edges()
        ]
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"グラフデータを出力しました: {filename}")


# テスト用のサンプルデータ
def create_sample_data():
    """テスト用のサンプルデータを作成"""
    method_definitions = {
        'checkUserExists': {'class_name': 'DataAccessUtil', 'file_path': 'DataAccessUtil.java'},
        'find': {'class_name': 'UserEntityManager', 'file_path': 'UserEntityManager.java'},
        'validateUserData': {'class_name': 'DataAccessUtil', 'file_path': 'DataAccessUtil.java'},
        'getName': {'class_name': 'UserEntity', 'file_path': 'UserEntity.java'},
        'addError': {'class_name': 'ValidationResult', 'file_path': 'ValidationResult.java'},
        'trim': {'class_name': 'String', 'file_path': 'java.lang.String'}
    }
    
    method_calls = {
        'checkUserExists': ['find'],
        'validateUserData': ['getName', 'trim', 'addError'],
        'find': [],
        'getName': [],
        'addError': [],
        'trim': []
    }
    
    return method_definitions, method_calls


if __name__ == "__main__":
    # テスト実行
    print("🧪 依存関係グラフのテスト実行")
    
    method_definitions, method_calls = create_sample_data()
    
    # グラフ作成
    G = create_dependency_graph(method_definitions, method_calls)
    
    # 分析
    metrics = analyze_graph_metrics(G)
    critical = find_critical_methods(G)
    
    # レポート生成
    generate_dependency_report(G, metrics, critical)
    
    # データ出力
    export_graph_data(G)
    
    # 可視化（matplotlibが利用可能な場合）
    try:
        visualize_dependency_graph(G)
    except Exception as e:
        print(f"可視化スキップ: {e}")
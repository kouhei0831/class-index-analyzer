# Class Index Analyzer

高度なクラスインデックス機能を活用したJavaコード解析ツール

## 概要

このツールは、Javaプロジェクトの全クラス・メソッド情報をインデックス化し、高速な検索・分析を可能にします。

## 主な機能

- **クラスインデックス構築**: 複数ソースパスからクラス情報を収集
- **クラス詳細表示**: 特定クラスのメソッド、インポート情報を表示
- **メソッド検索**: メソッド名パターンでクラスを検索
- **キャッシュ機能**: 高速な再解析のためのインデックスキャッシュ

## 使用方法

### 基本的な使い方

```bash
# 単一ディレクトリの解析
python main.py /path/to/java/src

# 設定ファイルを使用した複数ソースパスの解析
python main.py /path/to/java/src --settings .vscode/settings.json
```

### クラス詳細表示

```bash
# 特定クラスの詳細情報を表示
python main.py /path/to/java/src --class EventEntity
```

### メソッド検索

```bash
# "insert"を含むメソッドを持つクラスを検索
python main.py /path/to/java/src --method insert
```

### その他のオプション

```bash
# キャッシュを使用しない
python main.py /path/to/java/src --no-cache

# 詳細ログを出力
python main.py /path/to/java/src --verbose
```

## 設定ファイル例

`.vscode/settings.json`:
```json
{
    "files.autoGuessEncoding": true,
    "java.project.sourcePaths": [
        "src/main/java",
        "src/test/java"
    ]
}
```

## 依存関係

- Python 3.6+
- javalang

## インストール

```bash
pip install javalang
```

## ライセンス

MIT License
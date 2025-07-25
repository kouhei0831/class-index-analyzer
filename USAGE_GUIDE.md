# Smart Entity CRUD Analyzer v2.0 - 使用ガイド

## 🚀 はじめに

このガイドでは、Smart Entity CRUD Analyzer v2.0の基本的な使用方法から高度な機能まで、実際のコマンド例とともに説明します。

## 📋 前提条件

### 環境要件

- Python 3.7以上
- javalangライブラリ

### インストール

```bash
# 依存ライブラリのインストール
pip install javalang

# リポジトリのクローン（GitHubから）
git clone https://github.com/your-username/class-index-analyzer.git
cd class-index-analyzer
```

## 🎯 基本的な使用方法

### 1. 設定ファイルの準備

まず、解析対象のJavaソースパスを指定する設定ファイルを作成します。

**test_settings.json**:
```json
{
    "files.autoGuessEncoding": true,
    "java.project.sourcePaths": [
        "test_java_src"
    ],
    "java.project.referencedLibraries": [
        "lib/**/*.jar"
    ]
}
```

### 2. 最も基本的なコマンド

```bash
# 特定のJavaファイルを解析
python main.py test_java_src/com/example/util/DataAccessUtil.java --settings test_settings.json
```

このコマンドは以下を実行します：
1. クラスインデックスの構築
2. 指定されたファイル（DataAccessUtil）の依存関係を自動追跡
3. 結果の表示

## 🌳 依存関係追跡機能

### 特定メソッドの依存関係追跡

最も重要な機能である再帰的依存関係追跡の使用方法です。

```bash
# 基本的な依存関係追跡
python main.py test_java_src/com/example/util/DataAccessUtil.java --settings test_settings.json --trace-dependencies DataAccessUtil.checkUserExists

# 深度を指定した追跡
python main.py test_java_src/com/example/util/DataAccessUtil.java --settings test_settings.json --trace-dependencies DataAccessUtil.checkUserExists --max-depth 3
```

#### 出力例

```
🌳 依存関係ツリー（最大深度: 3）:

📍 DataAccessUtil.checkUserExists (深度: 0)
   📄 /home/user/project/test_java_src/com/example/util/DataAccessUtil.java
   📊 メソッド呼び出し: 1/1 解決
   🔗 依存関係 (1個):
  ├─ UserEntityManager.find (深度: 1)
     📄 /home/user/project/test_java_src/com/example/mapper/UserEntityManager.java
     📊 メソッド呼び出し: 1/2 解決
```

### より複雑なメソッドの追跡

```bash
# 複数の依存関係を持つメソッド
python main.py test_java_src/com/example/util/DataAccessUtil.java --settings test_settings.json --trace-dependencies DataAccessUtil.deleteUserCompletely --max-depth 2

# ビジネスロジックの追跡
python main.py test_java_src/com/example/business/UserBusinessLogic.java --settings test_settings.json --trace-dependencies UserBusinessLogic.registerUserWithWelcomeBonus --max-depth 3
```

### クラス全体の依存関係追跡

```bash
# 特定クラス全体の依存関係
python main.py test_java_src/com/example/util/DataAccessUtil.java --settings test_settings.json --trace-dependencies DataAccessUtil
```

## 🔍 クラス・メソッド検索機能

### クラス詳細情報の表示

```bash
# 基本的なクラス情報
python main.py --settings test_settings.json --class DataAccessUtil

# 全メソッドを表示
python main.py --settings test_settings.json --class DataAccessUtil --show-all-methods

# 全インポートを表示
python main.py --settings test_settings.json --class DataAccessUtil --show-all-imports

# 全ての情報を表示
python main.py --settings test_settings.json --class DataAccessUtil --show-all-methods --show-all-imports
```

#### 出力例

```
📄 ファイル: /path/to/DataAccessUtil.java
📦 パッケージ: com.example.util
📁 ソースパス: test_java_src
🔧 メソッド数: 20
📋 メソッド一覧:
  - boolean checkUserExists()
  - ValidationResult validateUserData()
  - void deleteUserCompletely()
  - UserBackup createUserBackup()
  - void restoreUserFromBackup()
📥 インポート数: 8
📋 主要インポート:
  - com.example.entity.UserEntity
  - com.example.entity.OrderEntity
  - com.example.mapper.UserEntityManager
```

### メソッド名による検索

```bash
# 特定のメソッド名を含むクラスを検索
python main.py --settings test_settings.json --method insert
python main.py --settings test_settings.json --method find
python main.py --settings test_settings.json --method delete
python main.py --settings test_settings.json --method update
```

#### 出力例

```
📋 'insert' を含むメソッドを持つクラス: 3個
  - UserEntityManager.insert() (/path/to/UserEntityManager.java)
  - UserORMapper.doInsert() (/path/to/UserORMapper.java)
  - DataAccessUtil.insertUser() (/path/to/DataAccessUtil.java)
```

## 🧪 各種Javaコンポーネントの解析例

### Entity層の解析

```bash
# User Entity
python main.py test_java_src/com/example/entity/UserEntity.java --settings test_settings.json --class UserEntity --show-all-methods

# Order Entity
python main.py test_java_src/com/example/entity/OrderEntity.java --settings test_settings.json --class OrderEntity --show-all-methods
```

### DAO/Mapper層の解析

```bash
# EntityManager
python main.py test_java_src/com/example/mapper/UserEntityManager.java --settings test_settings.json --trace-dependencies UserEntityManager.find --max-depth 2

# ORMapper
python main.py test_java_src/com/example/ormapper/UserORMapper.java --settings test_settings.json --trace-dependencies UserORMapper.findByName --max-depth 2
```

### Service層の解析

```bash
# User Service
python main.py test_java_src/com/example/UserService.java --settings test_settings.json --trace-dependencies UserService.createUser --max-depth 3

# Order Service  
python main.py test_java_src/com/example/service/OrderService.java --settings test_settings.json --trace-dependencies OrderService.createOrder --max-depth 3
```

### Controller層の解析

```bash
# User Controller
python main.py test_java_src/com/example/controller/UserController.java --settings test_settings.json --trace-dependencies UserController.createUser --max-depth 4

# Order Controller
python main.py test_java_src/com/example/controller/OrderController.java --settings test_settings.json --trace-dependencies OrderController.createOrder --max-depth 4
```

### ビジネスロジック層の解析

```bash
# 複雑なビジネスロジック
python main.py test_java_src/com/example/business/UserBusinessLogic.java --settings test_settings.json --trace-dependencies UserBusinessLogic.registerUserWithWelcomeBonus --max-depth 3

# ユーザー退会処理
python main.py test_java_src/com/example/business/UserBusinessLogic.java --settings test_settings.json --trace-dependencies UserBusinessLogic.withdrawUser --max-depth 3
```

### バッチ処理の解析

```bash
# データ移行バッチ
python main.py test_java_src/com/example/batch/UserDataMigrationBatch.java --settings test_settings.json --trace-dependencies UserDataMigrationBatch.migrateUsersFromLegacySystem --max-depth 3

# データクリーンアップバッチ
python main.py test_java_src/com/example/batch/UserDataMigrationBatch.java --settings test_settings.json --trace-dependencies UserDataMigrationBatch.cleanupOldData --max-depth 3
```

## ⚙️ 高度な機能

### キャッシュ管理

```bash
# キャッシュを使わずに実行（初回実行時や強制更新時）
python main.py test_java_src/com/example/util/DataAccessUtil.java --settings test_settings.json --no-cache

# キャッシュファイルの手動削除
rm multi_source_class_index_cache.json

# キャッシュの効果を確認
time python main.py --settings test_settings.json  # 初回実行
time python main.py --settings test_settings.json  # 2回目実行（キャッシュ使用）
```

### 詳細ログの出力

```bash
# 詳細な実行ログを出力
python main.py test_java_src/com/example/util/DataAccessUtil.java --settings test_settings.json --verbose

# デバッグ用の完全ログ
python main.py test_java_src/com/example/util/DataAccessUtil.java --settings test_settings.json --verbose --trace-dependencies DataAccessUtil.checkUserExists --max-depth 2
```

### 設定ファイルのみでの実行

```bash
# プロジェクト全体の概要を取得
python main.py --settings test_settings.json

# 特定クラスの情報のみ取得
python main.py --settings test_settings.json --class DataAccessUtil --show-all-methods
```

## 🎯 実践的な使用シナリオ

### シナリオ1: 新規プロジェクトの理解

```bash
# 1. まずプロジェクト全体を把握
python main.py --settings project_settings.json

# 2. 重要そうなクラスを詳細確認
python main.py --settings project_settings.json --class MainController --show-all-methods

# 3. 主要な処理の依存関係を追跡
python main.py MainController.java --settings project_settings.json --trace-dependencies MainController.processRequest --max-depth 4
```

### シナリオ2: バグ調査

```bash
# 1. 問題のあるメソッドを特定
python main.py --settings project_settings.json --method processPayment

# 2. そのメソッドの依存関係を詳細追跡
python main.py PaymentService.java --settings project_settings.json --trace-dependencies PaymentService.processPayment --max-depth 5

# 3. 関連するクラスの詳細を確認
python main.py --settings project_settings.json --class PaymentValidator --show-all-methods
```

### シナリオ3: リファクタリング前の影響調査

```bash
# 1. 変更予定のメソッドを使用している箇所を検索
python main.py --settings project_settings.json --method oldMethodName

# 2. 該当メソッドの依存関係を完全追跡
python main.py TargetClass.java --settings project_settings.json --trace-dependencies TargetClass.oldMethodName --max-depth 6

# 3. 影響範囲の詳細確認
python main.py --settings project_settings.json --class RelatedClass --show-all-methods
```

### シナリオ4: パフォーマンス問題の調査

```bash
# 1. 重いと思われる処理の依存関係を追跡
python main.py HeavyProcessor.java --settings project_settings.json --trace-dependencies HeavyProcessor.processLargeData --max-depth 4

# 2. データアクセス層の詳細確認
python main.py --settings project_settings.json --class DatabaseManager --show-all-methods

# 3. 呼び出し回数の多そうなメソッドを検索
python main.py --settings project_settings.json --method query
python main.py --settings project_settings.json --method select
```

## 🔧 トラブルシューティング

### よくある問題と解決方法

#### 1. "設定ファイルが見つかりません"

```bash
# 現在のディレクトリを確認
pwd

# 設定ファイルの存在確認
ls -la test_settings.json

# 絶対パスで指定
python main.py --settings /full/path/to/test_settings.json
```

#### 2. "クラスが見つかりません"

```bash
# キャッシュをクリアして再実行
rm multi_source_class_index_cache.json
python main.py --settings test_settings.json --no-cache

# 設定ファイルのソースパスを確認
cat test_settings.json

# 実際のファイル構造を確認
find . -name "*.java" | head -10
```

#### 3. "メソッドが見つかりません"

```bash
# クラス内のメソッド一覧を確認
python main.py --settings test_settings.json --class ClassName --show-all-methods

# 大文字小文字を確認
python main.py --settings test_settings.json --class ClassName --show-all-methods | grep -i methodname
```

#### 4. 処理が遅い

```bash
# 深度を制限
python main.py File.java --settings settings.json --trace-dependencies Class.method --max-depth 2

# キャッシュを使用（2回目以降）
python main.py --settings settings.json

# 詳細ログで処理状況を確認
python main.py --settings settings.json --verbose
```

### デバッグ用コマンド

```bash
# キャッシュの状態確認
ls -la multi_source_class_index_cache.json

# 設定ファイルの内容確認
cat test_settings.json | python -m json.tool

# Javaファイルの構造確認
find test_java_src -name "*.java" -exec basename {} \; | sort

# メモリ使用量の確認（Linux/Mac）
time python main.py --settings test_settings.json
```

## 📊 パフォーマンス最適化のヒント

### 1. キャッシュの効果的な利用

```bash
# 初回実行でキャッシュを構築
python main.py --settings project_settings.json

# 以降はキャッシュを活用した高速実行
python main.py File.java --settings project_settings.json --trace-dependencies Class.method
```

### 2. 適切な深度設定

```bash
# 概要把握には浅い深度
python main.py File.java --settings settings.json --trace-dependencies Class.method --max-depth 2

# 詳細調査には深い深度
python main.py File.java --settings settings.json --trace-dependencies Class.method --max-depth 5
```

### 3. 対象の絞り込み

```bash
# 特定メソッドのみに絞る
python main.py File.java --settings settings.json --trace-dependencies Class.specificMethod

# クラス全体ではなく特定ファイルを指定
python main.py specific/File.java --settings settings.json
```

## 🎉 まとめ

Smart Entity CRUD Analyzer v2.0を使用することで、Javaプロジェクトの複雑な依存関係を視覚的に理解し、効率的な開発・保守作業が可能になります。

### 基本的な使い方のまとめ

1. **設定ファイルの準備**: `test_settings.json`
2. **基本実行**: `python main.py File.java --settings test_settings.json`
3. **依存関係追跡**: `--trace-dependencies Class.method --max-depth 3`
4. **詳細情報取得**: `--class ClassName --show-all-methods`

### さらに学ぶために

- [SPECIFICATION.md](SPECIFICATION.md): 技術仕様の詳細
- [GitHub Issues](https://github.com/your-username/class-index-analyzer/issues): 問題報告・機能要望
- サンプルプロジェクト: `test_java_src/` ディレクトリ

---

*Smart Entity CRUD Analyzer v2.0 - 使用ガイド*
*最終更新: 2025年1月*
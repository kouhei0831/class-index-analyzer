# Smart Entity CRUD Analyzer v2.0 - 仕様書

## 📋 システム仕様

### システム概要

**Smart Entity CRUD Analyzer v2.0**は、Javaエンタープライズアプリケーションにおける特定のJavaファイルを起点とした再帰的なメソッド依存関係追跡システムです。

### バージョン情報

- **バージョン**: 2.0
- **リリース日**: 2025年1月
- **Python要求バージョン**: 3.7+
- **主要依存ライブラリ**: javalang

## 🎯 機能仕様

### 1. コア機能

#### 1.1 再帰的依存関係追跡

**概要**: 特定のメソッドから呼び出される全ての依存メソッドを階層的に追跡

**入力**:
- 起点Javaファイル
- 対象メソッド（オプション）
- 最大深度（デフォルト: 3）

**出力**:
- 依存関係ツリー
- 各レベルでのメソッド呼び出し解決率
- ファイルパス情報

**処理フロー**:
```
1. 起点メソッドの解析
2. メソッド内のメソッド呼び出し抽出
3. 呼び出し先の解決（クラスインデックス使用）
4. 解決済み依存関係の再帰的追跡
5. 循環参照チェック
6. 結果のツリー構造構築
7. 視覚的表示
```

#### 1.2 クラスインデックスシステム

**概要**: 高速なクラス・メソッド検索のための事前インデックス構築

**インデックス構造**:
```json
{
  "ClassName": {
    "class_name": "ClassName",
    "full_class_name": "com.example.ClassName",
    "file_path": "/path/to/ClassName.java",
    "package_name": "com.example",
    "methods": {
      "methodName": {
        "method_name": "methodName",
        "return_type": "String",
        "parameters": ["int", "String"]
      }
    },
    "imports": ["com.example.OtherClass"]
  }
}
```

**キー管理**:
- 基本名: `ClassName`
- ソース特定版: `ClassName@source_id`
- 完全名: `com.example.ClassName`
- 完全名+ソース: `com.example.ClassName@source_id`

#### 1.3 キャッシュシステム

**ファイル**: `multi_source_class_index_cache.json`

**無効化条件**:
- Javaファイルのタイムスタンプ変更
- ソースパス変更
- キャッシュファイルの手動削除

**パフォーマンス**: 約60倍の高速化

### 2. コマンドライン仕様

#### 2.1 基本構文

```bash
python main.py [TARGET] [OPTIONS]
```

#### 2.2 引数仕様

**位置引数**:
- `TARGET` (optional): Javaファイルまたはディレクトリ

**オプション引数**:

| オプション | 型 | 必須 | デフォルト | 説明 |
|-----------|----|----|----------|-----|
| `--settings` | string | No | - | 設定ファイルパス |
| `--trace-dependencies` | string | No | - | 依存関係追跡対象 |
| `--max-depth` | int | No | 3 | 追跡最大深度 |
| `--class` | string | No | - | クラス詳細表示 |
| `--method` | string | No | - | メソッド検索 |
| `--show-all-methods` | flag | No | false | 全メソッド表示 |
| `--show-all-imports` | flag | No | false | 全インポート表示 |
| `--no-cache` | flag | No | false | キャッシュ無効化 |
| `--verbose` | flag | No | false | 詳細ログ |

#### 2.3 実行パターン

**パターン1: 特定Javaファイル + 依存関係追跡**
```bash
python main.py DataAccessUtil.java --settings test_settings.json --trace-dependencies DataAccessUtil.checkUserExists --max-depth 3
```

**パターン2: 設定ファイルのみ**
```bash
python main.py --settings test_settings.json
```

**パターン3: クラス情報表示**
```bash
python main.py --settings test_settings.json --class DataAccessUtil --show-all-methods
```

### 3. 入出力仕様

#### 3.1 入力形式

**設定ファイル (settings.json)**:
```json
{
    "files.autoGuessEncoding": true,
    "java.project.sourcePaths": [
        "test_java_src",
        "additional_src"
    ],
    "java.project.referencedLibraries": [
        "lib/**/*.jar"
    ]
}
```

**Javaファイル要件**:
- 拡張子: `.java`
- エンコーディング: UTF-8（自動検出対応）
- 構文: Java 8+対応

#### 3.2 出力形式

**依存関係ツリー**:
```
🌳 依存関係ツリー（最大深度: 3）:

📍 DataAccessUtil.checkUserExists (深度: 0)
   📄 /path/to/DataAccessUtil.java
   📊 メソッド呼び出し: 1/1 解決
   🔗 依存関係 (1個):
  ├─ UserEntityManager.find (深度: 1)
     📄 /path/to/UserEntityManager.java
     📊 メソッド呼び出し: 2/3 解決
     🔗 依存関係 (2個):
    ├─ UserORMapper.select (深度: 2)
    ├─ Connection.prepareStatement (深度: 2)
```

**クラス詳細情報**:
```
📄 ファイル: /path/to/DataAccessUtil.java
📦 パッケージ: com.example.util
📁 ソースパス: test_java_src
🔧 メソッド数: 20
📋 メソッド一覧:
  - boolean checkUserExists()
  - void deleteUserCompletely()
  - UserBackup createUserBackup()
📥 インポート数: 8
📋 主要インポート:
  - com.example.entity.UserEntity
  - com.example.mapper.UserEntityManager
```

### 4. アルゴリズム仕様

#### 4.1 メソッド呼び出し抽出

**対象パターン**:
1. インスタンスメソッド: `object.method()`
2. コンストラクタ: `new ClassName()`
3. 静的メソッド: `ClassName.staticMethod()`

**正規表現**:
```python
# インスタンス呼び出し
INSTANCE_CALL_PATTERN = re.compile(r'(\w+)\.(\w+)\s*\(')

# コンストラクタ呼び出し
CONSTRUCTOR_CALL_PATTERN = re.compile(r'new\s+(\w+)\s*\(')
```

#### 4.2 メソッド範囲特定

**処理手順**:
1. メソッド定義行の検出（正規表現）
2. 開始中括弧の検出
3. 中括弧バランス計算による終了位置特定
4. 文字列リテラル内の中括弧除外

**実装例**:
```python
def extract_method_body(file_content: str, method_name: str) -> str:
    # メソッド定義パターン
    method_pattern = rf'(public|private|protected|static|\s)+.*?\b{re.escape(method_name)}\s*\([^)]*\)\s*\{{'
    
    # 中括弧バランス計算
    brace_count = 0
    for line in lines:
        for char in line:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    return method_body
```

#### 4.3 循環参照検出

**検出方法**:
```python
def trace_recursive(target_spec: str, visited: set):
    if target_spec in visited:
        return {"circular_reference": True}
    
    visited.add(target_spec)
    # 処理
    visited.remove(target_spec)
```

**表示**:
- `🔄 循環参照` として表示
- 重複するノードは `(既に表示済み)` として表示

### 5. エラーハンドリング仕様

#### 5.1 エラー分類

**システムエラー**:
- ファイル読み込みエラー
- JSON解析エラー
- 権限エラー

**解析エラー**:
- クラス未発見エラー
- メソッド未発見エラー
- 構文解析エラー

**設定エラー**:
- 設定ファイル未発見
- 不正な設定値

#### 5.2 エラー表示形式

```
❌ 予期しないエラーが発生しました: ファイルが見つかりません
⚠️  警告: 設定ファイルからソースパスを取得できませんでした
ℹ️  情報: キャッシュからクラスインデックスを読み込み中...
```

### 6. パフォーマンス仕様

#### 6.1 処理時間目標

| プロジェクト規模 | ファイル数 | 初回実行 | キャッシュ使用時 |
|----------------|-----------|---------|---------------|
| 小規模 | 10-50 | 1-3秒 | 0.1-0.5秒 |
| 中規模 | 100-500 | 5-15秒 | 0.5-2秒 |
| 大規模 | 1000+ | 30-60秒 | 2-5秒 |

#### 6.2 メモリ使用量

- **クラスインデックス**: 約1MB/100クラス
- **依存関係ツリー**: 約10KB/深度レベル
- **キャッシュファイル**: インデックスサイズの約1.5倍

#### 6.3 最適化技術

1. **正規表現の事前コンパイル**
2. **ファイル内容の効率的パース**
3. **タイムスタンプベースキャッシュ**
4. **メモリ効率的なツリー構造**

### 7. 制限事項

#### 7.1 言語サポート

- **サポート**: Java 8-17
- **未サポート**: Kotlin, Scala, Groovy

#### 7.2 解析範囲

- **対象**: プロジェクト内Javaファイルのみ
- **除外**: 外部ライブラリ、JDK標準ライブラリ

#### 7.3 解析精度

- **メソッド呼び出し解決率**: 60-80%
- **コンストラクタ解決率**: 90%+
- **動的呼び出し**: 未対応（リフレクション等）

### 8. セキュリティ仕様

#### 8.1 ファイルアクセス

- **読み取り専用**: Javaファイルの読み取りのみ
- **書き込み**: キャッシュファイルのみ
- **実行**: 外部コマンド実行なし

#### 8.2 入力検証

- **ファイルパス**: パストラバーサル攻撃防止
- **メソッド名**: 正規表現エスケープ
- **クラス名**: 安全な文字のみ許可

### 9. 拡張性仕様

#### 9.1 プラグインアーキテクチャ

```python
class AnalyzerPlugin:
    def analyze(self, class_info: ClassInfo) -> AnalysisResult:
        pass
    
    def format_output(self, result: AnalysisResult) -> str:
        pass
```

#### 9.2 カスタム出力フォーマット

- JSON形式
- XML形式
- GraphQL形式
- Markdown形式

#### 9.3 外部システム連携

- CI/CDパイプライン統合
- IDE拡張機能対応
- Web API提供

### 10. テスト仕様

#### 10.1 テストデータ

**テスト用Javaファイル**:
```
test_java_src/
├── com/example/
│   ├── entity/UserEntity.java
│   ├── mapper/UserEntityManager.java  
│   ├── ormapper/UserORMapper.java
│   ├── controller/UserController.java
│   ├── service/UserService.java
│   ├── business/UserBusinessLogic.java
│   ├── batch/UserDataMigrationBatch.java
│   └── util/DataAccessUtil.java
```

#### 10.2 テストケース

1. **単純な依存関係**
   - 1レベルの依存関係追跡
   - メソッド呼び出し解決

2. **複雑な依存関係**
   - 多レベル依存関係
   - 複数の呼び出しパス

3. **エッジケース**
   - 循環参照
   - メソッド未発見
   - ファイル読み込みエラー

#### 10.3 パフォーマンステスト

```bash
# 基本性能テスト
time python main.py test_java_src/com/example/util/DataAccessUtil.java --settings test_settings.json --trace-dependencies DataAccessUtil.checkUserExists --max-depth 3

# キャッシュ効果テスト
time python main.py --settings test_settings.json  # 初回
time python main.py --settings test_settings.json  # 2回目
```

---

*Smart Entity CRUD Analyzer v2.0 - 技術仕様書*
*最終更新: 2025年1月*
# WebClass_client
webclassの授業情報を取得するスクリプトです。

## ディレクトリ構成
```
.
├── README.md
├── main.py
└──webclass_client
    ├── __init__.py
    ├── assignments.py
    ├── client.py
    ├── lectures.py
    ├── logger_setup.py
    ├── messages.py
    └── session_manager.py
```

- **webclass_client/**  
  WebClass クライアントの各機能を実装したモジュール群です。
  - `client.py`: 全体のクライアントクラスを実装
  - `logger_setup.py`: ログ設定のためのユーティリティ
  - `session_manager.py`: セッション管理（ログイン／ログアウト）
  - `lectures.py`: 講義情報の取得
  - `assignments.py`: 課題情報の取得
  - `messages.py`: メッセージ情報の取得
  - `__init__.py`: パッケージ公開 API の定義

## 機能

- **セッション管理**  
  WebClass へのログイン、ログアウトを行い、セッション情報やクッキーを管理します。

- **講義情報の取得**  
  講義の一覧、講義ごとの詳細情報、講義名を取得できます。

- **課題情報の取得**  
  指定した期間内の課題情報を取得します。講義ごとに資料以外の課題をフィルタリングできます。

- **メッセージ情報の取得**  
  各講義のメッセージ（掲示板や通知）を取得します。

## セットアップ

### 必要な環境

- Python 3.x
- 必要なライブラリ:
  - `requests`
  - `beautifulsoup4`

必要に応じて以下のコマンドでインストールしてください:

```bash
pip install requests beautifulsoup4
```

## 使い方
1. main.pyの以下の部分に自分のWebClassのユーザー名とパスワードを入力してください。
```python
# WebClassのユーザー名とパスワードを入力
username = 'your_username'
password = 'your_password'
```
2. main.pyを実行してください。
```bash
python main.py
```
3. ログインに成功すると、講義情報、課題情報、メッセージ情報が取得されます。
4. ログインに失敗すると、ログインに失敗しましたと表示されます。

##  カスタマイズ
main.pyを変更することで任意の講義情報、課題情報、メッセージ情報を取得することができます。
client.set_wbt_sessionを使用してcookieを設定することで、loginをしなくても情報を取得することが可能

# MiniConnect

## 1. プロジェクト概要

Django で作った簡易 SNS アプリです。  
ユーザー登録・ログイン、投稿（テキスト・画像・ハッシュタグ）、いいね、フォロー、プロフィール編集、検索、タイムライン分割などができます。

### タイムライン（トップ `/`）

- **フォロー中**: 自分 + フォロー中ユーザーの投稿
- **みんな**: 自分以外かつ未フォローユーザーの投稿

### いいねランキング（`/ranking/`）

- カレンダーで月・年を切り替え、各日のマスに **その日の1位投稿のいいね数** を表示
- 日付をクリックすると、その日の代表投稿を表示
- **集計ルール**: その日（`Asia/Tokyo`）に投稿された全ユーザーの投稿のうち、**現在のいいね数** が最多の1件（同点は新しい投稿を優先）
- いいね日時は DB に保存していないため、「その日に付いたいいね」ではなく「その日の投稿のいいね数ランキング」

## 2. 技術スタック

- Python 3
- Django
- SQLite（ローカル開発）
- PostgreSQL（本番・Render 利用時は `DATABASE_URL` で接続）
- WhiteNoise（静的ファイル）
- Cloudinary（画像ストレージ・本番想定）
- Render（デプロイ先）

## 3. 前提条件

- Python 3 がインストールされていること
- Git
- （本番）Render アカウント、GitHub リポジトリ

## 4. セットアップ手順（ローカル）

### 4-1. リポジトリを取得

```powershell
git clone https://github.com/hal123w/miniconnect
cd miniconnect
```

### 4-2. 仮想環境

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

PowerShell で実行ポリシーエラーが出た場合:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 4-3. 依存パッケージのインストール

```powershell
pip install -r requirements.txt
```

`requirements.txt` には、このプロジェクトで使うパッケージとバージョンが記載されています。ローカル開発と Render のビルドの両方で同じファイルを使います。

### 4-4. 環境変数ファイル `.env`

プロジェクト直下に `.env` を作成し、次のキーを設定します（**値は README に書かない**）。

```text
SECRET_KEY=
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
```

### 4-5. データベースの準備

```powershell
python manage.py migrate
```

### 4-6. 開発サーバー起動

```powershell
python manage.py runserver
```

ブラウザで `http://127.0.0.1:8000/` を開きます。

### 4-7. （任意）管理画面用スーパーユーザー

```powershell
python manage.py createsuperuser
```

管理画面: `http://127.0.0.1:8000/admin/`

## 5. 環境変数一覧

| 変数名 | 用途 | ローカル | 本番（Render） |
|--------|------|----------|----------------|
| `SECRET_KEY` | Django の秘密鍵 | `.env` | Environment に設定 |
| `DEBUG` | デバッグモード | `True` | `False` |
| `ALLOWED_HOSTS` | 許可するホスト名 | `127.0.0.1,localhost` | 本番ドメイン（例: `*.onrender.com`） |
| `DATABASE_URL` | DB 接続 | 未設定なら SQLite | Render PostgreSQL の URL |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary クラウド名 | `.env` | Environment に設定 |
| `CLOUDINARY_API_KEY` | Cloudinary API キー | `.env` | Environment に設定 |
| `CLOUDINARY_API_SECRET` | Cloudinary API シークレット | `.env` | Environment に設定 |

**注意:** `.env` の中身（実際の値）は Git に commit しないこと。

Cloudinary の値は [Cloudinary Dashboard](https://cloudinary.com) から取得します。

## 6. 本番デプロイ（Render）概要

1. コードを GitHub に push する
2. Render で Web サービスを作成し、GitHub リポジトリと連携する
3. Render の **Environment** に上記の環境変数を設定する
4. ビルド・起動コマンドに従いデプロイする（`migrate` / `collectstatic` など）
5. デプロイ完了後、Render の URL で動作確認する

push していない commit は本番に反映されません。

## 7. 既知の制限・今後の改善

- 自動テストの追加

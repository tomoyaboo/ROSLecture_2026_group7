# ROS2 共同開発のための Git / GitHub ガイド

授業でのチーム開発を想定して、初期セットアップから日常のコマンド、ROS2 固有の注意点までまとめます。

---

## 1. Git と GitHub の関係

- **Git**: ローカル PC でファイル変更履歴を管理するツール（バージョン管理システム）
- **GitHub**: Git リポジトリをインターネット上に置いて共有するサービス

つまり「Git でローカルに記録 → GitHub で全員と共有」というイメージです。

---

## 2. 初期セットアップ（最初の1回だけ）

### 2.1 Git のインストール（Ubuntu）

ROS2 は Ubuntu で使うことが多いので Ubuntu 前提で書きます。

```bash
sudo apt update
sudo apt install git
git --version   # インストール確認
```

### 2.2 ユーザー情報の設定

コミット履歴に残る名前とメールアドレスを設定します。GitHub に登録したものと揃えるのがおすすめ。

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
git config --global init.defaultBranch main   # デフォルトブランチをmainに
```

確認:

```bash
git config --list
```

### 2.3 SSH 鍵の登録（推奨）

毎回パスワード入力をしなくて済むようにします。

```bash
ssh-keygen -t ed25519 -C "you@example.com"
# 何も入力せずEnter連打でOK（パスフレーズはお好みで）

cat ~/.ssh/id_ed25519.pub
```

表示された公開鍵を GitHub の `Settings → SSH and GPG keys → New SSH key` に貼り付けます。

接続確認:

```bash
ssh -T git@github.com
# "Hi <username>!" と返ってきたらOK
```

---

## 3. リポジトリの取得（チームメンバー向け）

すでに誰かが GitHub にリポジトリを作っている場合、各メンバーは **clone（クローン）** します。

```bash
cd ~/ros2_ws/src        # ROS2のワークスペース内のsrcへ
git clone git@github.com:username/repo_name.git
```

`ros2_ws/src` 配下に clone するのが ROS2 の流儀です。

---

## 4. 必ず覚える基本コマンド

### 4.1 全体の流れ

```
作業 → add → commit → push  （自分の変更を共有）
                      pull  ← (他人の変更を取り込む)
```

### 4.2 `git status`

今どのファイルが変わっているか確認。**何をするにもまず status**。

```bash
git status
```

### 4.3 `git add`

変更をコミット対象に「ステージング」する。

```bash
git add path/to/file.cpp      # 特定ファイルだけ
git add .                     # カレントディレクトリ以下すべて
```

**意味**: 「このファイルの変更を、次のコミットに含めます」と宣言する操作。いきなり commit するのではなく、add で対象を選んでから commit する2段階構成になっています。

### 4.4 `git commit`

ステージした変更を「履歴の1点」として確定する。

```bash
git commit -m "Add lidar publisher node"
```

**コミットメッセージのコツ**:
- 命令形・現在形（"Add", "Fix", "Update"）
- 1行目は50文字以内で要点
- 「何を」だけでなく「なぜ」も書くとレビューしやすい

### 4.5 `git push`

ローカルのコミットを GitHub にアップロード。

```bash
git push origin main          # mainブランチをoriginにpush
git push origin feature/lidar # ブランチ名を指定
```

### 4.6 `git pull`

GitHub 上の最新状態をローカルに取り込む。**作業を始める前に必ず実行**。

```bash
git pull origin main
```

`pull` は内部的に `fetch`（取得）+ `merge`（統合）をしている、と覚えておくと後で役に立ちます。

### 4.7 `git log`

履歴を確認。

```bash
git log --oneline --graph --all   # 見やすい表示
```

### 4.8 `git diff`

変更内容を行単位で確認。

```bash
git diff                # まだaddしていない変更
git diff --staged       # addしたがcommitしていない変更
```

---

## 5. ブランチを使った共同開発

複数人で同じ `main` を直接触るとほぼ確実に衝突します。**機能ごとにブランチを切る** のが鉄則。

### 5.1 ブランチの基本

```bash
git branch                          # ブランチ一覧
git switch -c feature/lidar-node    # 新規ブランチ作成 & 切り替え
git switch main                     # mainに戻る
```

（古い書き方では `git checkout -b` ですが、最近は `git switch` 推奨）

### 5.2 推奨ワークフロー

```bash
# 1. 最新のmainを取得
git switch main
git pull origin main

# 2. 作業用ブランチを作る
git switch -c feature/obstacle-detection

# 3. 開発・add・commit を繰り返す
git add .
git commit -m "Implement obstacle detection callback"

# 4. GitHubにpush
git push origin feature/obstacle-detection

# 5. GitHub上で Pull Request (PR) を作成
# → チームメンバーがレビュー → mainにマージ
```

### 5.3 ブランチ名の例

- `feature/xxx` — 新機能
- `fix/xxx` — バグ修正
- `docs/xxx` — ドキュメント
- `experiment/xxx` — 実験的な変更

---

## 6. Pull Request (PR) の流れ

1. GitHub のリポジトリページに行く
2. "Compare & pull request" ボタンを押す
3. 何をしたか・なぜそうしたかを書く
4. レビュアーを指定
5. レビューOKならマージ

**PRのメリット**:
- コードレビューができる
- 「いつ・誰が・何を入れたか」が記録される
- 問題があれば差し戻せる

---

## 7. コンフリクト（衝突）への対処

同じファイルの同じ行を別の人が編集すると `pull` や `merge` で衝突します。

```
<<<<<<< HEAD
自分の変更
=======
相手の変更
>>>>>>> origin/main
```

このマーカーを見つけたら:
1. エディタで該当箇所を **どちらか採用** or **両方を統合** するように手で書き直す
2. マーカー（`<<<`, `===`, `>>>`）を **すべて削除**
3. `git add <ファイル>` → `git commit`

慌てず1ファイルずつ処理すれば大丈夫です。

---

## 8. ROS2 開発で特に重要な `.gitignore`

ビルド成果物などは Git に入れません。`ros2_ws` 直下や ROS2 パッケージ直下に `.gitignore` を置きます。

```gitignore
# ROS2 ビルド成果物
build/
install/
log/

# Python
__pycache__/
*.pyc
*.egg-info/

# C++
*.o
*.so
*.a

# エディタ
.vscode/
.idea/
*.swp
.DS_Store
```

**`build/`, `install/`, `log/` を絶対にコミットしない** ことだけ覚えておけばOK。これを入れるとリポジトリが数GB単位で膨らみます。

すでに誤ってコミットしてしまった場合:

```bash
git rm -r --cached build install log
git commit -m "Remove build artifacts from tracking"
```

---

## 9. ROS2 リポジトリ構成の例

```
my_robot_ws/                    ← ワークスペース（通常 git 管理しない）
└── src/
    └── my_robot/               ← ここを git 管理する
        ├── .git/
        ├── .gitignore
        ├── README.md
        ├── my_robot_bringup/
        ├── my_robot_description/
        ├── my_robot_navigation/
        └── ...
```

ワークスペース全体ではなく、**`src/` 以下のパッケージ群を1つのリポジトリにする** のが一般的です。

---

## 10. 日常で使うコマンドのチートシート

| やりたいこと | コマンド |
|---|---|
| 今の状態を見る | `git status` |
| 変更を見る | `git diff` |
| 変更を記録対象に | `git add <file>` / `git add .` |
| 記録を確定 | `git commit -m "..."` |
| GitHubに送る | `git push origin <branch>` |
| GitHubから取る | `git pull origin <branch>` |
| ブランチを作って移動 | `git switch -c <name>` |
| ブランチを切替 | `git switch <name>` |
| ブランチ一覧 | `git branch` |
| 履歴を見る | `git log --oneline --graph` |
| 直前のコミットを取り消し（変更は残す）| `git reset --soft HEAD~1` |
| 作業内容を一時退避 | `git stash` / `git stash pop` |

---

## 11. チーム開発でのお作法

1. **作業前に必ず `git pull`** — 古い状態から派生すると衝突しやすい
2. **小さくコミット** — 1コミット1目的。後で戻しやすい
3. **メッセージは未来の自分とチームへの手紙** — "fix" だけはNG
4. **直接 `main` に push しない** — 必ずブランチ + PR
5. **コンフリクトを恐れない** — 落ち着いて1つずつ直せば必ず解決する
6. **動かないコードを push しない** — 最低限ビルドが通る状態で

---

## 12. 困ったときの相談コマンド

```bash
git help <コマンド名>      # 例: git help commit
git <コマンド> --help
```

公式日本語ドキュメント: https://git-scm.com/book/ja/v2

---

ROS2 のビルド (`colcon build`) と Git の組み合わせは、最初は戸惑うけど慣れます。何より「`build/` `install/` `log/` を ignore する」を徹底すれば、ほとんどの事故は防げます。頑張ってください！

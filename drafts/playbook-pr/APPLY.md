# Playbook への適用手順

**利用者が承認するまで、push、PR の作成、リモートの変更はしません。** Playbook の作業ツリー（`<Playbook のクローン>`）は他のセッションが使い、未コミットの変更を持つことがあるため、そこでは編集もブランチ切り替えも `fetch` 後の `checkout` もしません。

前提: Spoke の GitHub リポジトリが作成済みで、公開されていること（段階 4 の後）。

## 手順

1. 最新の `origin/main` を取得し、専用 worktree を作ります。

   ```bash
   git -C <Playbook のクローン> fetch origin
   git -C <Playbook のクローン> worktree add -b docs/related-repos-client-access-patterns ../playbook-related-repos origin/main
   ```

   `../playbook-related-repos` は Playbook のクローンと同じ親ディレクトリに作られます。ブランチ名が既にある場合は止まって確認します。

2. worktree に変更を入れます。
   - `README.md`: `## 関連リポジトリ — 判断の場所と実装の場所` の表の最後の行（`FSx-for-ONTAP-App-Modernization-Patterns`）の直後に、[README-related-repositories.md](README-related-repositories.md) の日本語の行を足します。
   - `docs/en/README.md`: 同じ節の英語版の表の最後の行の直後に、英語の行を足します。
   - `docs/ja/reference/cross-repo-index.md`: `## 分担の原則` の表で、`FSx-for-ONTAP-Container-Datastore-Patterns` の行の直後に、分担の原則の行を足します。
   - 任意: `llms.txt` の「Sibling repositories」節に、[index-check.md](index-check.md) の文案を足します。足したら [PR-BODY.md](PR-BODY.md) の Changes の任意の行も確定させます。

3. worktree 内でゲートを走らせます。先に Playbook の `make help` と `AGENTS.md` で、現役のターゲットと前提ツールを確認します。

   ```bash
   make audit
   make links
   make cross-repo
   make headings
   make i18n-check
   make switcher-check
   make ja-markers
   make anchors
   ```

   Playbook の pre-commit が、worktree にない前提（gitignore 対象の台帳など）で落ちるときは、`--no-verify` や回避の環境変数を使わず、ここで止まって stage までにして報告します。

4. 変更を小さい conventional commit にします。例: `docs: add Client Access Patterns row to related repos`、`docs: add Client Access Patterns to the citation index`。件名は 72 文字以内で、個人名やペルソナ名を入れません。

5. 利用者の承認を得てから、次をします。
   - `git push origin docs/related-repos-client-access-patterns`
   - [PR-BODY.md](PR-BODY.md) の本文とタイトルで PR を作成

6. 終わったら worktree を片付けます。

   ```bash
   git -C <Playbook のクローン> worktree remove ../playbook-related-repos
   ```

   削除後に `git worktree list` で消えたことを読み戻します。ブランチは PR がマージされるまで残します。

## 未解決の点

- 6 言語（ko、zh-CN、zh-TW、fr、de、es）の README。Playbook のルート README は 8 言語で検査される規約で、この下書きは日本語と英語だけを持ちます。`make i18n-check` が行の欠けを失敗にするかは未確認です。失敗する場合は、Playbook の持ち主が翻訳を足すか、日本語と英語を先に入れる方法（`docs/i18n-manifest.txt` の言語指定）の対象かを決めます。
- `make cross-repo-external` は、Spoke が公開されるまで通りません。

## 戻し方

PR 提出前なら、worktree を削除してからブランチを `git branch -d` で消します。マージ後は `git revert` します。

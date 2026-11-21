# Hub への適用手順

**利用者が承認するまで、push、PR の作成、リモートの変更はしません。** Hub の作業ツリー（`<Hub のクローン>`）は他のセッションが使うため、そこでは編集もブランチ切り替えもしません。

前提: Spoke の GitHub リポジトリが作成済みで、公開されていること（段階 4 の後）。

## 手順

1. 最新の `origin/main` を取得し、専用 worktree を作ります。

   ```bash
   git -C <Hub のクローン> fetch origin
   git -C <Hub のクローン> worktree add -b docs/related-repos-client-access-patterns ../fsxn-s3ap-relation origin/main
   ```

   `../fsxn-s3ap-relation` は Hub と同じ親ディレクトリに作られます。ブランチ名が既にある場合は止まって確認します。

2. worktree に 4 つの変更を入れます。
   - `README.md`: `### 関連リポジトリ` の `FSx-for-ONTAP-App-Modernization-Patterns` の行の直後に、[README-related-repositories.md](README-related-repositories.md) の日本語の行を足します。
   - `README.en.md`: `### Related Repositories` の同じ位置に、英語の行を足します。
   - `docs/client-access-patterns-relation.md`: [docs-hub-spoke-relation.md](docs-hub-spoke-relation.md) の `---` 以降を保存します。
   - `docs/client-access-patterns-relation.en.md`: [docs-hub-spoke-relation.en.md](docs-hub-spoke-relation.en.md) の `---` 以降を保存します。
   - 任意: `llms.txt` と `docs/index.md` に、[llms-txt-check.md](llms-txt-check.md) の文案を足します。足したら [PR-BODY.md](PR-BODY.md) の Changes の任意の行も確定させます。

3. worktree 内でゲートを走らせます（先に Hub の `make help` と `AGENTS.md` で現役のターゲットと前提ツールを確認します）。

   ```bash
   make drift
   python3 tools/ai_style_rules.py . --summary --fail
   python3 scripts/check_neutral_wording.py
   python3 scripts/check_doc_structural_parity.py --max-mismatches 50
   ```

   Hub の pre-commit が台帳など worktree にない前提で落ちるときは、`--no-verify` や回避の環境変数を使わず、ここで止まって報告します。

4. 変更を小さい conventional commit にします。例: `docs: add Client Access Patterns row to related repos`、`docs: add Hub and Spoke relation page`。件名は 72 文字以内で、個人名やペルソナ名を入れません。

5. 利用者の承認を得てから、次をします。
   - `git push origin docs/related-repos-client-access-patterns`
   - [PR-BODY.md](PR-BODY.md) の本文とタイトルで PR を作成

6. 終わったら worktree を片付けます。

   ```bash
   git -C <Hub のクローン> worktree remove ../fsxn-s3ap-relation
   ```

   削除後に `git worktree list` で消えたことを読み戻します。ブランチは PR がマージされるまで残します。

## 戻し方

PR 提出前なら、worktree を削除してからブランチを `git branch -d` で消します。マージ後は `git revert` します。

# Hub の `llms.txt` と他の索引に追記が要るかの確認

確認方法: Hub の作業ツリーでは何も実行せず、`git fetch origin` のあと `git show origin/main:<パス>` と `git grep origin/main` で読みました。実行したゲートはありません。

## 結論

| 対象 | 追記が要るか | 理由 |
|---|---|---|
| `README.md` / `README.en.md` の関連リポジトリ表 | 要る（[README-related-repositories.md](README-related-repositories.md)） | この PR の主目的 |
| `llms.txt` | 必須ではない。1 行足すのを推奨 | 冒頭の「Division of labour」節が隣接リポジトリを列挙しており、Spoke を足さないと Hub を読む AI が Spoke を知らない。ゲートは追記を要求しない（下の「新規ファイルが通すゲート」） |
| `docs/index.md` の `## 関連プロジェクト` 表 | 必須ではない。1 行足すのを推奨 | 同じ表が隣接リポジトリを一覧している。ja のみの文書 |
| `AGENTS.md` | 要らない | リポジトリ一覧はなく、Playbook へのリンクがあるだけ（`git grep` で確認） |
| `docs/i18n-manifest.toml` | 要らない | `docs/*.md` は `locales = "keep"` の規則に入る。新規の ja/en の組は義務を増やさず、既存の組として構造 parity の対象になるだけ |
| リンク検査の設定 | 要らない | 外部 URL の一覧は持たない。`repo-name-redirects.yml` は定期実行で、PR のゲートではない |

## `llms.txt` に足す場合の文案（任意）

「Division of labour」節の箇条書きの末尾に 1 つ足します。

```markdown
- [FSx-for-ONTAP-S3AccessPoints-Client-Access-Patterns](https://github.com/Yoshiki0705/FSx-for-ONTAP-S3AccessPoints-Client-Access-Patterns)
  holds client-tool setup steps, checklists, a compatibility matrix and measurement records for using
  FSx for ONTAP S3 Access Points from client tools. It links back to this repository for
  specifications and verification results ([relationship](docs/client-access-patterns-relation.en.md)).
```

`docs/index.md` に足す場合（表の列は 2 つ）:

```markdown
| [FSx-for-ONTAP-S3AccessPoints-Client-Access-Patterns](https://github.com/Yoshiki0705/FSx-for-ONTAP-S3AccessPoints-Client-Access-Patterns) | S3 Access Points をクライアントツールから使う手順、チェックリスト、互換性マトリクス、測定記録。[関係図](client-access-patterns-relation.md) |
```

## 新規ファイルが通すゲート（Hub `origin/main` の Makefile と CI から読んだもの）

| ゲート | 実行場所 | 新規ファイルへの要求 |
|---|---|---|
| `scripts/check_doc_pairs.py` | `make drift` | 言語切替の行が相互にあること。相対リンク先が git 管理下にあること。`llms.txt` も走査対象 |
| `scripts/check_i18n_parity.py --quiet` と `docs/i18n-manifest.toml` | `make drift` | `docs/*.md` は `keep`。ja と en の見出し構造が揃うこと |
| `scripts/check_doc_structural_parity.py --max-mismatches 50` | `agent-output-audit.yml` | 構造不一致の総数が上限以下。この下書きは ja/en で節の数を揃えてある |
| `scripts/sync_lang_switcher.py --check` | `make drift` | README の言語切替。README の行追加では切替部分を変えない |
| `scripts/check_en_doc_language.py` | `make drift` | `.en.md` に日本語が残らないこと。切替行は許可されている |
| `scripts/check_neutral_wording.py` | `make drift`、`agent-output-audit.yml` | 競合・優劣の語がないこと |
| 命名（`agent-output-audit.yml` の Naming 手順） | CI（変更ファイル） | FSx for ONTAP の表記。Hub の本文には略称の表記が残る箇所があるが、この下書きは略称を使わない |
| 公開物の漏えい、サポートケース番号 | CI（変更ファイル） | 個人名、ID、ケース番号がないこと |
| `tools/ai_style_rules.py --fail`（`ai-style.yml`） | CI | ja/en の新規ファイルの文体。fail 階層は D1、D2、D5、D14。下書きでは未実行 |
| `pr-title-check.yml` | CI | タイトルが conventional prefix で始まること |
| gitleaks | CI | 秘密情報がないこと |

## 未確認

- Hub の最新 `origin/main` で上記ゲートを実際に走らせた結果はありません（このセッションは Hub で何も実行しない条件）。適用時に [APPLY.md](APPLY.md) の手順で走らせてください。
- `check_doc_structural_parity.py` と命名手順の細部（許可語、対象拡張子）は、スクリプトの全文を読んでいません。
- Mermaid の描画は GitHub 上で確認していません。Hub の他文書も Mermaid を使っています（`git grep` で `README.md` を含む複数の文書にあることを確認）。`check_diagram_fonts.py` と `check_diagram_flow.py` は draw.io が対象と読めますが、Mermaid が対象外であることはスクリプトを読んで確かめていません。

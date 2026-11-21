# Playbook の索引への追記要否の確認

確認方法: Playbook の作業ツリーでは何も実行せず、`git show origin/main:<パス>` で読みました。読んだ `origin/main` は 2026-11-22（日本時間）に `git ls-remote` で先頭と一致を確認したコミット `038fef7` です。実行したゲートはありません。

## 結論

| 対象 | 追記が要るか | 理由 |
|---|---|---|
| `README.md` の「関連リポジトリ」表 | 要る（[README-related-repositories.md](README-related-repositories.md)） | この PR の主目的 |
| `docs/en/README.md` の同じ表 | 要る（同上） | ルートの README は 8 言語で検査される。日本語と英語は下書きあり |
| `docs/ko`、`zh-CN`、`zh-TW`、`fr`、`de`、`es` の README | 要る可能性が高い。下書きなし | 6 言語とも現在の表に最後の行（App-Modernization）を持つ。翻訳は Playbook の持ち主が決める |
| `docs/ja/reference/cross-repo-index.md` の「分担の原則」表 | 推奨 | 他の Spoke がここに行を持つ。ゲートは引用表だけを読み、この表は要求しない |
| `docs/ja/reference/cross-repo-index.md` の「引用表」 | 要らない | この PR は Spoke の `blob/` を引用しない。引用を足す PR で行を足す |
| `llms.txt` の「Sibling repositories」節 | 推奨（下の文案） | 節の説明が、兄弟リポジトリを AI に知らせる場所だと書いている。`llms.txt` を持たない兄弟は README へリンクする規則 |
| `docs/agent/inbound-probe-contract.txt` | 要らない | 他リポジトリが Playbook に固定した文字列の一覧で、生成物。Spoke は固定した文字列を持たない |
| `docs/ja/reference/performance-evidence-map.md` | 要らない | Spoke は測定値を持たない。測定値が入った時点で行を足す |
| `AGENTS.md` | 要らない | Spoke の一覧を持たない（`git grep` で確認） |
| `docs/i18n-manifest.txt` | 要らない | 対象は `docs/<lang>/` の Tier 1 文書で、ルート README は一覧に載らず常に全言語で検査される |

## `llms.txt` に足す場合の文案（任意）

「Sibling repositories」節の箇条書きの末尾に 1 つ足します。`llms.txt` を持たない兄弟のため、リンク先はリポジトリのトップです。

```markdown
- [S3 Access Points client access patterns](https://github.com/Yoshiki0705/FSx-for-ONTAP-S3AccessPoints-Client-Access-Patterns): Setup steps, manual checklists, a compatibility matrix and measurement records for using FSx for ONTAP S3 Access Points from client tools (AWS CLI, rclone, Mountpoint for Amazon S3, MCP clients and others). Currently an unconfirmed scaffold with no measurements. It defers S3 Access Points specifications and limits to this repository. It publishes no llms.txt.
```

## 新規の追記が通すゲート（Playbook の `origin/main` の Makefile から読んだもの）

| ゲート | 追記への要求（読めた範囲） |
|---|---|
| `cross-repo` | 本文の `blob/` リンクが引用表に載っていること。この下書きの行は `blob/` を使わないので対象外 |
| `cross-repo-external` | 本文に現れる兄弟リポジトリの名前を GitHub の API で引く。Spoke が作られるまで失敗する見込み |
| `audit` | 命名、中立性、PII、内部 ID。下書きは「FSx for ONTAP」「S3 Access Points」の表記で、優劣の語を使わない |
| `i18n-check` | ルート README と各言語 README の整合。**6 言語に行がないと失敗するかは未確認** |
| `switcher-check`、`ja-markers` | 言語切替と、英語から日本語のみの文書へのリンクの注記。下書きは日本語のみの文書へリンクしない |
| `headings` | 日本語の節見出しが名詞句であること。下書きは見出しを足さない |
| `links` | 内部リンクの解決。下書きの相対リンク（`../domains/client-access/notes/...`）は、`cross-repo-index.md` から `origin/main` に実在することを確認済み |
| `anchors` | 外部から引用された節見出しの改名を検知する。下書きは Playbook の見出しを変えない |
| `pr-title-check` | タイトルが conventional prefix で始まること |

## 未確認

- 上のゲートを Playbook で実行した結果はありません（Playbook の作業ツリーに触れない条件）。適用時に [APPLY.md](APPLY.md) の手順で走らせてください。
- `i18n-check` がルート README の「関連リポジトリ」表の行数まで比べるかは、スクリプトの全文を読んでいません。
- `tools/ai_style_rules.py` など文体の検査が、表のセルにどこまで及ぶかは確認していません。

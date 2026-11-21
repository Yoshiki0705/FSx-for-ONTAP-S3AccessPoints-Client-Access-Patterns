# Hub README「関連リポジトリ」表に加える 1 行 / Row for the Hub README related-repositories table

> 下書きです。Hub には適用していません。適用手順は [APPLY.md](APPLY.md)。 / Draft. Not applied to Hub. Steps are in [APPLY.md](APPLY.md).

## 対象 / Scope

| ファイル / File | 表の見出し / Table heading | 列 / Columns |
|---|---|---|
| Hub `README.md`（日本語） | `### 関連リポジトリ` | `リポジトリ` / `概要` |
| Hub `README.en.md` | `### Related Repositories` | `Repository` / `Summary` |

他の 6 言語（`README.de.md`、`README.es.md`、`README.fr.md`、`README.ko.md`、`README.zh-CN.md`、`README.zh-TW.md`）は、この下書きでは触りません。Hub の持ち主が別途決めます。 / The other six languages are not touched by this draft. The Hub owner decides them separately.

挿入位置は、既存の `FSx-for-ONTAP-App-Modernization-Patterns` の行の直後です（S3 Access Points を使う側の 2 行を並べるため）。位置は Hub の持ち主が変えてかまいません。 / Insert directly after the `FSx-for-ONTAP-App-Modernization-Patterns` row. The Hub owner may move it.

## 日本語（`README.md`）

```markdown
| [FSx-for-ONTAP-S3AccessPoints-Client-Access-Patterns](https://github.com/Yoshiki0705/FSx-for-ONTAP-S3AccessPoints-Client-Access-Patterns) | FSx for ONTAP S3 Access Points をクライアントツール（AWS CLI、rclone、Mountpoint for Amazon S3、MCP クライアント等）から使うときの手順、チェックリスト、互換性マトリクス、測定記録（現状は確認前の雛形で、未測定）。S3 Access Points の仕様と検証結果はこのリポジトリを参照する。[関係図](docs/client-access-patterns-relation.md) |
```

## English（`README.en.md`）

```markdown
| [FSx-for-ONTAP-S3AccessPoints-Client-Access-Patterns](https://github.com/Yoshiki0705/FSx-for-ONTAP-S3AccessPoints-Client-Access-Patterns) | Setup steps, checklists, a compatibility matrix and measurement records for using FSx for ONTAP S3 Access Points from client tools (AWS CLI, rclone, Mountpoint for Amazon S3, MCP clients and others). Currently an unconfirmed scaffold with no measurements. It links to this repository for S3 Access Points specifications and verification results. See the [relationship diagram](docs/client-access-patterns-relation.en.md) |
```

## 書式の確認 / Format check

- 列数は 2 で、既存の行と同じです。リンク先の `docs/client-access-patterns-relation*.md` は、同じ PR で追加する新規文書です（[docs-hub-spoke-relation.md](docs-hub-spoke-relation.md)）。 / Two columns, same as existing rows. The `docs/client-access-patterns-relation*.md` targets are new documents added by the same PR.
- 「FSx for ONTAP」は、Hub の README で既に正式名称が先に出ているため略称で書いています。 / The short name is used because the Hub README already gives the full name earlier.
- Spoke のリポジトリ URL は、段階 4 で作るまで存在しません。[README.md](README.md) を参照。 / The Spoke URL does not exist until stage 4. See [README.md](README.md).

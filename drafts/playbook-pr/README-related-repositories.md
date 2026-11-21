# Playbook の表に加える行 / Rows to add to the Playbook tables

> 下書きです。Playbook には適用していません。適用手順は [APPLY.md](APPLY.md)。 / Draft. Not applied to the Playbook. Steps are in [APPLY.md](APPLY.md).

## 対象 / Scope

| ファイル / File | 表の見出し / Table heading | 列 / Columns |
|---|---|---|
| Playbook `README.md`（日本語） | `## 関連リポジトリ — 判断の場所と実装の場所` | `ここで決まったこと` / `移る先` / `そちらにあるもの` |
| Playbook `docs/en/README.md` | 同じ節の英語版 / the English counterpart | `Decided here` / `Go to` / `What it holds` |
| Playbook `docs/ja/reference/cross-repo-index.md` | `## 分担の原則` | `種類` / `どこが持つか` / `このリポジトリの役割` |

挿入位置は、関連リポジトリ表では最後の行（`FSx-for-ONTAP-App-Modernization-Patterns`）の直後です。分担の原則の表では、コンテナのデータストアの行（`FSx-for-ONTAP-Container-Datastore-Patterns`）の直後、`最小構成を動かす手順` の行の前です。位置は Playbook の持ち主が変えてかまいません。 / Insert after the last row of the related-repositories table, and after the container datastore row in the division-of-labour table. The Playbook owner may move them.

行には Spoke の **リポジトリのトップ URL** だけを書き、`blob/` のリンクは書きません。`blob/` のリンクは Playbook の引用表への登録（確認する文字列つき）が要る引用になるためです。 / Each row links only to the Spoke repository root. A `blob/` link would be a citation that must be registered in the citation table with a probe string.

## 日本語（`README.md`）

```markdown
| **FSx for ONTAP の S3 Access Points を、クライアントツール（AWS CLI、rclone、Mountpoint for Amazon S3、MCP クライアント等）から使う** | [FSx-for-ONTAP-S3AccessPoints-Client-Access-Patterns](https://github.com/Yoshiki0705/FSx-for-ONTAP-S3AccessPoints-Client-Access-Patterns) | ツール別の手順、手動チェックリスト、互換性マトリクス、測定記録。**現状は確認前の雛形で、測定値はありません。** S3 Access Points の仕様と上限はこのリポジトリを参照する分担です |
```

## English（`docs/en/README.md`）

```markdown
| **Using FSx for ONTAP S3 Access Points from client tools (AWS CLI, rclone, Mountpoint for Amazon S3, MCP clients and others)** | [FSx-for-ONTAP-S3AccessPoints-Client-Access-Patterns](https://github.com/Yoshiki0705/FSx-for-ONTAP-S3AccessPoints-Client-Access-Patterns) | Per-tool setup steps, manual checklists, a compatibility matrix and measurement records. **Currently an unconfirmed scaffold with no measurements.** S3 Access Points specifications and limits are referenced back to this repository |
```

## 分担の原則の行（`docs/ja/reference/cross-repo-index.md`）

```markdown
| S3 Access Points をクライアントツールから使う手順、チェックリスト、互換性マトリクス、測定記録 | [FSx-for-ONTAP-S3AccessPoints-Client-Access-Patterns](https://github.com/Yoshiki0705/FSx-for-ONTAP-S3AccessPoints-Client-Access-Patterns) | S3 Access Points の仕様と上限、端末から届く条件（[端末から S3 Access Points に届くには何が要るか](../domains/client-access/notes/what-an-endpoint-needs-to-reach-s3-access-points.md)）を持つ。ツール別の確認結果は持たない |
```

## 書式の確認 / Format check

- 関連リポジトリ表の列数は 3 で、既存の行と同じです。分担の原則の表の列数も 3 です。 / Three columns in both tables, as in the existing rows.
- 「FSx for ONTAP」は、Playbook の README で正式名称が先に出ているため略称で書いています。 / The short name is used because the Playbook README gives the full name earlier.
- 「判断を扱うのはこのリポジトリ、実装と測定は各リポジトリ」という README 冒頭の分担に合わせ、行の第 3 列は「持つもの」を書き、優劣の表現を使っていません。 / The third column states what the repository holds and makes no comparative claim.
- Spoke のリポジトリ URL は、段階 4 で作るまで存在しません。[README.md](README.md) を参照。 / The Spoke URL does not exist until stage 4.

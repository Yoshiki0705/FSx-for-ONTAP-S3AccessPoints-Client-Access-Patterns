# 参照の固定（Reference pins）

このリポジトリは、Playbook 配下の Spoke の 1 つです。参照する他リポジトリは 2 つで、固定の方式がそれぞれ違います。固定した値は、このファイルの 1 か所だけに書きます。他の文書やワークフローに値を書くときは、`make drift` の `check_pins` がこのファイルの値と照合します。

| 参照先 | 役割 | 固定の方式 |
|---|---|---|
| [FSx-for-ONTAP-Adoption-Playbook](https://github.com/Yoshiki0705/FSx-for-ONTAP-Adoption-Playbook)（以下 Playbook） | 全体の入口。FSx for ONTAP のコア仕様のうち、他サービスとの選定に影響するもの、S3 Access Points の仕様と上限、横断の規約を持つ | コミット SHA（Playbook にはリリースタグがない） |
| [FSx-for-ONTAP-S3AccessPoints-Serverless-Patterns](https://github.com/Yoshiki0705/FSx-for-ONTAP-S3AccessPoints-Serverless-Patterns)（以下 Serverless-Patterns） | このリポジトリの兄弟の Spoke。後続のサーバーレス処理の実装を持つ | リリースタグ |

## 固定している値

Playbook pinned commit: `038fef7fb6ad3c5d0fabae7580f4983343504c70`
Serverless-Patterns pinned tag: `v10.0.0-portal-line-icons-and-deps`
Serverless-Patterns pinned commit: `7fe6ee62366aff0e7b944bc8eb719f872c95b477`

| 項目 | 値 |
|---|---|
| Playbook の固定コミットの確認日 | 2026-11-22（日本時間）。`git ls-remote` で `main` の先頭と一致することを確認 |
| Serverless-Patterns のタグの作成日 | 2026-11-11（`git tag --sort=-creatordate` で確認） |
| Serverless-Patterns の固定を確認した日 | 2026-11-21（日本時間） |
| 比較方法 | 文字列の一致のみ。版の大小では比較しない |
| 互換性マトリクスの「固定した Playbook コミット」列 | 上の Playbook のコミット SHA の先頭 12 桁 |

リンクは次の形で書きます。`blob/main/` は使いません。

- Playbook: `https://github.com/Yoshiki0705/FSx-for-ONTAP-Adoption-Playbook/blob/<固定コミットの 40 桁>/<パス>`
- Serverless-Patterns: `https://github.com/Yoshiki0705/FSx-for-ONTAP-S3AccessPoints-Serverless-Patterns/blob/<固定タグ>/<パス>`

Issue の起票用リンク（`issues/new?template=...`）は文書ではないので固定の対象外です。

## 固定の追従手順

新しい固定先ができたときだけ行います。Playbook は `main` が進み続けるため、追従の時期は利用者が決めます。

1. 旧固定と新固定の差分を、このリポジトリが参照している文書だけについて読む（`git diff <旧> <新> -- <参照している文書>`）。
2. 参照先が移動または削除されていれば、リンクを直す。
3. S3 Access Points の仕様や上限が変わっていれば、影響を受ける互換性マトリクスの行を特定し、再確認が済むまで `stale` として扱う。
4. このファイルの値を更新し、全リンクを一括で置換する。この変更は 1 つのコミットにまとめる（戻すときは `git revert`）。
5. `make drift` を通す。ネットワークを使う `make drift-pins` で、固定先の実在と記録の一致を確認する。
6. 下の更新履歴に 1 行足す。参照先の文書に変更がなかった場合も、差分を読んだ記録を残す。

## 更新履歴

| 日付（日本時間） | 参照先 | 固定 | 差分の確認 |
|---|---|---|---|
| 2026-11-21 | Serverless-Patterns | `v10.0.0-portal-line-icons-and-deps` | 初回の固定。比較対象の旧タグなし |
| 2026-11-22 | Playbook | `038fef7fb6ad` | 初回の固定。比較対象の旧コミットなし。参照元の定義を Playbook 起点の 3 層へ変更した |

## English summary

This file is the only place that records the pins. The repository is one Spoke under the Playbook. Playbook links must use `blob/<pinned commit SHA>/` because the Playbook publishes no release tags. Serverless-Patterns links, a sibling Spoke, must use `blob/<pinned release tag>/`. `blob/main/` is never allowed. The matrix column "Pinned Playbook commit" holds the first 12 hex digits of the Playbook SHA. When a pin moves, follow the steps above: read the diff of the referenced documents, fix moved links, mark affected matrix rows `stale`, update the values in one commit, run `make drift` and `make drift-pins`, and add a history row.

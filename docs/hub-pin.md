# Hub 固定タグ（Hub pin）

このリポジトリが参照する Hub（[FSx-for-ONTAP-S3AccessPoints-Serverless-Patterns](https://github.com/Yoshiki0705/FSx-for-ONTAP-S3AccessPoints-Serverless-Patterns)）のタグは、このファイルの 1 か所だけに書く。他の文書やワークフローにタグ文字列を書くときは、`make drift` の `check_hub_pin` がこのファイルの値と照合する。

## 固定している値

Pinned tag: `v10.0.0-portal-line-icons-and-deps`
Pinned commit: `7fe6ee62366aff0e7b944bc8eb719f872c95b477`

| 項目 | 値 |
|---|---|
| タグの作成日 | 2026-11-11（Hub の `git tag --sort=-creatordate` で確認） |
| この固定を確認した日 | 2026-11-21（日本時間） |
| 比較方法 | 文字列の一致のみ。タグ名は版の大小で比較しない |

Hub へのリンクは、すべて `https://github.com/Yoshiki0705/FSx-for-ONTAP-S3AccessPoints-Serverless-Patterns/blob/<固定タグ>/<パス>` の形で書く。`blob/main/` は使わない。

## 固定タグの追従手順

Hub に新しいタグが付いたときだけ行う。新しいタグがない間は固定を動かさない。

1. 旧タグと新タグの差分を、Spoke が参照している Hub 文書だけについて読む（`git diff <旧タグ> <新タグ> -- <参照している文書>`）。
2. 参照先が移動または削除されていれば、リンクを直す。
3. S3 Access Points の仕様や上限が変わっていれば、影響を受ける互換性マトリクスの行を特定し、再確認が済むまで `stale` として扱う。
4. このファイルのタグとコミット SHA を更新し、全リンクを一括で置換する。この変更は 1 つのコミットにまとめる（戻すときは `git revert`）。
5. `make drift` を通す。ネットワークを使う `make drift-hub` で、タグの実在と SHA の一致を確認する。
6. 下の更新履歴に 1 行足す。Hub 文書に変更がなかった場合も、差分を読んだ記録を残す。

## 更新履歴

| 日付（日本時間） | タグ | 差分の確認 |
|---|---|---|
| 2026-11-21 | `v10.0.0-portal-line-icons-and-deps` | 初回の固定。比較対象の旧タグなし |

## English summary

The only place that records the Hub tag is this file (`Pinned tag` and `Pinned commit` above). Every Hub link in this repository must use `blob/<pinned tag>/`, never `blob/main/`. When Hub publishes a new tag, follow the steps in the Japanese section above: read the diff of the referenced documents, fix moved links, mark affected matrix rows `stale`, update the pin in one commit, run `make drift` and `make drift-hub`, and add a history row.

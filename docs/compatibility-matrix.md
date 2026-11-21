# 互換性マトリクス

クライアントツールが FSx for ONTAP の S3 Access Points に対して行う操作の確認状況です。全セルが `candidate`（未確認）で、数値はありません。

> **読み方**: セルの先頭の記号が確認水準です。`C` は未確認、`D` は公式ドキュメントで確認（URL と確認日）、`M` は実行して確認（記録へのリンク）、`-` は対象外です。S3 Access Points 自体の上限は、このマトリクスに書かず [Hub の互換性ノート](https://github.com/Yoshiki0705/FSx-for-ONTAP-S3AccessPoints-Serverless-Patterns/blob/v10.0.0-portal-line-icons-and-deps/docs/s3ap-compatibility-notes.md) を参照してください。

## 凡例

| 記号 | 水準 | セルの書き方 |
|---|---|---|
| `C` | `candidate` | `C` だけを書く。数値は書かない |
| `D` | `documented` | `D` と公式 URL と確認日（YYYY-MM-DD） |
| `M` | `measured` | `M` と測定記録またはチェックリスト記録へのリンク |

## 取り込み・転送ツール

| ツール | 一覧 | 取得 | 書き込み | マルチパート | 削除 | マウント時の挙動 | 確認日 | 固定 Hub タグ | 出典 |
|---|---|---|---|---|---|---|---|---|---|
| AWS CLI（版は未確認） | C | C | C | C | C | - | - | - | - |
| rclone（版は未確認） | C | C | C | C | C | - | - | - | - |
| s5cmd（版は未確認） | C | C | C | C | C | - | - | - | - |
| AWS Transfer Family（版は未確認） | C | C | C | C | C | - | - | - | - |
| File Mover Express（版は未確認） | C | C | C | C | C | - | - | - | - |

## ストリーミング・マウントツール

| ツール | 一覧 | 取得 | 書き込み | マルチパート | 削除 | マウント時の挙動 | 確認日 | 固定 Hub タグ | 出典 |
|---|---|---|---|---|---|---|---|---|---|
| Mountpoint for Amazon S3（版は未確認） | C | C | C | C | C | C | - | - | - |
| rclone mount（版は未確認） | C | C | C | C | C | C | - | - | - |
| LucidLink Connect（版は未確認） | C | C | C | C | C | C | - | - | - |
| LucidLink Suite（版は未確認） | C | C | C | C | C | C | - | - | - |

## 更新の手順

1. 確認した操作のセルを `C` から `D` または `M` に変え、確認日と固定 Hub タグを同じ行に書く。
2. `make drift` の `check_matrix` を通す。
3. Hub の固定タグを更新したときは、影響を受けた行を `stale` として再確認する（[docs/hub-pin.md](hub-pin.md)）。

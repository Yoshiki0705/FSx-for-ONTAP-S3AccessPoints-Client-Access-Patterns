# 互換性マトリクス

クライアントツールが FSx for ONTAP の S3 Access Points に対して行う操作の確認状況です。実機で確認したセルは `M` で、記録へリンクしています。それ以外は `candidate`（未確認）です。数値はありません。

> **読み方**: セルの先頭の記号が確認水準です。`C` は未確認、`D` は公式ドキュメントで確認（URL と確認日）、`M` は実行して確認（記録へのリンク）、`-` は対象外です。S3 Access Points 自体の上限は、このマトリクスに書かず [Playbook の S3 Access Points の制約ノート](https://github.com/Yoshiki0705/FSx-for-ONTAP-Adoption-Playbook/blob/a4c8367f9172ee88f0af25731752af63dc2c6225/docs/ja/domains/data-utilization/notes/s3-access-point-constraints.md) を参照してください。

## 凡例

| 記号 | 水準 | セルの書き方 |
|---|---|---|
| `C` | `candidate` | `C` だけを書く。数値は書かない |
| `D` | `documented` | `D` と公式 URL と確認日（YYYY-MM-DD） |
| `M` | `measured` | `M` と測定記録またはチェックリスト記録へのリンク |

## 取り込み・転送ツール

| ツール | 一覧 | 取得 | 書き込み | マルチパート | 削除 | マウント時の挙動 | 確認日 | 固定した Playbook コミット | 出典 |
|---|---|---|---|---|---|---|---|---|---|
| AWS CLI 2.38.0 | M [記録](../benchmarks/records/2026-11-24-client-tools-stage3.md) | M [記録](../benchmarks/records/2026-11-24-client-tools-stage3.md) | M [記録](../benchmarks/records/2026-11-24-client-tools-stage3.md) | M [記録](../benchmarks/records/2026-11-24-client-tools-stage3.md) | M [記録](../benchmarks/records/2026-11-24-client-tools-stage3.md) | - | 2026-11-24 | a4c8367f9172 | [2026-11-24 の記録](../benchmarks/records/2026-11-24-client-tools-stage3.md) |
| rclone v1.76.0 | M [記録](../benchmarks/records/2026-11-24-client-tools-stage3.md) | M [記録](../benchmarks/records/2026-11-24-client-tools-stage3.md) | M [記録](../benchmarks/records/2026-11-24-client-tools-stage3.md) | C | M [記録](../benchmarks/records/2026-11-24-client-tools-stage3.md) | - | 2026-11-24 | a4c8367f9172 | [2026-11-24 の記録](../benchmarks/records/2026-11-24-client-tools-stage3.md) |
| s5cmd v2.3.0 | M [記録](../benchmarks/records/2026-11-24-client-tools-stage3.md) | M [記録](../benchmarks/records/2026-11-24-client-tools-stage3.md) | M [記録](../benchmarks/records/2026-11-24-client-tools-stage3.md) | C | M [記録](../benchmarks/records/2026-11-24-client-tools-stage3.md) | - | 2026-11-24 | a4c8367f9172 | [2026-11-24 の記録](../benchmarks/records/2026-11-24-client-tools-stage3.md) |
| AWS Transfer Family（版は未確認） | C | C | C | C | C | - | - | - | - |
| File Mover Express（版は未確認） | C | C | C | C | C | - | - | - | - |

## ストリーミング・マウントツール

| ツール | 一覧 | 取得 | 書き込み | マルチパート | 削除 | マウント時の挙動 | 確認日 | 固定した Playbook コミット | 出典 |
|---|---|---|---|---|---|---|---|---|---|
| Mountpoint for Amazon S3 1.24.0 | M [記録](../benchmarks/records/2026-11-24-client-tools-stage3.md) | M [記録](../benchmarks/records/2026-11-24-client-tools-stage3.md) | M [記録](../benchmarks/records/2026-11-24-client-tools-stage3.md) | M [記録](../benchmarks/records/2026-11-24-client-tools-stage3.md) | M [記録](../benchmarks/records/2026-11-24-client-tools-stage3.md) | M [記録](../benchmarks/records/2026-11-24-client-tools-stage3.md) | 2026-11-24 | a4c8367f9172 | [2026-11-24 の記録](../benchmarks/records/2026-11-24-client-tools-stage3.md) |
| rclone mount（版は未確認） | C | C | C | C | C | C | - | - | - |
| LucidLink Connect（版は未確認） | C | C | C | C | C | C | - | - | - |
| LucidLink Suite（版は未確認） | C | C | C | C | C | C | - | - | - |

## ツールが使う S3 操作と対応表の照合

左の列は AWS の対応表（[Access point compatibility](https://docs.aws.amazon.com/fsx/latest/ONTAPGuide/access-points-for-fsxn-object-api-support.html)、2026-11-24 に閲覧）の記載です。ツールの列は、そのツールがその操作を発行するかどうかで、全セル `C`（未実測）です。文書から読み取れた範囲は [ツールの事実確認](tool-facts.md) にあります。

| S3 操作 | AWS の対応表 | AWS CLI | s5cmd | rclone | Mountpoint for Amazon S3 |
|---|---|---|---|---|---|
| ListObjectsV2 | 対応 | M | C | C | M |
| GetObject と HeadObject | 対応 | M | C | C | M |
| PutObject | 対応 | M | C | M | M |
| マルチパート（CreateMultipartUpload、UploadPart、CompleteMultipartUpload、AbortMultipartUpload） | 対応 | M | C | C | M |
| CopyObject（同一リージョン） | 対応 | M | C | M | C |
| UploadPartCopy（同一リージョン） | 対応 | M | C | C | C |
| DeleteObject と DeleteObjects | 対応 | C | C | C | M |
| GetObjectTagging と PutObjectTagging | 対応 | M | C | C | C |
| HeadBucket と GetBucketLocation | 対応 | C | C | C | C |
| 条件付き書き込み（`If-None-Match`、`If-Match`） | 未対応 | M | C | C | C |
| ListObjectVersions | 未対応 | C | C | C | C |

> **照合の読み方**: 「AWS の対応表」が未対応の操作をツールが発行すると、その操作は失敗するはずです。たとえば `aws s3 cp --no-overwrite` がどの方式で上書きを防ぐかは文書に書かれておらず、条件付き書き込みを使うなら失敗しえます。段階 3 で、対応表が未対応とする行を発行するかをツールごとに確かめます。

> **実測で埋めたセル**: `M` のセルは、そのツールがその操作を発行したことを、ツールのデバッグログで確かめたものです（[2026-11-24 の記録](../benchmarks/records/2026-11-24-client-tools-stage3.md)）。s5cmd はログに API 名が出ないため `C` のままです。AWS CLI は `aws s3 cp --no-overwrite` で `If-None-Match` を送り、アクセスポイントは `NotImplemented` を返しました。

## 更新の手順

1. 確認した操作のセルを `C` から `D` または `M` に変え、確認日と固定した Playbook コミット（SHA の先頭 12 桁）を同じ行に書く。
2. `make drift` の `check_matrix` を通す。
3. Playbook の固定コミットを更新したときは、影響を受けた行を `stale` として再確認する（[docs/reference-pins.md](reference-pins.md)）。

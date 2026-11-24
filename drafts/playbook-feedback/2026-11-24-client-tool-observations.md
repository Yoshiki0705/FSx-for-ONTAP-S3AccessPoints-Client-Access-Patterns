# Playbook フィードバック下書き / Playbook feedback draft

> 提出は利用者の承認後です。顧客名、アカウント ID、リソース ID、実際のアクセスポイント別名を書きません。 / Submit only after the user approves. Do not write customer names, account IDs, resource IDs, or real access point aliases.

- 種別 / Kind: Issue
- 宛先 / Destination: Playbook
- 状態 / Status: 下書き / draft
- 関係する文書と節 / Related document and section: https://github.com/Yoshiki0705/FSx-for-ONTAP-Adoption-Playbook/blob/038fef7fb6ad3c5d0fabae7580f4983343504c70/docs/ja/domains/data-utilization/notes/s3-access-point-constraints.md#パターンごと成立しない-4-つの不在 （条件付き書き込み）と、未マージのサーバー側コピーの節 / (conditional writes) and the unmerged server-side copy section

## 観測した事実 / Observed facts

1. `aws s3 cp --no-overwrite` は `If-None-Match: *` を付けた `PutObject` を送る。FSx for ONTAP のアクセスポイントは `NotImplemented`（A header you provided implies functionality that is not implemented）を返し、アップロードは失敗した。同じ回の通常のバケットでは成功した。 / `aws s3 cp --no-overwrite` sends `PutObject` with `If-None-Match: *`. The FSx for ONTAP access point returned `NotImplemented` and the upload failed. It succeeded on an ordinary bucket in the same run.
2. `rclone copyto` のサーバー側コピー（バケットからアクセスポイント）は、コピー元の `X-Amz-Storage-Class: STANDARD` を付けた `CopyObject` を送り、`InvalidStorageClass` で失敗した。`--s3-storage-class FSX_ONTAP` を付けると成功し、中身のハッシュが一致した。 / rclone's server-side copy (bucket to access point) sent `CopyObject` with the source's `X-Amz-Storage-Class: STANDARD` and failed with `InvalidStorageClass`. With `--s3-storage-class FSX_ONTAP` it succeeded and the content hash matched.

どちらも、対応表に書かれた制約（条件付き書き込みの非対応、ストレージクラスは `FSX_ONTAP` だけ）の帰結で、新しい制約ではない。クライアントツールの既定の動作がこの制約に当たる、という点が設計に関わる。 / Both follow from documented constraints (no conditional writes; `FSX_ONTAP` as the only storage class). They are not new constraints. What matters for design is that a client tool's default behavior hits them.

## 再現手順 / Steps to reproduce

Spoke の段階 3 の手順書と `stage3-measure.sh --case aws-cli`、`--case server-side-copy`。 / The Spoke stage 3 runbook with `stage3-measure.sh --case aws-cli` and `--case server-side-copy`.

## 環境 / Environment

2026-11-24（日本時間）、ap-northeast-1、第 1 世代 `SINGLE_AZ_1`、128 MBps、検証専用の UNIX ボリューム、VPC 起点のアクセスポイント、EC2 c6in.xlarge（Amazon Linux 2023）、AWS CLI 2.38.0、rclone 1.76.0。ONTAP の版は確認していない。各操作 1 回。 / 2026-11-24 (JST), ap-northeast-1, Gen1 `SINGLE_AZ_1`, 128 MBps, dedicated UNIX volume, VPC-origin access point, EC2 c6in.xlarge (Amazon Linux 2023), AWS CLI 2.38.0, rclone 1.76.0. ONTAP version not checked. One run per operation.

## 成功した対照 / Control that succeeded

同じ回、同じ操作を通常の S3 汎用バケットで実行して成功した。アクセスポイントへの `--no-overwrite` なしの `aws s3 cp` と、`aws s3api copy-object` も成功した。 / In the same run the same operations succeeded on an ordinary general purpose bucket. `aws s3 cp` without `--no-overwrite` and `aws s3api copy-object` to the access point also succeeded.

## 提案する変更 / Proposed change

制約ノートの「条件付き書き込み」の行と、サーバー側コピーの節に、クライアントツールの既定動作が当たる例として 1 文ずつ加え、Spoke の記録へリンクする（Spoke の記録を公開した後）。 / Add one sentence each to the conditional-writes row and the server-side copy section as examples where a client tool's default behavior hits the constraint, linking to the Spoke record (after the Spoke record is published).

## 公開安全の確認 / Public safety check

- [x] 顧客名、個人名、アカウント ID、リソース ID、別名、ケース番号を含まない / No customer or personal names, account IDs, resource IDs, aliases, or case numbers
- [x] `make drift` が通る / `make drift` passes

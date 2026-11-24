# s5cmd: クライアントアクセスパターン

🌐 **言語**: **日本語** | [English](README.en.md)

> **確認水準**: 版と README の記載は公式文書で確認（`D`、2026-11-24）。FSx for ONTAP のアクセスポイントを受け付けるかは文書に記載がなく、未実測（`C`）です。 実測（2026-11-24）: `--endpoint-url` なしでエイリアスを受け付け、`cp`、取得、`rm` が通り、中身のハッシュが一致した。バケットからアクセスポイントへの `cp` は、クライアントをデータが通らない形（送受信 27,340 バイト）で完了した。

## 概要と対象の利用場面

並列度の高い一括の取得、アップロード、S3 から S3 へのコピーを `s5cmd` で行います。バケットとアクセスポイントの間のサーバー側コピー（[サーバー側コピー](../../../docs/server-side-copy.md)）を発行するかの確認も対象です。

## 前提

S3 Access Points の前提と上限は [Playbook の S3 Access Points の制約ノート](https://github.com/Yoshiki0705/FSx-for-ONTAP-Adoption-Playbook/blob/a4c8367f9172ee88f0af25731752af63dc2c6225/docs/ja/domains/data-utilization/notes/s3-access-point-constraints.md) を参照してください。このページには書き写しません。ツールの版と出典は [ツールの事実確認](../../../docs/tool-facts.md) にあります。

## 構成と流れ

`s5cmd` は AWS SDK を通して S3 のエンドポイントへ HTTPS で届きます。README は、アップロードの完全性を `Content-MD5` と `X-Amz-Content-Sha256` で検証すると書いています（[README](https://github.com/peak/s5cmd/blob/master/README.md)、2026-11-24 に閲覧）。FSx for ONTAP のアクセスポイントは、チェックサムを保存しません（[Access point compatibility](https://docs.aws.amazon.com/fsx/latest/ONTAPGuide/access-points-for-fsxn-object-api-support.html)）。両者の関係は未確認です（`C`）。

## 設定手順

アクセスポイントの ARN またはエイリアスの指定方法は、README に記載がありません（`C`）。エイリアスをバケット名の位置に置く形を、段階 3 で試します。

```bash
s5cmd ls s3://<エイリアス>/
```

S3 Access Points は仮想ホスト形式だけを受け付けます（[Referencing access points](https://docs.aws.amazon.com/fsx/latest/ONTAPGuide/referencing-access-points-for-fsxn.html)）。README によると、`--endpoint-url` を指定するとパススタイルに戻るので、`--endpoint-url` を付けない形で試します。

## 確認手順

[段階 3 の手順書](../../../benchmarks/stage3-runbook.md)の s5cmd の項で行います。成功するはずの対照として、先に AWS CLI で同じエイリアスを一覧します。

## 既知の制約

- アクセスポイント側の制約は Playbook にあります。
- S3 から S3 へのコピーは、README によるとサーバー側で行われ、5 GB を超えるオブジェクトは未対応です。FSx for ONTAP 側のアップロードのサイズ上限は Playbook にあります。
- 最新のリリースは v2.3.0（2024-12-16）です。

## 選び方

| 項目 | 内容 |
|---|---|
| 向く場面 | 並列度の高い一括転送。S3 から S3 のコピーの確認 |
| 制約 | アクセスポイントを受け付けるか未確認。5 GB を超えるサーバー側コピーは未対応 |
| 他の選択肢 | [選び方](../../../docs/how-to-choose.md) |

## 後片付けと戻し方

クライアント側に残るものはありません。段階 3 で作ったリソースの削除は、手順書の後片付けの台本に従います。

## 確認水準と出典

| 項目 | 水準 | 出典 |
|---|---|---|
| 現行版（v2.3.0） | `D` | [s5cmd リリース](https://github.com/peak/s5cmd/releases)、2026-11-24 |
| S3 から S3 のコピー、`--endpoint-url` の挙動 | `D` | [README](https://github.com/peak/s5cmd/blob/master/README.md)、2026-11-24 |
| 設定手順 | `C` | - |
| 確認手順 | `M` | [2026-11-24 の記録](../../../benchmarks/records/2026-11-24-client-tools-stage3.md) |

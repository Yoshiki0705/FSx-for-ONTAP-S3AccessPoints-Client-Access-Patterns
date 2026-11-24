# AWS CLI: クライアントアクセスパターン

🌐 **言語**: **日本語** | [English](README.en.md)

> **確認水準**: 設定手順の書式は公式文書で確認（`D`、2026-11-24）。FSx for ONTAP のアクセスポイントに対する動作は未実測（`C`）です。 実測（2026-11-24）: エイリアスと ARN の両方で `ls`、`cp`（64 MiB はマルチパート）、`sync`、`rm` が通り、中身のハッシュが一致した。`--no-overwrite` は `If-None-Match` を送るため `NotImplemented` で失敗した。バケットからアクセスポイントへの `aws s3 cp` は `UploadPartCopy` のサーバー側コピーになった。

## 概要と対象の利用場面

`aws s3` と `aws s3api` で、アクセスポイントへ読み書きとコピーを行います。スクリプトや定期ジョブでの一括転送と、バケットとアクセスポイントの間のサーバー側コピー（[サーバー側コピー](../../../docs/server-side-copy.md)）が対象です。

## 前提

S3 Access Points の前提と上限は [Playbook の S3 Access Points の制約ノート](https://github.com/Yoshiki0705/FSx-for-ONTAP-Adoption-Playbook/blob/a4c8367f9172ee88f0af25731752af63dc2c6225/docs/ja/domains/data-utilization/notes/s3-access-point-constraints.md) を参照してください。このページには書き写しません。ツールの版と出典は [ツールの事実確認](../../../docs/tool-facts.md) にあります。

## 構成と流れ

クライアントの IAM 認証情報で S3 が判定し、次にアクセスポイントに設定したファイルシステムユーザーの権限で判定します（[FSx for ONTAP ユーザーガイド](https://docs.aws.amazon.com/fsx/latest/ONTAPGuide/s3-ap-manage-access-fsxn.html)、2026-11-24 に閲覧）。

## 設定手順

アクセスポイントは ARN かエイリアスで指定します。AWS CLI のリファレンスに、ARN の書式の例があります（[aws s3 cp](https://docs.aws.amazon.com/cli/latest/reference/s3/cp.html)、2026-11-24 に閲覧）。

```bash
aws s3 cp mydoc.txt s3://arn:aws:s3:us-west-2:123456789012:accesspoint/myaccesspoint/mykey
aws s3 cp s3://arn:aws:s3:us-west-2:123456789012:accesspoint/myaccesspoint/mykey mydoc.txt
```

エイリアスは、バケット名の代わりに使えると記載されています（`<名前>-<メタデータ>-ext-s3alias`。[Referencing access points](https://docs.aws.amazon.com/fsx/latest/ONTAPGuide/referencing-access-points-for-fsxn.html)、2026-11-24 に閲覧）。

## 確認手順

[段階 3 の手順書](../../../benchmarks/stage3-runbook.md)の AWS CLI の項で行います。成功するはずの対照として、先に `aws s3api list-objects-v2` を同じエイリアスに対して実行します。

## 既知の制約

- アクセスポイント側の制約（条件付き書き込み、バージョニング、アップロードのサイズ上限など）は Playbook にあります。
- S3 から S3 へのマルチパートのコピーでは、既定の `--copy-props` が `HeadObject`、`GetObjectTagging`、`PutObjectTagging` を追加で呼びうる。`--copy-props none` で避けられます。
- `aws s3 cp --no-overwrite` が、条件付き書き込みを使って上書きを防ぐのかは、文書に記載がありません（`C`）。

## 選び方

| 項目 | 内容 |
|---|---|
| 向く場面 | スクリプトとバッチ。サーバー側コピーの確認（`--debug` で発行する API を確認できる） |
| 制約 | 実機での動作は未測定。`--no-overwrite` の方式は未確認 |
| 他の選択肢 | [選び方](../../../docs/how-to-choose.md) |

## 後片付けと戻し方

クライアント側に残るものはありません。段階 3 で作った S3 Access Points とバケットの削除は、手順書の後片付けの台本に従います。

## 確認水準と出典

| 項目 | 水準 | 出典 |
|---|---|---|
| 現行版（2.42.2） | `D` | [AWS CLI のタグ](https://github.com/aws/aws-cli/tags)、2026-11-24 |
| ARN とエイリアスの指定 | `D` | 上の 2 つの AWS ドキュメント、2026-11-24 |
| 設定手順 | `C` | - |
| 確認手順 | `M` | [2026-11-24 の記録](../../../benchmarks/records/2026-11-24-client-tools-stage3.md) |

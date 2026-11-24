# rclone: クライアントアクセスパターン

🌐 **言語**: **日本語** | [English](README.en.md)

> **確認水準**: 版と S3 バックエンドの記載は公式文書で確認（`D`、2026-11-24）。FSx for ONTAP のアクセスポイントに対する動作は未実測（`C`）です。

## 概要と対象の利用場面

`rclone copy`、`sync`、`ls` で、アクセスポイントへ転送します。同じリモートの中でのサーバー側コピー（[サーバー側コピー](../../../docs/server-side-copy.md)）と、ファイルシステムとしてマウントする [rclone mount](../../streaming/rclone-mount/README.md) は別のパターンです。

## 前提

S3 Access Points の前提と上限は [Playbook の S3 Access Points の制約ノート](https://github.com/Yoshiki0705/FSx-for-ONTAP-Adoption-Playbook/blob/038fef7fb6ad3c5d0fabae7580f4983343504c70/docs/ja/domains/data-utilization/notes/s3-access-point-constraints.md) を参照してください。このページには書き写しません。ツールの版と出典は [ツールの事実確認](../../../docs/tool-facts.md) にあります。

## 構成と流れ

rclone は更新日時を `X-Amz-Meta-Mtime` に持ち、読むのに追加の `HEAD` が要ります。マルチパートや暗号化したオブジェクトでは、`X-Amz-Meta-Md5chksum` に MD5 を持ちます（[rclone の S3 ドキュメント](https://rclone.org/s3/)、2026-11-24 に閲覧）。FSx for ONTAP のアクセスポイントの ETag は MD5 ではありません（[Access point compatibility](https://docs.aws.amazon.com/fsx/latest/ONTAPGuide/access-points-for-fsxn-object-api-support.html)）。

## 設定手順

アクセスポイントの ARN またはエイリアスの指定方法は、rclone の文書に記載がありません（`C`）。S3 Access Points は仮想ホスト形式だけを受け付けます（[Referencing access points](https://docs.aws.amazon.com/fsx/latest/ONTAPGuide/referencing-access-points-for-fsxn.html)）。rclone の `force_path_style` の既定は `true` なので、`false` にした設定を段階 3 で試します。

```ini
[ap]
type = s3
provider = AWS
env_auth = true
region = ap-northeast-1
force_path_style = false
no_check_bucket = true
```

`no_check_bucket` は、バケットの存在確認と作成を省くための設定です（rclone の文書）。

## 確認手順

[段階 3 の手順書](../../../benchmarks/stage3-runbook.md)の rclone の項で行います。成功するはずの対照として、先に AWS CLI で同じエイリアスを一覧します。

## 既知の制約

- アクセスポイント側の制約は Playbook にあります。
- サーバー側コピーは、コピー元とコピー先で同じリモートを使うときだけです。`--s3-copy-cutoff` の既定は 4.656 GiB、最大は 5 GiB です。
- `--checksum` による比較は、MD5 を ETag から読む前提です。FSx for ONTAP のアクセスポイントでの結果は未確認です（`C`）。

## 選び方

| 項目 | 内容 |
|---|---|
| 向く場面 | 差分同期と、リモートの種類をまたぐ転送 |
| 制約 | 仮想ホスト形式の設定が要る見込み。`--checksum` の結果は未確認 |
| 他の選択肢 | [選び方](../../../docs/how-to-choose.md) |

## 後片付けと戻し方

クライアント側には設定ファイルが残ります。段階 3 で作った設定は、手順書の後片付けの台本で削除します。

## 確認水準と出典

| 項目 | 水準 | 出典 |
|---|---|---|
| 現行版（v1.76.0） | `D` | [rclone リリース](https://github.com/rclone/rclone/releases)、2026-11-24 |
| S3 バックエンドの設定項目 | `D` | [rclone の S3 ドキュメント](https://rclone.org/s3/)、2026-11-24 |
| 設定手順 | `C` | - |
| 確認手順 | `C` | - |

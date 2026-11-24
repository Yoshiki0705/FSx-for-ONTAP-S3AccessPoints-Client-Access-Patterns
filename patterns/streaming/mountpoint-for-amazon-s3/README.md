# Mountpoint for Amazon S3: クライアントアクセスパターン

🌐 **言語**: **日本語** | [English](README.en.md)

> **確認水準**: 版とファイル操作の挙動は公式文書で確認（`D`、2026-11-24）。FSx for ONTAP のアクセスポイントをマウントできるかは文書に記載がなく、未実測（`C`）です。 実測（2026-11-24）: エイリアスと ARN の両方でマウントできた。新規書き込み、読み出し、上書きと削除（フラグ付き）、リネーム、追記の結果は、同じ回の通常のバケットのマウントと同じだった。

## 概要と対象の利用場面

S3 のオブジェクトを、`open` や `read` のファイル操作で扱うためのクライアントです。FSx for ONTAP のデータには、S3 Access Points 経由のマウント、S3 API を直接使うツール、NFS または SMB の直接マウントの 3 つの経路があります。使い分けは [Mountpoint for Amazon S3 と S3 Access Points の使い分け](../../../docs/mountpoint-vs-s3-access-points.md) にあります。

## 前提

S3 Access Points の前提と上限は [Playbook の S3 Access Points の制約ノート](https://github.com/Yoshiki0705/FSx-for-ONTAP-Adoption-Playbook/blob/a4c8367f9172ee88f0af25731752af63dc2c6225/docs/ja/domains/data-utilization/notes/s3-access-point-constraints.md) を参照してください。このページには書き写しません。

## 構成と流れ

Mountpoint は、ファイル操作を S3 の API 呼び出しに変換します。S3 の IAM の判定の後に、アクセスポイントに設定したファイルシステムユーザーの権限で判定されます（[FSx for ONTAP ユーザーガイド](https://docs.aws.amazon.com/fsx/latest/ONTAPGuide/s3-ap-manage-access-fsxn.html)、2026-11-24 に閲覧）。

## 設定手順

Mountpoint の文書は、S3 標準バケットのアクセスポイントを、ARN かエイリアスで指定できると書いています（[CONFIGURATION.md](https://github.com/awslabs/mountpoint-s3/blob/main/doc/CONFIGURATION.md)、2026-11-24 に閲覧）。

```bash
mount-s3 arn:aws:s3:region:account-id:accesspoint/my-access-point /path/to/mount
mount-s3 my-access-point-hrzrlukc5m36ft7okagglf3gmwluquse1b-s3alias /path/to/mount
```

FSx for ONTAP のアクセスポイントのエイリアス（`-ext-s3alias`）をこの形で渡せるかは、文書に記載がありません（`C`）。段階 3 で試します。

## 確認手順

[段階 3 の手順書](../../../benchmarks/stage3-runbook.md)の Mountpoint の項で行います。成功するはずの対照として、先に AWS CLI で同じエイリアスを一覧します。マウントに失敗したときは、`mount-s3` のエラーとデバッグログを証跡にします。

## 既知の制約

- アクセスポイント側の制約は Playbook にあります。
- 既定では新規ファイルの作成だけができます。上書きは `--allow-overwrite`、削除は `--allow-delete` が要ります。
- リネームと追記は、S3 Express One Zone だけが対象です。
- ディレクトリの作成はローカルだけの操作で、既存のディレクトリは削除もリネームもできません。
- Mountpoint の README は、Amazon S3 以外の S3 互換ストレージをサポートしないと書いています。

出典は [SEMANTICS.md](https://github.com/awslabs/mountpoint-s3/blob/main/doc/SEMANTICS.md) と [README](https://github.com/awslabs/mountpoint-s3/blob/main/README.md)（2026-11-24 に閲覧）です。

## 選び方

| 項目 | 内容 |
|---|---|
| 向く場面 | 大きなオブジェクトの読み出しが中心のアプリケーション。新規ファイルを 1 つのクライアントから順に書く用途 |
| 制約 | FSx for ONTAP のアクセスポイントを受け付けるか未確認。リネームと追記は使えない見込み |
| 他の選択肢 | [選び方](../../../docs/how-to-choose.md) |

## 後片付けと戻し方

`umount` でマウントを外します。段階 3 で作ったアクセスポイントとバケットの削除は、手順書の後片付けの台本に従います。

## 確認水準と出典

| 項目 | 水準 | 出典 |
|---|---|---|
| 現行版（1.25.0） | `D` | [Mountpoint の変更履歴](https://github.com/awslabs/mountpoint-s3/blob/main/mountpoint-s3/CHANGELOG.md)、2026-11-24 |
| ファイル操作の挙動 | `D` | [SEMANTICS.md](https://github.com/awslabs/mountpoint-s3/blob/main/doc/SEMANTICS.md)、2026-11-24 |
| 設定手順 | `C` | - |
| 確認手順 | `M` | [2026-11-24 の記録](../../../benchmarks/records/2026-11-24-client-tools-stage3.md) |

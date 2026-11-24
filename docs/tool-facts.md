# ツールの事実確認

🌐 **言語**: **日本語** | [English](tool-facts.en.md)

> **確認日と水準**: 確認日は 2026-11-24（日本時間）です。表の `D` は公式ドキュメントまたは公式リポジトリの文書を開いて読んだ範囲、`C` は文書に記載がなく未実測の項目です。実機で動作を確認した項目はありません。

AWS CLI、s5cmd、rclone、Mountpoint for Amazon S3 の 4 つについて、現行版、使う S3 API、S3 Access Points の指定方法を、公式の文書から確認した結果です。S3 Access Points 側の対応 API と上限は、[互換性表の照合](compatibility-matrix.md#ツールが使う-s3-操作と対応表の照合)と Playbook の制約ノートにあります。ここには複製しません。

## 確認した範囲

- 対象は、段階 3 で実機にかける 4 つ（AWS CLI、s5cmd、rclone、Mountpoint for Amazon S3）です。AWS Transfer Family は事実確認だけを行いました。File Mover Express と LucidLink の 2 製品は、手動チェックリストに載せる事実だけを確認しました。
- 検索結果の抜粋は出典にしていません。表に載せた URL は、本文を開いて読んだものです。
- 版は、確認日時点で公式リポジトリが最新として示すものです。段階 3 で使う版は、実行時に `--version` で記録します。

## 現行版と指定方法

| ツール | 確認日時点の最新の版 | 通常の S3 操作での入口 | S3 Access Points の指定方法 | 出典 |
|---|---|---|---|---|
| AWS CLI v2 | 2.42.2（GitHub のタグ。コミット日 2026-11-23 UTC）。 | `aws s3`（`cp`、`sync`、`ls`、`rm`）と `aws s3api` | ARN は `s3://arn:aws:s3:<リージョン>:<アカウント>:accesspoint/<名前>/<キー>` の形で書ける（`D`）。エイリアスはバケット名の代わりに使える（`D`）。FSx for ONTAP のエイリアスの形は `<名前>-<メタデータ>-ext-s3alias` | S2、S6、S8 |
| s5cmd | v2.3.0（2024-12-16 のリリース。GitHub が示す最新） | `s5cmd cp`、`ls`、`sync`、`rm` | README に記載なし（`C`）。`--endpoint-url` を指定するとパススタイルに戻ると README にある（`D`）。S3 Access Points は仮想ホスト形式だけを受け付ける（`D`、S2）ので、エイリアスと `--endpoint-url` を併用できるかは未確認 | S2、S9、S10 |
| rclone | v1.76.0（2026-11-06） | `rclone copy`、`ls`、`sync`、`mount` | 文書に記載なし（`C`）。`force_path_style` の既定は `true`（`D`）で、S3 Access Points は仮想ホスト形式だけ（`D`、S2）なので、`false` にする必要があるかは未確認 | S2、S11、S12 |
| Mountpoint for Amazon S3 | 1.25.0（2026-11-12） | `mount-s3 <バケット名またはアクセスポイント> <マウント先>` | S3 標準バケットとディレクトリバケットのアクセスポイントは、ARN またはエイリアスで指定できると記載（`D`）。FSx for ONTAP のアクセスポイントを指定できるかは、文書に記載なし（`C`） | S13、S15、S16 |

## 使う S3 API の確認状況

| ツール | 文書から確認できた発行 API | 文書から確認できなかったこと |
|---|---|---|
| AWS CLI | S3 から S3 へのコピーは `--copy-props` が効き、マルチパートのコピーでは既定で `HeadObject`、`GetObjectTagging`、`PutObjectTagging` を追加で呼びうる（`D`、S6）。`--copy-props none` で追加の呼び出しを避けられる（`D`、S6）。`preferred_transfer_client` が `auto` のとき、S3 から S3 へのコピーは CRT 転送クライアントを使わない（`D`、S7） | `CopyObject` と `UploadPartCopy` のどちらを、どの大きさで発行するか（`C`。`--debug` で確認する） |
| s5cmd | S3 から S3 へのコピーはサーバー側で行う（`D`、S9）。5 GB を超えるオブジェクトのコピーは未対応（`D`、S9）。一覧は最初に `ListObjects` を送る（`D`、S9）。`--use-list-objects-v1` で V1 の一覧に切り替わる（`D`、S9） | アップロードのマルチパート、削除、`HeadObject` の呼び出し（`C`） |
| rclone | 同じリモートの中のコピーはサーバー側コピー（`D`、S11）。`--s3-copy-cutoff`（既定 4.656 GiB、最大 5 GiB）を超えるものはこの大きさのチャンクでコピーする（`D`、S11）。更新日時は `X-Amz-Meta-Mtime` に持ち、読むのに追加の `HEAD` が要る（`D`、S11）。マルチパートや暗号化したオブジェクトでは `X-Amz-Meta-Md5chksum` を使う（`D`、S11） | 一覧に使う API の版、`CopyObject` と `UploadPartCopy` の使い分け（`C`） |
| Mountpoint for Amazon S3 | 書き込みは新規ファイルの作成が既定。上書きは `--allow-overwrite`、削除は `--allow-delete` が要る（`D`、S14）。リネームとファイル末尾への追記は S3 Express One Zone だけが対象（`D`、S14）。ディレクトリの作成はローカルだけの操作（`D`、S14） | FSx for ONTAP のアクセスポイントに対して、起動時と各操作でどの API を呼ぶか（`C`） |

## 取り込み・転送以外のツールで確認した事実

| ツール | 確認した事実 | 出典 |
|---|---|---|
| AWS Transfer Family | FSx for ONTAP は S3 Access Points 経由で使う。エイリアスだけが使え、ARN と仮想ホスト形式の URI は使えない。リネームと追記は未対応。アクセスポイントのネットワーク起点が VPC の場合、Transfer Family からの要求は拒否される。IAM ポリシーのリソースにはエイリアスではなく ARN を書く | S17 |
| File Mover Express | AWS が公開しているオープンソースのツール（awslabs）。設定にバケット名とリージョンとプロファイルを書き、ネットワーク欄に「S3 Access Point/VPC Endpoint」のアドレスを書く欄がある。FSx for ONTAP のアクセスポイントのエイリアスを指定できるかは、文書に記載なし | S18 |
| LucidLink Connect | データストアの設定に、バケット名、アクセスキー、シークレットキー、リージョン、エンドポイント、仮想ホスト形式の使用の有無を書く。必要な権限は `GetObject` だけと記載。FSx for ONTAP のアクセスポイントのエイリアスを指定できるかは、文書に記載なし | S19 |

## 確認できなかったこと

項目 1〜3 は、2026-11-24 に実機で確かめました（[2026-11-24 の記録](../benchmarks/records/2026-11-24-client-tools-stage3.md)）。s5cmd と rclone はエイリアスを受け付け、Mountpoint はエイリアスと ARN でマウントできました。下の一覧は、文書だけでは確認できなかったことの記録として残します。

1. s5cmd と rclone が、FSx for ONTAP のアクセスポイントのエイリアスを受け付けるか。
2. Mountpoint for Amazon S3 が、FSx for ONTAP のアクセスポイントのエイリアスをマウントできるか。Mountpoint の README は、Amazon S3 以外の S3 互換ストレージについてはサポートしないと書いている（S16）。FSx for ONTAP のアクセスポイントは AWS の S3 エンドポイントだが、この README が対象にするかは読み取れない。
3. 各ツールが、サーバー側コピーで `CopyObject` と `UploadPartCopy` のどちらを発行するか（[サーバー側コピー](server-side-copy.md)）。
4. File Mover Express と LucidLink の 2 製品が、FSx for ONTAP のアクセスポイントのエイリアスを受け付けるか。公式文書に記載がないので、利用者の手元で埋めるチェックリストに残す。

## 出典一覧

確認日はすべて 2026-11-24（日本時間）です。

| ID | 出典 | URL |
|---|---|---|
| S1 | FSx for ONTAP ユーザーガイド: Access point compatibility | https://docs.aws.amazon.com/fsx/latest/ONTAPGuide/access-points-for-fsxn-object-api-support.html |
| S2 | FSx for ONTAP ユーザーガイド: Referencing access points | https://docs.aws.amazon.com/fsx/latest/ONTAPGuide/referencing-access-points-for-fsxn.html |
| S3 | FSx for ONTAP ユーザーガイド: Configuring network access | https://docs.aws.amazon.com/fsx/latest/ONTAPGuide/configuring-network-access-for-s3-access-points.html |
| S4 | FSx for ONTAP ユーザーガイド: Managing access point access | https://docs.aws.amazon.com/fsx/latest/ONTAPGuide/s3-ap-manage-access-fsxn.html |
| S5 | What's New（2026-11、S3 Access Points のサーバー側コピー） | https://aws.amazon.com/about-aws/whats-new/2026/11/s3-access-points-server-side-copy-fsx/ |
| S6 | AWS CLI リファレンス: `aws s3 cp` | https://docs.aws.amazon.com/cli/latest/reference/s3/cp.html |
| S7 | AWS CLI の S3 設定 | https://docs.aws.amazon.com/cli/latest/topic/s3-config.html |
| S8 | AWS CLI のタグ（GitHub） | https://github.com/aws/aws-cli/tags |
| S9 | s5cmd README | https://github.com/peak/s5cmd/blob/master/README.md |
| S10 | s5cmd リリース | https://github.com/peak/s5cmd/releases |
| S11 | rclone の S3 ドキュメント | https://rclone.org/s3/ |
| S12 | rclone リリース | https://github.com/rclone/rclone/releases |
| S13 | Mountpoint の設定（CONFIGURATION.md） | https://github.com/awslabs/mountpoint-s3/blob/main/doc/CONFIGURATION.md |
| S14 | Mountpoint のファイル操作の挙動（SEMANTICS.md） | https://github.com/awslabs/mountpoint-s3/blob/main/doc/SEMANTICS.md |
| S15 | Mountpoint の変更履歴 | https://github.com/awslabs/mountpoint-s3/blob/main/mountpoint-s3/CHANGELOG.md |
| S16 | Mountpoint README | https://github.com/awslabs/mountpoint-s3/blob/main/README.md |
| S17 | Transfer Family ユーザーガイド: FSx for NetApp ONTAP | https://docs.aws.amazon.com/transfer/latest/userguide/fsx-s3-access-points.html |
| S18 | File Mover Express: Configuration | https://awslabs.github.io/filemoverexpress/docs/Configuration |
| S19 | LucidLink Connect Overview | https://developer.lucidlink.com/docs/connect/overview |
| S20 | FSx for ONTAP の料金 | https://aws.amazon.com/fsx/netapp-ontap/pricing/ |

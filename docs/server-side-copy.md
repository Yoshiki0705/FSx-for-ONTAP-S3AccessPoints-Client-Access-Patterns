# サーバー側コピーとクライアントツール

🌐 **言語**: **日本語** | [English](server-side-copy.en.md)

> **区分**: このページは公式文書の読み取りと、段階 3 の確認手順を持ちます。AWS CLI、s5cmd、rclone は 2026-11-24 に 1 回ずつ実機で確かめました（[2026-11-24 の記録](../benchmarks/records/2026-11-24-client-tools-stage3.md#サーバー側コピーの結果)）。Mountpoint for Amazon S3 は確かめていません（`C`）。

2026-11 に、S3 Access Points を使って Amazon S3 の汎用バケットと FSx for ONTAP のボリュームの間を、`CopyObject` と `UploadPartCopy` でサーバー側コピーできるようになりました（同一リージョン。[What's New](https://aws.amazon.com/about-aws/whats-new/2026/11/s3-access-points-server-side-copy-fsx/)、2026-11-24 に閲覧）。それまでは、サーバー側コピーができず、オブジェクトを一度取得してアップロードし直す必要がありました。このページは、クライアントツールがその新しい経路を使うのか、取得とアップロードに戻るのかを整理します。

## Playbook との分担

| 論点 | 持つ場所 | 内容 |
|---|---|---|
| API の可否と制約（コピーの組み合わせ、暗号化は SSE-FSX、ストレージクラスは `FSX_ONTAP`、API 単位の実測） | Playbook | 制約ノートの該当節。固定コミットにその節が入るまで、このリポジトリからはリンクしない |
| どのツールが、どの指定で、サーバー側コピーを発行するか | このリポジトリ | 下の表と段階 3 の確認手順 |
| ファイルレベルとブロックレベルの汎用のコピー・移行ツール（DataSync、rsync、robocopy、XCP など）の実機確認 | Playbook の Issue（コピー・移行ツールの実機確認） | このリポジトリは扱わない |

境界は、使う経路にあります。Playbook の Issue は NFS、SMB、iSCSI を通すツールが対象です。このリポジトリは、S3 API で S3 Access Points に届くクライアントツール（AWS CLI、s5cmd、rclone、Mountpoint for Amazon S3 など）だけを扱います。

## ツールごとの発行の見込み

| ツール | サーバー側コピーを起こす指定 | 文書からの見込み | 判定の方法 | 水準 |
|---|---|---|---|---|
| AWS CLI | `aws s3 cp s3://<バケット>/<キー> s3://<エイリアス>/<キー>` | S3 から S3 へのコピーとして扱われる。マルチパートのコピーでは追加で `HeadObject`、`GetObjectTagging`、`PutObjectTagging` を呼びうる | `--debug` の出力で `CopyObject` か `UploadPartCopy` を探す。`--copy-props none` との差も取る | `M` |
| s5cmd | `s5cmd cp s3://<バケット>/<キー> s3://<エイリアス>/<キー>` | README は S3 から S3 のコピーをサーバー側と書く。5 GB を超えるオブジェクトは未対応と書く | 同じコピーの前後で、クライアントの送受信バイト数を比べる。CloudTrail のデータイベントで確認する | `M` |
| rclone | 同じリモートの中で `rclone copy <リモート>:<バケット> <リモート>:<エイリアス>` | 同じリモートの中のコピーはサーバー側コピー（公式文書）。`--s3-copy-cutoff` を超えるとチャンクでコピーする | `-vv --dump headers` で `x-amz-copy-source` ヘッダーを探す | `M` |
| Mountpoint for Amazon S3 | なし | サーバー側コピーを起こす指定が文書にない。マウント先どうしの `cp` は、読み出して書く操作になると見込む（未確認）。リネームは S3 Express One Zone だけが対象 | マウント先から別のアクセスポイントへ `cp` し、送受信バイト数がオブジェクトの大きさに近いことを確認する | `C` |

## 段階 3 での確認方法

発行された API を、次の 3 つの独立した証拠で確かめます。どれか 1 つだけでは判定しません。

1. クライアントのデバッグ出力: AWS CLI は `--debug`、rclone は `-vv --dump headers`。
2. クライアントの送受信バイト数: コピーの前後で `/proc/net/dev` の差を取る。256 MiB のオブジェクトをサーバー側でコピーすると、差はオブジェクトの大きさよりずっと小さいはずです。取得とアップロードなら、差が大きさの 2 倍に近づきます。
3. CloudTrail のデータイベント（任意）: `CopyObject` と `UploadPartCopy` の `eventName` を読む。専用の証跡を作るため、手順書の承認項目に入れてあります。スクリプトには含めないので、承認を得てから手で作ります。

成功するはずの対照として、同じオブジェクトを `aws s3api copy-object` で直接コピーし、1 つ目と 2 つ目の証拠にサーバー側コピーの形が出ることを先に確かめます。

```bash
benchmarks/scripts/stage3-measure.sh --dry-run --case server-side-copy
```

## 確認できていないこと

- 各ツールが `CopyObject` と `UploadPartCopy` のどちらを、どの大きさで発行するか。
- Playbook 側の API 単位の測定を、クライアントツールの結果として読めるかどうか。ツールごとの結果は、このリポジトリの段階 3 で測ります。
- Playbook の該当節への参照。固定コミットにその節が入った後に、[docs/reference-pins.md](reference-pins.md) の追従手順でリンクを追加します。

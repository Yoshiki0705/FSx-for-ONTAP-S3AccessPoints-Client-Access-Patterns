# 2026-11-27 クライアントツールの追加確認
🌐 **言語**: **日本語** | [English](2026-11-27-client-tools-additional.en.md)
> **区分**: サンプル測定です。2026-11-24 の記録（[段階 3](2026-11-24-client-tools-stage3.md)）と同じ環境で、サーバー側コピーの逆向きと大きなオブジェクト、NFS との併用、アクセスポイントの作り分けを、各 1 回ずつ確かめました。性能の数値は記録していません。ID、アカウント ID、アクセスポイントのエイリアスは伏せています。
## 環境欄
| 項目 | 記入 |
|---|---|
| 測定日 | 2026-11-27 01:33〜02:17（日本時間） |
| リージョン | ap-northeast-1 |
| FSx for ONTAP の構成 | 段階 3 と同じ既存の検証用ファイルシステム（第 1 世代 `SINGLE_AZ_1`、スループット容量 128 MBps、SSD 1,024 GiB）。検証専用の 20 GiB の UNIX セキュリティスタイルのボリュームを作り、撤去で削除 |
| ONTAP バージョン | 9.19.1P4（ONTAP REST の `GET /api/cluster?fields=version`） |
| クライアント | EC2 c6in.xlarge、Amazon Linux 2023（カーネル 6.18）。ファイルシステムと同じサブネット |
| ツールと版 | AWS CLI 2.38.0、s5cmd 2.3.0、rclone 1.76.0、Mountpoint for Amazon S3 1.24.0 |
| オブジェクトサイズ | 256 MiB、6 GiB（乱数） |
| 繰り返し回数と集計 | 各操作 1 回。集計なし |
| 測定区分 | サンプル測定 |
| 後片付け | 追加で作った 2 つのアクセスポイントを削除し、段階 3 のスクリプトで残りを撤去。S3 バケット、ボリューム、アクセスポイント、IAM ロール、EC2 を describe で読み戻して消えたことを確認（EC2 は `terminated`） |
## サーバー側コピー（ボリュームからバケット、256 MiB）
送受信バイト数は、送信と受信の合計を、コピーの前後にクライアントのデフォルトルートのネットワークインターフェイスで読んだ差です。
| コピーの方法 | 結果 | 送受信の合計（バイト） | ハッシュ |
|---|---|---|---|
| `aws s3api copy-object` | 成功 | 16,372 | 一致 |
| `aws s3 cp` | 成功 | 227,211 | 一致 |
| `s5cmd cp` | 成功 | 19,265 | 一致 |
| `rclone copyto`（既定） | `InvalidArgument: FSX_ONTAP is not allowed` で失敗 | 82,449 | コピー先なし |
| `rclone copyto --s3-storage-class STANDARD` | 成功 | 49,100 | 一致 |
## サーバー側コピー（6 GiB = 6,442,450,944 バイト）
| 向き | コピーの方法 | 結果 | 送受信の合計（バイト） | ハッシュ |
|---|---|---|---|---|
| バケット→ボリューム | `aws s3api copy-object` | `InvalidRequest`（コピー元が 5,368,709,120 バイトより大きい） | 16,423 | - |
| バケット→ボリューム | `aws s3 cp` | 成功（`UploadPartCopy`） | 3,358,458 | 一致 |
| バケット→ボリューム | `s5cmd cp` | 同じ `InvalidRequest` で失敗 | 16,313 | - |
| バケット→ボリューム | `rclone copyto --s3-storage-class FSX_ONTAP` | 成功 | 969,668 | 一致 |
| ボリューム→バケット | `aws s3 cp` | 成功 | 3,026,741 | 一致 |
## NFS（バージョン 4.1）との併用
| 操作 | 結果 |
|---|---|
| S3 API で書いたファイルを NFS で読む（256 MiB） | ハッシュ一致。所有者 0:2（root:daemon）、モード 644 |
| NFS で書いたファイルを S3 API で読む（1 MiB） | 一覧に出て、ハッシュ一致 |
| NFS でリネームと追記をしたあと、S3 API で読む | 新しい名前で一覧に出て、追記後の内容と大きさ（1,048,585 バイト）に一致 |
| S3 API で削除したあと、NFS で見る | ファイルが消える |
| S3 API で作られたディレクトリ | 2 つとも `drwxrwxrwx`（777） |
## アクセスポイントの作り分け
1 つのボリュームに 3 つ付けた（VPC 起点で `root`、VPC 起点で `pcuser`（UID 65534）、インターネット起点で `root`）。
| 操作 | 結果 |
|---|---|
| `pcuser`: `root` が作ったファイルの先頭 100 バイトの読み取り | 成功 |
| `pcuser`: ルートが `root` 所有（モード 755）のボリュームへの書き込み | `AccessDenied` |
| `pcuser`: ボリュームのルートの所有者を UID 65534 に変えたあとの書き込み | 成功。できたファイルの所有者は 65534:65534、モード 644 |
| `pcuser`: 777 のディレクトリにある `root` 所有のファイル（モード 644）の上書き | 成功 |
| VPC の外（手元の Mac）から、VPC 起点のアクセスポイントを一覧 | `AccessDenied`（リソースポリシーの明示的な拒否） |
| VPC の外（手元の Mac）から、インターネット起点のアクセスポイントの一覧、書き込み、`head-object` | 成功 |
| 完了していないマルチパートアップロードの 100 MiB のパート（ONTAP REST でボリュームの使用量を読む） | 置く前後と中止後で 274,239,488 バイトのまま。NFS からは見えない |
## 使ったコマンド
```sh
mount -t nfs -o vers=4.1 <NFS エンドポイント>:/<ジャンクションパス> /mnt/nfs
rclone copyto "ap:<エイリアス>/<キー>" "ap:<バケット>/<キー>" --s3-storage-class STANDARD
aws fsx create-and-attach-s3-access-point --name <名前> --type ONTAP \
  --ontap-configuration "VolumeId=<ボリューム ID>,FileSystemIdentity={Type=UNIX,UnixUser={Name=<UNIX ユーザー名>}}" \
  --s3-access-point "VpcConfiguration={VpcId=<VPC ID>}"
```

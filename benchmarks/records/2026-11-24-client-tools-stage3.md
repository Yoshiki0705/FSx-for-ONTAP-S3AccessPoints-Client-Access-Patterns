# 2026-11-24 クライアントツールの実機確認（段階 3）

🌐 **言語**: **日本語** | [English](2026-11-24-client-tools-stage3.en.md)

> **区分**: サンプル測定です。1 構成で各操作を 1 回ずつ実行し、成否と中身のハッシュの一致だけを記録しました。性能の数値は記録していません。ID、アカウント ID、アクセスポイントのエイリアスは伏せています。

## 環境欄

| 項目 | 記入 |
|---|---|
| benchmark_run_id | 20261124-1500 |
| 測定日 | 2026-11-24 15:03〜15:12（日本時間） |
| リージョン | ap-northeast-1 |
| FSx for ONTAP の構成 | 既存の検証用ファイルシステム（第 1 世代 `SINGLE_AZ_1`、スループット容量 128 MBps、SSD 1,024 GiB）。この検証のためだけに 20 GiB の UNIX セキュリティスタイルのボリュームを作り、撤去で削除 |
| ONTAP バージョン | 確認していない（ONTAP REST は使わなかった。`describe-file-systems` は版を返さない） |
| S3 Access Points の設定 | ネットワーク起点は VPC。ファイルシステムユーザーは UNIX の `root`。アクセスポイントのポリシーは付けない（同一アカウントの IAM ロールで許可） |
| クライアント | EC2 c6in.xlarge、Amazon Linux 2023（カーネル 6.18）。ファイルシステムと同じサブネット。S3 にはゲートウェイ型の VPC エンドポイント経由で接続 |
| ツールと版 | AWS CLI 2.38.0（AMI に同梱）、s5cmd 2.3.0、rclone 1.76.0、Mountpoint for Amazon S3 1.24.0（`dnf` で導入） |
| オブジェクトサイズ | 1 MiB、64 MiB、256 MiB（乱数） |
| 並列度 | 各ツールの既定 |
| 繰り返し回数と集計 | 各操作 1 回。集計なし |
| 測定区分 | サンプル測定 |
| 結果 | 下の各表。成否、エラー、ハッシュの一致。サーバー側コピーはクライアントの送受信バイト数も記録 |
| 再現手順 | [段階 3 の手順書](../stage3-runbook.md)。`stage3-setup.sh`、`stage3-measure.sh --case <ケース>`、`stage3-export-evidence.sh`、`stage3-teardown.sh` |
| 後片付け | 作った 5 種類（バケット、ボリューム、アクセスポイント、IAM ロールとインスタンスプロファイル、EC2）をすべて削除し、describe で読み戻した。[後片付けの結果](#後片付けの結果)を参照 |

## 対照の結果

同じ回に、通常の S3 汎用バケットでも同じ操作を行いました。

| 操作 | 通常のバケット | アクセスポイント（エイリアス） | アクセスポイント（ARN） |
|---|---|---|---|
| `aws s3api list-objects-v2` | 成功 | 成功 | 成功 |
| `put-object`（1 MiB）、`head-object`、`get-object` | - | 成功。ハッシュ一致。`StorageClass` は `FSX_ONTAP`、暗号化は `aws:fsx` | - |

## ツールごとの結果

| ツール | 操作 | 通常のバケット | アクセスポイント |
|---|---|---|---|
| AWS CLI | `aws s3 ls`、`cp`（1 MiB と 64 MiB）、`sync`、`rm`（エイリアスと ARN の両方） | 成功 | 成功。64 MiB はハッシュ一致。64 MiB はマルチパート（8 パート）で送られた |
| AWS CLI | `aws s3 cp --no-overwrite` | 成功 | 失敗。`NotImplemented`（A header you provided implies functionality that is not implemented）。`--debug` で `If-None-Match: *` を送っていた |
| s5cmd | `cp`（1 MiB と 64 MiB）、取得、`rm`（ワイルドカード） | 成功 | 成功。64 MiB はハッシュ一致。`--endpoint-url` なしでエイリアスを受け付けた |
| s5cmd | 空のプレフィックスの `ls` | 終了コード 1（no object found） | 終了コード 1（同じ） |
| rclone | `lsf`、`copyto`、取得、`delete`（`force_path_style = false`） | 成功 | 成功。64 MiB はハッシュ一致（単一の `PutObject`） |
| rclone | `check` | 1 matching files | 0 differences。ただし 1 hashes could not be checked |
| Mountpoint for Amazon S3 | エイリアスでのマウント、ARN でのマウント | 成功 | 成功 |
| Mountpoint for Amazon S3 | 既定のフラグ: 新規書き込み、読み出し | 成功 | 成功 |
| Mountpoint for Amazon S3 | 既定のフラグ: 上書き、追記、削除 | Operation not permitted | Operation not permitted（同じ） |
| Mountpoint for Amazon S3 | `--allow-overwrite --allow-delete`: 上書き、削除 | 成功 | 成功 |
| Mountpoint for Amazon S3 | リネーム | Function not implemented | Function not implemented（同じ） |
| Mountpoint for Amazon S3 | `mkdir` と、その下への書き込み | 成功 | 成功 |

Mountpoint のデバッグログには、アクセスポイントに対して `ListObjectsV2`、`HeadObject`、`GetObject`、`PutObject`、`CreateMultipartUpload`、`UploadPart`、`CompleteMultipartUpload`、`DeleteObject` が出ていました。通常のバケットのマウントでも、同じ種類の API が出ていました。

## サーバー側コピーの結果

256 MiB のオブジェクトを、通常のバケットからアクセスポイントのエイリアスへコピーしました。送受信バイト数は、コピーの前後のクライアントのネットワークインターフェイスの差です（256 MiB = 268,435,456 バイト）。

| コピーの方法 | 発行された API（ログから） | 送受信バイト数 | 中身のハッシュ |
|---|---|---|---|
| 対照: `aws s3api copy-object` | `CopyObject` | 26,740 | 一致 |
| `aws s3 cp`（既定） | `HeadObject`、`GetObjectTagging`、`CreateMultipartUpload`、`UploadPartCopy` 32 回、`CompleteMultipartUpload` | 236,963 | 一致 |
| `aws s3 cp --copy-props none` | `HeadObject`、`CreateMultipartUpload`、`UploadPartCopy` 32 回、`CompleteMultipartUpload` | 232,721 | 一致 |
| `s5cmd cp` | ログに API 名が出ない | 27,340 | 一致 |
| `rclone copyto`（既定） | `CopyObject`。`X-Amz-Storage-Class: STANDARD` を付けて送り、`InvalidStorageClass` で 3 回失敗 | 82,198 | コピー先なし |
| `rclone copyto --s3-storage-class FSX_ONTAP` | `CopyObject`（`X-Amz-Storage-Class: FSX_ONTAP`） | 66,991 | 一致 |
| 参照: `aws s3 cp` で取得して標準入力からアップロード | 取得とアップロード | 551,933,428 | 一致 |

送受信バイト数が 1 MB 未満のものは、データがクライアントを通っていません。取得とアップロードの参照は、オブジェクトの大きさの約 2 倍でした。s5cmd はログに API 名が出ないため、バイト数とハッシュだけで判定しました。CloudTrail のデータイベントは使っていません。

## 後片付けの結果

撤去の前に、クライアントのログ、ハッシュ、送受信バイト数、各リソースの describe の出力を、非公開の退避先に移しました（108 ファイル）。実値を伏せた結果の表（ハッシュ、送受信バイト数、各操作の終了コード、ツールの版、撤去の読み戻し）は [20261124-1500/](20261124-1500/) にあります。撤去は 15:12〜15:15（日本時間）で、各リソースを describe で読み戻しました。

| リソース | 読み戻し |
|---|---|
| S3 Access Points | `NotFound` |
| 検証専用のボリューム | `VolumeNotFound` |
| EC2 | `terminated`。付いていた EBS は 0 件 |
| IAM ロール、インスタンスプロファイル | `NoSuchEntity` |
| S3 バケット | 404 |

タグ（`Project=client-access-patterns`）の検索では、終了済みの EC2 が 1 件だけ残って見えました。終了したインスタンスは、しばらくタグ検索に残ります。動作中または停止中のインスタンスは 0 件でした。

> **補足**: 作業中に、単体テストが `--execute` の経路で実際の `aws` を呼び、空のバケットを 1 つ作っていました（14:57 作成、タグ `Run=old`）。見つけた時点で削除し、404 を読み戻しました。テストは、クラウドの CLI を偽物に差し替えてから実行するように直しました。

## 確認できていないこと

- ONTAP のバージョン。
- 5 GiB を超えるオブジェクトのコピー、50 GiB 前後のアップロード。
- s5cmd が発行した API の名前（ログに出ないため）。
- NFS での直接マウント（経路 c）との比較。セキュリティグループの変更が要るため行っていません。
- 複数回の実行、並列度を変えた実行、性能の数値。

# 段階 3 の手順書: 実機での確認

🌐 **言語**: **日本語** | [English](stage3-runbook.en.md)

> **実行の条件**: 実機の実行は費用が発生します。利用者の承認と費用の上限の範囲内でだけ実行します。スクリプトは既定で何も作らない dry run で、`--execute` を付けたときだけ作ります。ID、アカウント ID、エイリアスの実値は、リポジトリの外の設定ファイルに置き、記録では伏せます。

## 目的と範囲

AWS CLI、s5cmd、rclone、Mountpoint for Amazon S3 が、FSx for ONTAP の S3 Access Points に対して何をできるかを、ケースごとに実機で確かめます。あわせて、サーバー側コピー（`CopyObject`、`UploadPartCopy`）を各ツールが発行するかを確かめます。AWS Transfer Family、File Mover Express、LucidLink は対象外です。

## 承認の条件と上限

- 費用の上限は 20 USD です。[費用の見積もり](#費用の見積もり)が上限を超える場合は、何も作りません。
- 既存の FSx for ONTAP は変更しません。作るのは、検証専用のボリューム 1 つ、S3 Access Points 1 つ、S3 バケット 1 つ、EC2 1 台とその IAM ロールだけです。
- すべてのリソースに `Project=client-access-patterns` と `Run=<日時>` のタグを付けます。削除保護や保持期間のように、消せなくなる設定は使いません。
- AWS の認証は SSO です。`Token has expired` が出たら止めて、利用者に `aws sso login` を頼みます。

## 作るものと命名

| リソース | 名前 | 作るコマンド | 消すコマンド |
|---|---|---|---|
| S3 バケット（対照とコピー元） | `s3apbench-<日時>-<乱数>` | `aws s3api create-bucket` | `aws s3 rm`、`aws s3api delete-bucket` |
| 検証専用のボリューム | `s3apbench_<日時>` | `aws fsx create-volume` | `aws fsx delete-volume` |
| S3 Access Points | `s3apbench-<日時>` | `aws fsx create-and-attach-s3-access-point` | `aws fsx detach-and-delete-s3-access-point` |
| IAM ロールとインスタンスプロファイル | `s3apbench-<日時>-role`、`-profile` | `aws iam create-role` ほか | `aws iam delete-role` ほか |
| EC2 クライアント（c6in.xlarge） | タグ `Name=s3apbench-<日時>` | `aws ec2 run-instances` | `aws ec2 terminate-instances` |

検証専用のボリュームを作る理由は、S3 Access Points を付けたボリュームは、アクセスポイントを外した後も ONTAP からは削除できず、FSx for ONTAP の API から削除する必要があるためです（[Playbook の制約ノート](https://github.com/Yoshiki0705/FSx-for-ONTAP-Adoption-Playbook/blob/038fef7fb6ad3c5d0fabae7580f4983343504c70/docs/ja/domains/data-utilization/notes/s3-access-point-constraints.md)）。既存のボリュームに付けないので、既存の構成に影響しません。

## 実行手順

1. `benchmarks/stage3.env.example` を `~/.config/s3ap-client-patterns/stage3.env` にコピーし、実値を入れる。SVM に ONTAP のオブジェクトストアサーバーがないことを確認する。
2. dry run で、作るコマンドをすべて確認する。
3. `--execute` でリソースを作る。作った ID は状態ファイルに記録される。
4. Session Manager でクライアントに入り、`/opt/stage3/.ready` ができるのを待つ（ツールの導入が終わった印）。
5. クライアントでケースを実行する。実行時にツールの版を `versions.txt` に記録する。
6. 証跡をクライアントからバケットへ、バケットから手元の `benchmarks/records/<日時>/raw/` へ退避する。
7. 記録を書く（雛形は [benchmark-record.md](../docs/templates/benchmark-record.md)）。実値は伏せる。
8. 後片付けの台本を実行し、読み戻しと残り 0 件の確認を記録に加える。

```bash
benchmarks/scripts/stage3-setup.sh --dry-run
benchmarks/scripts/stage3-setup.sh --execute
aws ssm start-session --region ap-northeast-1 --target <インスタンス ID>
/opt/stage3/stage3-measure.sh --execute --case all
benchmarks/scripts/stage3-export-evidence.sh --execute
benchmarks/scripts/stage3-teardown.sh --execute
```

## 各ケースの確認内容

| ケース | 対照（成功するはずの操作） | 確認すること | 証跡 |
|---|---|---|---|
| control | 通常の S3 バケットでの一覧、書き込み、取得 | エイリアスと ARN で、一覧、書き込み、取得、`HeadObject` が通るか。取得した中身のハッシュが一致するか | `control-*.json`、`hashes.tsv` |
| aws-cli | 通常のバケットでの `cp`、`sync`、`rm` | エイリアスと ARN の両方で、1 MiB と 64 MiB（マルチパート）の `cp`、`sync`、`--no-overwrite`、`rm`。`--debug` に出る API 名 | `awscli-*.log`、`probes.tsv` |
| s5cmd | 通常のバケットでの `ls`、`cp`、`rm` | エイリアスを受け付けるか。`--endpoint-url` なしで通るか。失敗したときのエラー | `probe-s5cmd-*.log` |
| rclone | 通常のバケットでの `lsf`、`copyto`、`check` | `force_path_style = false` でエイリアスに届くか。`check` の結果。`--dump headers` に出るヘッダー | `probe-rclone-*.log` |
| mountpoint | 通常のバケットのマウントで同じ操作 | エイリアスと ARN でマウントできるか。新規書き込み、上書き、リネーム、追記、`mkdir`、削除の結果と、`--allow-overwrite`、`--allow-delete` を付けたときの違い。NFS 経路（任意）との違い | `probe-mp-*.log`、`mp-*-logs/` |
| server-side-copy | `aws s3api copy-object` の直接実行 | 各ツールの送受信バイト数、`--debug` と `--dump headers` の API 名、コピー後のハッシュ。取得とアップロードを重ねた参照との差 | `nic.tsv`、`probe-ssc-*.log`、`hashes.tsv` |

## 後片付けの台本と証跡の退避

撤去で消えるもの（バケットの中身、使い捨てボリューム上のファイル、クライアント上のログ）は、撤去の前に退避します。

1. クライアントで `stage3-measure.sh --execute --case export` を実行し、結果をバケットの `evidence/` に置く（`--case all` に含まれる）。
2. 手元で `stage3-export-evidence.sh --execute` を実行し、`benchmarks/records/<日時>/raw/` に退避する。リソースの describe の出力もここに置く。
3. `raw/` が空だと、`stage3-teardown.sh` は何も消さずに止まる。
4. `stage3-teardown.sh --execute` を実行する。消す順序は、S3 Access Points、ボリューム、EC2、ロール、バケット。消す対象の ID は状態ファイルから読み、ボリュームは `Run` タグが今回の値と一致するときだけ消す。
5. 各リソースを約 15 秒おきに describe し、消えたことを読み戻す。結果は `raw/teardown-readback.tsv` に残る。
6. `Run` タグで検索し、残りが 0 件であることを `raw/teardown-tag-search.json` で確かめる。

作ったリソースの削除に失敗したときは、再実行せずに、残ったリソースの ID と費用の発生を報告します。

## IAM 権限の対応表

| 実行主体 | 操作 | 使う場面 |
|---|---|---|
| 操作者（SSO の管理者ロール） | `fsx:CreateVolume`、`fsx:CreateAndAttachS3AccessPoint`、`s3:CreateAccessPoint`、`s3:GetAccessPoint`、`fsx:DescribeVolumes`、`fsx:DescribeS3AccessPointAttachments`、`fsx:TagResource` | ボリュームとアクセスポイントの作成と確認 |
| 操作者 | `fsx:DetachAndDeleteS3AccessPoint`、`fsx:DeleteVolume`、`s3:DeleteAccessPoint`（必要かは未確認） | 後片付け |
| 操作者 | `ec2:RunInstances`、`ec2:TerminateInstances`、`ec2:DescribeInstances`、`iam:CreateRole`、`iam:PutRolePolicy`、`iam:PassRole` ほか | クライアントとロールの作成と削除 |
| 操作者 | `s3:CreateBucket`、`s3:PutBucketTagging`、`s3:DeleteBucket`、`tag:GetResources` | バケットの作成、削除、タグ検索 |
| EC2 のインスタンスロール | `s3:GetObject`、`s3:PutObject`、`s3:DeleteObject`、`s3:GetObjectTagging`、`s3:PutObjectTagging`、`s3:AbortMultipartUpload`、`s3:ListMultipartUploadParts`（アクセスポイントとバケットの両方） | 各ツールの読み書きとコピー |
| EC2 のインスタンスロール | `s3:ListBucket`、`s3:GetBucketLocation`、`s3:ListBucketMultipartUploads`（アクセスポイントとバケットの両方） | 一覧、Mountpoint のマウント |
| EC2 のインスタンスロール | `AmazonSSMManagedInstanceCore` | Session Manager での接続 |

インスタンスロールのポリシーは [stage3-instance-policy.json](stage3-instance-policy.json) です。アクセスポイントは `s3apbench-*`、バケットは実行時に今回の名前（ファイル中の `example-bucket`）へ置き換えて、対象を限ります。

## 費用の見積もり

見積もりは、2026-11-24 に Pricing API（および FSx for ONTAP と S3 の料金ページ）から読んだ ap-northeast-1 の単価です。単価の発効日は 2026-11-01（IPv4 は 2026-11-17）です。測定は 4 時間以内、リクエスト数は上限を仮定した値です。

| 項目 | 前提 | 単価 | 見積もり（USD） |
|---|---|---|---|
| EC2 c6in.xlarge | Linux、オンデマンド、4 時間 | 0.2856 USD/時間 | 1.14 |
| EBS gp3 | 8 GiB、4 時間 | 0.096 USD/GB-月 | 0.00 |
| S3 の PUT、COPY、POST、LIST | 10,000 リクエスト（上限の仮定） | 0.0047 USD/1,000 リクエスト | 0.05 |
| S3 の GET とその他 | 50,000 リクエスト（上限の仮定） | 0.0037 USD/10,000 リクエスト | 0.02 |
| S3 の保存 | 2 GiB、4 時間 | 0.025 USD/GB-月 | 0.00 |
| パブリック IPv4 | 1 アドレス、4 時間（付ける場合） | 0.005 USD/時間 | 0.02 |
| FSx for ONTAP | 既存の空き容量に検証専用のボリュームを作る。追加の課金なし（提供済み容量の範囲内） | - | 0.00 |
| 合計 |  |  | 約 1.2 |

> **前提と除外**: 同一リージョンの S3 とのデータ転送は、S3 の料金ページで課金の対象外と読んだ範囲です。既存の FSx for ONTAP（1,024 GiB の SSD、128 MBps、単一 AZ）は 0.15 USD/GB-月と 0.906 USD/MBps-月（約 0.37 USD/時間）で、既に稼働中なので増分ではありません。S3 Access Points 自体の課金は、FSx for ONTAP の料金ページに S3 リクエストとデータ転送だけが載っています。時間が 2 倍（8 時間）になっても約 2.4 USD で、上限の 20 USD に届きません。

## 確認できていないこと

- `s3:DeleteAccessPoint` が、アクセスポイントの削除に必要かどうか。必要なら、実行時に権限エラーで分かり、操作者のロールで補います。
- Session Manager のプラグインが操作者の端末にあるか。
- Mountpoint の、`dnf` で入る版が最新（1.25.0）か。実行時に `versions.txt` で記録します。
- 検証用 SVM に ONTAP のオブジェクトストアサーバーがないこと。あると、アクセスポイントの作成が失敗します（Playbook）。
- CloudTrail のデータイベントによる `CopyObject` の確認。スクリプトには含めていないので、必要なら承認を得て手で追加します。

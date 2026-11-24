# 連携先の一覧: AWS サービスと製品、用途、クライアントツール

🌐 **言語**: **日本語** | [English](integrations-map.en.md)

> **区分**: 連携先の動作は、AWS と NetApp の文書、ブログ、著者の検証記事の記述です（閲覧日 2026-11-25、日本時間）。実機で確かめたのは、4 つのクライアントツールが S3 Access Points に対して動く範囲だけで、[2026-11-24 の記録](../benchmarks/records/2026-11-24-client-tools-stage3.md)にあります。連携先のサービス側の動作は、このリポジトリでは測っていません。用途の記号（N1〜N8、E1〜E9）と出典の記号（U1〜U14）は、[ユースケース](use-cases.md)の表のものです。

Amazon FSx for NetApp ONTAP（以下 FSx for ONTAP）の S3 Access Points は、S3 の API を読む相手に、ボリュームのファイルを見せます。相手が S3 Access Points を直接読むなら、クライアントツールは出てきません。クライアントツールが関わるのは、データを投入する、確認する、バケットとの間で移す、S3 API を使えないアプリへ見せる、という操作の側です。

## 連携先と用途の対応

| 連携先 | 種別 | 想定用途 | 根拠の区分 | 関わるクライアントツール | 出典 |
|---|---|---|---|---|---|
| Amazon Athena と AWS Glue Data Catalog | AWS サービス | N1、E1: ファイル共有のデータへの SQL 分析 | 公式の想定 | AWS CLI（データ投入と確認） | U6、U5 |
| AWS Glue（Apache Spark、Python シェル、Ray） | AWS サービス | N1、E1: ETL。結果を同じボリュームへ書き戻す | 公式の想定 | AWS CLI（確認） | U6 |
| Amazon Bedrock Knowledge Bases | AWS サービス | N2: 文書共有を元にした RAG | 公式の想定 | AWS CLI（文書の投入と確認） | U6 |
| Amazon Quick | AWS サービス | N2、E1: Access Point のエイリアスをナレッジベースの元にする | 公式の想定 | AWS CLI（確認） | U5、U7 |
| Amazon Bedrock AgentCore | AWS サービス | N3: MCP ゲートウェイと AWS Lambda から、一覧、読み取り、検索をする | 公式の想定（AWS ブログの構成例） | MCP クライアント（Kiro、Claude Desktop）は推定、未確認 | U7 |
| Amazon Quick のダッシュボード（AWS ブログの表記は Quick Sight） | AWS サービス | N3: 集計済みのデータをダッシュボードにする | 公式の想定（AWS ブログの構成例） | なし | U7 |
| Amazon SageMaker | AWS サービス | E1: 機械学習のデータとして読む | 公式の想定 | AWS CLI（確認） | U5、U10 |
| Amazon EMR Serverless | AWS サービス | N1、E1: Spark のジョブ | 公式の想定 | なし | U6 |
| Amazon Redshift と Amazon OpenSearch Service | AWS サービス | E1: 分析とログ分析 | 公式の想定（NetApp のブログ） | なし | U10 |
| AWS Lambda | AWS サービス | N7、E3: ファイル投入の処理、共有データの読み取り | 公式の想定 | AWS CLI（動作確認） | U6、U5 |
| Amazon CloudFront | AWS サービス | N6: HLS 動画の配信 | 公式の想定 | なし | U6 |
| AWS Transfer Family | AWS サービス | N4: 外部との SFTP、FTPS、FTP の受け渡し | 公式の想定 | なし（相手の SFTP クライアントは Transfer Family の文書の範囲） | U6、U9 |
| Amazon S3 の汎用バケット | AWS サービス | N5、E4: サーバー側コピー（`CopyObject`、`UploadPartCopy`） | 公式の想定 | AWS CLI、s5cmd、rclone | U8、記録 |
| S3 Batch Operations | AWS サービス | E4: 大量のコピーのジョブ | Playbook に実機の記録 | AWS CLI | [Playbook のノート](https://github.com/Yoshiki0705/FSx-for-ONTAP-Adoption-Playbook/blob/a4c8367f9172ee88f0af25731752af63dc2c6225/docs/ja/domains/data-utilization/notes/s3-access-points-server-side-copy-use-cases.md) |
| Dremio Cloud | 外部製品 | E8: Access Point を読み、結果を FSx for ONTAP の S3 バケットへ書く | 公式の想定（Dremio と NetApp のブログ） | なし | U11、U12 |
| Snowflake | 外部製品 | E8: ステージの `AWS_ACCESS_POINT_ARN` を指定した外部テーブル | 公開事例（著者の 1 環境） | なし | U13 |
| Databricks | 外部製品 | E8: Access Point の読み取り。経路により結果が分かれる | 公開事例（著者の 1 環境） | なし | U14 |
| ファイルパスとして使うアプリ | アプリ | N8: S3 API を使えないアプリへのファイルパスの提供 | 推定。マウントと基本操作は確認 | Mountpoint for Amazon S3 | 記録 |
| 商用の転送・ストリーミング製品 | 外部製品 | E9: File Mover Express、LucidLink Connect、LucidLink Suite | 推定 | 商用ツール（手動チェックリスト） | tool-facts |

## クライアントツールごとの関わり

| ツール | 関わる連携と用途 | このリポジトリの実測 | パターン |
|---|---|---|---|
| AWS CLI | データの投入と確認（N1、N2、N7、E1、E3）、サーバー側コピー（N5、E4）、定期ジョブ（E5） | 一覧、取得、書き込み、マルチパート、削除、サーバー側コピー | [patterns/ingest/aws-cli](../patterns/ingest/aws-cli/README.md) |
| s5cmd | 大量転送（E6）、サーバー側コピー（N5、E4）、定期ジョブ（E5） | 一覧、取得、書き込み、削除、サーバー側コピー（性能は未測定） | [patterns/ingest/s5cmd](../patterns/ingest/s5cmd/README.md) |
| rclone | ほかのストレージとの同期（E7）、サーバー側コピー（N5、E4） | 一覧、取得、書き込み、削除、サーバー側コピー。コピーには `--s3-storage-class FSX_ONTAP` が要った | [patterns/ingest/rclone](../patterns/ingest/rclone/README.md) |
| Mountpoint for Amazon S3 | S3 API を使えないアプリへのファイルパス（N8） | エイリアスと ARN でのマウント、新規書き込み、読み出し、`--allow-overwrite --allow-delete` での上書きと削除 | [patterns/streaming/mountpoint-for-amazon-s3](../patterns/streaming/mountpoint-for-amazon-s3/README.md) |
| MCP クライアント（Kiro、Claude Desktop） | AI クライアントからの一覧、読み取り、検索（N3 に近い構成） | なし（推定） | [patterns/mcp](../patterns/mcp/kiro/README.md) |
| 商用の転送・ストリーミング製品 | E9 | なし（手動チェックリストを利用者が記入） | [checklists/vendor](../checklists/vendor/file-mover-express/CHECKLIST.md) |

## 経路の選び方

連携先ごとに、入口は次の 3 つに分かれます。

| 入口 | 向く場面 | 制約 |
|---|---|---|
| サービスが Access Point を直接読む | 連携先が S3 API に対応している（Athena、Glue、Bedrock Knowledge Bases など） | Access Point が対応する S3 操作の範囲に収まること。連携先ごとの設定（例: Snowflake のステージ）が要る |
| クライアントツールでバケットへ移してから読ませる | 連携先がバケットを前提にする、またはバケットの機能（ライフサイクル、イベント通知）が要る | 複製が 2 か所になる。ファイルの属性は写らない |
| クライアントツールでファイルパスとして見せる | S3 API を使えないアプリが読み書きする | ツールの書き込みの制約に従う（Mountpoint は既定で上書き、追記、削除が不可） |

仕様と上限は、Playbook の[制約ノート](https://github.com/Yoshiki0705/FSx-for-ONTAP-Adoption-Playbook/blob/a4c8367f9172ee88f0af25731752af63dc2c6225/docs/ja/domains/data-utilization/notes/s3-access-point-constraints.md)が一次の情報です。ここには複製しません。

## 確認できていないこと

- 表の連携先が、FSx for ONTAP の Access Point を実際に読めること。
- 連携先ごとの設定の要件。Snowflake の `AWS_ACCESS_POINT_ARN` のような設定は、著者の 1 環境の記録です。
- Amazon Macie など、表にないサービスの対応。Playbook は、Macie が対象外であるという記録を引いています。
- 連携先ごとの性能と費用。

# 連携先の一覧: AWS サービスと製品、用途、クライアントツール

🌐 **言語**: **日本語** | [English](integrations-map.en.md)

> **区分**: 連携先の動作は、AWS と NetApp の文書、ブログ、著者の検証記事の記述です（閲覧日 2026-11-25、日本時間）。実機で確かめたのは、4 つのクライアントツールが S3 Access Points に対して動く範囲だけで、[2026-11-24 の記録](../benchmarks/records/2026-11-24-client-tools-stage3.md)にあります。連携先のサービス側の動作は、このリポジトリでは測っていません。用途の記号（N1〜N8、E1〜E9）と出典の記号（U1〜U14）は、[ユースケース](use-cases.md)の表のものです。

Amazon FSx for NetApp ONTAP（以下 FSx for ONTAP）の S3 Access Points は、S3 の API を読む相手に、ボリュームのファイルを見せます。相手が S3 Access Points を直接読むなら、クライアントツールは出てきません。クライアントツールが関わるのは、データを投入する、確認する、バケットとの間で移す、S3 API を使えないアプリへ見せる、という操作の側です。

## 連携先と用途の対応

区分の違いは、公開された根拠の種類の違いで、製品の優劣ではありません。表にない連携先は、未対応という意味ではなく、このリポジトリが調べていないものです。

| 連携先 | 種別 | 想定用途 | 根拠の区分 | 関わるクライアントツール | 出典 |
|---|---|---|---|---|---|
| Amazon Athena と AWS Glue Data Catalog | AWS サービス | N1、E1: ファイル共有のデータへの SQL 分析 | 公式の想定 | AWS CLI（データ投入と確認） | U6、U5 |
| AWS Glue（Apache Spark、Python シェル、Ray） | AWS サービス | N1、E1: ETL。結果を同じボリュームへ書き戻す | 公式の想定 | AWS CLI（確認） | U6 |
| Amazon Bedrock Knowledge Bases | AWS サービス | N2: 文書共有を元にした RAG | 公式の想定 | AWS CLI（文書の投入と確認） | U6 |
| Amazon Quick（呼称は出典により異なる。U5 は Quick Suite、U7 は AWS Quick と Quick Sight。同じサービスの時期の違いかは確認していない） | AWS サービス | N2、N3、E1: Access Point のエイリアスを S3 の連携先に指定してナレッジベースにする（U5 の手順）。U7 は、集計済みのデータのダッシュボードと定期実行の自動化も構成例に挙げる | 公式の想定 | AWS CLI（確認） | U5、U7 |
| Amazon Bedrock AgentCore | AWS サービス | N3: MCP ゲートウェイと AWS Lambda から、一覧、読み取り、検索をする | 公式の想定（U7 の構成例） | なし（読むのは AgentCore 側の Lambda。MCP クライアントのパターンはこのリポジトリでは未確認） | U7 |
| Amazon SageMaker | AWS サービス | E1: 機械学習のデータとして読む | 公式の想定 | AWS CLI（確認） | U5、U10 |
| Amazon EMR Serverless | AWS サービス | N1、E1: Spark のジョブ | 公式の想定 | なし | U6 |
| Amazon Redshift と Amazon OpenSearch Service | AWS サービス | E1: 分析とログ分析 | 公式の想定（NetApp のブログの例示。AWS の文書 U6 には記載なし） | なし | U10 |
| AWS Lambda | AWS サービス | N7、E3: ファイル投入の処理、共有データの読み取り | 公式の想定 | AWS CLI（動作確認） | U6、U5 |
| Amazon CloudFront | AWS サービス | N6: HLS 動画の配信 | 公式の想定 | なし | U6 |
| AWS Transfer Family | AWS サービス | N4: 外部との SFTP、FTPS、FTP の受け渡し。前提は ONTAP 9.17.1 以降、エイリアスのみ、リネームと追記は未対応、ネットワーク起点が VPC の Access Point は拒否される（U9。Snowflake も同じ型の制約、U13）。本検証の構成はそのままは使えない | 公式の想定 | なし（相手の SFTP クライアントは Transfer Family の文書の範囲） | U6、U9 |
| Amazon S3 の汎用バケット | AWS サービス | N5、E4a、E4b: サーバー側コピー（`CopyObject`、`UploadPartCopy`） | 公式の想定。バケット→ボリュームとボリューム→バケットを本検証で測定 | AWS CLI、s5cmd、rclone（ボリューム→バケットは本検証で未測定） | U8、Playbook、記録 |
| S3 Batch Operations | AWS サービス | E4a、E4b: 大量のコピーのジョブ | 公式の想定に加えて、[Playbook の記録](https://github.com/Yoshiki0705/FSx-for-ONTAP-Adoption-Playbook/blob/a4c8367f9172ee88f0af25731752af63dc2c6225/docs/ja/domains/data-utilization/notes/s3-access-points-server-side-copy-use-cases.md) | なし（本検証では未実行） | Playbook |
| Dremio Cloud | 外部製品 | E8a: 読み取りと、結果の書き戻し | 公式の想定（NetApp と、ほぼ同じ内容の Dremio 自身のブログ） | なし | U11、U12 |
| Snowflake | 外部製品 | E8b: 外部テーブル。検証 2026-05、読めた。条件は [use-cases の注 E8-b](use-cases.md) | 公開事例（著者の記事、1 環境） | なし | U13 |
| Databricks | 外部製品 | E8c: 検証 2026-05、一部だけ読めた。条件は [use-cases の注 E8-c](use-cases.md) | 公開事例（著者の記事、1 環境） | なし | U14 |
| ファイルパスとして使うアプリ | アプリ | N8: S3 API を使えないアプリへのファイルパスの提供 | 推定。マウントと基本操作は確認 | Mountpoint for Amazon S3 | 記録 |
| 商用の転送・ストリーミング製品 | 外部製品 | E9: File Mover Express、LucidLink Connect、LucidLink Suite | 推定 | 商用ツール（手動チェックリスト） | tool-facts |

## クライアントツールごとの関わり

| ツール | 関わる連携と用途 | 関連する操作の実測（用途の実測ではない） | パターン |
|---|---|---|---|
| AWS CLI | データの投入と確認（N1、N2、N7、E1、E3）、サーバー側コピー（N5、E4a、E4b）、定期ジョブ（E5） | 一覧、取得、書き込み、マルチパート、削除、サーバー側コピー | [patterns/ingest/aws-cli](../patterns/ingest/aws-cli/README.md) |
| s5cmd | 大量転送（E6）、サーバー側コピー（N5、E4a、E4b）、定期ジョブ（E5） | 一覧、取得、書き込み、削除、サーバー側コピー（性能は未測定） | [patterns/ingest/s5cmd](../patterns/ingest/s5cmd/README.md) |
| rclone | ほかのストレージとの同期（E7）、サーバー側コピー（N5、E4a、E4b） | 一覧、取得、書き込み、削除、サーバー側コピー。コピーには `--s3-storage-class FSX_ONTAP` が要った | [patterns/ingest/rclone](../patterns/ingest/rclone/README.md) |
| Mountpoint for Amazon S3 | S3 API を使えないアプリへのファイルパス（N8） | エイリアスと ARN でのマウント、新規書き込み、読み出し、`--allow-overwrite --allow-delete` での上書きと削除 | [patterns/streaming/mountpoint-for-amazon-s3](../patterns/streaming/mountpoint-for-amazon-s3/README.md) |
| MCP クライアント（Kiro、Claude Desktop） | AI クライアントからの一覧、読み取り、検索（N3 に近い構成） | なし（推定） | [patterns/mcp](../patterns/mcp/kiro/README.md) |
| 商用の転送・ストリーミング製品 | E9 | なし（手動チェックリストを利用者が記入） | [checklists/vendor](../checklists/vendor/file-mover-express/CHECKLIST.md) |

## 経路の選び方

連携先ごとに、入口は次の 3 つに分かれます。

| 入口 | 向く場面 | 制約 |
|---|---|---|
| サービスが Access Point を直接読む | 連携先が S3 API に対応している（Athena、Glue、Bedrock Knowledge Bases など） | Access Point が対応する S3 操作の範囲に収まること。連携先ごとの設定（例: Snowflake のステージ）が要る |
| クライアントツールでバケットへ移してから読ませる | 連携先がバケットを前提にする、またはバケットの機能（ライフサイクル、イベント通知）が要る | 複製が 2 か所になる。写るのは中身だけで、所有者、モード、更新時刻は、コピー先の設定とコピーした時刻になった（Playbook の実測。ファイルシステムユーザーが root の構成のみ）。コピーは同一リージョン内（U8） |
| クライアントツールでファイルパスとして見せる | S3 API を使えないアプリが読み書きする | ツールの書き込みの制約に従う（Mountpoint は既定で上書き、追記、削除が不可） |

仕様と上限は、Playbook の[制約ノート](https://github.com/Yoshiki0705/FSx-for-ONTAP-Adoption-Playbook/blob/a4c8367f9172ee88f0af25731752af63dc2c6225/docs/ja/domains/data-utilization/notes/s3-access-point-constraints.md)が一次の情報です。ここには複製しません。

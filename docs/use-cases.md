# ユースケース: S3 Access Points とクライアントツールが使われる場面

🌐 **言語**: **日本語** | [English](use-cases.en.md)

> **区分**: このページの用途は、公開された文書と記事から集めた想定です。出典の閲覧日は 2026-11-25（日本時間）です。実機で確かめたのは、4 つのクライアントツール（AWS CLI、s5cmd、rclone、Mountpoint for Amazon S3）が S3 Access Points に対して動く範囲だけで、[2026-11-24 の記録](../benchmarks/records/2026-11-24-client-tools-stage3.md)にあります。用途そのものの性能、費用、運用の確認は含みません。

Amazon FSx for NetApp ONTAP（以下 FSx for ONTAP）のボリュームに S3 Access Points を付けると、NFS や SMB で置いたファイルを S3 の API で読み書きできます。このページは、その使われ方を 3 つの面から整理します。オンプレミスの ONTAP での S3 の使われ方、FSx for ONTAP を新しく使う利用者の用途、すでに使っている利用者の用途です。どの用途にクライアントツールが関わるかは、[連携先の一覧](integrations-map.md)に表で示します。

## 根拠の区分

| 区分 | 意味 | 扱い |
|---|---|---|
| 公開事例 | 第三者または著者が、実際の環境で試した結果を公開している | 出典の環境と日付を添える。ほかの環境で同じとは書かない |
| 公式の想定 | AWS または NetApp の文書やブログが、その用途を想定として書いている | 「動く」とは書かず、「想定されている」と書く |
| 推定 | このリポジトリの推定（`candidate`） | 数値を書かない。確かめるまで推定のままにする |

用途ごとに「この Spoke の実測」の列を別に置きます。2026-11-24 の記録で確かめた操作だけに、`あり` と書きます。

## オンプレミスの ONTAP での S3 の使われ方

オンプレミスの ONTAP は、ボリュームを S3 のバケットのように見せる機能（S3 NAS バケット）を ONTAP 9.12.1 から持ちます。NetApp の文書が挙げる用途は次のとおりです。公開された導入事例は、2026-11-25 の検索（NetApp の文書、技術レポート、ブログ）では見つけられませんでした。

| # | 用途 | 内容 | 根拠の区分 | 出典 |
|---|---|---|---|---|
| 1 | NAS のデータを S3 クライアントで分析する | NAS クライアントが書いたデータを、S3 クライアントが読む。分析、BI、機械学習、光学文字認識が例に挙がる | 公式の想定 | U1、U2 |
| 2 | NAS と S3 の両方で読み書きするアプリの置き場 | Spark や Kafka のように、同じデータを両方のプロトコルで読み書きできるアプリ | 公式の想定 | U2 |
| 3 | 機械学習の学習データの置き場 | 準備したデータを ONTAP の NAS バケットに置き、学習の宛先として ONTAP S3 を選ぶパイプラインの例 | 公式の想定 | U4 |
| 4 | NFS と S3 の二重アクセス（Cloud Volumes ONTAP） | データサイエンティストは NFS で、ほかの利用者やアプリは S3 で、同じデータを使う | 公式の想定 | U3 |
| 5 | 非アクティブなデータの階層化先 | ONTAP の FabricPool が、非アクティブなデータをバケットへ移す。S3 NAS バケットは FabricPool の階層化先にできない | 公式の想定 | U1、U2 |

S3 NAS バケットは、通常のバケットの動作と違う点があります。NetApp の文書は、バージョニング、ライフサイクル、Object Lock の取得操作などを未対応とし、マルチパートアップロードは ONTAP 9.16.1 以降の条件付きで対応するとしています（U2）。FSx for ONTAP の S3 Access Points の対応範囲は別に決まっていて、Playbook の[制約ノート](https://github.com/Yoshiki0705/FSx-for-ONTAP-Adoption-Playbook/blob/a4c8367f9172ee88f0af25731752af63dc2c6225/docs/ja/domains/data-utilization/notes/s3-access-point-constraints.md)にあります。両者を同じ機能として扱わないでください。

## FSx for ONTAP を新しく使う利用者の想定用途

「新しく使う」は、これから FSx for ONTAP を入れる、または入れる前に S3 側の要件を決めたい利用者です。

| # | 用途 | 内容 | 根拠の区分 | この Spoke の実測 | 関わるクライアントツール | 出典 |
|---|---|---|---|---|---|---|
| N1 | ファイル共有のデータへの SQL 分析 | NFS や SMB に置かれたファイルを、Amazon Athena と AWS Glue Data Catalog で問い合わせる | 公式の想定 | なし | AWS CLI（データ投入と確認） | U6 |
| N2 | 文書共有を元にした RAG | Amazon Bedrock Knowledge Bases が、共有に置かれた文書を読み込む | 公式の想定 | なし | AWS CLI（文書の投入と確認） | U6、U5 |
| N3 | EDA のログの AI 分析 | NFS に書かれたシミュレーションのログを、Amazon Quick と Amazon Bedrock AgentCore から読む構成例 | 公式の想定（AWS ブログの構成例） | なし | なし（サービスが直接読む） | U7 |
| N4 | 外部との SFTP 受け渡し | AWS Transfer Family の SFTP、FTPS、FTP の入口を、Access Point の先のボリュームにつなぐ | 公式の想定 | なし | なし（Transfer Family が API を呼ぶ） | U6、U9 |
| N5 | バケットのデータをボリュームへ初期投入 | パートナーのバケットのデータを、マウントせずにボリュームへ写す | 公式の想定 | あり（コピーは 3 ツール） | AWS CLI、s5cmd、rclone | U8 |
| N6 | 動画のストリーミング配信 | ボリュームの HLS 動画を Amazon CloudFront で配信する | 公式の想定 | なし | なし | U6 |
| N7 | ファイル投入のサーバーレス処理 | AWS Lambda でサムネイルの生成、文書からのテキスト抽出、音声の書き起こしをする | 公式の想定 | なし | AWS CLI（動作確認） | U6 |
| N8 | アプリが S3 API を使えない環境へのファイルパス提供 | S3 API を前提にしないアプリへ、Access Point をファイルパスとして見せる | 推定 | あり（Mountpoint のマウントと基本操作） | Mountpoint for Amazon S3 | 記録 |

新しく使う利用者には、データの置き場所を決める選択肢が最初にあります。ボリュームを正本にして Access Point で読む、バケットを正本にして必要な分だけをボリュームへコピーする、の 2 つです。N5 は後者の入口です。

## すでに FSx for ONTAP を使っている利用者の想定用途

「すでに使っている」は、NFS や SMB のアプリがボリュームを使っている利用者です。既存のアプリは変えず、読み手を足す用途が中心です。

| # | 用途 | 内容 | 根拠の区分 | この Spoke の実測 | 関わるクライアントツール | 出典 |
|---|---|---|---|---|---|---|
| E1 | 既存の NAS データへ分析と AI の読み手を足す | アプリは NFS や SMB のまま、Amazon SageMaker、Amazon Athena、AWS Glue などが同じデータを読む | 公式の想定 | なし | AWS CLI | U5、U10 |
| E2 | オンプレミスの ONTAP から移したデータの S3 利用 | SnapMirror で FSx for ONTAP へ移したデータに、Access Point で S3 の読み手をつなぐ | 公式の想定（NetApp と Dremio のブログ） | なし | なし | U10、U11、U12 |
| E3 | サーバーレスとコンテナのアプリが共有データを読む | 設定ファイル、参照データ、コンテンツ、モデルのファイルなどを、S3 API で読む | 公式の想定 | なし | AWS CLI | U5 |
| E4 | ボリュームとバケットの間のサーバー側コピー | アーカイブ用のストレージクラスへの退避、バケットの機能（ライフサイクル、イベント通知）の利用、他チームのバケットへの書き出し | 公式の想定。Playbook に実機の記録あり | あり（コピーは 3 ツール） | AWS CLI、s5cmd、rclone | U8、記録 |
| E5 | 定期ジョブでのバックアップ、同期、取り込み | cron や定期ジョブから、ボリュームのファイルをバケットや他のストレージと同期する | 推定 | あり（一覧、取得、書き込み、削除） | AWS CLI、s5cmd、rclone | 記録 |
| E6 | 大量のファイルの並列転送 | 多数のファイルを並列に転送する | 推定 | あり（動作のみ。性能は未測定） | s5cmd、AWS CLI | 記録 |
| E7 | ほかのクラウドやストレージとの同期 | rclone で、複数のバックエンドの間を同期する | 推定 | あり（Access Point に対する操作のみ） | rclone | 記録 |
| E8 | 外部のデータ基盤からの読み取り | Dremio、Snowflake、Databricks が Access Point を読む | 公開事例（Snowflake と Databricks は著者の検証記事）、公式の想定（Dremio はベンダーのブログ） | なし | なし | U12、U13、U14 |
| E9 | 商用のファイル転送・ストリーミング製品の利用 | File Mover Express、LucidLink Connect、LucidLink Suite が Access Point を使う | 推定 | なし（チェックリストは利用者が記入） | 商用ツール | tool-facts |

E4 のサーバー側コピーは、Access Point を直接読めるサービス（Athena、Glue、Bedrock Knowledge Bases）へ渡すだけなら要りません。判断の表は、Playbook の[サーバー側コピーのユースケース](https://github.com/Yoshiki0705/FSx-for-ONTAP-Adoption-Playbook/blob/a4c8367f9172ee88f0af25731752af63dc2c6225/docs/ja/domains/data-utilization/notes/s3-access-points-server-side-copy-use-cases.md)にあります。

## 新規と既存の分け方

| 観点 | 新しく使う利用者 | すでに使っている利用者 |
|---|---|---|
| 最初の問い | データをどちらに置くか（ボリュームかバケットか） | 既存のアプリを変えずに、読み手をどう足すか |
| Access Point の役割 | 分析、AI、受け渡しの入口を最初から設計に入れる | 既存のボリュームに、あとから読み手の入口を付ける |
| クライアントツールの出番 | 初期投入、動作確認 | 定期ジョブ、バケットとの間の移動 |
| 先に確かめる制約 | Access Point が対応する S3 操作の範囲 | 既存アプリの書き込みと Access Point の読み取りの見え方 |

2 つの利用者の用途は重なります。N5 と E4 は同じ操作で、違いは、それが最初に一度だけか、運用の中で繰り返されるかです。

## 経路の選び方

同じデータを使う経路は、次の 5 つです。どれにも向く場面と制約があります。

| 経路 | 向く場面 | 制約 | 確認の状況 |
|---|---|---|---|
| Access Point を S3 の API で直接使う | 読み手が S3 API に対応し、アクセスポイントのエイリアスか ARN を指定できる | 対応する S3 操作に範囲がある。上限は Playbook の制約ノートを参照 | 4 ツールで操作を確認（2026-11-24） |
| ボリュームを NFS や SMB でマウントする | アプリがファイルパスを前提にする。名前の変更や追記が要る | ホストからボリュームへのネットワーク到達とマウントの権限が要る | このリポジトリでは未確認 |
| Mountpoint for Amazon S3 でファイルパスとして見せる | S3 API を使えないアプリが、ファイルとして読み書きする | 既定では上書き、追記、削除が不可。リネームは未実装 | 確認（2026-11-24、[記録](../benchmarks/records/2026-11-24-client-tools-stage3.md)） |
| バケットへサーバー側コピーする | バケット側の機能が要る。または正本がバケットにある | 複製が 2 か所になる。ファイルの属性は写らない | 3 ツールで確認（2026-11-24） |
| SnapMirror や AWS DataSync で複製や移行をする | ボリューム単位の複製、属性を保つ移行 | このリポジトリの範囲外 | 範囲外 |

軸ごとの比較は、[Mountpoint と S3 Access Points の使い分け](mountpoint-vs-s3-access-points.md)と、[選び方](how-to-choose.md)にあります。

## 確認できていないこと

- オンプレミスの ONTAP で S3 NAS バケットを使う公開事例。2026-11-25 の検索では見つかりませんでした。
- 表の用途ごとの性能、費用、運用の負荷。このリポジトリは測っていません。
- AWS サービスと外部のデータ基盤が、FSx for ONTAP の Access Point を読めること。AWS の文書と記事の記述で、実機では確かめていません。
- 商用ツール 3 製品の動作。
- Snowflake と Databricks の構成は、著者の 1 環境での検証記事で、各社が FSx for ONTAP の Access Point を対応構成として文書化しているとは確認していません。
- 検索で見つけた文書のうち、本文を開いて読んだものだけを出典に載せました。

## 出典一覧

閲覧日は、すべて 2026-11-25（日本時間）です。

| ID | 出典 | URL |
|---|---|---|
| U1 | NetApp: ONTAP S3 primary use cases | https://docs.netapp.com/us-en/ontap/s3-config/use-cases.html |
| U2 | NetApp: Learn about ONTAP S3 multiprotocol support | https://docs.netapp.com/us-en/ontap/s3-multiprotocol/ |
| U3 | NetApp: Solution technology（NFS と S3 の二重アクセス） | https://docs.netapp.com/us-en/netapp-solutions-ai/data-analytics/cdm-fod-solution-technology.html |
| U4 | NetApp: Solution Overview（AI パイプライン） | https://docs.netapp.com/us-en/netapp-solutions-ai/infra/ai-pipeline-solution-overview.html |
| U5 | AWS ニュースブログ: Amazon FSx for NetApp ONTAP now integrates with Amazon S3 | https://aws.amazon.com/jp/blogs/aws/amazon-fsx-for-netapp-ontap-now-integrates-with-amazon-s3-for-seamless-data-access/ |
| U6 | FSx for ONTAP ユーザーガイド: Using access points with AWS services | https://docs.aws.amazon.com/fsx/latest/ONTAPGuide/using-access-points-with-aws-services.html |
| U7 | AWS Storage ブログ: Enable zero-copy access to AWS services on Amazon FSx for NetApp ONTAP with Amazon S3 Access Points | https://aws.amazon.com/blogs/storage/enable-zero-copy-access-to-aws-services-on-amazon-fsx-for-netapp-ontap-with-amazon-s3-access-points/ |
| U8 | AWS What's New: server-side copy between S3 buckets and FSx file systems | https://aws.amazon.com/about-aws/whats-new/2026/11/s3-access-points-server-side-copy-fsx/ | <!-- allow:naming: verbatim page title -->
| U9 | AWS Transfer Family ユーザーガイド: FSx for NetApp ONTAP | https://docs.aws.amazon.com/transfer/latest/userguide/fsx-s3-access-points.html |
| U10 | NetApp ブログ: Simplify data access with S3 Access Points for FSx for ONTAP | https://www.netapp.com/blog/data-access-s3-access-points-fsx-ontap/ |
| U11 | NetApp ブログ: Unlock AI insights with ONTAP and S3 access points | https://www.netapp.com/blog/ai-insights-ontap-s3-access-points-dremio/ |
| U12 | Dremio ブログ: From file systems to AI insights | https://www.dremio.com/blog/from-file-systems-to-ai-insights-dremio-cloud-amazon-fsx-for-netapp-ontap/ |
| U13 | 著者の検証記事: Snowflake と S3 Access Points | https://dev.to/aws-builders/snowflake-and-fsx-for-ontap-s3-access-points-from-access-denied-to-working-external-tables-9k8 |
| U14 | 著者の検証記事: Databricks と S3 Access Points | https://dev.to/aws-builders/databricks-and-fsx-for-ontap-s3-access-points-a-layer-by-layer-validation-of-observed-boundaries-p4d |
| 記録 | このリポジトリの 2026-11-24 の実機確認 | [2026-11-24-client-tools-stage3.md](../benchmarks/records/2026-11-24-client-tools-stage3.md) |
| tool-facts | このリポジトリのツールの事実確認 | [tool-facts.md](tool-facts.md) |

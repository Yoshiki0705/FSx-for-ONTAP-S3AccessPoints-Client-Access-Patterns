# ユースケース: S3 Access Points とクライアントツールが使われる場面

🌐 **言語**: **日本語** | [English](use-cases.en.md)

> **区分**: このページの用途は、公開された文書と記事から集めた想定です。出典の閲覧日は 2026-11-25（日本時間）です。実機で確かめたのは、4 つのクライアントツール（AWS CLI、s5cmd、rclone、Mountpoint for Amazon S3）が S3 Access Points に対して動く範囲だけで、[2026-11-24 の記録](../benchmarks/records/2026-11-24-client-tools-stage3.md)にあります。用途そのものの性能、費用、運用の確認は含みません。

Amazon FSx for NetApp ONTAP（以下 FSx for ONTAP）のボリュームに S3 Access Points を付けると、NFS や SMB で置いたファイルを S3 の API で読み書きできます。このページは、その使われ方を 3 つの面から整理します。オンプレミスの ONTAP での S3 の使われ方、FSx for ONTAP を新しく使う利用者の用途、すでに使っている利用者の用途です。どの用途にクライアントツールが関わるかは、[連携先の一覧](integrations-map.md)に表で示します。

## 根拠の区分

| 区分 | 意味 | 扱い |
|---|---|---|
| 公開事例 | 第三者または著者が、実際の環境で試した結果を公開している | 出典の環境と日付を添える。ほかの環境で同じとは書かない |
| 公式の想定 | AWS または NetApp の文書、ブログ、構成例が、その用途を想定として書いている | 「動く」とは書かず、「想定されている」と書く |
| 推定 | このリポジトリの推定（`candidate`） | 数値を書かない。確かめるまで推定のままにする |

用途の表には「関連する操作の実測」の列を置きます。これは用途の実測ではありません。2026-11-24 の記録で動作を確かめた操作の名前だけを書き、用途そのもの（性能、運用、整合）は未測定です。

公式の想定は、導入や調達、監査の根拠には使えません。製品ごとに区分が違うのは、公開された根拠の種類が違うためで、製品の優劣ではありません。

## オンプレミスの ONTAP での S3 の使われ方

オンプレミスの ONTAP は、ボリュームを S3 のバケットのように見せる機能（S3 NAS バケット）を ONTAP 9.12.1 から持ちます。NetApp の文書が挙げる用途は次のとおりです。FSx for ONTAP の S3 Access Points とは別の機能で、同じ ONTAP の S3 の考え方がオンプレミスでどう使われてきたかの参考として置いています。公開された導入事例は、2026-11-25 の検索（NetApp の文書、技術レポート、ブログ）では見つけられませんでした。

| # | 用途 | 内容 | 根拠の区分 | 出典 |
|---|---|---|---|---|
| 1 | NAS のデータを S3 クライアントで分析する | NAS クライアントが書いたデータを、S3 クライアントが読む。分析、BI、機械学習、光学文字認識が例に挙がる | 公式の想定 | U1、U2 |
| 2 | NAS と S3 の両方で読み書きするアプリの置き場 | Spark や Kafka のように、同じデータを両方のプロトコルで読み書きできるアプリ | 公式の想定 | U2 |
| 3 | 機械学習の学習データの置き場 | 準備したデータを ONTAP の NAS バケットに置き、学習の宛先として ONTAP S3 を選ぶパイプラインの例。FSx for ONTAP での確認はない | 公式の想定 | U4 |
| 4 | NFS と S3 の二重アクセス（Cloud Volumes ONTAP） | データサイエンティストは NFS で、ほかの利用者やアプリは S3 で、同じデータを使う | 公式の想定 | U3 |

オンプレミスの ONTAP の FabricPool は、非アクティブなデータをバケットへ移す別の機能です。S3 NAS バケットは FabricPool の階層化先にできません（U2）。U1 は、FabricPool が ONTAP の通常の S3 バケットへ階層化できることを挙げています。

S3 NAS バケットは、通常のバケットの動作と違う点があります。NetApp の文書は、バージョニング、ライフサイクル、Object Lock の取得操作などを未対応とし、マルチパートアップロードは ONTAP 9.16.1 以降の条件付きで対応するとしています（U2）。FSx for ONTAP の S3 Access Points の対応範囲は別に決まっていて、Playbook の[制約ノート](https://github.com/Yoshiki0705/FSx-for-ONTAP-Adoption-Playbook/blob/a4c8367f9172ee88f0af25731752af63dc2c6225/docs/ja/domains/data-utilization/notes/s3-access-point-constraints.md)にあります。両者を同じ機能として扱わないでください。

## FSx for ONTAP を新しく使う利用者の想定用途

「新しく使う」は、これから FSx for ONTAP を入れる、または入れる前に S3 側の要件を決めたい利用者です。

| # | 用途 | 内容 | 根拠の区分 | 関連する操作の実測（用途の実測ではない） | 関わるクライアントツール | 出典 |
|---|---|---|---|---|---|---|
| N1 | ファイル共有のデータへの SQL 分析 | NFS や SMB に置かれたファイルを、Amazon Athena と AWS Glue Data Catalog で問い合わせる | 公式の想定 | なし | AWS CLI（データ投入と確認） | U6 |
| N2 | 文書共有を元にした RAG | Amazon Bedrock Knowledge Bases が、共有に置かれた文書を読み込む。権限は、Access Point のファイルシステムユーザー 1 つに集約される（U9）。文書の更新を反映する方法（同期の再実行など）は、出典に書かれておらず未確認 | 公式の想定 | なし | AWS CLI（文書の投入と確認） | U6、U5 |
| N3 | EDA のログの AI 分析 | NFS に書かれたシミュレーションのログを、Amazon Quick と Amazon Bedrock AgentCore から読む構成例 | 公式の想定（U7 の構成例） | なし | なし（サービスが直接読む） | U7 |
| N4 | 外部との SFTP 受け渡し | AWS Transfer Family の SFTP、FTPS、FTP の入口を、Access Point の先のボリュームにつなぐ。前提は U9 に書かれている。ONTAP 9.17.1 以降、ファイルシステムと Access Point が同一リージョン・同一アカウント、指定はエイリアスのみ（ARN は不可）、リネームと追記は未対応（WinSCP の一時ファイル名のアップロードは失敗する）。Transfer Family は VPC の外から要求するため、ネットワーク起点が VPC の Access Point は拒否される。本検証の構成（起点が VPC）は、そのままは使えない | 公式の想定 | なし | なし（Transfer Family が API を呼ぶ） | U6、U9 |
| N5 | バケットのデータをボリュームへ初期投入 | パートナーのバケットのデータを、マウントせずにボリュームへ写す | 公式の想定 | バケット→ボリュームのコピー（AWS CLI、s5cmd、rclone） | AWS CLI、s5cmd、rclone | U8 |
| N6 | 動画のストリーミング配信 | ボリュームの HLS 動画を Amazon CloudFront で配信する | 公式の想定 | なし | なし | U6 |
| N7 | ファイル投入のサーバーレス処理 | AWS Lambda でサムネイルの生成、文書からのテキスト抽出、音声の書き起こしをする | 公式の想定 | なし | AWS CLI（動作確認） | U6 |
| N8 | アプリが S3 API を使えない環境へのファイルパス提供 | S3 API を前提にしないアプリへ、Access Point をファイルパスとして見せる | 推定 | Mountpoint のマウントと基本操作のみ。用途は未測定 | Mountpoint for Amazon S3 | 記録 |

新しく使う利用者には、データの置き場所を決める選択肢が最初にあります。ボリュームを正本にして Access Point で読む、バケットを正本にして必要な分だけをボリュームへコピーする、の 2 つです。N5 は後者の入口です。

## すでに FSx for ONTAP を使っている利用者の想定用途

「すでに使っている」は、NFS や SMB のアプリがボリュームを使っている利用者です。既存のアプリは変えず、読み手を足す用途が中心です。

| # | 用途 | 内容 | 根拠の区分 | 関連する操作の実測（用途の実測ではない） | 関わるクライアントツール | 出典 |
|---|---|---|---|---|---|---|
| E1 | 既存の NAS データへ分析と AI の読み手を足す | アプリは NFS や SMB のまま、Amazon SageMaker、Amazon Athena、AWS Glue などが同じデータを読む | 公式の想定 | なし | AWS CLI | U5、U10 |
| E2 | オンプレミスの ONTAP から移したデータの S3 利用 | SnapMirror で FSx for ONTAP へ移したデータに、Access Point で S3 の読み手をつなぐ | 公式の想定（NetApp と Dremio の、ほぼ同じ内容のブログ 2 本） | なし | なし | U10、U11、U12 |
| E3 | サーバーレスとコンテナのアプリが共有データを読む | 設定ファイル、参照データ、コンテンツ、モデルのファイルなどを、S3 API で読む | 公式の想定 | なし | AWS CLI | U5 |
| E4a | バケットからボリュームへのサーバー側コピー | バケットのデータをボリュームへ入れる（パートナーのバケットからの取り込みなど） | 公式の想定（U8） | バケット→ボリュームのコピー（3 ツール） | AWS CLI、s5cmd、rclone | U8、記録 |
| E4b | ボリュームからバケットへのサーバー側コピー | アーカイブ用のストレージクラスへの退避、バケットの機能（ライフサイクル、イベント通知）の利用、他チームのバケットへの書き出し。退避、ライフサイクル、イベント通知の記述は Playbook のノートにあり、U8 にはない | 公式の想定（U8 はコピー自体、Playbook の[ノート](https://github.com/Yoshiki0705/FSx-for-ONTAP-Adoption-Playbook/blob/a4c8367f9172ee88f0af25731752af63dc2c6225/docs/ja/domains/data-utilization/notes/s3-access-points-server-side-copy-use-cases.md)が用途） | 本検証で未測定。Playbook に実測の記録がある | なし（クライアントツールでの動作は未確認） | U8、Playbook |
| E5 | 定期ジョブでのバックアップ、同期、取り込み | cron や定期ジョブから、ボリュームのファイルをバケットや他のストレージと同期する。Access Point は S3 のイベント通知に対応しないため、更新の検知は定期実行になる（U15、U13）。通知を自作する取り込みは、通知が捨てられてもパイプが正常と報告しうるので、オブジェクト数と読み込んだ行数の突き合わせで監視する（U13、著者の 1 環境） | 推定 | 一覧、取得、書き込み、削除（1 回ずつ）。定期実行は未測定 | AWS CLI、s5cmd、rclone | 記録 |
| E6 | 大量のファイルの並列転送 | 多数のファイルを並列に転送する | 推定 | 取得と書き込みを 1 ファイルずつ。並列転送は未測定 | s5cmd、AWS CLI | 記録 |
| E7 | ほかのクラウドやストレージとの同期 | rclone で、複数のバックエンドの間を同期する | 推定 | rclone の一覧、取得、書き込み、削除（1 つのバックエンドのみ） | rclone | 記録 |
| E8a | Dremio が Access Point を読む | 読み取り、結果の書き戻し | 公式の想定（NetApp と、ほぼ同じ内容の Dremio 自身のブログ） | なし | なし | U11、U12 |
| E8b | Snowflake が Access Point を読む | 検証 2026-05、読めた。条件は注 E8-b | 公開事例（著者の記事、1 環境） | なし | なし | U13 |
| E8c | Databricks が Access Point を読む | 検証 2026-05、一部だけ読めた。条件は注 E8-c | 公開事例（著者の記事、1 環境） | なし | なし | U14 |

E8 の 3 行は、同じ項目（検証の時期と環境、動いたこと、動かなかったこと、各社の文書での扱い）の順に書きます。区分の違いは公開された根拠の種類の違いで、製品の優劣ではありません。

- 注 E8-a（Dremio）: 検証の記述はなく、読み取りと、結果の FSx for ONTAP の S3 バケットへの書き戻しが、ブログに構成として書かれている。各社の文書での扱いは確認していない（U11、U12）。
- 注 E8-b（Snowflake）: 検証は 2026-05（Standard edition、ap-northeast-1、ONTAP 9.17.1）。ステージに `AWS_ACCESS_POINT_ARN` を指定すると読め、指定しないと LIST は通り SELECT は失敗した。2026-09 に周辺の記述が訂正され、この中心の発見は変わっていない。検証した Access Point は、ネットワーク起点がインターネットで、起点が VPC の Access Point は Snowflake の SaaS から使えない（U13）。Snowflake 自身の文書では、対応構成として確認していない（U13 自身が、公式の対応構成ではないと書く）。
- 注 E8-c（Databricks）: 検証は 2026-05（DBR 17.3 LTS、ap-northeast-1）、2026-09 に訂正。Instance Profile と boto3 による直接の読み取りは、利用者が管理する VPC（Databricks の用語で customer-managed VPC）の中で、FSx for ONTAP と同じ VPC に置いた Dedicated クラスターだけで通り、Databricks が管理する VPC（VPC ピアリング）では read timeout だった。ドライバーノードだけの検証で、Spark のエグゼキューターは未検証。この経路は Unity Catalog のガバナンスの外にある（PoC 向け）。Unity Catalog の External Location は、著者の追記（2026-05-26）が、`access_point` フィールドは一般提供でなく文書から削除されており、部分的な成功は非対応の副作用と読むのが妥当、と書く。U14 の冒頭の判断表が推奨するステージング経路（FPolicy を使う構成）は、S3 Access Points 経由の書き込みを FPolicy が検知しないため使えない（U13 の 2026-09 の訂正）。各社の文書では、対応構成として確認していない。
- 外部製品へ読ませると、データの処理場所や保存場所が変わりうる。たとえば Snowflake の COPY INTO は、Snowflake が管理するストレージへの複製を作り、Cortex の cross-region inference は別リージョンへ流しうる（U13）。公式の想定は、調達の根拠にならない。

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

| 経路 | 向く場面 | 制約 | 確認の状況（確認済み / 文書上 / 未確認 / 範囲外） |
|---|---|---|---|
| Access Point を S3 の API で直接使う | 読み手が S3 API に対応し、アクセスポイントのエイリアスか ARN を指定できる | 条件付き書き込み（`If-None-Match`）は未対応で、`aws s3 cp --no-overwrite` は失敗した（U15）。ストレージクラスは `FSX_ONTAP` だけ。そのほかの上限は [Playbook の制約ノート](https://github.com/Yoshiki0705/FSx-for-ONTAP-Adoption-Playbook/blob/a4c8367f9172ee88f0af25731752af63dc2c6225/docs/ja/domains/data-utilization/notes/s3-access-point-constraints.md) | 確認済み（4 ツールの操作、2026-11-24） |
| ボリュームを NFS や SMB でマウントする | アプリがファイルパスを前提にする。名前の変更や追記が要る | ホストからボリュームへのネットワーク到達と、マウントの権限が要る | 未確認（このリポジトリでは測っていない） |
| Mountpoint for Amazon S3 でファイルパスとして見せる | S3 API を使えないアプリが、ファイルとして読み書きする | 既定では上書き、追記、削除ができない。リネームは汎用バケットでは対応しない（S3 Express One Zone のみ。Mountpoint の SEMANTICS.md）。上書きを許可しない既定でも、存在確認の後に別のクライアントがアップロードすると置き換わりうる | 確認済み（2026-11-24、[記録](../benchmarks/records/2026-11-24-client-tools-stage3.md)） |
| バケットへサーバー側コピーする | バケット側の機能が要る。または正本がバケットにある | 複製が 2 か所になる。写るのは中身だけで、所有者、モード、更新時刻は、コピー先の設定とコピーした時刻になった（Playbook の実測。ファイルシステムユーザーが root の構成のみ。root 以外は未測定）。コピーは同一リージョン内（U8）。ファイルシステム間（FSx for OpenZFS を含む）のコピーは U8 にあるが、このリポジトリの範囲外 | 確認済み（バケット→ボリュームを 3 ツールで、2026-11-24）。ボリューム→バケットは Playbook の記録 |
| SnapMirror や AWS DataSync で複製や移行をする | ボリューム単位の複製、属性を保つ移行 | このリポジトリはクライアントツールが対象のため扱わない | 範囲外 |

軸ごとの比較は、[Mountpoint と S3 Access Points の使い分け](mountpoint-vs-s3-access-points.md)と、[選び方](how-to-choose.md)にあります。

## ネットワーク起点の選び方

Access Point を作るときに、ネットワーク起点を選びます。2 つの選択肢に、向く場面と制約があります。

| 起点 | 向く場面 | 制約 | 確認の状況 |
|---|---|---|---|
| VPC | 自分の VPC の中のクライアントが使う | VPC の外から呼ぶサービス（Snowflake、AWS Transfer Family）は、この起点の Access Point を使えない（U13、U9） | 確認済み（本検証の EC2 から、VPC 内で使った） |
| インターネット | VPC の外から呼ぶサービスが使う | 公開の入口ではなく、IAM とアクセスポイントのポリシー、ファイルシステムユーザーの権限が制御になる。U9 は、通信が AWS のバックボーンを通ると書く。root でなく最小権限のユーザーを選ぶ | 文書上（U9、U13）。本検証では未確認 |

## 確認できていないこと

- オンプレミスの ONTAP で S3 NAS バケットを使う公開事例。2026-11-25 の検索では見つかりませんでした。
- 表の用途ごとの性能、費用、運用の負荷。このリポジトリは測っていません。
- AWS サービスと外部のデータ基盤が、FSx for ONTAP の Access Point を読めること。AWS の文書と記事の記述で、実機では確かめていません。
- 商用ツール 3 製品の動作。
- ボリューム→バケット方向のサーバー側コピーのクライアントツールでの動作（本検証は逆方向のみ）。
- サーバー側コピーが途中で失敗したときの挙動と再試行。
- NTFS セキュリティスタイルのボリューム（SMB）での動作。本検証は UNIX セキュリティスタイルのみ。
- 書きかけのファイルや、SMB のロック中のファイルが、S3 の読み手にどう見えるか。
- Access Point 経由のアクセスが、監査ログにどう記録されるか。Playbook の[制約ノート](https://github.com/Yoshiki0705/FSx-for-ONTAP-Adoption-Playbook/blob/a4c8367f9172ee88f0af25731752af63dc2c6225/docs/ja/domains/data-utilization/notes/s3-access-point-constraints.md)に記載があるが、本検証では確認していない。
- Access Point を付けたことによる、既存の NFS と SMB のワークロードへの影響（スループット容量の共有）。
- Athena が読むファイル形式、パーティション、小さなファイルが多い場合の挙動。
- サーバー側コピーで、ストレージクラスと暗号化の指定が当たる落とし穴。AWS の対応表は、コピー先が FSx for ONTAP の Access Point のとき、SSE-FSX 以外の暗号化の指定は 400 を返すと書く（U15）。Playbook に実測の記録がある。本検証では測っていない。
- 表にない連携先の対応。表にないことは、未対応を意味しない。
- Snowflake と Databricks の構成は、著者の 1 環境での検証記事です。NetApp のブログ（U10）は、Snowflake と Databricksへつなげられると書いていますが、各社自身の文書では、対応構成として確認していません。
- 検索で見つけた文書のうち、本文を開いて読んだものだけを出典に載せました。

## 出典一覧

閲覧日は、すべて 2026-11-25（日本時間）です。

| ID | 出典 | URL |
|---|---|---|
| U1 | NetApp: ONTAP S3 primary use cases | https://docs.netapp.com/us-en/ontap/s3-config/use-cases.html |
| U2 | NetApp: Learn about ONTAP S3 multiprotocol support | https://docs.netapp.com/us-en/ontap/s3-multiprotocol/ |
| U3 | NetApp: Solution technology（NFS と S3 の二重アクセス） | https://docs.netapp.com/us-en/netapp-solutions-ai/data-analytics/cdm-fod-solution-technology.html |
| U4 | NetApp: Solution Overview（AI パイプライン） | https://docs.netapp.com/us-en/netapp-solutions-ai/infra/ai-pipeline-solution-overview.html |
| U5 | AWS ニュースブログ: Amazon FSx for NetApp ONTAP now integrates with Amazon S3 | https://aws.amazon.com/blogs/aws/amazon-fsx-for-netapp-ontap-now-integrates-with-amazon-s3-for-seamless-data-access/ |
| U6 | FSx for ONTAP ユーザーガイド: Using access points with AWS services | https://docs.aws.amazon.com/fsx/latest/ONTAPGuide/using-access-points-with-aws-services.html |
| U7 | AWS Storage ブログ: Enable zero-copy access to AWS services on Amazon FSx for NetApp ONTAP with Amazon S3 Access Points | https://aws.amazon.com/blogs/storage/enable-zero-copy-access-to-aws-services-on-amazon-fsx-for-netapp-ontap-with-amazon-s3-access-points/ |
| U8 | AWS What's New: server-side copy between S3 buckets and FSx file systems | https://aws.amazon.com/about-aws/whats-new/2026/11/s3-access-points-server-side-copy-fsx/ | <!-- allow:naming: verbatim page title -->
| U9 | AWS Transfer Family ユーザーガイド: FSx for NetApp ONTAP | https://docs.aws.amazon.com/transfer/latest/userguide/fsx-s3-access-points.html |
| U10 | NetApp ブログ: Simplify data access with S3 Access Points for FSx for ONTAP | https://www.netapp.com/blog/data-access-s3-access-points-fsx-ontap/ |
| U11 | NetApp ブログ: Unlock AI insights with ONTAP and S3 access points | https://www.netapp.com/blog/ai-insights-ontap-s3-access-points-dremio/ |
| U12 | Dremio ブログ: From file systems to AI insights | https://www.dremio.com/blog/from-file-systems-to-ai-insights-dremio-cloud-amazon-fsx-for-netapp-ontap/ |
| U13 | 著者の検証記事: Snowflake と S3 Access Points | https://dev.to/aws-builders/snowflake-and-fsx-for-ontap-s3-access-points-from-access-denied-to-working-external-tables-9k8 |
| U14 | 著者の検証記事: Databricks と S3 Access Points（2026-05 の検証、2026-05-26 の追記、2026-09 の訂正を含む） | https://dev.to/aws-builders/databricks-and-fsx-for-ontap-s3-access-points-a-layer-by-layer-validation-of-observed-boundaries-p4d |
| U15 | FSx for ONTAP ユーザーガイド: Access point compatibility | https://docs.aws.amazon.com/fsx/latest/ONTAPGuide/access-points-for-fsxn-object-api-support.html |
| 記録 | このリポジトリの 2026-11-24 の実機確認 | [2026-11-24-client-tools-stage3.md](../benchmarks/records/2026-11-24-client-tools-stage3.md) |
| tool-facts | このリポジトリのツールの事実確認 | [tool-facts.md](tool-facts.md) |

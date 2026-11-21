# Hub PR の下書き（段階 3）

Hub（FSx-for-ONTAP-S3AccessPoints-Serverless-Patterns）の関連リポジトリ表にこの Spoke を載せる PR の下書きです。**Hub には何も適用していません。**

**この PR は、Spoke の GitHub リポジトリ（`https://github.com/Yoshiki0705/FSx-for-ONTAP-S3AccessPoints-Client-Access-Patterns`）が作られて公開されるまで開かないでください。** 作る前は、PR 内のリンクがすべて 404 になります（段階 4 で作成）。

| ファイル | 内容 |
|---|---|
| [README-related-repositories.md](README-related-repositories.md) | Hub の `README.md` / `README.en.md` に足す 1 行 |
| [docs-hub-spoke-relation.md](docs-hub-spoke-relation.md)、[英語版](docs-hub-spoke-relation.en.md) | Hub に新規追加する関係図の文書（Mermaid） |
| [PR-BODY.md](PR-BODY.md) | PR のタイトル案と本文 |
| [llms-txt-check.md](llms-txt-check.md) | `llms.txt` などの索引の確認結果と、新規ファイルが通すゲート |
| [APPLY.md](APPLY.md) | 専用 worktree で Hub に適用する手順 |

他の 6 言語の README は対象外で、Hub の持ち主が別途決めます。

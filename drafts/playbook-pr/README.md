# Playbook PR の下書き

Adoption-Playbook（以下 Playbook）に、この Spoke を載せる PR の下書きです。**Playbook には何も適用していません。**

**この PR は、Spoke の GitHub リポジトリ（`https://github.com/Yoshiki0705/FSx-for-ONTAP-S3AccessPoints-Client-Access-Patterns`）が作られて公開されるまで開かないでください。** Playbook の `cross-repo-external` は、本文に現れる兄弟リポジトリの名前を GitHub の API で引くため、作る前は失敗します。

| ファイル | 内容 |
|---|---|
| [README-related-repositories.md](README-related-repositories.md) | Playbook の `README.md` と `docs/en/README.md` の「関連リポジトリ」表に足す 1 行、`docs/ja/reference/cross-repo-index.md` の「分担の原則」表に足す 1 行 |
| [index-check.md](index-check.md) | `llms.txt` などの索引への追記要否の確認結果、`llms.txt` に足す文案、新規の追記が通すゲート |
| [PR-BODY.md](PR-BODY.md) | PR のタイトル案と本文 |
| [APPLY.md](APPLY.md) | 専用 worktree で Playbook に適用する手順 |

3 層の関係図（Playbook、Spoke 2 つ）は Playbook には足さず、このリポジトリの [docs/spoke-relations.md](../../docs/spoke-relations.md) に置いています。Playbook の「関連リポジトリ」表と引用索引が、同じ分担を文章で持っているためです。

Playbook のルート `README.md` は 8 言語すべてで検査される規約です。この下書きが持つのは日本語と英語の 2 言語だけで、残りの 6 言語（ko、zh-CN、zh-TW、fr、de、es）は含みません。扱いは Playbook の持ち主が決めます。詳しくは [APPLY.md](APPLY.md) の「未解決の点」を参照してください。

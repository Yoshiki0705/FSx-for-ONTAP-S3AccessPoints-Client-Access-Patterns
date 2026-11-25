# Playbook へのフィードバックの流れ

このリポジトリでの確認中に、Playbook に記録のない S3 Access Points の制約や挙動、または選定に影響する FSx for ONTAP の仕様を見つけたときの手順です。

1. `drafts/playbook-feedback/TEMPLATE.md` をコピーし、`drafts/playbook-feedback/<日付>-<トピック>.md` を作る。
2. 観測した事実を 1 文 1 事実で書き、再現手順、環境、成功した対照操作、関係する Playbook 文書と節を埋める。
3. 組織名、アカウント ID、リソース ID、実際のアクセスポイント別名を書かない。
4. このリポジトリの文書には、先に事実として書かない。書く場合は「Playbook へ報告済み・未反映」と明示する。
5. 下書きを Playbook に出すかどうかは、利用者が決める。エージェントは Issue も PR も作らない。出すときの入口は、Playbook の [cross-repo finding の Issue テンプレート](https://github.com/Yoshiki0705/FSx-for-ONTAP-Adoption-Playbook/issues/new?template=cross-repo-finding.yml)（Direction は「Absorb」）。事実の誤りの訂正は、Playbook の別テンプレート（`correction.yml`）を使う。
6. Playbook が新しい `main` を進めたら、`docs/reference-pins.md` の手順で固定を追従し、下書きの状態を「反映済み（Playbook のコミット）」に更新する。

## 兄弟 Spoke に向く所見

後続のサーバーレス処理の実装（Lambda、AWS Step Functions など）に関する所見は、Playbook ではなく兄弟 Spoke の Serverless-Patterns に向きます。下書きの「宛先」欄に `Serverless-Patterns` と書き、同じ流れで利用者が提出先を決めます。S3 Access Points の仕様や上限そのものに関する所見は、Playbook が持ちます（Serverless-Patterns は仕様と上限を Playbook に委ねています）。

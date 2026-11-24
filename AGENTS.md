# AGENTS.md

> このリポジトリで作業する AI コーディングエージェント向けの指示です。着手前に必要な最小限だけを書き、詳細は `docs/agent/` にあります。

## 概要

FSx for ONTAP の S3 Access Points をクライアントツールから使うときの手順、チェックリスト、測定記録、互換性マトリクスを持つリポジトリです（Spoke）。全体の入口は Adoption-Playbook（以下 Playbook）で、S3 Access Points の仕様と上限、他サービスとの選定に影響する FSx for ONTAP のコア仕様は Playbook が持ち、ここには複製しません。FSx-for-ONTAP-S3AccessPoints-Serverless-Patterns（以下 Serverless-Patterns）は、後続のサーバーレス処理の実装を持つ兄弟の Spoke です。参照の固定は [docs/reference-pins.md](docs/reference-pins.md) の 2 つに限ります（Playbook はコミット SHA、Serverless-Patterns はリリースタグ）。

## 詳細知識の所在

| 作業 | 参照先 |
|---|---|
| 確認水準（`C` / `D` / `M`）の付け方、数値の扱い | [docs/agent/confirmation-levels.md](docs/agent/confirmation-levels.md) |
| パターン、チェックリスト、記録の雛形の使い方 | [docs/agent/templates-howto.md](docs/agent/templates-howto.md) |
| Playbook に見つけた不足を伝える | [docs/agent/playbook-feedback-flow.md](docs/agent/playbook-feedback-flow.md) |
| 参照の固定（Playbook のコミット、Serverless-Patterns のタグ）の更新 | [docs/reference-pins.md](docs/reference-pins.md) |
| 言語の追加 | [docs/adding-a-language.md](docs/adding-a-language.md) |
| 実機ベンチマーク | [benchmarks/README.md](benchmarks/README.md) |
| ベンダーの「できない」を書く、仕様を引く | [Playbook の証拠の方針](https://github.com/Yoshiki0705/FSx-for-ONTAP-Adoption-Playbook/blob/a4c8367f9172ee88f0af25731752af63dc2c6225/docs/ja/evidence-policy.md)、[Playbook の技術主張の書き方](https://github.com/Yoshiki0705/FSx-for-ONTAP-Adoption-Playbook/blob/a4c8367f9172ee88f0af25731752af63dc2c6225/docs/agent/domain-knowledge.md) |
| Playbook 全体の規約（命名、中立性、公開安全） | [Playbook の AGENTS.md](https://github.com/Yoshiki0705/FSx-for-ONTAP-Adoption-Playbook/blob/a4c8367f9172ee88f0af25731752af63dc2c6225/AGENTS.md) |

命名、ベンダー中立性、公開安全の規約の本体は Playbook 側にあり、ここには写しません。このリポジトリでの機械検査は `scripts/check_naming.py` と `scripts/check_public_safety.py` です。

## このリポジトリ固有の規則

1. Playbook の数値（上限、サイズ、価格）をこのリポジトリの文書に書き写さない。Playbook の該当節へのリンクにする。Serverless-Patterns の実装に関する記述も同様に、リンクにする。
2. `candidate` のセルと記述に数値を書かない。ツールの版、上限、対応状況は、公式ドキュメントで確認できるまで記憶から書かない。
3. 商用ツールの操作は、利用者の承認なしに実行しない。手動チェックリストは利用者が手元で記入する。
4. 実機ベンチマークは、費用の見込みと後片付けの手順を示して承認を得てから実行する。CI では実行しない。

不可逆または公開に関わる操作（リポジトリの作成、リモートの追加、push、Playbook や Serverless-Patterns への Issue や PR の提出）は、利用者の承認を得てから行います。

## 主要なコマンド

`make help` が現役のターゲットを出します。毎回使うものは次のとおりです。

```bash
make all        # lint、drift、test、secrets を通す
make lint       # Markdown 構造、ruff、shellcheck
make drift      # 参照の固定、命名、公開安全、ja/en パリティ、マトリクス、make ターゲット
make test       # ゲートのテスト（失敗する入力と網羅性）
make secrets    # gitleaks
make drift-pins  # 手動、ネットワーク使用: 固定した参照の実在確認
```

## 変更を出す前の確認

1. `make all` が通ること。
2. ゲートを触ったときは、通してはいけない入力で落ちることを `make test` のテストで確かめる。
3. 文書を触ったときは、日本語版と英語版の見出し、表の列数、注記の数を揃える。日本語の節見出しは名詞句にする。
4. コミットは Conventional Commits、件名 72 文字以内。個人名、ペルソナ名、サポートケース番号を含めない。

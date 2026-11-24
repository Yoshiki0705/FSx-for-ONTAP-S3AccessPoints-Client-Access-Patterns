# Playbook フィードバック下書き / Playbook feedback draft

> 提出は利用者の承認後です。顧客名、アカウント ID、リソース ID、実際のアクセスポイント別名を書きません。 / Submit only after the user approves. Do not write customer names, account IDs, resource IDs, or real access point aliases.

- 種別 / Kind: Issue または PR / Issue or PR
- 宛先 / Destination: Playbook（既定） または Serverless-Patterns（サーバーレス処理の実装に関する所見） / Playbook (default) or Serverless-Patterns (findings on the serverless implementation)
- 状態 / Status: 下書き / 提出済み / 反映済み（Playbook のコミット） — draft / submitted / reflected (Playbook commit)
- 関係する文書と節 / Related document and section: https://github.com/Yoshiki0705/FSx-for-ONTAP-Adoption-Playbook/blob/a4c8367f9172ee88f0af25731752af63dc2c6225/<path>#<section>

## 観測した事実 / Observed facts

1 文 1 事実で書く。 / One fact per sentence.

## 再現手順 / Steps to reproduce

## 環境 / Environment

[benchmark-record の環境欄](../../docs/templates/benchmark-record.md) と同じ項目を書く。 / Use the same fields as the [benchmark record environment table](../../docs/templates/benchmark-record.en.md).

## 成功した対照 / Control that succeeded

同じ手順で動く別の操作。 / A different operation that works with the same steps.

## 提案する変更 / Proposed change

## 公開安全の確認 / Public safety check

- [ ] 顧客名、個人名、アカウント ID、リソース ID、別名、ケース番号を含まない / No customer or personal names, account IDs, resource IDs, aliases, or case numbers
- [ ] `make drift` が通る / `make drift` passes

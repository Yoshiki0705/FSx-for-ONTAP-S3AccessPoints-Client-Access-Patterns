# Kiro: MCP クライアントとしての利用

🌐 **言語**: **日本語** | [English](README.en.md)

> **確認水準**: `candidate`（未確認）。設定ファイルの場所と書式だけを公式ドキュメントで確認しています。FSx for ONTAP の S3 Access Points に接続する MCP サーバを動かした確認は、まだありません。

## 概要と対象の利用場面

Kiro から MCP サーバを呼び出し、S3 Access Points 経由のデータを AI クライアントのツールとして使う場面を対象にします。どの MCP サーバを使うかは未確定です。

## 前提

S3 Access Points の前提と上限は [Playbook の S3 Access Points の制約ノート](https://github.com/Yoshiki0705/FSx-for-ONTAP-Adoption-Playbook/blob/038fef7fb6ad3c5d0fabae7580f4983343504c70/docs/ja/domains/data-utilization/notes/s3-access-point-constraints.md) を参照してください。
## 構成と流れ

未記入。

## 設定手順

設定ファイルは、ワークスペース単位の `.kiro/settings/mcp.json` と、ユーザー単位の `~/.kiro/settings/mcp.json` です。両方あれば合成され、同じ名前のサーバはワークスペース側が優先されます。保存すると再読み込みされます（[Kiro の公式ドキュメント](https://kiro.dev/docs/mcp/configuration/)、2026-11-21 に確認）。

サーバ 1 件の書式の例です（値はプレースホルダ）。

```json
{
  "mcpServers": {
    "<server-name>": {
      "command": "<command-that-starts-the-server>",
      "args": ["<argument>"],
      "env": { "<NAME>": "<value-or-reference>" }
    }
  }
}
```

認証情報は設定ファイルに直接書かず、環境変数などの参照で渡します。

## 確認手順

未記入。成功するはずの対照操作を 1 つ以上含めます。

## 既知の制約

未記入。

## 選び方

| 項目 | 内容 |
|---|---|
| 向く場面 | 未確認 |
| 制約 | 未確認 |
| 他の選択肢 | [選び方](../../../docs/how-to-choose.md) |

## 後片付けと戻し方

設定ファイルに足したサーバの項目を削除します。`disabled` を `true` にしても無効にできます。

## 確認水準と出典

| 項目 | 水準 | 出典 |
|---|---|---|
| 設定ファイルの場所と書式 | `D` | https://kiro.dev/docs/mcp/configuration/（2026-11-21） |
| S3 Access Points に接続する MCP サーバでの動作 | `C` | - |

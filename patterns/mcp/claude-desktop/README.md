# Claude Desktop: MCP クライアントとしての利用

🌐 **言語**: **日本語** | [English](README.en.md)

> **確認水準**: `candidate`（未確認）。設定ファイルの場所と書式だけを公式ドキュメントで確認しています。FSx for ONTAP の S3 Access Points に届く MCP サーバを動かした確認は、まだありません。

## 概要と対象の利用場面

Claude Desktop から MCP サーバを呼び出し、S3 Access Points 経由のデータを AI クライアントのツールとして使う場面を対象にします。どの MCP サーバを使うかは未確定です。

## 前提

S3 Access Points の前提と上限は [Hub の互換性ノート](https://github.com/Yoshiki0705/FSx-for-ONTAP-S3AccessPoints-Serverless-Patterns/blob/v10.0.0-portal-line-icons-and-deps/docs/s3ap-compatibility-notes.md) を参照してください。
関連: Hub には、別の MCP クライアント（Amazon Quick Desktop）を使うデモの手順があります。構成は異なるため、Claude Desktop の手順としては読まず、参考として [Hub のデモガイド](https://github.com/Yoshiki0705/FSx-for-ONTAP-S3AccessPoints-Serverless-Patterns/blob/v10.0.0-portal-line-icons-and-deps/docs/demo-agentcore-mcp-quick-desktop.md) を参照してください。

## 構成と流れ

未記入。

## 設定手順

設定ファイルは `claude_desktop_config.json` です。macOS は `~/Library/Application Support/Claude/claude_desktop_config.json`、Windows は `%APPDATA%\Claude\claude_desktop_config.json` にあります。メニューの設定、開発者、設定を編集の順に開くと作られます。編集後は Claude Desktop を再起動します（[MCP の公式ドキュメント](https://github.com/modelcontextprotocol/docs/blob/main/quickstart/user.mdx)、2026-11-21 に確認。画面の文言は現行の版では未確認）。

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

設定ファイルに足したサーバの項目を削除します。削除後に Claude Desktop を再起動します。

## 確認水準と出典

| 項目 | 水準 | 出典 |
|---|---|---|
| 設定ファイルの場所と書式 | `D` | https://github.com/modelcontextprotocol/docs/blob/main/quickstart/user.mdx（2026-11-21） |
| S3 Access Points に届く MCP サーバでの動作 | `C` | - |

# Claude Desktop: use as an MCP client

🌐 **Language**: [日本語](README.md) | **English**

> **Confirmation level**: `candidate` (unconfirmed). Only the config file location and format are confirmed in official documentation. No MCP server that reaches FSx for ONTAP S3 Access Points has been run yet.

## Overview and target use cases

This covers calling an MCP server from Claude Desktop to use data reached through S3 Access Points as tools in an AI client. Which MCP server to use is undecided.

## Prerequisites

For the prerequisites and limits of S3 Access Points, see the [Playbook note on S3 Access Points constraints](https://github.com/Yoshiki0705/FSx-for-ONTAP-Adoption-Playbook/blob/038fef7fb6ad3c5d0fabae7580f4983343504c70/docs/ja/domains/data-utilization/notes/s3-access-point-constraints.md) (Japanese).
Related: the sibling Spoke Serverless-Patterns has a demo for a different MCP client (Amazon Quick Desktop). Its architecture differs, so do not read it as Claude Desktop steps; see the [Serverless-Patterns demo guide](https://github.com/Yoshiki0705/FSx-for-ONTAP-S3AccessPoints-Serverless-Patterns/blob/v10.0.0-portal-line-icons-and-deps/docs/en/demo-agentcore-mcp-quick-desktop.md) for reference only.

## Architecture and flow

Not written yet.

## Setup steps

The config file is `claude_desktop_config.json`. On macOS it is `~/Library/Application Support/Claude/claude_desktop_config.json`, and on Windows `%APPDATA%\Claude\claude_desktop_config.json`. Open it from the menu: Settings, Developer, Edit Config. Restart Claude Desktop after editing ([MCP official documentation](https://github.com/modelcontextprotocol/docs/blob/main/quickstart/user.mdx), confirmed 2026-11-21; the on-screen wording is unconfirmed for the current app version).

Format for one server (values are placeholders):

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

Do not write credentials directly in the config file; pass them by reference, such as environment variables.

## Verification steps

Not written yet. Include at least one control operation that is expected to succeed.

## Known constraints

Not written yet.

## How to choose

| Item | Content |
|---|---|
| Suited to | Unconfirmed |
| Constraints | Unconfirmed |
| Other options | [How to choose](../../../docs/how-to-choose.en.md) |

## Cleanup and rollback

Remove the server entry you added to the config file. Restart Claude Desktop after removing it.

## Confirmation level and sources

| Item | Level | Source |
|---|---|---|
| Config file location and format | `D` | https://github.com/modelcontextprotocol/docs/blob/main/quickstart/user.mdx (2026-11-21) |
| Behavior with an MCP server that reaches S3 Access Points | `C` | - |

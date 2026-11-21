# Kiro: use as an MCP client

🌐 **Language**: [日本語](README.md) | **English**

> **Confirmation level**: `candidate` (unconfirmed). Only the config file location and format are confirmed in official documentation. No MCP server that reaches FSx for ONTAP S3 Access Points has been run yet.

## Overview and target use cases

This covers calling an MCP server from Kiro to use data reached through S3 Access Points as tools in an AI client. Which MCP server to use is undecided.

## Prerequisites

For the prerequisites and limits of S3 Access Points, see the [Hub compatibility notes](https://github.com/Yoshiki0705/FSx-for-ONTAP-S3AccessPoints-Serverless-Patterns/blob/v10.0.0-portal-line-icons-and-deps/docs/s3ap-compatibility-notes.en.md).
## Architecture and flow

Not written yet.

## Setup steps

The config files are the workspace-level `.kiro/settings/mcp.json` and the user-level `~/.kiro/settings/mcp.json`. When both exist they are merged, and the workspace entry wins for a server with the same name. Saving the file reloads it ([Kiro official documentation](https://kiro.dev/docs/mcp/configuration/), confirmed 2026-11-21).

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

Remove the server entry you added to the config file. You can also disable it by setting `disabled` to `true`.

## Confirmation level and sources

| Item | Level | Source |
|---|---|---|
| Config file location and format | `D` | https://kiro.dev/docs/mcp/configuration/ (2026-11-21) |
| Behavior with an MCP server that reaches S3 Access Points | `C` | - |

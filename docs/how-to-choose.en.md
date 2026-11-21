# How to choose: by use case and requirements

This page is a table for choosing a client tool by use case and requirements. Every tool has constraints, and the table asks the same questions of each option. Confirmed results are reflected in the [compatibility matrix](compatibility-matrix.en.md). Every cell is currently `candidate` (unconfirmed), so this page states no ranking and no numbers.

## Options to consider per use case

| Use case | Group to consider | Constraints to check for each option |
|---|---|---|
| Move large amounts of data by command or scheduled job | Ingest and transfer (AWS CLI, rclone, s5cmd, AWS Transfer Family, File Mover Express) | Authentication method, multipart handling, retry behavior, where it must run |
| Present the data to applications or users like a file system | Streaming and mount (Mountpoint for Amazon S3, rclone mount, LucidLink Connect, LucidLink Suite) | Whether writes and deletes work, how consistency appears, cache location and size |
| Call it as a tool from an AI client | MCP clients (Kiro, Claude Desktop) | Where the config file lives, how the server starts, how credentials are passed |

## Axes for choosing

1. Direction of operations: ingest only, or both reads and writes.
2. Presentation: whether the S3 API is enough, or the data should look like a file system.
3. Operations: availability of commercial support, effort to install and update, where it runs.
4. Cost: licenses, data transfer, and the cost of measuring on real infrastructure.

## Rules for listing constraints

- Write constraints for the same items in the same format for every option. Write constraints for the option you lean toward as well.
- Write a constraint only when it has an official source or your own measurement record. Otherwise write `candidate`.
- Do not use words that rank options, such as "better", "inferior", or "competing".

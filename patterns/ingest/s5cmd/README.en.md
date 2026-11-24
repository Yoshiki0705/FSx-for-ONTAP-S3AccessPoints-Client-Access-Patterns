# s5cmd: client access pattern

🌐 **Language**: [日本語](README.md) | **English**

> **Confirmation level**: The version and the README statements are confirmed from the official documents (`D`, 2026-11-24). Whether it accepts an FSx for ONTAP access point is not stated and has not been measured (`C`). Measured (2026-11-24): It accepted the alias without `--endpoint-url`; `cp`, download and `rm` worked and the content hash matched. `cp` from a bucket to the access point completed without the data passing through the client (27,340 bytes sent and received).

## Overview and target use cases

Use `s5cmd` for highly parallel bulk downloads, uploads, and S3-to-S3 copies. Checking whether it issues a server-side copy between a bucket and an access point ([server-side copy](../../../docs/server-side-copy.en.md)) is also in scope.

## Prerequisites

For the prerequisites and limits of S3 Access Points, see the [Playbook note on S3 Access Points constraints](https://github.com/Yoshiki0705/FSx-for-ONTAP-Adoption-Playbook/blob/a4c8367f9172ee88f0af25731752af63dc2c6225/docs/ja/domains/data-utilization/notes/s3-access-point-constraints.md) (Japanese). They are not copied into this page. The tool version and the sources are in the [tool fact check](../../../docs/tool-facts.en.md).

## Architecture and flow

`s5cmd` reaches the S3 endpoint over HTTPS through the AWS SDK. The README says it verifies upload integrity with `Content-MD5` and `X-Amz-Content-Sha256` ([README](https://github.com/peak/s5cmd/blob/master/README.md), read on 2026-11-24). FSx for ONTAP access points do not store checksums ([Access point compatibility](https://docs.aws.amazon.com/fsx/latest/ONTAPGuide/access-points-for-fsxn-object-api-support.html)). How the two interact is unconfirmed (`C`).

## Setup steps

The README does not say how to specify an access point ARN or alias (`C`). Stage 3 tries putting the alias in the bucket-name position.

```bash
s5cmd ls s3://<alias>/
```

S3 Access Points accept only virtual-hosted-style requests ([Referencing access points](https://docs.aws.amazon.com/fsx/latest/ONTAPGuide/referencing-access-points-for-fsxn.html)). The README says a custom `--endpoint-url` falls back to path-style, so the first attempt omits `--endpoint-url`.

## Verification steps

Run them in the s5cmd section of the [stage 3 runbook](../../../benchmarks/stage3-runbook.en.md). As a control that should succeed, first list the same alias with AWS CLI.

## Known constraints

- The constraints on the access point side are in the Playbook.
- According to the README an S3-to-S3 copy runs on the server side, and objects larger than 5 GB are unsupported. The upload size limit on the FSx for ONTAP side is in the Playbook.
- The latest release is v2.3.0 (2024-12-16).

## How to choose

| Item | Content |
|---|---|
| Suited to | Highly parallel bulk transfers. Checking S3-to-S3 copy |
| Constraints | Whether it accepts access points is unconfirmed. Server-side copy above 5 GB is unsupported |
| Other options | [How to choose](../../../docs/how-to-choose.en.md) |

## Cleanup and rollback

Nothing remains on the client. The resources created in stage 3 are removed by the cleanup script in the runbook.

## Confirmation level and sources

| Item | Level | Source |
|---|---|---|
| Current version (v2.3.0) | `D` | [s5cmd releases](https://github.com/peak/s5cmd/releases), 2026-11-24 |
| S3-to-S3 copy and `--endpoint-url` behavior | `D` | [README](https://github.com/peak/s5cmd/blob/master/README.md), 2026-11-24 |
| Setup steps | `C` | - |
| Verification steps | `M` | [2026-11-24 record](../../../benchmarks/records/2026-11-24-client-tools-stage3.en.md) |

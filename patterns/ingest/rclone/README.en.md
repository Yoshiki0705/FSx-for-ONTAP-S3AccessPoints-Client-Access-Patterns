# rclone: client access pattern

🌐 **Language**: [日本語](README.md) | **English**

> **Confirmation level**: The version and the S3 backend statements are confirmed from the official documents (`D`, 2026-11-24). Behavior against an FSx for ONTAP access point has not been measured (`C`).

## Overview and target use cases

Use `rclone copy`, `sync`, and `ls` to transfer to an access point. Server-side copy within one remote ([server-side copy](../../../docs/server-side-copy.en.md)) and [rclone mount](../../streaming/rclone-mount/README.en.md), which mounts as a file system, are separate patterns.

## Prerequisites

For the prerequisites and limits of S3 Access Points, see the [Playbook note on S3 Access Points constraints](https://github.com/Yoshiki0705/FSx-for-ONTAP-Adoption-Playbook/blob/038fef7fb6ad3c5d0fabae7580f4983343504c70/docs/ja/domains/data-utilization/notes/s3-access-point-constraints.md) (Japanese). They are not copied into this page. The tool version and the sources are in the [tool fact check](../../../docs/tool-facts.en.md).

## Architecture and flow

rclone keeps the modification time in `X-Amz-Meta-Mtime`, and reading it needs an extra `HEAD`. For multipart or encrypted objects it keeps an MD5 in `X-Amz-Meta-Md5chksum` ([rclone S3 documentation](https://rclone.org/s3/), read on 2026-11-24). The ETag of an FSx for ONTAP access point object is not an MD5 ([Access point compatibility](https://docs.aws.amazon.com/fsx/latest/ONTAPGuide/access-points-for-fsxn-object-api-support.html)).

## Setup steps

The rclone documents do not say how to specify an access point ARN or alias (`C`). S3 Access Points accept only virtual-hosted-style requests ([Referencing access points](https://docs.aws.amazon.com/fsx/latest/ONTAPGuide/referencing-access-points-for-fsxn.html)). The default of rclone's `force_path_style` is `true`, so stage 3 tries a configuration with it set to `false`.

```ini
[ap]
type = s3
provider = AWS
env_auth = true
region = ap-northeast-1
force_path_style = false
no_check_bucket = true
```

`no_check_bucket` skips checking whether the bucket exists and creating it (rclone documentation).

## Verification steps

Run them in the rclone section of the [stage 3 runbook](../../../benchmarks/stage3-runbook.en.md). As a control that should succeed, first list the same alias with AWS CLI.

## Known constraints

- The constraints on the access point side are in the Playbook.
- Server-side copy happens only when the source and destination use the same remote. The default of `--s3-copy-cutoff` is 4.656 GiB and the maximum is 5 GiB.
- A comparison with `--checksum` assumes the MD5 can be read from the ETag. The result against an FSx for ONTAP access point is unconfirmed (`C`).

## How to choose

| Item | Content |
|---|---|
| Suited to | Differential sync and transfers across different kinds of remotes |
| Constraints | A virtual-hosted-style setting is expected to be needed. The result of `--checksum` is unconfirmed |
| Other options | [How to choose](../../../docs/how-to-choose.en.md) |

## Cleanup and rollback

A configuration file remains on the client. The configuration created in stage 3 is removed by the cleanup script in the runbook.

## Confirmation level and sources

| Item | Level | Source |
|---|---|---|
| Current version (v1.76.0) | `D` | [rclone releases](https://github.com/rclone/rclone/releases), 2026-11-24 |
| S3 backend options | `D` | [rclone S3 documentation](https://rclone.org/s3/), 2026-11-24 |
| Setup steps | `C` | - |
| Verification steps | `C` | - |

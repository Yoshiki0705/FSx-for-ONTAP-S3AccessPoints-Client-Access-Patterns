# Mountpoint for Amazon S3: client access pattern

🌐 **Language**: [日本語](README.md) | **English**

> **Confirmation level**: The version and the file operation behavior are confirmed from the official documents (`D`, 2026-11-24). Whether an FSx for ONTAP access point can be mounted is not stated and has not been measured (`C`).

## Overview and target use cases

A client that lets applications handle S3 objects with file operations such as `open` and `read`. FSx for ONTAP data has three paths: mounting through S3 Access Points, tools that use the S3 API directly, and a direct NFS or SMB mount. The comparison is in [Mountpoint for Amazon S3 and S3 Access Points: choosing between them](../../../docs/mountpoint-vs-s3-access-points.en.md).

## Prerequisites

For the prerequisites and limits of S3 Access Points, see the [Playbook note on S3 Access Points constraints](https://github.com/Yoshiki0705/FSx-for-ONTAP-Adoption-Playbook/blob/038fef7fb6ad3c5d0fabae7580f4983343504c70/docs/ja/domains/data-utilization/notes/s3-access-point-constraints.md) (Japanese). They are not copied into this page.

## Architecture and flow

Mountpoint translates file operations into S3 API calls. After the S3 IAM decision, the permissions of the file system user set on the access point decide ([FSx for ONTAP User Guide](https://docs.aws.amazon.com/fsx/latest/ONTAPGuide/s3-ap-manage-access-fsxn.html), read on 2026-11-24).

## Setup steps

The Mountpoint documents say an access point of an S3 general purpose bucket can be given by ARN or alias ([CONFIGURATION.md](https://github.com/awslabs/mountpoint-s3/blob/main/doc/CONFIGURATION.md), read on 2026-11-24).

```bash
mount-s3 arn:aws:s3:region:account-id:accesspoint/my-access-point /path/to/mount
mount-s3 my-access-point-hrzrlukc5m36ft7okagglf3gmwluquse1b-s3alias /path/to/mount
```

The documents do not say whether the alias of an FSx for ONTAP access point (`-ext-s3alias`) can be given in this form (`C`). Stage 3 tries it.

## Verification steps

Run them in the Mountpoint section of the [stage 3 runbook](../../../benchmarks/stage3-runbook.en.md). As a control that should succeed, first list the same alias with AWS CLI. If the mount fails, keep the `mount-s3` error and the debug log as the evidence.

## Known constraints

- The constraints on the access point side are in the Playbook.
- By default only creating new files is allowed. Overwrite needs `--allow-overwrite` and delete needs `--allow-delete`.
- Rename and append apply only to S3 Express One Zone.
- Creating a directory is a local-only operation, and an existing directory can be neither removed nor renamed.
- The Mountpoint README says it does not support S3-compatible storage other than Amazon S3.

The sources are [SEMANTICS.md](https://github.com/awslabs/mountpoint-s3/blob/main/doc/SEMANTICS.md) and the [README](https://github.com/awslabs/mountpoint-s3/blob/main/README.md) (read on 2026-11-24).

## How to choose

| Item | Content |
|---|---|
| Suited to | Applications that mostly read large objects. Writing new files sequentially from one client |
| Constraints | Whether it accepts FSx for ONTAP access points is unconfirmed. Rename and append are expected to be unavailable |
| Other options | [How to choose](../../../docs/how-to-choose.en.md) |

## Cleanup and rollback

Unmount with `umount`. The access point and the bucket created in stage 3 are removed by the cleanup script in the runbook.

## Confirmation level and sources

| Item | Level | Source |
|---|---|---|
| Current version (1.25.0) | `D` | [Mountpoint changelog](https://github.com/awslabs/mountpoint-s3/blob/main/mountpoint-s3/CHANGELOG.md), 2026-11-24 |
| File operation behavior | `D` | [SEMANTICS.md](https://github.com/awslabs/mountpoint-s3/blob/main/doc/SEMANTICS.md), 2026-11-24 |
| Setup steps | `C` | - |
| Verification steps | `C` | - |

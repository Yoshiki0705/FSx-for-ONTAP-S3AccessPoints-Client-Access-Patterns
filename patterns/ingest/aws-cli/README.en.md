# AWS CLI: client access pattern

🌐 **Language**: [日本語](README.md) | **English**

> **Confirmation level**: The syntax of the setup steps is confirmed from the official documents (`D`, 2026-11-24). Behavior against an FSx for ONTAP access point has not been measured (`C`). Measured (2026-11-24): With both alias and ARN, `ls`, `cp` (64 MiB as multipart), `sync` and `rm` worked and the content hash matched. `--no-overwrite` sends `If-None-Match` and failed with `NotImplemented`. `aws s3 cp` from a bucket to the access point became a server-side copy with `UploadPartCopy`.

## Overview and target use cases

Use `aws s3` and `aws s3api` to read, write, and copy through an access point. The targets are bulk transfers in scripts and scheduled jobs, and server-side copy between a bucket and an access point ([server-side copy](../../../docs/server-side-copy.en.md)).

## Prerequisites

For the prerequisites and limits of S3 Access Points, see the [Playbook note on S3 Access Points constraints](https://github.com/Yoshiki0705/FSx-for-ONTAP-Adoption-Playbook/blob/a4c8367f9172ee88f0af25731752af63dc2c6225/docs/ja/domains/data-utilization/notes/s3-access-point-constraints.md) (Japanese). They are not copied into this page. The tool version and the sources are in the [tool fact check](../../../docs/tool-facts.en.md).

## Architecture and flow

S3 decides with the client's IAM credentials, then the permissions of the file system user set on the access point decide ([FSx for ONTAP User Guide](https://docs.aws.amazon.com/fsx/latest/ONTAPGuide/s3-ap-manage-access-fsxn.html), read on 2026-11-24).

## Setup steps

Specify the access point by ARN or alias. The AWS CLI reference has examples of the ARN syntax ([aws s3 cp](https://docs.aws.amazon.com/cli/latest/reference/s3/cp.html), read on 2026-11-24).

```bash
aws s3 cp mydoc.txt s3://arn:aws:s3:us-west-2:123456789012:accesspoint/myaccesspoint/mykey
aws s3 cp s3://arn:aws:s3:us-west-2:123456789012:accesspoint/myaccesspoint/mykey mydoc.txt
```

The documents say an alias can be used in place of a bucket name (`<name>-<metadata>-ext-s3alias`; [Referencing access points](https://docs.aws.amazon.com/fsx/latest/ONTAPGuide/referencing-access-points-for-fsxn.html), read on 2026-11-24).

## Verification steps

Run them in the AWS CLI section of the [stage 3 runbook](../../../benchmarks/stage3-runbook.en.md). As a control that should succeed, first run `aws s3api list-objects-v2` against the same alias.

## Known constraints

- The constraints on the access point side (conditional writes, versioning, the upload size limit and so on) are in the Playbook.
- In a multipart S3-to-S3 copy, the default `--copy-props` may make extra `HeadObject`, `GetObjectTagging` and `PutObjectTagging` calls. `--copy-props none` avoids them.
- The documents do not say whether `aws s3 cp --no-overwrite` uses a conditional write to prevent an overwrite (`C`).

## How to choose

| Item | Content |
|---|---|
| Suited to | Scripts and batch jobs. Checking server-side copy (`--debug` shows the API that was issued) |
| Constraints | Behavior on a real file system is not measured. The mechanism of `--no-overwrite` is unconfirmed |
| Other options | [How to choose](../../../docs/how-to-choose.en.md) |

## Cleanup and rollback

Nothing remains on the client. The S3 Access Points and the bucket created in stage 3 are removed by the cleanup script in the runbook.

## Confirmation level and sources

| Item | Level | Source |
|---|---|---|
| Current version (2.42.2) | `D` | [AWS CLI tags](https://github.com/aws/aws-cli/tags), 2026-11-24 |
| Specifying an ARN and an alias | `D` | The two AWS documents above, 2026-11-24 |
| Setup steps | `C` | - |
| Verification steps | `M` | [2026-11-24 record](../../../benchmarks/records/2026-11-24-client-tools-stage3.en.md) |

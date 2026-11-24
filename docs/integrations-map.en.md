# Integration map: AWS services and products, use cases, client tools

🌐 **Language**: [日本語](integrations-map.md) | **English**

> **Classification**: The behavior of each integration target is as described in AWS and NetApp documents, blogs, and the author's validation articles (read on 2026-11-25, Japan time). What was run on real hardware is limited to the range in which four client tools work against S3 Access Points, recorded in the [2026-11-24 record](../benchmarks/records/2026-11-24-client-tools-stage3.en.md). The behavior of the integration targets' own services was not measured in this repository. The use case IDs (N1 to N8, E1 to E9) and source IDs (U1 to U14) are those in the tables of [Use cases](use-cases.en.md).

S3 Access Points on Amazon FSx for NetApp ONTAP (FSx for ONTAP below) show volume files to anything that reads the S3 API. When the other side reads the access point directly, no client tool is involved. Client tools matter on the other side of the operation: loading data, checking it, moving it to and from buckets, and presenting it to apps that cannot use the S3 API.

## Integration targets and use cases

The classes differ by the kind of public evidence, not by product merit. A target missing from the table is one this repository did not look into, not one that is unsupported.

| Target | Type | Expected use case | Evidence class | Client tools involved | Source |
|---|---|---|---|---|---|
| Amazon Athena and AWS Glue Data Catalog | AWS service | N1, E1: SQL analysis of file-share data | Official expectation | AWS CLI (loading and checking data) | U6, U5 |
| AWS Glue (Apache Spark, Python shell, Ray) | AWS service | N1, E1: ETL, with results written back to the same volume | Official expectation | AWS CLI (checking) | U6 |
| Amazon Bedrock Knowledge Bases | AWS service | N2: RAG over a document share | Official expectation | AWS CLI (loading and checking documents) | U6 |
| Amazon Quick (the name differs by source: U5 writes Quick Suite, U7 writes AWS Quick and Quick Sight; I did not confirm whether these are the same service at different times) | AWS service | N2, N3, E1: Give an access point alias as an S3 integration and make a knowledge base (the steps in U5). U7 also shows dashboards over summarized data and scheduled automations in its example | Official expectation | AWS CLI (checking) | U5, U7 |
| Amazon Bedrock AgentCore | AWS service | N3: List, read, and search through an MCP gateway and AWS Lambda | Official expectation (the U7 example architecture) | None (the reader is the Lambda on the AgentCore side. The MCP client patterns are not checked in this repository) | U7 |
| Amazon SageMaker | AWS service | E1: Read as machine learning data | Official expectation | AWS CLI (checking) | U5, U10 |
| Amazon EMR Serverless | AWS service | N1, E1: Spark jobs | Official expectation | None | U6 |
| Amazon Redshift and Amazon OpenSearch Service | AWS service | E1: Analytics and log analytics | Official expectation (an example in the NetApp blog; not in the AWS documentation, U6) | None | U10 |
| AWS Lambda | AWS service | N7, E3: Processing arriving files, reading shared data | Official expectation | AWS CLI (checking behavior) | U6, U5 |
| Amazon CloudFront | AWS service | N6: HLS video delivery | Official expectation | None | U6 |
| AWS Transfer Family | AWS service | N4: SFTP, FTPS, and FTP hand-off to outside parties. Prerequisites: ONTAP 9.17.1 or later, alias only, rename and append unsupported, and an access point with a VPC network origin is refused (U9). The setup in this check cannot be used as is | Official expectation | None (the SFTP clients on the other side are within the Transfer Family documentation) | U6, U9 |
| Amazon S3 general purpose bucket | AWS service | N5, E4a, E4b: Server-side copy (`CopyObject`, `UploadPartCopy`) | Official expectation. Bucket to volume was run in this check | AWS CLI, s5cmd, rclone (volume to bucket was not run here) | U8, Playbook, Record |
| S3 Batch Operations | AWS service | E4a, E4b: Jobs for bulk copy | Official expectation, plus a [Playbook record](https://github.com/Yoshiki0705/FSx-for-ONTAP-Adoption-Playbook/blob/a4c8367f9172ee88f0af25731752af63dc2c6225/docs/ja/domains/data-utilization/notes/s3-access-points-server-side-copy-use-cases.md) (Japanese) | None (not run in this check) | Playbook |
| Dremio Cloud | External product | E8: Read the access point and write results to an FSx for ONTAP S3 bucket | Official expectation (Dremio and NetApp blogs) | None | U11, U12 |
| Snowflake | External product | E8: An external table with `AWS_ACCESS_POINT_ARN` set on the stage. Checked 2026-05 (Standard edition, ap-northeast-1, ONTAP 9.17.1). Surrounding claims were corrected in 2026-09; the central finding (without it LIST works and SELECT fails; with it reads work) did not change. The article says Snowflake does not officially document this configuration | Public case (the author, one environment) | None | U13 |
| Databricks | External product | E8: Direct reads with an instance profile and boto3 worked but sit outside Unity Catalog governance (PoC use). For a Unity Catalog external location, the author's 2026-05-26 addendum says the `access_point` field was never generally available and was removed from the documentation, and that the partial success is best read as an unsupported side effect (checked 2026-05, corrected 2026-09) | Public case (the author, one environment) | None | U14 |
| Apps that use file paths | App | N8: Provide file paths to apps that cannot use the S3 API | Estimate. Mount and basic operations checked | Mountpoint for Amazon S3 | Record |
| Commercial transfer and streaming products | External product | E9: File Mover Express, LucidLink Connect, LucidLink Suite | Estimate | Commercial tools (manual checklist) | tool-facts |

## What each client tool is involved in

| Tool | Integrations and use cases | Related operations run (not a test of the use case) | Pattern |
|---|---|---|---|
| AWS CLI | Loading and checking data (N1, N2, N7, E1, E3), server-side copy (N5, E4a; E4b not confirmed), scheduled jobs (E5) | List, get, put, multipart, delete, server-side copy | [patterns/ingest/aws-cli](../patterns/ingest/aws-cli/README.en.md) |
| s5cmd | Bulk transfer (E6), server-side copy (N5, E4a; E4b not confirmed), scheduled jobs (E5) | List, get, put, delete, server-side copy (performance not measured) | [patterns/ingest/s5cmd](../patterns/ingest/s5cmd/README.en.md) |
| rclone | Sync with other storage (E7), server-side copy (N5, E4a; E4b not confirmed) | List, get, put, delete, server-side copy. The copy needed `--s3-storage-class FSX_ONTAP` | [patterns/ingest/rclone](../patterns/ingest/rclone/README.en.md) |
| Mountpoint for Amazon S3 | File paths for apps that cannot use the S3 API (N8) | Mount by alias and by ARN, new writes, reads, overwrite and delete with `--allow-overwrite --allow-delete` | [patterns/streaming/mountpoint-for-amazon-s3](../patterns/streaming/mountpoint-for-amazon-s3/README.en.md) |
| MCP clients (Kiro, Claude Desktop) | List, read, and search from an AI client (a setup close to N3) | None (estimate) | [patterns/mcp](../patterns/mcp/kiro/README.en.md) |
| Commercial transfer and streaming products | E9 | None (the user fills in a manual checklist) | [checklists/vendor](../checklists/vendor/file-mover-express/CHECKLIST.en.md) |

## How to choose an entry

For each integration target, the entry falls into one of three kinds.

| Entry | Fits when | Constraint |
|---|---|---|
| The service reads the access point directly | The target supports the S3 API (Athena, Glue, Bedrock Knowledge Bases, and others) | Stay within the S3 operations the access point supports. Per-target settings are needed (for example the Snowflake stage) |
| Move to a bucket with a client tool, then let the target read it | The target assumes a bucket, or bucket features (lifecycle, event notifications) are needed | Two copies of the data exist. Only the content is carried over; owner, mode, and modification time became the destination's settings and the copy time (a Playbook measurement, file system user root only). Copy stays within one Region (U8) |
| Present it as a file path with a client tool | An app that cannot use the S3 API reads and writes | Follow the tool's write constraints (Mountpoint does not allow overwrite, append, or delete by default) |

Specifications and limits are first-hand information in the Playbook [constraints note (Japanese)](https://github.com/Yoshiki0705/FSx-for-ONTAP-Adoption-Playbook/blob/a4c8367f9172ee88f0af25731752af63dc2c6225/docs/ja/domains/data-utilization/notes/s3-access-point-constraints.md). They are not copied here.

## What is not confirmed

- That the targets in the table can actually read an FSx for ONTAP access point.
- The per-target configuration requirements. A setting such as the Snowflake `AWS_ACCESS_POINT_ARN` is a record from the author's one environment.
- Support for services not in the table. Where the Playbook [constraints note](https://github.com/Yoshiki0705/FSx-for-ONTAP-Adoption-Playbook/blob/a4c8367f9172ee88f0af25731752af63dc2c6225/docs/ja/domains/data-utilization/notes/s3-access-point-constraints.md) or [server-side copy note](https://github.com/Yoshiki0705/FSx-for-ONTAP-Adoption-Playbook/blob/a4c8367f9172ee88f0af25731752af63dc2c6225/docs/ja/domains/data-utilization/notes/s3-access-points-server-side-copy-use-cases.md) (both Japanese) covers one, read that.
- Performance and cost per target.

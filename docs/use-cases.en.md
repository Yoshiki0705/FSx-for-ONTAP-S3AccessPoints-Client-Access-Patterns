# Use cases: where S3 Access Points and client tools are used

🌐 **Language**: [日本語](use-cases.md) | **English**

> **Classification**: The use cases on this page are expectations collected from public documents and articles. Sources were read on 2026-11-25 (Japan time). What was run on real hardware is limited to the range in which four client tools (AWS CLI, s5cmd, rclone, Mountpoint for Amazon S3) work against S3 Access Points, recorded in the [2026-11-24 record](../benchmarks/records/2026-11-24-client-tools-stage3.en.md). Performance, cost, and operational checks of the use cases themselves are not included.

When S3 Access Points are attached to an Amazon FSx for NetApp ONTAP (FSx for ONTAP below) volume, files placed over NFS or SMB can be read and written through the S3 API. This page sorts how that is used from three sides: how S3 is used on on-premises ONTAP, the use cases of people starting with FSx for ONTAP, and the use cases of people already running it. Which use case involves which client tool is shown in the [integration map](integrations-map.en.md).

## Evidence classes

| Class | Meaning | Handling |
|---|---|---|
| Public case | A third party or the author published the result of trying it in a real environment | State the source's environment and date. Do not write that other environments behave the same |
| Official expectation | An AWS or NetApp document, blog, or example architecture describes the use case as an expectation | Write "is expected", not "works" |
| Estimate | This repository's estimate (`candidate`) | Write no numbers. Keep it an estimate until checked |

The use case tables have a "Related operations run" column. It is not a test of the use case. It names only the operations whose behavior was checked in the 2026-11-24 record. The use cases themselves (performance, operation, consistency) were not measured.

An official expectation is not a basis for adoption, procurement, or audit. The classes differ by product because the kind of public evidence differs, not as a ranking of products.

## How S3 is used on on-premises ONTAP

On-premises ONTAP has had a feature that presents a volume as an S3 bucket (an S3 NAS bucket) since ONTAP 9.12.1. The use cases NetApp's documents list are below. This is a different feature from FSx for ONTAP S3 Access Points. It is here as a reference for how the same S3 idea has been used on-premises. No published adoption case was found in the 2026-11-25 search of NetApp documents, technical reports, and blogs.

| # | Use case | Content | Evidence class | Source |
|---|---|---|---|---|
| 1 | Analyze NAS data with S3 clients | NAS clients write data and S3 clients read it. Analytics, BI, machine learning, and optical character recognition are given as examples | Official expectation | U1, U2 |
| 2 | A home for apps that read and write over both NAS and S3 | Apps such as Spark and Kafka that read and write the same data over both protocols | Official expectation | U2 |
| 3 | Training data for machine learning | A pipeline example that places prepared data in an ONTAP NAS bucket and selects ONTAP S3 as the training destination. Not checked on FSx for ONTAP | Official expectation | U4 |
| 4 | Dual NFS and S3 access (Cloud Volumes ONTAP) | Data scientists use NFS, and other users or apps use S3, for the same data | Official expectation | U3 |

On-premises ONTAP FabricPool, which moves inactive data to a bucket, is a separate feature. An S3 NAS bucket cannot be a FabricPool tier target (U1, U2).

An S3 NAS bucket differs from a regular bucket in some behaviors. NetApp's document lists versioning, lifecycle, and the Object Lock read operations among the unsupported items, and says multipart upload is supported from ONTAP 9.16.1 under a condition (U2). The range supported by FSx for ONTAP S3 Access Points is decided separately and is in the Playbook [constraints note (Japanese)](https://github.com/Yoshiki0705/FSx-for-ONTAP-Adoption-Playbook/blob/a4c8367f9172ee88f0af25731752af63dc2c6225/docs/ja/domains/data-utilization/notes/s3-access-point-constraints.md). Do not treat the two as the same feature.

## Expected use cases for people starting with FSx for ONTAP

"Starting" means people about to adopt FSx for ONTAP, or people who want to fix their S3-side requirements before adopting it.

| # | Use case | Content | Evidence class | Related operations run (not a test of the use case) | Client tools involved | Source |
|---|---|---|---|---|---|---|
| N1 | SQL analysis of file-share data | Query files on NFS or SMB with Amazon Athena and the AWS Glue Data Catalog | Official expectation | No | AWS CLI (loading and checking data) | U6 |
| N2 | RAG over a document share | Amazon Bedrock Knowledge Bases reads documents placed on the share | Official expectation | No | AWS CLI (loading and checking documents) | U6, U5 |
| N3 | AI analysis of EDA logs | An example architecture where Amazon Quick and Amazon Bedrock AgentCore read simulation logs written over NFS | Official expectation (the U7 example architecture) | No | None (the services read directly) | U7 |
| N4 | SFTP hand-off to outside parties | Connect an AWS Transfer Family SFTP, FTPS, or FTP endpoint to the volume behind an access point | Official expectation | No | None (Transfer Family calls the API) | U6, U9 |
| N5 | Initial load from a bucket into a volume | Copy a partner bucket's data into the volume without mounting it | Official expectation | Copy from bucket to volume (AWS CLI, s5cmd, rclone) | AWS CLI, s5cmd, rclone | U8 |
| N6 | Video streaming delivery | Deliver HLS video from the volume with Amazon CloudFront | Official expectation | No | None | U6 |
| N7 | Serverless processing of arriving files | AWS Lambda generates thumbnails, extracts text from documents, or transcribes audio | Official expectation | No | AWS CLI (checking behavior) | U6 |
| N8 | Provide a file path to apps that cannot use the S3 API | Present the access point as a file path to an app that does not assume the S3 API | Estimate | Mountpoint mount and basic operations only. The use case is not measured | Mountpoint for Amazon S3 | Record |

People starting out face a first choice about where the data lives: keep the volume as the source and read it through the access point, or keep the bucket as the source and copy only what is needed into the volume. N5 is the entry to the second.

## Expected use cases for people already running FSx for ONTAP

"Already running" means NFS or SMB apps are using the volume. The center is adding readers without changing the existing apps.

| # | Use case | Content | Evidence class | Related operations run (not a test of the use case) | Client tools involved | Source |
|---|---|---|---|---|---|---|
| E1 | Add analytics and AI readers to existing NAS data | Apps stay on NFS or SMB while Amazon SageMaker, Amazon Athena, AWS Glue, and others read the same data | Official expectation | No | AWS CLI | U5, U10 |
| E2 | S3 use of data moved from on-premises ONTAP | Connect S3 readers through an access point to data moved to FSx for ONTAP with SnapMirror | Official expectation (NetApp and Dremio blogs) | No | None | U10, U11, U12 |
| E3 | Serverless and container apps read shared data | Read configuration files, reference data, content, and model files through the S3 API | Official expectation | No | AWS CLI | U5 |
| E4 | Server-side copy between volume and bucket | Move to an archive storage class, use bucket features (lifecycle, event notifications), or export to another team's bucket | Official expectation (U8), plus a [Playbook record](https://github.com/Yoshiki0705/FSx-for-ONTAP-Adoption-Playbook/blob/a4c8367f9172ee88f0af25731752af63dc2c6225/docs/ja/domains/data-utilization/notes/s3-access-points-server-side-copy-use-cases.md) (Japanese) that covers both bucket-to-volume and volume-to-bucket | Bucket-to-volume copy with 3 tools only. Volume-to-bucket is not measured here | AWS CLI, s5cmd, rclone | U8, Record |
| E5 | Backup, sync, and ingest from scheduled jobs | A cron or scheduled job syncs volume files with a bucket or other storage | Estimate | List, get, put, delete (once each). Scheduled runs not measured | AWS CLI, s5cmd, rclone | Record |
| E6 | Parallel transfer of many files | Transfer many files in parallel | Estimate | Get and put of one file at a time. Parallel transfer not measured | s5cmd, AWS CLI | Record |
| E7 | Sync with other clouds and storage | rclone syncs between multiple backends | Estimate | rclone list, get, put, delete (one backend only) | rclone | Record |
| E8 | Reads from external data platforms | Dremio, Snowflake, and Databricks read the access point | Public case (Snowflake and Databricks: the author's validation articles), official expectation (Dremio: a vendor blog) | No | None | U12, U13, U14 |
| E9 | Commercial file transfer and streaming products | File Mover Express, LucidLink Connect, and LucidLink Suite use the access point | Estimate | No (the checklist is filled in by the user) | Commercial tools | tool-facts |

The server-side copy in E4 is not needed when the data is only handed to a service that can read the access point directly (Athena, Glue, Bedrock Knowledge Bases). The decision table is in the Playbook [server-side copy use cases](https://github.com/Yoshiki0705/FSx-for-ONTAP-Adoption-Playbook/blob/a4c8367f9172ee88f0af25731752af63dc2c6225/docs/ja/domains/data-utilization/notes/s3-access-points-server-side-copy-use-cases.md) (Japanese).

## Splitting new and existing users

| Aspect | People starting out | People already running it |
|---|---|---|
| First question | Where does the data live (volume or bucket) | How to add readers without changing existing apps |
| Role of the access point | Build the entry for analytics, AI, and hand-off into the design from the start | Attach an entry for readers to an existing volume later |
| Where client tools appear | Initial load, checking behavior | Scheduled jobs, moves to and from buckets |
| Constraint to check first | The range of S3 operations the access point supports | How existing apps' writes appear to access-point reads |

The use cases of the two groups overlap. N5 and E4 are the same operation. The difference is whether it happens once at the start or repeatedly in operation.

## How to choose a path

There are five paths to the same data. Each has situations it fits and constraints.

| Path | Fits when | Constraint | Status (confirmed / documented / not confirmed / out of scope) |
|---|---|---|---|
| Use the access point directly through the S3 API | The reader supports the S3 API and can take an access point alias or ARN | Conditional writes (`If-None-Match`) are unsupported, and `aws s3 cp --no-overwrite` failed. The only storage class is `FSX_ONTAP`. Other limits are in the [Playbook constraints note](https://github.com/Yoshiki0705/FSx-for-ONTAP-Adoption-Playbook/blob/a4c8367f9172ee88f0af25731752af63dc2c6225/docs/ja/domains/data-utilization/notes/s3-access-point-constraints.md) (Japanese) | Confirmed (operations with 4 tools, 2026-11-24) |
| Mount the volume over NFS or SMB | The app assumes file paths. Renames or appends are needed | The host needs network reach to the volume and mount privileges | Not confirmed (not measured in this repository) |
| Present it as a file path with Mountpoint for Amazon S3 | An app that cannot use the S3 API reads and writes files | Overwrite, append, and delete are off by default. Rename is not implemented | Confirmed (2026-11-24, [record](../benchmarks/records/2026-11-24-client-tools-stage3.en.md)) |
| Copy server-side to a bucket | Bucket features are needed, or the source of truth is the bucket | Two copies of the data exist. Owner, mode, and modification time are not carried over (a Playbook measurement; attributes were not measured here). Copy stays within one Region (U8) | Confirmed (bucket to volume with 3 tools, 2026-11-24). Volume to bucket is in the Playbook record |
| Replicate or migrate with SnapMirror or AWS DataSync | Volume-level replication, or a migration that keeps attributes | Not covered, because this repository is about client tools | Out of scope |

A comparison by axis is in [Mountpoint and S3 Access Points](mountpoint-vs-s3-access-points.en.md) and [How to choose](how-to-choose.en.md).

## What is not confirmed

- Published cases of S3 NAS buckets on on-premises ONTAP. The 2026-11-25 search found none.
- Performance, cost, and operational load of each use case in the tables. This repository did not measure them.
- That AWS services and external data platforms can read an FSx for ONTAP access point. This rests on AWS documents and articles and was not checked on real hardware.
- Behavior of the three commercial tools.
- How client tools behave for server-side copy from volume to bucket (this check ran only the other direction).
- Behavior and retries when a server-side copy fails midway.
- Volumes with the NTFS security style (SMB). This check used only the UNIX security style.
- How a file still being written, or locked over SMB, appears to an S3 reader.
- How access through an access point is recorded in audit logs. The Playbook [constraints note](https://github.com/Yoshiki0705/FSx-for-ONTAP-Adoption-Playbook/blob/a4c8367f9172ee88f0af25731752af63dc2c6225/docs/ja/domains/data-utilization/notes/s3-access-point-constraints.md) (Japanese) covers it, but this check did not confirm it.
- The effect of attaching an access point on existing NFS and SMB workloads (shared throughput capacity).
- Which file formats Athena reads, partitioning, and behavior with many small files.
- Integration targets not in the tables. Absence from a table does not mean unsupported.
- The Snowflake and Databricks configurations are the author's validation articles from one environment each. This page does not confirm that either vendor documents an FSx for ONTAP access point as a supported configuration.
- Only documents whose body was opened and read are listed as sources.

## Source list

All sources were read on 2026-11-25 (Japan time).

| ID | Source | URL |
|---|---|---|
| U1 | NetApp: ONTAP S3 primary use cases | https://docs.netapp.com/us-en/ontap/s3-config/use-cases.html |
| U2 | NetApp: Learn about ONTAP S3 multiprotocol support | https://docs.netapp.com/us-en/ontap/s3-multiprotocol/ |
| U3 | NetApp: Solution technology (dual NFS and S3 access) | https://docs.netapp.com/us-en/netapp-solutions-ai/data-analytics/cdm-fod-solution-technology.html |
| U4 | NetApp: Solution Overview (AI pipeline) | https://docs.netapp.com/us-en/netapp-solutions-ai/infra/ai-pipeline-solution-overview.html |
| U5 | AWS News Blog: Amazon FSx for NetApp ONTAP now integrates with Amazon S3 | https://aws.amazon.com/jp/blogs/aws/amazon-fsx-for-netapp-ontap-now-integrates-with-amazon-s3-for-seamless-data-access/ |
| U6 | FSx for ONTAP User Guide: Using access points with AWS services | https://docs.aws.amazon.com/fsx/latest/ONTAPGuide/using-access-points-with-aws-services.html |
| U7 | AWS Storage Blog: Enable zero-copy access to AWS services on Amazon FSx for NetApp ONTAP with Amazon S3 Access Points | https://aws.amazon.com/blogs/storage/enable-zero-copy-access-to-aws-services-on-amazon-fsx-for-netapp-ontap-with-amazon-s3-access-points/ |
| U8 | AWS What's New: server-side copy between S3 buckets and FSx file systems | https://aws.amazon.com/about-aws/whats-new/2026/11/s3-access-points-server-side-copy-fsx/ | <!-- allow:naming: verbatim page title -->
| U9 | AWS Transfer Family User Guide: FSx for NetApp ONTAP | https://docs.aws.amazon.com/transfer/latest/userguide/fsx-s3-access-points.html |
| U10 | NetApp blog: Simplify data access with S3 Access Points for FSx for ONTAP | https://www.netapp.com/blog/data-access-s3-access-points-fsx-ontap/ |
| U11 | NetApp blog: Unlock AI insights with ONTAP and S3 access points | https://www.netapp.com/blog/ai-insights-ontap-s3-access-points-dremio/ |
| U12 | Dremio blog: From file systems to AI insights | https://www.dremio.com/blog/from-file-systems-to-ai-insights-dremio-cloud-amazon-fsx-for-netapp-ontap/ |
| U13 | The author's validation article: Snowflake and S3 Access Points | https://dev.to/aws-builders/snowflake-and-fsx-for-ontap-s3-access-points-from-access-denied-to-working-external-tables-9k8 |
| U14 | The author's validation article: Databricks and S3 Access Points | https://dev.to/aws-builders/databricks-and-fsx-for-ontap-s3-access-points-a-layer-by-layer-validation-of-observed-boundaries-p4d |
| Record | This repository's 2026-11-24 real-environment check | [2026-11-24-client-tools-stage3.en.md](../benchmarks/records/2026-11-24-client-tools-stage3.en.md) |
| tool-facts | This repository's tool fact check | [tool-facts.en.md](tool-facts.en.md) |

# FSx for ONTAP S3 Access Points Client Access Patterns

🌐 **Language**: [日本語](README.md) | **English**

This repository collects setup steps, confirmation results, and selection guidance for using Amazon FSx for NetApp ONTAP (FSx for ONTAP) S3 Access Points from client tools on your own machines and servers.

> **Current state**: scaffold only. Every cell of the compatibility matrix is `candidate` (unconfirmed) and carries no numbers. Items move to `documented` or `measured` as they are confirmed.

## Role of this repository

Specifications and limits for S3 Access Points, and the core FSx for ONTAP specifications that affect how it is chosen against other services, live in the entry-point repository [FSx-for-ONTAP-Adoption-Playbook](https://github.com/Yoshiki0705/FSx-for-ONTAP-Adoption-Playbook) (the Playbook). This repository is one Spoke under the Playbook. It does not copy those specifications; it links to them. The Spoke holds client-tool setup steps, checklists, and measurement records. The serverless processing that follows is held by a sibling Spoke, [FSx-for-ONTAP-S3AccessPoints-Serverless-Patterns](https://github.com/Yoshiki0705/FSx-for-ONTAP-S3AccessPoints-Serverless-Patterns).

| Where | What it holds |
|---|---|
| Playbook | S3 Access Points specifications and limits, the core FSx for ONTAP specifications that affect choosing it against other services, cross-repository conventions |
| Spoke (this repository) | Client-tool setup steps, manual checklists, benchmark records, the compatibility matrix |
| Sibling Spoke (Serverless-Patterns) | Serverless processing implementations, operational patterns for the file system |

The relationship among the three repositories is shown in [docs/spoke-relations.en.md](docs/spoke-relations.en.md).

## Pinned references

Links to the Playbook are pinned to a commit SHA, and links to Serverless-Patterns are pinned to a release tag. The values are written only in [docs/reference-pins.md](docs/reference-pins.md), and `make drift` checks every link against them. For specifications and limits, start with the Playbook [note on S3 Access Points constraints](https://github.com/Yoshiki0705/FSx-for-ONTAP-Adoption-Playbook/blob/a4c8367f9172ee88f0af25731752af63dc2c6225/docs/ja/domains/data-utilization/notes/s3-access-point-constraints.md) (Japanese).

## Target tools

| Group | Tools | Directory |
|---|---|---|
| Ingest and transfer | AWS CLI, rclone, s5cmd, AWS Transfer Family, File Mover Express | [patterns/ingest](patterns/ingest) |
| Streaming and mount | Mountpoint for Amazon S3, rclone mount, LucidLink Connect, LucidLink Suite | [patterns/streaming](patterns/streaming) |
| MCP clients | Kiro, Claude Desktop | [patterns/mcp](patterns/mcp) |

For commercial tools (File Mover Express and the two LucidLink products), [checklists/vendor](checklists/vendor) holds manual checklists limited to what can be confirmed by hand. Agents do not operate commercial tools.

## Confirmation levels

| Mark | Level | Meaning |
|---|---|---|
| `C` | `candidate` | Unconfirmed. No numbers are written |
| `D` | `documented` | Stated in official documentation. Carries a URL and a date |
| `M` | `measured` | Run and confirmed by hand. Carries a link to the record |

Details are in [docs/compatibility-matrix.en.md](docs/compatibility-matrix.en.md).

## Where to start choosing

[docs/how-to-choose.en.md](docs/how-to-choose.en.md) selects by use case and requirements. Every option has constraints, and the table lists them in the same format for each.

## Getting started

1. Run `make install` to install the development dependencies (ruff, pinned).
2. Run `make all` for lint, gates, tests, and the secret scan.
3. Create new patterns from the templates in [docs/templates](docs/templates).
4. Run real benchmarks by hand, only after you have shown the cost estimate and cleanup steps and received approval ([benchmarks/README.en.md](benchmarks/README.en.md)).

## Adding a language

README files exist in Japanese and English. Steps for adding another are in [docs/adding-a-language.en.md](docs/adding-a-language.en.md).

## License

MIT. See [LICENSE](LICENSE).

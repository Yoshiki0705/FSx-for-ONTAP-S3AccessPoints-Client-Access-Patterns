#!/usr/bin/env python3
"""Generate the architecture figure from a spec, one .drawio per language (light theme only).

Provenance: the machinery here (direct `.drawio` XML, icons embedded as `data:image/svg+xml,<base64>`
data URIs, `--check` against the committed file, `stabilize_svg()`) is reduced from
`tools/build_diagrams.py` in the repository FSx-for-ONTAP-Container-Datastore-Patterns, which took it
from the Adoption Playbook. What is this repository's: the spec, the label table, and the icon list.
The dark theme and the Kubernetes icons of that file are left out because no figure here uses them.

Why the XML is written directly: `insert_image_vertex` of the draw.io MCP tools embeds icons in a form
the CLI drops on export; `mxgraph.aws4.*` carries the 2019 icon generation; and the data URI must be
`data:image/svg+xml,<base64>`, because `;base64,` renders nothing while the export still succeeds.

Icons are read from the AWS Architecture Icons package and are never committed. The package is a
quarterly release from https://aws.amazon.com/architecture/icons/ . Regenerating is therefore an
authoring step, not a gate: the committed `.drawio`, SVG and PNG are the artefacts, and
`make drift` runs the font and flow checkers on them.

Set DRAWIO_FLAGS="--no-sandbox --disable-gpu" when the CLI cannot start an Electron sandbox (a restricted shell).

Run:
  python3 scripts/build_diagrams.py --check           # committed files still match the spec
  python3 scripts/build_diagrams.py --write           # regenerate the .drawio files
  python3 scripts/build_diagrams.py --write --export  # and run the draw.io CLI for SVG and PNG
"""

from __future__ import annotations

import argparse
import base64
import os
import re
import shlex
import subprocess
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from xml.sax.saxutils import quoteattr

ROOT = Path(__file__).resolve().parent.parent
DIAGRAM_DIR = ROOT / "docs" / "diagrams"
IMAGE_DIR = ROOT / "docs" / "images"
PNG_DIR = IMAGE_DIR / "png"

LANGS = ("ja", "en")

# Fixed so regeneration is byte-stable. A changing timestamp puts every diagram in every diff.
MODIFIED = "2026-11-25T00:00:00.000Z"
DRAWIO_CLI = Path("/Applications/draw.io.app/Contents/MacOS/draw.io")

# Relative to the package root; `{d}` is the release date read off the directory name.
ICONS = {
    "fsx_ontap": "Architecture-Service-Icons_{d}/Arch_Storage/64/Arch_Amazon-FSx-for-NetApp-ONTAP_64.svg",
    "s3": "Architecture-Service-Icons_{d}/Arch_Storage/64/Arch_Amazon-Simple-Storage-Service_64.svg",
    "ec2": "Architecture-Service-Icons_{d}/Arch_Compute/64/Arch_Amazon-EC2_64.svg",
    "lambda": "Architecture-Service-Icons_{d}/Arch_Compute/64/Arch_AWS-Lambda_64.svg",
    "athena": "Architecture-Service-Icons_{d}/Arch_Analytics/64/Arch_Amazon-Athena_64.svg",
    "bedrock": "Architecture-Service-Icons_{d}/Arch_Artificial-Intelligence/64/Arch_Amazon-Bedrock_64.svg",
    "transfer": "Architecture-Service-Icons_{d}/Arch_Migration-Modernization/64/Arch_AWS-Transfer-Family_64.svg",
    # The resource icon for an access point, which the standard prefers over the generic bucket.
    "s3_access_point": (
        "Resource-Icons_{d}/Res_Storage/Res_Amazon-Simple-Storage-Service_General-Access-Points_48.svg"
    ),
}

# Native sizes. Rescaling is what the AWS icon guidelines forbid: 80 for a service icon, 48 for a
# resource icon.
ICON_SIZE = {key: 80 for key in ICONS} | {"s3_access_point": 48}

GROUP_POINTS = (
    "points=[[0,0],[0.25,0],[0.5,0],[0.75,0],[1,0],[1,0.25],[1,0.5],[1,0.75],"
    "[1,1],[0.75,1],[0.5,1],[0.25,1],[0,1],[0,0.75],[0,0.5],[0,0.25]]"
)

# The readability floor, enforced by scripts/check_diagram_fonts.py: fontSize >= 16 and at least 14px
# after the image is scaled to the 880px publication width. Canvas width and font size are one
# decision, so the canvas stays under about 1000px.
FONT_BODY = 16
FONT_GROUP = 18

BACKGROUND = "#FFFFFF"
INK = "#232F3E"
FRAME_STROKE = "#666666"


def group_style() -> str:
    return (
        f"{GROUP_POINTS};outlineConnect=0;gradientColor=none;html=1;whiteSpace=wrap;"
        f"fontSize={FONT_GROUP};fontStyle=1;fontColor={INK};shape=mxgraph.aws4.group;"
        "grIcon=mxgraph.aws4.group_aws_cloud;"
        f"strokeColor={INK};fillColor=none;verticalAlign=top;align=left;spacingLeft=30;"
        f"spacingTop=4;dashed=0;labelBackgroundColor={BACKGROUND};"
    )


def icon_style(data_uri: str) -> str:
    return (
        "sketch=0;html=1;shape=image;verticalLabelPosition=bottom;verticalAlign=top;"
        f"labelPosition=center;align=center;imageAspect=1;aspect=fixed;fontSize={FONT_BODY};"
        f"fontColor={INK};image={data_uri};"
    )


def box_style() -> str:
    """A named thing with no AWS icon: a tool, or the NFS / SMB clients."""
    return (
        f"rounded=1;whiteSpace=wrap;html=1;strokeColor={INK};fillColor=none;"
        f"fontColor={INK};fontSize={FONT_BODY};verticalAlign=middle;align=center;"
    )


def frame_style() -> str:
    return (
        f"rounded=1;whiteSpace=wrap;html=1;dashed=1;dashPattern=8 4;strokeColor={FRAME_STROKE};"
        f"fillColor=none;fontColor={INK};fontSize={FONT_BODY};verticalAlign=top;align=center;"
        f"spacingTop=8;labelBackgroundColor={BACKGROUND};"
    )


def note_style() -> str:
    return (
        "rounded=1;absoluteArcSize=1;arcSize=24;whiteSpace=wrap;html=1;"
        f"strokeColor={INK};fillColor=none;fontColor={INK};fontSize={FONT_BODY};"
        "verticalAlign=top;align=left;spacingLeft=10;spacingRight=10;spacingTop=8;"
    )


EDGE_STYLE = (
    "edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=open;endFill=0;"
    f"strokeColor={INK};strokeWidth=1;fontSize={FONT_BODY};fontColor={INK};"
    f"labelBackgroundColor={BACKGROUND};"
)

# --- labels ------------------------------------------------------------------------------------

# Product names stay English in both languages: the naming rule requires the official service name
# with its Amazon / AWS prefix. A role goes in a second line under the full service name.
LABELS: dict[str, dict[str, str]] = {
    "aws_cloud": {"ja": "AWS Cloud", "en": "AWS Cloud"},
    "nfs": {
        "ja": "NFS / SMB のクライアント ※4<br>(置き場所は問わない)",
        "en": "NFS / SMB clients *4<br>(location not specified)",
    },
    "fsx": {
        "ja": "Amazon FSx for NetApp ONTAP<br>(ボリューム)",
        "en": "Amazon FSx for NetApp ONTAP<br>(volume)",
    },
    "ap": {"ja": "S3 Access Points<br>(FSx for ONTAP 用)", "en": "S3 Access Points<br>(for FSx for ONTAP)"},
    "frame_client": {"ja": "クライアントツール ※1", "en": "Client tools *1"},
    "ec2": {"ja": "Amazon EC2<br>(クライアント)", "en": "Amazon EC2<br>(client)"},
    "tool_cli": {"ja": "AWS CLI", "en": "AWS CLI"},
    "tool_s5cmd": {"ja": "s5cmd", "en": "s5cmd"},
    "tool_rclone": {"ja": "rclone", "en": "rclone"},
    "tool_mp": {"ja": "Mountpoint for Amazon S3", "en": "Mountpoint for Amazon S3"},
    "frame_bucket": {"ja": "S3 の汎用バケット", "en": "S3 general purpose bucket"},
    "s3": {"ja": "Amazon S3<br>(汎用バケット)", "en": "Amazon S3<br>(general purpose bucket)"},
    "frame_services": {
        "ja": "S3 API で読む AWS サービス（想定）※3",
        "en": "AWS services (expected) *3",
    },
    "athena": {"ja": "Amazon Athena<br>(SQL)", "en": "Amazon Athena<br>(SQL)"},
    "bedrock": {"ja": "Amazon Bedrock<br>(Knowledge Bases)", "en": "Amazon Bedrock<br>(Knowledge Bases)"},
    "lambda": {"ja": "AWS Lambda<br>(処理)", "en": "AWS Lambda<br>(processing)"},
    "transfer": {"ja": "AWS Transfer Family<br>(SFTP)", "en": "AWS Transfer Family<br>(SFTP)"},
    "e_nfs": {"ja": "NFS / SMB", "en": "NFS / SMB"},
    "e_files": {"ja": "同じファイル", "en": "Same files"},
    "e_client": {"ja": "S3 API", "en": "S3 API"},
    "e_copy": {"ja": "コピー ※2", "en": "Copy *2"},
    "e_services": {"ja": "S3 API", "en": "S3 API"},
    "notes": {
        "ja": (
            "<b>補足</b><br>"
            "※1 <b>クライアントツールは 4 つ</b><br>"
            "AWS CLI、s5cmd、rclone、Mountpoint for Amazon S3。2026-11-24 に ap-northeast-1 の EC2 から"
            "操作を実機で確認した（1 構成、各 1 回）。<br>"
            "※2 <b>実機で測ったコピーは、バケットからボリュームへの向きだけ</b><br>"
            "AWS CLI、s5cmd、rclone で確認。逆向きは Playbook の記録。ドキュメントでは同一リージョン内。"
            "所有者、モード、更新時刻は写らなかった（Playbook の実測。root のユーザーの構成のみ）。<br>"
            "※3 <b>枠内の AWS サービスは文書上の想定</b><br>"
            "このリポジトリでは実機を確認していない。<br>"
            "※4 <b>NFS / SMB クライアントの置き場所は問わない</b><br>"
            "VPC 内かオンプレミスかを、図は示さない。"
        ),
        "en": (
            "<b>Notes</b><br>"
            "*1 <b>Four client tools</b><br>"
            "AWS CLI, s5cmd, rclone, and Mountpoint for Amazon S3. Checked on real hardware from an EC2 "
            "instance in ap-northeast-1 on 2026-11-24 (one configuration, one run each).<br>"
            "*2 <b>The copy measured on real hardware ran only from bucket to volume</b><br>"
            "With AWS CLI, s5cmd, and rclone. The other direction is in a Playbook record. The documents "
            "say one Region only. Owner, mode, and modification time were not carried over (a Playbook "
            "measurement, root user configuration only).<br>"
            "*3 <b>The AWS services in the frame are expectations from documents</b><br>"
            "Not checked on real hardware in this repository.<br>"
            "*4 <b>Where the NFS / SMB clients run is not specified</b><br>"
            "The figure does not show VPC or on premises."
        ),
    },
}

CJK = re.compile(r"[\u3000-\u30ff\u4e00-\u9fff]")


def label(key: str, lang: str) -> str:
    """Look up a label, refusing to emit Japanese into an English diagram.

    A missing English string is otherwise invisible: the file exports and the Japanese text simply
    sits in the English figure.
    """
    if key not in LABELS:
        raise SystemExit(f"build_diagrams: no label {key!r}")
    text = LABELS[key][lang]
    if lang != "ja" and CJK.search(text):
        raise SystemExit(f"build_diagrams: label {key!r} for {lang!r} contains Japanese")
    return text


# --- spec --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Node:
    cid: str
    icon: str
    label: str
    x: int
    y: int


@dataclass(frozen=True)
class Rect:
    """A frame, a box or a notes box: a rectangle with a text label."""

    cid: str
    kind: str  # "group", "frame", "box" or "note"
    label: str
    x: int
    y: int
    width: int
    height: int


@dataclass(frozen=True)
class Edge:
    cid: str
    source: str
    target: str
    label: str = ""
    exit_at: tuple[float, float] | None = None
    entry_at: tuple[float, float] | None = None
    # A line with no arrowhead: it states that two things are connected without claiming a direction.
    plain: bool = False
    # Where the label sits: position along the path (-1..1, 0 = midpoint) and a pixel nudge.
    label_at: float | None = None
    label_offset: tuple[int, int] | None = None

    def style(self) -> str:
        style = EDGE_STYLE
        if self.plain:
            style = style.replace("endArrow=open;endFill=0;", "endArrow=none;")
        if self.exit_at:
            style += f"exitX={self.exit_at[0]};exitY={self.exit_at[1]};exitDx=0;exitDy=0;"
        if self.entry_at:
            style += f"entryX={self.entry_at[0]};entryY={self.entry_at[1]};entryDx=0;entryDy=0;"
        return style

    def geometry(self) -> list[str]:
        if self.label_at is None and self.label_offset is None:
            return ['          <mxGeometry relative="1" as="geometry" />']
        x = "" if self.label_at is None else f'x="{self.label_at}" '
        dx, dy = self.label_offset or (0, 0)
        return [
            f'          <mxGeometry {x}relative="1" as="geometry">',
            f'            <mxPoint as="offset" x="{dx}" y="{dy}" />',
            "          </mxGeometry>",
        ]


@dataclass(frozen=True)
class Diagram:
    name: str
    diagram_id: str
    width: int
    height: int
    rects: tuple[Rect, ...] = ()
    nodes: tuple[Node, ...] = ()
    edges: tuple[Edge, ...] = ()

    def filename(self, lang: str) -> str:
        return self.name + ("" if lang == "ja" else f"-{lang}") + ".drawio"


def _overview() -> Diagram:
    """The volume keeps its NFS / SMB path; an access point adds the S3 API to the same files.

    Reading order is left to right, then down. The access point is the hinge: files on the volume
    appear through it to three kinds of reader. The client tools run on an EC2 instance and are the
    part this repository ran on real hardware. The bucket is reached by a two-way server-side copy.
    The AWS services at the lower right are expectations taken from documents, and the figure says
    so in its frame title and in note *3, because a picture of a connection reads as "works".
    """
    return Diagram(
        name="s3ap-client-access-overview",
        diagram_id="s3ap-client-access-overview",
        width=980,
        height=900,
        rects=(
            Rect("aws_cloud", "group", "aws_cloud", 10, 10, 960, 880),
            Rect("nfs", "box", "nfs", 30, 52, 300, 56),
            Rect("frame_client", "frame", "frame_client", 590, 40, 370, 270),
            Rect("tool_cli", "box", "tool_cli", 745, 78, 205, 38),
            Rect("tool_s5cmd", "box", "tool_s5cmd", 745, 124, 205, 38),
            Rect("tool_rclone", "box", "tool_rclone", 745, 170, 205, 38),
            Rect("tool_mp", "box", "tool_mp", 745, 216, 205, 38),
            Rect("frame_bucket", "frame", "frame_bucket", 590, 340, 370, 200),
            Rect("frame_services", "frame", "frame_services", 590, 570, 370, 310),
            Rect("notes", "note", "notes", 30, 340, 440, 370),
        ),
        nodes=(
            Node("fsx", "fsx_ontap", "fsx", 140, 140),
            Node("ap", "s3_access_point", "ap", 370, 156),
            Node("ec2", "ec2", "ec2", 620, 90),
            Node("s3", "s3", "s3", 735, 380),
            Node("athena", "athena", "athena", 620, 610),
            Node("bedrock", "bedrock", "bedrock", 810, 610),
            Node("lambda", "lambda", "lambda", 620, 750),
            Node("transfer", "transfer", "transfer", 810, 750),
        ),
        edges=(
            Edge("e_nfs", "nfs", "fsx", "e_nfs", exit_at=(0.5, 1.0), entry_at=(0.5, 0.0), plain=True),
            Edge("e_files", "fsx", "ap", "e_files", exit_at=(1.0, 0.5), entry_at=(0.0, 0.5), plain=True),
            Edge(
                "e_client",
                "ap",
                "frame_client",
                "e_client",
                exit_at=(1.0, 0.5),
                entry_at=(0.0, 0.5),
                label_at=0.85,
                label_offset=(0, -14),
            ),
            Edge(
                "e_copy",
                "ap",
                "frame_bucket",
                "e_copy",
                exit_at=(1.0, 0.5),
                entry_at=(0.0, 0.5),
                plain=True,
                label_at=0.82,
                label_offset=(0, -14),
            ),
            Edge(
                "e_services",
                "ap",
                "frame_services",
                "e_services",
                exit_at=(1.0, 0.5),
                entry_at=(0.0, 0.5),
                label_at=0.9,
                label_offset=(0, -14),
            ),
        ),
    )


DIAGRAMS = (_overview(),)

# --- icons -------------------------------------------------------------------------------------


def icon_package(explicit: str | None) -> Path:
    """Locate the AWS Architecture Icons package."""
    candidate = explicit or os.environ.get("AWS_ICON_PACKAGE")
    if candidate:
        path = Path(candidate).expanduser()
        if not path.is_dir():
            raise SystemExit(f"build_diagrams: {path} is not a directory")
        return path
    raise SystemExit(
        "build_diagrams: the AWS Architecture Icons package was not found.\n"
        "  Download the current quarterly release from https://aws.amazon.com/architecture/icons/ ,\n"
        "  unzip it outside the repository, and pass --icons <dir> or set AWS_ICON_PACKAGE.\n"
        "  The package is never committed here; the generated .drawio files are."
    )


def package_date(package: Path) -> str:
    """Read the release date from a package root or an extracted service-icon directory."""
    match = re.search(r"(?:Icon-package_|Architecture-Service-Icons_)(\d{8})", package.name)
    if not match:
        for child in package.iterdir():
            match = re.search(r"Architecture-Service-Icons_(\d{8})", child.name)
            if match:
                break
    if not match:
        raise SystemExit(f"build_diagrams: cannot read a release date from {package!s}")
    return match.group(1)


def data_uris(package: Path) -> dict[str, str]:
    """Read every icon and build its draw.io data URI (comma form, not `;base64,`)."""
    date = package_date(package)
    uris: dict[str, str] = {}
    for key, relative in ICONS.items():
        resolved = relative.format(d=date)
        path = package / resolved
        if not path.is_file():
            raise SystemExit(f"build_diagrams: {resolved} missing from {package}")
        uris[key] = "data:image/svg+xml," + base64.b64encode(path.read_bytes()).decode("ascii")
    return uris


# --- rendering ---------------------------------------------------------------------------------


def render(diagram: Diagram, lang: str, uris: dict[str, str]) -> str:
    suffix = "" if lang == "ja" else f"-{lang}"
    name = f"{diagram.name}{suffix}"
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<mxfile host="app.diagrams.net" modified="{MODIFIED}" agent="build_diagrams.py" '
        'version="24.0.0" type="device">',
        f'  <diagram id="{diagram.diagram_id}{suffix}" name="{name}">',
        '    <mxGraphModel dx="1422" dy="762" grid="1" gridSize="10" guides="1" tooltips="1" '
        'connect="1" arrows="1" fold="1" page="1" pageScale="1" '
        f'pageWidth="{diagram.width}" pageHeight="{diagram.height}" background="{BACKGROUND}" '
        'math="0" shadow="0">',
        "      <root>",
        '        <mxCell id="0" />',
        '        <mxCell id="1" parent="0" />',
    ]

    def vertex(cid: str, value: str, style: str, x: int, y: int, w: int, h: int) -> None:
        lines.append(
            f"        <mxCell id={quoteattr(cid)} value={quoteattr(value)} "
            f'style={quoteattr(style)} vertex="1" parent="1">'
        )
        lines.append(f'          <mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry" />')
        lines.append("        </mxCell>")

    # Edges first, so a frame title and an icon paint over a line rather than under it.
    for edge in diagram.edges:
        value = label(edge.label, lang) if edge.label else ""
        lines.append(
            f"        <mxCell id={quoteattr(edge.cid)} value={quoteattr(value)} "
            f'style={quoteattr(edge.style())} edge="1" source={quoteattr(edge.source)} '
            f'target={quoteattr(edge.target)} parent="1">'
        )
        lines += edge.geometry()
        lines.append("        </mxCell>")
    styles = {"group": group_style(), "frame": frame_style(), "box": box_style(), "note": note_style()}
    for kind in ("group", "frame", "box", "note"):
        for rect in diagram.rects:
            if rect.kind == kind:
                vertex(
                    rect.cid, label(rect.label, lang), styles[kind], rect.x, rect.y, rect.width, rect.height
                )
    for node in diagram.nodes:
        size = ICON_SIZE[node.icon]
        vertex(node.cid, label(node.label, lang), icon_style(uris[node.icon]), node.x, node.y, size, size)

    lines += ["      </root>", "    </mxGraphModel>", "  </diagram>", "</mxfile>", ""]
    xml = "\n".join(lines)
    # A note marker must also appear on a label in the figure, or the note points at nothing.
    note_text = label("notes", lang)
    figure_text = " ".join(
        label(k, lang)
        for k in {e.label for e in diagram.edges if e.label}
        | {n.label for n in diagram.nodes}
        | {r.label for r in diagram.rects if r.kind != "note"}
    )
    for marker in re.findall(r"(?:※|\*)\d", note_text):
        if marker not in figure_text:
            raise SystemExit(f"build_diagrams: note marker {marker} is not on any label of the figure")
    ET.fromstring(xml)  # a corrupt cell is dropped silently by draw.io; fail here instead
    for cid in (
        [e.cid for e in diagram.edges] + [r.cid for r in diagram.rects] + [n.cid for n in diagram.nodes]
    ):
        if f"id={quoteattr(cid)}" not in xml:
            raise SystemExit(f"build_diagrams: cell {cid!r} did not reach the output")
    return xml


def cells(xml: str) -> list[tuple[str, str, str, str]]:
    """Reduce a document to what a reader sees, so formatting is not compared."""
    out = []
    for cell in ET.fromstring(xml).find(".//root").iter("mxCell"):
        geometry = cell.find("mxGeometry")
        geo = " ".join(f"{k}={v}" for k, v in sorted(geometry.attrib.items())) if geometry is not None else ""
        style = re.sub(
            r"image=data:image/svg\+xml,([A-Za-z0-9+/=]{16})[A-Za-z0-9+/=]*",
            r"image=<\1...>",
            cell.get("style") or "",
        )
        out.append((cell.get("id") or "", cell.get("value") or "", style, geo))
    return out


def check(uris: dict[str, str], diagrams: tuple[Diagram, ...]) -> int:
    problems = 0
    total = 0
    for diagram in diagrams:
        for lang in LANGS:
            total += 1
            path = DIAGRAM_DIR / diagram.filename(lang)
            if not path.is_file():
                print(f"  missing   {path.relative_to(ROOT)}", file=sys.stderr)
                problems += 1
                continue
            want = cells(render(diagram, lang, uris))
            got = cells(path.read_text(encoding="utf-8"))
            if want != got:
                problems += 1
                print(f"  differs   {path.relative_to(ROOT)}", file=sys.stderr)
    if problems:
        print(
            "\n  A generated diagram was edited by hand, or the spec moved without a regenerate.\n"
            "  Run: python3 scripts/build_diagrams.py --write --export",
            file=sys.stderr,
        )
        return 1
    print(f"diagrams: {total} file(s) match the spec")
    return 0


# draw.io stamps a fresh random id into every SVG export. Left alone, re-exporting an unchanged
# diagram still rewrites the file. The id only has to be unique within the document.
SVG_RANDOM_ID = re.compile(r"ge-svg-[A-Za-z0-9_-]+")


def stabilize_svg(target: Path) -> None:
    text = target.read_text(encoding="utf-8")
    stabilized = SVG_RANDOM_ID.sub(f"ge-svg-{target.stem}", text)
    if stabilized != text:
        target.write_text(stabilized, encoding="utf-8")


def export(diagram: Diagram, lang: str) -> None:
    source = DIAGRAM_DIR / diagram.filename(lang)
    if not DRAWIO_CLI.is_file():
        print(f"  draw.io CLI not found at {DRAWIO_CLI}; skipping export", file=sys.stderr)
        return
    runs = (
        # SVG for the repository: crawlers and screen readers can reach the text.
        (IMAGE_DIR / f"{source.stem}.svg", ["--format", "svg", "--embed-svg-images"]),
        # PNG at 2x for the blog posts, which do not render SVG reliably.
        (PNG_DIR / f"{source.stem}@2x.png", ["--format", "png", "--scale", "2"]),
    )
    for target, extra in runs:
        target.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [
                str(DRAWIO_CLI),
                *shlex.split(os.environ.get("DRAWIO_FLAGS", "")),
                "--export",
                "--border",
                "12",
                *extra,
                "--output",
                str(target),
                str(source),
            ],
            check=True,
            capture_output=True,
        )
        if target.suffix == ".svg":
            stabilize_svg(target)
        print(f"  exported  {target.relative_to(ROOT)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="regenerate the .drawio files")
    parser.add_argument("--export", action="store_true", help="also export SVG and PNG")
    parser.add_argument("--check", action="store_true", help="compare committed files to the spec")
    parser.add_argument("--icons", help="path to the AWS Architecture Icons package")
    args = parser.parse_args()
    if not (args.write or args.check):
        parser.error("give --write or --check")

    uris = data_uris(icon_package(args.icons))
    if args.check:
        return check(uris, DIAGRAMS)

    DIAGRAM_DIR.mkdir(parents=True, exist_ok=True)
    for diagram in DIAGRAMS:
        for lang in LANGS:
            path = DIAGRAM_DIR / diagram.filename(lang)
            path.write_text(render(diagram, lang, uris), encoding="utf-8")
            print(f"  wrote     {path.relative_to(ROOT)}")
            if args.export:
                export(diagram, lang)
    return 0


if __name__ == "__main__":
    sys.exit(main())

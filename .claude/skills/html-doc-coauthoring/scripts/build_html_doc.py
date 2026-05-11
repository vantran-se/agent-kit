#!/usr/bin/env python3

import html
import json
import re
import sys
from pathlib import Path

PALETTE = [
    "#2563eb",
    "#7c3aed",
    "#059669",
    "#dc2626",
    "#d97706",
    "#0891b2",
    "#be185d",
    "#4f46e5",
]

ACCENTS = [
    {"bar": "bg-blue-500", "soft": "bg-blue-50", "border": "border-blue-200", "text": "text-blue-700", "ring": "ring-blue-100"},
    {"bar": "bg-violet-500", "soft": "bg-violet-50", "border": "border-violet-200", "text": "text-violet-700", "ring": "ring-violet-100"},
    {"bar": "bg-emerald-500", "soft": "bg-emerald-50", "border": "border-emerald-200", "text": "text-emerald-700", "ring": "ring-emerald-100"},
    {"bar": "bg-amber-500", "soft": "bg-amber-50", "border": "border-amber-200", "text": "text-amber-700", "ring": "ring-amber-100"},
    {"bar": "bg-rose-500", "soft": "bg-rose-50", "border": "border-rose-200", "text": "text-rose-700", "ring": "ring-rose-100"},
    {"bar": "bg-cyan-500", "soft": "bg-cyan-50", "border": "border-cyan-200", "text": "text-cyan-700", "ring": "ring-cyan-100"},
]


def text(value):
    if value is None:
        return ""
    return str(value)


def esc(value):
    return html.escape(text(value), quote=True)


def safe_href(value):
    href = text(value).strip()
    allowed = ("http://", "https://", "#", "mailto:", "./", "../", "/")
    if href.startswith(allowed):
        return esc(href)
    return "#"


def slugify(value):
    slug = re.sub(r"[^a-z0-9]+", "-", text(value).lower()).strip("-")
    return slug or "section"


def accent(index):
    return ACCENTS[index % len(ACCENTS)]


def inline_md(value):
    result = esc(value)
    result = re.sub(r"`([^`]+)`", r'<code class="rounded bg-slate-100 px-1.5 py-0.5 text-sm text-slate-900">\1</code>', result)
    result = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", result)
    result = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", result)

    def link(match):
        label = match.group(1)
        href = safe_href(match.group(2))
        return f'<a class="font-medium text-blue-700 underline decoration-blue-300 underline-offset-2" href="{href}">{label}</a>'

    result = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, result)
    return result


def markdown_to_html(value):
    lines = text(value).splitlines()
    out = []
    paragraph = []
    list_type = None
    in_code = False
    code_lines = []
    code_lang = ""

    def close_list():
        nonlocal list_type
        if list_type:
            out.append(f"</{list_type}>")
            list_type = None

    def flush_paragraph():
        nonlocal paragraph
        if paragraph:
            out.append(f'<p>{inline_md(" ".join(paragraph))}</p>')
            paragraph = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            if in_code:
                out.append(render_code_block("\n".join(code_lines), code_lang))
                in_code = False
                code_lines = []
                code_lang = ""
            else:
                flush_paragraph()
                close_list()
                in_code = True
                code_lang = stripped[3:].strip()
            continue
        if in_code:
            code_lines.append(line)
            continue
        if not stripped:
            flush_paragraph()
            close_list()
            continue
        heading = re.match(r"^(#{1,4})\s+(.+)$", stripped)
        if heading:
            flush_paragraph()
            close_list()
            level = min(len(heading.group(1)) + 1, 4)
            out.append(f'<h{level}>{inline_md(heading.group(2))}</h{level}>')
            continue
        bullet = re.match(r"^\s*[-*]\s+(.+)$", line)
        numbered = re.match(r"^\s*\d+\.\s+(.+)$", line)
        if bullet:
            flush_paragraph()
            if list_type != "ul":
                close_list()
                out.append("<ul>")
                list_type = "ul"
            out.append(f"<li>{inline_md(bullet.group(1))}</li>")
            continue
        if numbered:
            flush_paragraph()
            if list_type != "ol":
                close_list()
                out.append("<ol>")
                list_type = "ol"
            out.append(f"<li>{inline_md(numbered.group(1))}</li>")
            continue
        if line.startswith(">"):
            flush_paragraph()
            close_list()
            out.append(f'<blockquote>{inline_md(line.lstrip("> "))}</blockquote>')
            continue
        paragraph.append(stripped)
    if in_code:
        out.append(render_code_block("\n".join(code_lines), code_lang))
    flush_paragraph()
    close_list()
    return "\n".join(out)


def column_class(columns):
    try:
        count = int(columns)
    except (TypeError, ValueError):
        count = 3
    if count <= 1:
        return "grid-cols-1"
    if count == 2:
        return "grid-cols-1 md:grid-cols-2"
    if count == 4:
        return "grid-cols-1 md:grid-cols-2 xl:grid-cols-4"
    return "grid-cols-1 md:grid-cols-2 xl:grid-cols-3"


def render_cards(block):
    items = block.get("items", [])
    cols = column_class(block.get("columns", 3))
    parts = [f'<div class="grid {cols} gap-4">']
    for index, item in enumerate(items):
        color = accent(index)
        badge = item.get("badge")
        badge_html = f'<span class="rounded-full {color["soft"]} px-2.5 py-1 text-xs font-semibold {color["text"]}">{esc(badge)}</span>' if badge else ""
        parts.append(
            f'<article class="overflow-hidden rounded-2xl border {color["border"]} bg-white shadow-sm ring-4 {color["ring"]}">'
            f'<div class="h-1.5 {color["bar"]}"></div>'
            '<div class="p-5">'
            f'<div class="mb-3 flex items-center justify-between gap-3"><h3 class="text-base font-semibold text-slate-950">{esc(item.get("title"))}</h3>{badge_html}</div>'
            f'<div class="doc-prose text-sm text-slate-600">{markdown_to_html(item.get("body", ""))}</div>'
            '</div></article>'
        )
    parts.append("</div>")
    return "\n".join(parts)


def render_metrics(block):
    items = block.get("items", [])
    parts = ['<div class="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">']
    for index, item in enumerate(items):
        color = accent(index)
        parts.append(
            f'<div class="rounded-2xl border {color["border"]} bg-white p-5 shadow-sm ring-4 {color["ring"]}">'
            f'<div class="mb-4 inline-flex rounded-full {color["soft"]} px-3 py-1 text-xs font-semibold uppercase tracking-wide {color["text"]}">{esc(item.get("label"))}</div>'
            f'<div class="text-3xl font-black tracking-tight text-slate-950">{esc(item.get("value"))}</div>'
            f'<div class="mt-2 text-sm text-slate-500">{esc(item.get("hint"))}</div>'
            '</div>'
        )
    parts.append("</div>")
    return "\n".join(parts)


def render_table(block):
    headers = block.get("headers", [])
    rows = block.get("rows", [])
    parts = ['<div class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm"><div class="overflow-x-auto"><table class="min-w-full divide-y divide-slate-200">']
    if headers:
        parts.append('<thead class="bg-gradient-to-r from-blue-50 via-violet-50 to-cyan-50"><tr>')
        for header in headers:
            parts.append(f'<th class="px-4 py-3 text-left text-xs font-bold uppercase tracking-wide text-slate-700">{esc(header)}</th>')
        parts.append("</tr></thead>")
    parts.append('<tbody class="divide-y divide-slate-100">')
    for row in rows:
        parts.append('<tr class="transition hover:bg-blue-50/40">')
        for cell in row:
            parts.append(f'<td class="px-4 py-3 align-top text-sm text-slate-700">{markdown_to_html(cell)}</td>')
        parts.append("</tr>")
    parts.append("</tbody></table></div></div>")
    return "\n".join(parts)


def render_callout(block):
    tone = text(block.get("tone", "info")).lower()
    styles = {
        "info": "border-blue-200 bg-blue-50 text-blue-950",
        "success": "border-emerald-200 bg-emerald-50 text-emerald-950",
        "warning": "border-amber-200 bg-amber-50 text-amber-950",
        "danger": "border-rose-200 bg-rose-50 text-rose-950",
    }
    style = styles.get(tone, styles["info"])
    title = block.get("title")
    title_html = f'<div class="mb-1 font-semibold">{esc(title)}</div>' if title else ""
    return f'<aside class="rounded-2xl border p-5 shadow-sm {style}">{title_html}<div class="doc-prose text-sm">{markdown_to_html(block.get("content", ""))}</div></aside>'


def render_chart(block, charts):
    chart_id = f"chart-{len(charts) + 1}"
    chart = {
        "id": chart_id,
        "type": block.get("chartType", block.get("typeName", "bar")),
        "labels": block.get("labels", []),
        "datasets": block.get("datasets", []),
        "options": block.get("options", {}),
    }
    charts.append(chart)
    title = block.get("title")
    title_html = f'<div class="mb-4 text-sm font-bold uppercase tracking-wide text-slate-600">{esc(title)}</div>' if title else ""
    return f'<div class="rounded-2xl border border-blue-100 bg-white p-5 shadow-sm ring-4 ring-blue-50">{title_html}<div class="h-80"><canvas id="{chart_id}"></canvas></div></div>'


def render_steps(block):
    items = block.get("items", [])
    parts = ['<ol class="space-y-4">']
    for index, item in enumerate(items, 1):
        color = accent(index - 1)
        parts.append(
            f'<li class="flex gap-4 rounded-2xl border {color["border"]} bg-white p-5 shadow-sm">'
            f'<div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full {color["bar"]} text-sm font-bold text-white shadow-sm">{index}</div>'
            '<div>'
            f'<h3 class="font-semibold text-slate-950">{esc(item.get("title"))}</h3>'
            f'<div class="doc-prose mt-1 text-sm text-slate-600">{markdown_to_html(item.get("body", ""))}</div>'
            '</div></li>'
        )
    parts.append("</ol>")
    return "\n".join(parts)


def render_flow(block):
    items = block.get("items", [])
    title = block.get("title")
    title_html = f'<h3 class="mb-4 text-sm font-bold uppercase tracking-wide text-slate-600">{esc(title)}</h3>' if title else ""
    parts = [f'<div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">{title_html}<div class="grid gap-4 lg:grid-cols-{min(max(len(items), 1), 4)}">']
    for index, item in enumerate(items, 1):
        color = accent(index - 1)
        parts.append(
            '<div class="relative">'
            f'<div class="h-full rounded-2xl border {color["border"]} {color["soft"]} p-4">'
            f'<div class="mb-3 flex h-8 w-8 items-center justify-center rounded-full {color["bar"]} text-sm font-bold text-white">{index}</div>'
            f'<div class="font-semibold text-slate-950">{esc(item.get("title"))}</div>'
            f'<div class="doc-prose mt-1 text-sm text-slate-600">{markdown_to_html(item.get("body", ""))}</div>'
            '</div></div>'
        )
    parts.append("</div></div>")
    return "\n".join(parts)


def render_timeline(block):
    items = block.get("items", [])
    title = block.get("title")
    title_html = f'<h3 class="mb-5 text-sm font-bold uppercase tracking-wide text-slate-600">{esc(title)}</h3>' if title else ""
    parts = [f'<div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">{title_html}<div class="relative space-y-5 before:absolute before:left-4 before:top-2 before:h-[calc(100%-1rem)] before:w-0.5 before:bg-slate-200">']
    for index, item in enumerate(items):
        color = accent(index)
        date = item.get("date")
        date_html = f'<div class="mb-1 text-xs font-bold uppercase tracking-wide {color["text"]}">{esc(date)}</div>' if date else ""
        parts.append(
            '<div class="relative flex gap-4">'
            f'<div class="z-10 mt-1 h-8 w-8 shrink-0 rounded-full border-4 border-white {color["bar"]} shadow"></div>'
            '<div class="flex-1 rounded-2xl border border-slate-200 bg-slate-50/70 p-4">'
            f'{date_html}<div class="font-semibold text-slate-950">{esc(item.get("title"))}</div>'
            f'<div class="doc-prose mt-1 text-sm text-slate-600">{markdown_to_html(item.get("body", ""))}</div>'
            '</div></div>'
        )
    parts.append("</div></div>")
    return "\n".join(parts)


KIND_STYLES = {
    "internet": {"icon": "🌐", "bg": "#dbeafe", "border": "#60a5fa", "text": "#1e3a8a"},
    "client": {"icon": "👤", "bg": "#ede9fe", "border": "#a78bfa", "text": "#4c1d95"},
    "load-balancer": {"icon": "⚖️", "bg": "#e0f2fe", "border": "#38bdf8", "text": "#075985"},
    "api": {"icon": "⚙️", "bg": "#dbeafe", "border": "#3b82f6", "text": "#1d4ed8"},
    "server": {"icon": "🖥️", "bg": "#f1f5f9", "border": "#94a3b8", "text": "#334155"},
    "compute": {"icon": "🖥️", "bg": "#f1f5f9", "border": "#94a3b8", "text": "#334155"},
    "function": {"icon": "λ", "bg": "#fff7ed", "border": "#fb923c", "text": "#9a3412"},
    "database": {"icon": "🗄️", "bg": "#dcfce7", "border": "#22c55e", "text": "#166534"},
    "cache": {"icon": "⚡", "bg": "#fef3c7", "border": "#f59e0b", "text": "#92400e"},
    "queue": {"icon": "📬", "bg": "#fce7f3", "border": "#ec4899", "text": "#9d174d"},
    "storage": {"icon": "🪣", "bg": "#ccfbf1", "border": "#14b8a6", "text": "#115e59"},
    "security": {"icon": "🔐", "bg": "#fee2e2", "border": "#ef4444", "text": "#991b1b"},
    "observability": {"icon": "📈", "bg": "#e0e7ff", "border": "#6366f1", "text": "#3730a3"},
    "ci": {"icon": "🚀", "bg": "#f0fdf4", "border": "#22c55e", "text": "#166534"},
    "service": {"icon": "▣", "bg": "#f8fafc", "border": "#94a3b8", "text": "#334155"},
}


def cloud_id(value):
    identifier = slugify(value).replace("-", "_")
    if identifier and identifier[0].isdigit():
        identifier = f"n_{identifier}"
    return identifier or "node"


def cloud_style(kind):
    return KIND_STYLES.get(text(kind).lower(), KIND_STYLES["service"])


def normalize_cloud(block):
    groups = []
    nodes = []
    edges = []
    node_ids = set()
    group_ids = set()

    for group_index, group in enumerate(block.get("groups", [])):
        group_id = cloud_id(group.get("id", group.get("title", f"group-{group_index}")))
        group_ids.add(group_id)
        groups.append({
            "id": group_id,
            "label": text(group.get("title", group_id)),
            "parent": cloud_id(group.get("parent")) if group.get("parent") else None,
        })

    def add_node(node, fallback_parent=None):
        node_id = cloud_id(node.get("id", node.get("label", node.get("title", "service"))))
        if node_id in node_ids:
            return
        node_ids.add(node_id)
        kind = text(node.get("kind", node.get("type", "service"))).lower()
        style = cloud_style(kind)
        label = text(node.get("label", node.get("title", node_id)))
        parent = node.get("group", node.get("parent", fallback_parent))
        parent_id = cloud_id(parent) if parent else None
        nodes.append({
            "data": {
                "id": node_id,
                "label": label,
                "displayLabel": f'{node.get("icon", style["icon"])} {label}',
                "kind": kind,
                "group": parent_id if parent_id in group_ids else None,
                "groupLabel": next((group["label"] for group in groups if group["id"] == parent_id), ""),
                "bg": node.get("bg", style["bg"]),
                "border": node.get("border", style["border"]),
                "textColor": node.get("textColor", style["text"]),
                "meta": text(node.get("body", node.get("description", node.get("meta", "")))),
            }
        })

    for group in block.get("groups", []):
        parent = cloud_id(group.get("id", group.get("title", "group")))
        for item in group.get("items", []):
            add_node(item, parent)

    for node in block.get("nodes", []):
        add_node(node)

    for index, connection in enumerate(block.get("connections", block.get("edges", []))):
        source = cloud_id(connection.get("from"))
        target = cloud_id(connection.get("to"))
        if source in node_ids and target in node_ids:
            edges.append({
                "data": {
                    "id": f"edge_{index}_{source}_{target}",
                    "source": source,
                    "target": target,
                    "label": text(connection.get("label", "")),
                }
            })

    return groups, nodes, edges


def render_image(block):
    src = safe_href(block.get("src", "#"))
    title = block.get("title")
    caption = block.get("caption", block.get("body", ""))
    alt = block.get("alt", title or "Document image")
    title_html = f'<h3 class="mb-4 text-sm font-bold uppercase tracking-wide text-slate-600">{esc(title)}</h3>' if title else ""
    caption_html = f'<div class="mt-3 text-sm text-slate-500">{esc(caption)}</div>' if caption else ""
    return (
        f'<figure class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">{title_html}'
        f'<img class="w-full rounded-2xl border border-slate-100 bg-slate-50 object-contain" src="{src}" alt="{esc(alt)}">'
        f'{caption_html}</figure>'
    )


def render_cloud(block, cloud_diagrams):
    graph_id = f"cloud-diagram-{len(cloud_diagrams) + 1}"
    groups, nodes, edges = normalize_cloud(block)
    cloud_diagrams.append({
        "id": graph_id,
        "elements": nodes + edges,
        "groups": groups,
        "layout": block.get("layout", "LR"),
    })
    title = block.get("title")
    caption = block.get("caption", block.get("body", ""))
    provider = block.get("provider", "Cloud")
    title_html = f'<h3 class="mb-4 text-sm font-bold uppercase tracking-wide text-slate-600">{esc(title)}</h3>' if title else ""
    caption_html = f'<div class="mt-3 text-sm text-slate-500">{esc(caption)}</div>' if caption else ""
    kinds = []
    for node in nodes:
        kind = node["data"].get("kind", "service")
        if kind not in kinds:
            kinds.append(kind)
    legend_html = "".join(
        f'<span class="inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-semibold" style="background:{cloud_style(kind)["bg"]};border-color:{cloud_style(kind)["border"]};color:{cloud_style(kind)["text"]}"><span>{cloud_style(kind)["icon"]}</span>{esc(kind)}</span>'
        for kind in kinds
    )
    group_html = "".join(
        f'<span class="rounded-full border border-slate-200 bg-slate-50 px-2.5 py-1 text-xs font-semibold text-slate-600">{esc(group["label"])}</span>'
        for group in groups
    )
    source_html = ""
    if block.get("showSource"):
        source = json.dumps({"groups": block.get("groups", []), "nodes": block.get("nodes", []), "connections": block.get("connections", block.get("edges", []))}, ensure_ascii=False, indent=2)
        source_html = f'<details class="mt-4 rounded-2xl border border-slate-200 bg-slate-50 p-4"><summary class="cursor-pointer font-semibold text-slate-800">Topology source</summary><div class="mt-3">{render_code_block(source, "json")}</div></details>'
    return (
        f'<div class="rounded-2xl border border-cyan-200 bg-white p-5 shadow-sm ring-4 ring-cyan-50">{title_html}'
        f'<div class="mb-4 flex flex-wrap items-center justify-between gap-3">'
        f'<div class="flex flex-wrap items-center gap-2"><span class="inline-flex rounded-full bg-cyan-50 px-3 py-1 text-xs font-bold uppercase tracking-wide text-cyan-700">Cloud topology · {esc(provider)}</span>{legend_html}</div>'
        f'<div class="flex gap-2"><button class="cloud-reset rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-600 shadow-sm hover:bg-slate-50" data-cloud-target="{graph_id}" type="button">Reset view</button><button class="cloud-fullscreen rounded-lg bg-slate-900 px-3 py-1.5 text-xs font-semibold text-white shadow-sm hover:bg-slate-700" data-cloud-target="{graph_id}" type="button">Fullscreen</button></div>'
        f'</div>'
        f'<div id="{graph_id}" class="cloud-diagram h-[620px] rounded-2xl border border-cyan-100 bg-gradient-to-br from-white via-slate-50 to-cyan-50"></div>'
        f'<div class="mt-4 flex flex-wrap gap-2"><span class="text-xs font-bold uppercase tracking-wide text-slate-400">Groups</span>{group_html}</div>'
        f'{caption_html}{source_html}</div>'
    )


def render_checklist(block):
    items = block.get("items", [])
    title = block.get("title")
    title_html = f'<h3 class="mb-4 text-sm font-bold uppercase tracking-wide text-slate-600">{esc(title)}</h3>' if title else ""
    parts = [f'<div class="rounded-2xl border border-emerald-200 bg-white p-5 shadow-sm ring-4 ring-emerald-50">{title_html}<div class="space-y-3">']
    for item in items:
        if isinstance(item, str):
            label = item
            body = ""
            checked = False
        else:
            label = item.get("label", item.get("title", "Item"))
            body = item.get("body", "")
            checked = bool(item.get("checked", False))
        marker = "✓" if checked else ""
        marker_class = "bg-emerald-500 text-white border-emerald-500" if checked else "bg-white text-white border-slate-300"
        body_html = f'<div class="doc-prose mt-1 text-sm text-slate-500">{markdown_to_html(body)}</div>' if body else ""
        parts.append(
            '<div class="flex gap-3 rounded-xl border border-slate-200 bg-slate-50/70 p-3">'
            f'<div class="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded border text-xs font-bold {marker_class}">{marker}</div>'
            f'<div><div class="font-medium text-slate-900">{esc(label)}</div>{body_html}</div>'
            '</div>'
        )
    parts.append('</div></div>')
    return "\n".join(parts)


def render_resources(block):
    items = block.get("items", [])
    title = block.get("title")
    title_html = f'<h3 class="mb-4 text-sm font-bold uppercase tracking-wide text-slate-600">{esc(title)}</h3>' if title else ""
    parts = [f'<div class="rounded-2xl border border-violet-200 bg-white p-5 shadow-sm ring-4 ring-violet-50">{title_html}<div class="grid gap-3 md:grid-cols-2">']
    for index, item in enumerate(items):
        color = accent(index)
        href = safe_href(item.get("href", "#"))
        parts.append(
            f'<a class="block rounded-xl border {color["border"]} {color["soft"]} p-4 transition hover:-translate-y-0.5 hover:shadow-sm" href="{href}">'
            f'<div class="font-semibold {color["text"]}">{esc(item.get("label", item.get("title", "Resource")))}</div>'
            f'<div class="mt-1 text-sm text-slate-600">{esc(item.get("description", ""))}</div>'
            '</a>'
        )
    parts.append('</div></div>')
    return "\n".join(parts)


def render_details(block):
    items = block.get("items", [])
    title = block.get("title")
    title_html = f'<h3 class="mb-4 text-sm font-bold uppercase tracking-wide text-slate-600">{esc(title)}</h3>' if title else ""
    parts = [f'<div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">{title_html}<div class="space-y-3">']
    for item in items:
        parts.append(
            '<details class="group rounded-xl border border-slate-200 bg-slate-50 p-4 open:bg-white">'
            f'<summary class="cursor-pointer select-none font-semibold text-slate-900">{esc(item.get("title", "Details"))}</summary>'
            f'<div class="doc-prose mt-3 text-sm text-slate-600">{markdown_to_html(item.get("body", ""))}</div>'
            '</details>'
        )
    parts.append('</div></div>')
    return "\n".join(parts)


def render_code_block(content, language=""):
    label = f'<span class="text-xs font-semibold uppercase tracking-wide text-slate-400">{esc(language)}</span>' if language else '<span></span>'
    return (
        '<div class="code-wrap" data-code-block>'
        f'<div class="mb-2 flex items-center justify-between gap-3">{label}'
        '<button class="copy-code rounded-lg bg-slate-700 px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-slate-600" type="button">Copy</button>'
        '</div>'
        f'<pre><code>{esc(content)}</code></pre>'
        '</div>'
    )


def render_code(block):
    return render_code_block(block.get("content", ""), block.get("language", ""))


def render_block(block, charts, cloud_diagrams):
    if isinstance(block, str):
        return f'<div class="doc-prose">{markdown_to_html(block)}</div>'
    kind = text(block.get("type", "markdown")).lower()
    if kind == "cards":
        return render_cards(block)
    if kind == "metrics":
        return render_metrics(block)
    if kind == "table":
        return render_table(block)
    if kind == "callout":
        return render_callout(block)
    if kind == "chart":
        return render_chart(block, charts)
    if kind == "steps":
        return render_steps(block)
    if kind == "flow":
        return render_flow(block)
    if kind == "timeline":
        return render_timeline(block)
    if kind in ("cloud", "cloud-diagram", "infrastructure", "infra"):
        return render_cloud(block, cloud_diagrams)
    if kind == "image":
        return render_image(block)
    if kind == "checklist":
        return render_checklist(block)
    if kind == "resources":
        return render_resources(block)
    if kind in ("details", "accordion"):
        return render_details(block)
    if kind == "code":
        return render_code(block)
    return f'<div class="doc-prose">{markdown_to_html(block.get("content", ""))}</div>'


def normalize_paths(input_path, output_arg=None):
    input_path = input_path.resolve()
    if input_path.parent.name == "raw" and input_path.parent.parent.name == "docs":
        source_path = input_path
        docs_dir = input_path.parent.parent
    elif input_path.parent.name == "docs":
        docs_dir = input_path.parent
        source_path = docs_dir / "raw" / input_path.name
    else:
        docs_dir = input_path.parent / "docs"
        source_path = docs_dir / "raw" / input_path.name

    output_path = Path(output_arg).resolve() if output_arg else docs_dir / f"{input_path.stem}.html"
    return source_path, output_path


def normalize_source_file(input_path, source_path):
    source_path.parent.mkdir(parents=True, exist_ok=True)
    if input_path.resolve() == source_path.resolve():
        return source_path
    source_path.write_text(input_path.read_text(encoding="utf-8"), encoding="utf-8")
    input_path.unlink()
    return source_path


def render_doc(doc):
    title = doc.get("title", "Document")
    subtitle = doc.get("subtitle", "")
    summary = doc.get("summary", "")
    audience = doc.get("audience", "")
    badges = doc.get("badges", [])
    actions = doc.get("actions", [])
    sections = doc.get("sections", [])
    charts = []
    cloud_diagrams = []
    used_slugs = set()
    nav = []
    section_html = []

    for section_index, section in enumerate(sections):
        section_title = section.get("title", "Section")
        base_slug = slugify(section_title)
        slug = base_slug
        suffix = 2
        while slug in used_slugs:
            slug = f"{base_slug}-{suffix}"
            suffix += 1
        used_slugs.add(slug)
        nav.append((slug, section_title))
        blocks = section.get("blocks", [])
        intro = section.get("intro")
        color = accent(section_index)
        parts = [f'<section id="{slug}" class="scroll-mt-8 rounded-3xl border {color["border"]} bg-white/90 p-6 shadow-sm ring-4 {color["ring"]}">']
        parts.append('<div class="flex items-start gap-4">')
        parts.append(f'<div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl {color["bar"]} text-sm font-black text-white shadow-sm">{section_index + 1}</div>')
        parts.append('<div>')
        parts.append(f'<h2 class="text-2xl font-black tracking-tight text-slate-950">{esc(section_title)}</h2>')
        if intro:
            parts.append(f'<p class="mt-2 max-w-3xl text-slate-600">{esc(intro)}</p>')
        parts.append('</div></div>')
        parts.append('<div class="mt-6 space-y-5">')
        for block in blocks:
            parts.append(render_block(block, charts, cloud_diagrams))
        parts.append("</div></section>")
        section_html.append("\n".join(parts))

    badge_html = "".join(f'<span class="rounded-full border border-white/20 bg-white/10 px-3 py-1 text-xs font-semibold text-white/90">{esc(badge)}</span>' for badge in badges)
    action_html = "".join(f'<a class="inline-flex items-center rounded-xl bg-white px-3 py-2 text-sm font-semibold text-slate-950 shadow-sm transition hover:bg-blue-50" href="{safe_href(action.get("href", "#"))}">{esc(action.get("label", "Open"))}</a>' for action in actions)
    nav_html = "".join(f'<a class="block rounded-xl px-3 py-2 text-sm font-medium text-slate-300 transition hover:bg-white/10 hover:text-white" href="#{slug}">{esc(label)}</a>' for slug, label in nav)
    audience_html = f'<div class="mt-4 rounded-2xl border border-white/10 bg-white/5 p-3 text-sm text-slate-300"><span class="font-semibold text-white">Audience:</span> {esc(audience)}</div>' if audience else ""
    summary_html = f'<p class="mt-5 max-w-3xl text-lg leading-8 text-slate-600">{esc(summary)}</p>' if summary else ""
    subtitle_html = f'<p class="mt-3 max-w-3xl text-xl text-slate-500">{esc(subtitle)}</p>' if subtitle else ""
    chart_json = json.dumps(charts, ensure_ascii=False).replace("</", "<\\/")
    cloud_json = json.dumps(cloud_diagrams, ensure_ascii=False).replace("</", "<\\/")
    palette_json = json.dumps(PALETTE)

    return f'''<!doctype html>
<html lang="en" class="scroll-smooth">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/cytoscape@3.30.2/dist/cytoscape.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/dagre@0.8.5/dist/dagre.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/cytoscape-dagre@2.5.0/cytoscape-dagre.min.js"></script>
  <style>
    body {{ font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    .doc-prose p {{ margin: 0.65rem 0; line-height: 1.7; }}
    .doc-prose p:first-child {{ margin-top: 0; }}
    .doc-prose p:last-child {{ margin-bottom: 0; }}
    .doc-prose h2, .doc-prose h3, .doc-prose h4 {{ margin: 1rem 0 0.5rem; font-weight: 800; color: #020617; }}
    .doc-prose ul, .doc-prose ol {{ margin: 0.75rem 0; padding-left: 1.25rem; }}
    .doc-prose ul {{ list-style: disc; }}
    .doc-prose ol {{ list-style: decimal; }}
    .doc-prose li {{ margin: 0.35rem 0; }}
    .doc-prose blockquote {{ border-left: 4px solid #60a5fa; color: #475569; padding-left: 1rem; margin: 1rem 0; }}
    .code-wrap {{ border: 1px solid #1e293b; border-radius: 1rem; background: #0f172a; padding: 1rem; box-shadow: 0 1px 2px rgb(15 23 42 / 0.08); }}
    .code-wrap pre {{ overflow-x: auto; border-radius: 0.75rem; background: #020617; color: #e2e8f0; padding: 1rem; font-size: 0.875rem; line-height: 1.6; }}
    .cloud-diagram canvas {{ border-radius: 1rem; }}
    .cloud-diagram:fullscreen {{ height: 100vh !important; border-radius: 0; background: #f8fafc; }}
  </style>
</head>
<body class="bg-gradient-to-br from-slate-50 via-blue-50/60 to-violet-50 text-slate-900">
  <div class="min-h-screen lg:flex">
    <aside class="relative overflow-hidden bg-slate-950 px-6 py-8 text-white lg:sticky lg:top-0 lg:h-screen lg:w-80 lg:shrink-0 lg:overflow-y-auto">
      <div class="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(59,130,246,0.45),transparent_35%),radial-gradient(circle_at_bottom_right,rgba(168,85,247,0.35),transparent_30%)]"></div>
      <div class="relative">
        <div class="flex flex-wrap gap-2">{badge_html}</div>
        <h1 class="mt-6 text-3xl font-black tracking-tight">{esc(title)}</h1>
        <p class="mt-3 text-sm leading-6 text-slate-300">{esc(subtitle or summary)}</p>
        {audience_html}
        <div class="mt-5 flex flex-wrap gap-2">{action_html}</div>
        <nav class="mt-8 space-y-1 border-t border-white/10 pt-5">
          <div class="mb-2 px-3 text-xs font-bold uppercase tracking-[0.2em] text-slate-500">Sections</div>
          {nav_html}
        </nav>
      </div>
    </aside>
    <main class="min-w-0 flex-1 px-5 py-8 lg:px-10 lg:py-12">
      <div class="mx-auto max-w-5xl">
        <header class="mb-8 rounded-3xl border border-white bg-white/80 p-8 shadow-sm backdrop-blur">
          <h2 class="mt-5 text-4xl font-black tracking-tight text-slate-950">{esc(title)}</h2>
          {subtitle_html}
          {summary_html}
        </header>
        <div class="space-y-8">
          {''.join(section_html)}
        </div>
        <footer class="px-2 py-8 text-sm text-slate-500">Generated as lightweight HTML documentation from a reusable JSON source.</footer>
      </div>
    </main>
  </div>
  <script>
    const chartSpecs = {chart_json};
    const cloudDiagrams = {cloud_json};
    const palette = {palette_json};
    document.querySelectorAll('[data-code-block]').forEach((block) => {{
      const button = block.querySelector('.copy-code');
      const code = block.querySelector('code');
      if (!button || !code) return;
      button.addEventListener('click', async () => {{
        try {{
          await navigator.clipboard.writeText(code.innerText);
          const previous = button.innerText;
          button.innerText = 'Copied';
          setTimeout(() => button.innerText = previous, 1200);
        }} catch (error) {{
          button.innerText = 'Select code';
        }}
      }});
    }});
    if (window.cytoscape && window.cytoscapeDagre) {{
      cytoscape.use(cytoscapeDagre);
    }}
    for (const diagram of cloudDiagrams) {{
      const container = document.getElementById(diagram.id);
      if (!container || !window.cytoscape) continue;
      const cy = cytoscape({{
        container,
        elements: diagram.elements,
        layout: {{ name: 'dagre', rankDir: diagram.layout || 'LR', nodeSep: 95, rankSep: 150, padding: 55 }},
        wheelSensitivity: 0.18,
        style: [
          {{ selector: 'node', style: {{
            'shape': 'round-rectangle',
            'background-color': 'data(bg)',
            'border-color': 'data(border)',
            'border-width': 2,
            'label': 'data(displayLabel)',
            'text-valign': 'center',
            'text-halign': 'center',
            'text-wrap': 'wrap',
            'text-max-width': 132,
            'font-size': 13,
            'font-weight': 700,
            'color': 'data(textColor)',
            'width': 146,
            'height': 86,
            'padding': 12,
            'overlay-opacity': 0,
          }} }},
          {{ selector: 'edge', style: {{
            'width': 2.5,
            'line-color': '#38bdf8',
            'target-arrow-color': '#38bdf8',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'label': 'data(label)',
            'font-size': 10,
            'font-weight': 700,
            'color': '#0f766e',
            'text-background-color': '#ffffff',
            'text-background-opacity': 0.9,
            'text-background-padding': 3,
          }} }},
          {{ selector: 'node:selected', style: {{ 'border-width': 4, 'border-color': '#2563eb' }} }},
        ],
      }});
      const fitCloud = () => {{ cy.fit(undefined, 48); cy.center(); }};
      fitCloud();
      const resetButton = document.querySelector(`[data-cloud-target="${{diagram.id}}"].cloud-reset`);
      const fullscreenButton = document.querySelector(`[data-cloud-target="${{diagram.id}}"].cloud-fullscreen`);
      if (resetButton) resetButton.addEventListener('click', fitCloud);
      if (fullscreenButton) fullscreenButton.addEventListener('click', async () => {{
        if (container.requestFullscreen) await container.requestFullscreen();
        setTimeout(() => {{ cy.resize(); fitCloud(); }}, 120);
      }});
      document.addEventListener('fullscreenchange', () => {{ cy.resize(); fitCloud(); }});
    }}
    for (const spec of chartSpecs) {{
      const ctx = document.getElementById(spec.id);
      if (!ctx) continue;
      const datasets = (spec.datasets || []).map((dataset, index) => {{
        const color = palette[index % palette.length];
        const multi = ['pie', 'doughnut', 'polarArea'].includes(spec.type);
        return {{
          ...dataset,
          borderColor: dataset.borderColor || color,
          backgroundColor: dataset.backgroundColor || (multi ? palette : color + '33'),
          tension: dataset.tension ?? 0.35,
          borderWidth: dataset.borderWidth ?? 2
        }};
      }});
      new Chart(ctx, {{
        type: spec.type || 'bar',
        data: {{ labels: spec.labels || [], datasets }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {{ legend: {{ position: 'bottom' }} }},
          scales: ['pie', 'doughnut', 'polarArea', 'radar'].includes(spec.type) ? undefined : {{ y: {{ beginAtZero: true }} }},
          ...(spec.options || {{}})
        }}
      }});
    }}
  </script>
</body>
</html>
'''


def main():
    if len(sys.argv) not in (2, 3):
        print("Usage: build_html_doc.py <docs/raw/doc.json|docs/doc.json> [docs/doc.html]", file=sys.stderr)
        return 2
    input_path = Path(sys.argv[1])
    source_path, output_path = normalize_paths(input_path, sys.argv[2] if len(sys.argv) == 3 else None)
    source_path = normalize_source_file(input_path, source_path)
    doc = json.loads(source_path.read_text(encoding="utf-8"))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_doc(doc), encoding="utf-8")
    print(f"source: {source_path}")
    print(f"html: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

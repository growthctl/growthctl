import html

lines = [
    {"text": "$ cat campaign.yaml", "color": "#d4d4d4", "prompt": True},
    {"text": 'version: "1.0"', "color": "#ce9178"},
    {"text": "campaigns:", "color": "#9cdcfe"},
    {"text": "  - id: summer-sale", "color": "#9cdcfe"},
    {"text": "    name: Summer Sale 2026", "color": "#ce9178"},
    {"text": "    objective: OUTCOME_SALES", "color": "#ce9178"},
    {"text": "    status: ACTIVE", "color": "#ce9178"},
    {"text": "    ad_sets:", "color": "#9cdcfe"},
    {"text": "      - id: us-audience", "color": "#9cdcfe"},
    {"text": "        name: US Audience", "color": "#ce9178"},
    {"text": "        status: ACTIVE", "color": "#ce9178"},
    {"text": "        budget_daily: 5000.00", "color": "#b5cea8"},
    {"text": "        targeting:", "color": "#9cdcfe"},
    {"text": '          locations: ["US"]', "color": "#ce9178"},
    {"text": "", "color": "#d4d4d4"},
    {"text": "$ growthctl plan campaign.yaml", "color": "#d4d4d4", "prompt": True},
    {
        "text": "╭──────────────────────────────────────────────────────────────────────────────╮",
        "color": "#569cd6",
    },
    {
        "text": "│ Running Plan for campaign.yaml                                               │",
        "color": "#569cd6",
    },
    {
        "text": "╰──────────────────────────────────────────────────────────────────────────────╯",
        "color": "#569cd6",
    },
    {
        "text": "+ Create Campaign: Summer Sale 2026 (ID: summer-sale)",
        "color": "#4ec9b0",
    },
    {"text": "  + Create AdSet: US Audience", "color": "#4ec9b0"},
    {"text": "", "color": "#d4d4d4"},
    {"text": "$ growthctl apply campaign.yaml", "color": "#d4d4d4", "prompt": True},
    {
        "text": "╭──────────────────────────────────────────────────────────────────────────────╮",
        "color": "#569cd6",
    },
    {
        "text": "│ Applying Plan for campaign.yaml                                              │",
        "color": "#569cd6",
    },
    {
        "text": "╰──────────────────────────────────────────────────────────────────────────────╯",
        "color": "#569cd6",
    },
    {
        "text": "Are you sure you want to apply these changes to the LIVE ad account? [y/N]: y",
        "color": "#d4d4d4",
    },
    {"text": "Creating Campaign: Summer Sale 2026...", "color": "#d4d4d4"},
    {
        "text": "[Remote] Created campaign: summer-sale with 1 ad sets",
        "color": "#4ec9b0",
    },
    {"text": "Apply Complete!", "color": "#4ec9b0"},
    {"text": "", "color": "#d4d4d4"},
    {"text": "$ ", "color": "#d4d4d4", "prompt": True, "cursor": True},
]

line_height = 20
font_size = 14
padding = 20
header_height = 40
width = 800
height = header_height + (len(lines) * line_height) + padding

svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <style>
    .text {{ font-family: 'Menlo', 'Monaco', 'Courier New', monospace; font-size: {font_size}px; }}
    .cursor {{ animation: blink 1s step-end infinite; }}
    @keyframes blink {{ 50% {{ opacity: 0; }} }}
  </style>
  <rect x="0" y="0" width="{width}" height="{height}" rx="10" ry="10" fill="#1e1e1e" />

  <!-- Window Controls -->
  <circle cx="20" cy="20" r="6" fill="#ff5f56" />
  <circle cx="40" cy="20" r="6" fill="#ffbd2e" />
  <circle cx="60" cy="20" r="6" fill="#27c93f" />

  <g transform="translate({padding}, {header_height + 10})">
"""

for i, line in enumerate(lines):
    y = i * line_height
    text = html.escape(line["text"])
    color = line["color"]

    # Simple prompt styling
    content = (
        f'<text x="0" y="{y}" fill="{color}" class="text" xml:space="preserve">{text}'
    )

    if line.get("cursor"):
        content += '<tspan fill="#d4d4d4" class="cursor">▋</tspan>'

    content += "</text>"
    svg_content += content + "\n"

svg_content += """
  </g>
</svg>"""

with open("docs/website/static/img/terminal-demo.svg", "w") as f:
    f.write(svg_content)

print("SVG generated at docs/website/static/img/terminal-demo.svg")

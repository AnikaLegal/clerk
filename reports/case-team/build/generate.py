"""Build the workflow import from an export of the live workflow.

Every block's code comes from blocks/, by block name. A block the export
lacks is cloned from a similar one, so its settings keep the shape Retool
exported; the connections between blocks are then rebuilt from FLOW below.
Settings that live only in Retool (the Drive, Slides and Sheets blocks, the
findFolder and createFolder functions) are kept as exported.

Usage: generate.py <export.json> <out.json>
"""
import copy
import json
import pathlib
import sys
import uuid

from transit import decode, encode

HERE = pathlib.Path(__file__).resolve().parent.parent
BLOCKS = HERE / "blocks"

src, out = sys.argv[1:3]
export = json.load(open(src))
template = decode(export["templateData"])
plugins = template["v"]["v"]["plugins"]["v"]  # flat [name, record, name, record, ...]
blocks = {b["pluginId"]: b for b in export["blockData"]}

# Blocks a missing block is cloned from.
CLONE_FROM = {
    "readPrevious": "readPrevious",
    "saveSnapshot": "readPrevious",
    "saveSnapshotOnly": "readPrevious",
    "slide4": "slide5",
    "slide6": "slide5",
    "slide7": "slide5",
    "slide8": "slide5",
    "slide9": "slide5",
    "snapshotDone": "existingLink",
    "snapshotSaved": "existingLink",
    "isSnapshot": "alreadyMade",
}

# Run order. Each path is a chain; a path that starts at a branch names the
# branch and which way it leaves it (0 = condition true, 1 = else).
MAIN = ["startTrigger", "whoami", "setup", "readPrevious", "slide4", "slide5", "slide6", "slide7", "slide8", "slide9", "figures", "isSnapshot"]
SNAPSHOT_PATH = ("isSnapshot", 0, ["saveSnapshotOnly", "snapshotDone"])
REPORT_PATH = ("isSnapshot", 1, ["folders", "findExisting", "alreadyMade"])
EXISTS_PATH = ("alreadyMade", 0, ["existingLink"])
MAKE_PATH = ("alreadyMade", 1, [
    "saveSnapshot", "snapshotSaved", "copyChartSheet", "writeChart", "writeChart6", "writeChart7",
    "copyDeck", "fillText", "chartRequests", "fillCharts",
])
BRANCHES = {
    "isSnapshot": 'setup.data.mode === "snapshot"',
    "alreadyMade": "findExisting.data.files.length > 0 && setup.data.force !== true",
}


def record(name):
    return plugins[plugins.index(name) + 1]


def settings(name):
    return record(name)["v"]["v"]["template"]["v"]


def set_query(name, text):
    t = settings(name)
    t[t.index("query") + 1] = text


cloned = set()


def ensure(name):
    if name in blocks:
        return
    cloned.add(name)
    like = CLONE_FROM[name]
    rec = copy.deepcopy(record(like))
    rec["v"]["v"]["id"] = name
    plugins.extend([name, rec])
    block = copy.deepcopy(blocks[like])
    block["pluginId"] = name
    block["uuid"] = str(uuid.uuid4())
    blocks[name] = block


def query_text(path):
    text = path.read_text()
    # Clerk queries take :month so they also run in psql.
    return text.replace(":month", "{{ setup.data.month }}") if path.suffix == ".sql" else text


for name in CLONE_FROM:
    ensure(name)
for path in sorted(BLOCKS.iterdir()):
    assert path.stem in blocks, f"no block {path.stem} in the export"
    set_query(path.stem, query_text(path))


def set_branch(name, statement):
    block = blocks[name]
    ports = [str(uuid.uuid4()), str(uuid.uuid4())] if name not in BRANCH_PORTS else BRANCH_PORTS[name]
    block["outgoingPorts"] = [{"id": p, "name": str(i), "type": "conditional"} for i, p in enumerate(ports)]
    block["options"]["conditions"] = [
        {"id": str(uuid.uuid4()), "type": "if", "statement": statement, "outgoingPortId": ports[0]},
        {"id": str(uuid.uuid4()), "type": "else", "statement": "", "outgoingPortId": ports[1]},
    ]
    set_query(name, f"if ({statement}) {{\n  executePathAtMostOnce('0')\n}}\nelse {{ executePathAtMostOnce('1') }}")
    return ports


# Keep a branch's existing port IDs so nothing outside FLOW loses its link.
BRANCH_PORTS = {
    name: [p["id"] for p in sorted(blocks[name]["outgoingPorts"], key=lambda p: p["name"])]
    for name in BRANCHES
    if blocks[name].get("outgoingPorts") and name not in cloned
}
ports = {name: set_branch(name, statement) for name, statement in BRANCHES.items()}


def chain(names):
    for before, after in zip(names, names[1:]):
        blocks[after]["incomingOnSuccessEdges"] = [blocks[before]["uuid"]]
        blocks[after].pop("incomingPorts", None)


chain(MAIN)
blocks[MAIN[0]]["incomingOnSuccessEdges"] = []
for branch, way, names in (SNAPSHOT_PATH, REPORT_PATH, EXISTS_PATH, MAKE_PATH):
    chain(names)
    blocks[names[0]]["incomingOnSuccessEdges"] = []
    blocks[names[0]]["incomingPorts"] = [{"portId": ports[branch][way], "blockId": blocks[branch]["uuid"]}]

# Layout: the main row, then the report path; the snapshot and "already
# exists" paths sit below where they leave their branch.
STEP, ROW = 512, 304
x = 48
for name in MAIN + REPORT_PATH[2] + MAKE_PATH[2]:
    blocks[name]["left"], blocks[name]["top"] = x, 48
    x += STEP
for branch, _, names in (SNAPSHOT_PATH, EXISTS_PATH):
    for i, name in enumerate(names):
        blocks[name]["left"] = blocks[branch]["left"] + (i + 1) * STEP
        blocks[name]["top"] = 48 + ROW

order = MAIN + SNAPSHOT_PATH[2] + REPORT_PATH[2] + EXISTS_PATH[2] + MAKE_PATH[2]
functions = [b["pluginId"] for b in export["blockData"] if b["blockType"] == "function"]
unplaced = set(blocks) - set(order) - set(functions)
assert not unplaced, f"blocks not in the flow: {sorted(unplaced)}"
export["blockData"] = [blocks[name] for name in order + functions]
export["templateData"] = encode(template)
export["name"] = "Case Team report"
export["triggerWebhooks"][0]["exampleInputJSON"] = '{"month": "2026-02-01", "mode": "report"}'
json.dump(export, open(out, "w"))

# Checks: every block has its settings, every edge points at a block, and
# the encoding reads back.
names = plugins[0::2]
assert all(b["pluginId"] in names for b in export["blockData"])
uuids = {b["uuid"] for b in export["blockData"]}
for b in export["blockData"]:
    assert all(e in uuids for e in b.get("incomingOnSuccessEdges", [])), b["pluginId"]
    assert all(p["blockId"] in uuids for p in b.get("incomingPorts", [])), b["pluginId"]
assert decode(export["templateData"]) == template
print(" > ".join(MAIN))
for branch, way, names in (SNAPSHOT_PATH, REPORT_PATH, EXISTS_PATH, MAKE_PATH):
    print(f"  {branch} {'true' if way == 0 else 'else'}: " + " > ".join(names))

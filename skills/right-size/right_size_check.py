#!/usr/bin/env python3
"""Right-size check: list agent jobs that ran on a bigger model than their type needs.

It reads the Claude Code session transcripts on this computer
(~/.claude/projects/<project>/<session>/subagents/). It uses no model, sends
nothing anywhere and changes nothing. It prints numbers and the short label of
each job, never the text of a prompt. Use --no-labels before you share the output.

Usage:
  python3 right_size_check.py                 # the last 7 days, all projects
  python3 right_size_check.py --days 30
  python3 right_size_check.py --project my-app --no-labels
  python3 right_size_check.py --rules my-rules.json --all

Python 3.8 or newer, standard library only.
"""
import argparse
import glob
import json
import os
import statistics
import sys
import time
from datetime import datetime

# The rules. To change them, write only the parts you change into a JSON file and pass
# --rules. Types in your file are added to these; other keys replace these.
DEFAULT_RULES = {
    # Model tiers from small to large. Each name is looked for inside the model id.
    "tiers": ["haiku", "sonnet", "opus", "fable"],
    # The highest tier a job type may use without a reason in its brief.
    "default_max": "sonnet",
    "types": {
        "Explore": {"max": "haiku"},
        "scout": {"max": "haiku"},
        "builder": {"max": "sonnet"},
        "clerk": {"max": "sonnet"},
        "workflow-checker": {"max": "sonnet"},
        "final-reviewer": {"min": "opus", "max": "opus"},
        "design-agent": {"max": "fable"},
    },
    # A brief that holds one of these lines may go up to "with_reason_max".
    "reason_markers": ["model reason:"],
    "with_reason_max": "opus",
}


def load_rules(path):
    rules = json.loads(json.dumps(DEFAULT_RULES))
    if path:
        try:
            with open(path, encoding="utf-8") as fh:
                mine = json.load(fh)
        except (OSError, ValueError) as err:
            sys.exit(f"Cannot read the rules file {path}: {err}")
        if not isinstance(mine, dict) or not isinstance(mine.get("types", {}), dict):
            sys.exit("The rules file must be a JSON object, and its 'types' an object.")
        # Your types are added to the defaults; a type you write replaces that type's whole entry.
        rules["types"].update(mine.pop("types", {}))
        rules.update(mine)
    # Every tier name in the rules must be one of the tiers.
    names = [rules["default_max"], rules["with_reason_max"]]
    for rule in rules["types"].values():
        names += [rule[k] for k in ("min", "max") if k in rule]
    unknown = sorted({n for n in names if n not in rules["tiers"]})
    if unknown:
        sys.exit(f"These names are not in 'tiers' {rules['tiers']}: {', '.join(unknown)}")
    return rules


def tier_of(model, tiers):
    """Index of the tier whose name is in the model id, or None."""
    model = (model or "").lower()
    for i, name in enumerate(tiers):
        if name in model:
            return i
    return None


def read_job(path):
    """Read one subagent transcript. Returns a dict of numbers, or None."""
    meta_path = path[: -len(".jsonl")] + ".meta.json"
    if not os.path.exists(meta_path):
        return None
    try:
        with open(meta_path, encoding="utf-8") as fh:
            meta = json.load(fh)
    except (OSError, ValueError):
        return None
    job = {
        "type": meta.get("agentType") or "unknown",
        "label": meta.get("description") or "",
        "asked": meta.get("model"),  # None: no model in the call
        "model": None,
        "start": None,
        "cwd": None,
        "startup": None,  # context of the first reply: what the job read before it did anything
        "peak": 0,  # the largest context of any reply: how big the job grew
        "turns": 0,
        "has_reason": False,
    }
    seen, prompt_read = set(), False
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if job["start"] is None and row.get("timestamp"):
                job["start"] = row["timestamp"]
            if job["cwd"] is None and row.get("cwd"):
                job["cwd"] = row["cwd"]
            msg = row.get("message")
            if not isinstance(msg, dict):
                continue
            if not prompt_read and msg.get("role") == "user":
                # The brief is the first user message. Only a yes/no is kept:
                # the prompt text is never stored or printed.
                prompt_read = True
                text = msg.get("content")
                if isinstance(text, list):
                    text = "\n".join(b.get("text", "") for b in text if isinstance(b, dict))
                lines = [l.strip().lower() for l in str(text or "").splitlines()]
                job["has_reason"] = any(l.startswith(m) for l in lines for m in RULES["reason_markers"])
            if msg.get("role") != "assistant":
                continue
            # One reply can be split over several lines with the same id and usage.
            mid = msg.get("id")
            if mid is not None:
                if mid in seen:
                    continue
                seen.add(mid)
            model = msg.get("model") or ""
            if job["model"] is None and model and not model.startswith("<"):
                job["model"] = model
            u = msg.get("usage") or {}
            read_in = (u.get("input_tokens") or 0) + (u.get("cache_creation_input_tokens") or 0) \
                + (u.get("cache_read_input_tokens") or 0)
            if not read_in:
                continue
            job["turns"] += 1
            if job["startup"] is None:
                job["startup"] = read_in
            job["peak"] = max(job["peak"], read_in)
    return job


def agent_file_models(cwds):
    """Model fixed in each agent file (~/.claude/agents and <project>/.claude/agents)."""
    found = {}
    folders = [os.path.expanduser("~/.claude/agents")] + [os.path.join(c, ".claude", "agents") for c in cwds]
    for folder in folders:
        for f in glob.glob(os.path.join(folder, "*.md")):
            name, model = os.path.basename(f)[:-3], None
            try:
                with open(f, encoding="utf-8") as fh:
                    lines = fh.read().split("\n")
            except OSError:
                continue
            if not lines or lines[0].strip() != "---":
                continue
            for line in lines[1:]:
                if line.strip() == "---":
                    break
                key, _, value = line.partition(":")
                if key.strip() == "name":
                    name = value.strip().strip("'\"")
                elif key.strip() == "model":
                    model = value.strip().strip("'\"")
            if model and model != "inherit":
                found.setdefault(name, model)
    return found


def judge(job, rules):
    tiers = rules["tiers"]
    used = tier_of(job["model"], tiers)
    if used is None:
        return "other"
    rule = rules["types"].get(job["type"], {})
    # A type with no rule may use the model its own agent file fixes: that choice is written down.
    plain_max = tier_of(rule.get("max") or FILE_MODELS.get(job["type"]) or rules["default_max"], tiers)
    if plain_max is None:
        plain_max = tier_of(rules["default_max"], tiers)
    top = plain_max
    if job["has_reason"]:
        top = max(top, tier_of(rules["with_reason_max"], tiers))
    floor = tier_of(rule["min"], tiers) if rule.get("min") else None
    if used > top:
        return "over"
    if floor is not None and used < floor:
        return "under"
    if used > plain_max:
        return "reason"
    return "ok"


def short(n):
    if n is None:
        return "-"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.0f}k"
    return str(n)


def local_time(ts):
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone().strftime("%d %b %H:%M")
    except (AttributeError, ValueError):
        return "?"


def model_name(model):
    i = tier_of(model, RULES["tiers"])
    return RULES["tiers"][i] if i is not None else (model or "?")


def main():
    global RULES
    ap = argparse.ArgumentParser(description="List agent jobs that ran on a bigger model than their type needs.")
    ap.add_argument("--days", type=float, default=7, help="how many days back to read (default 7)")
    ap.add_argument("--project", default="", help="only project folders whose name contains this text")
    ap.add_argument("--projects-dir", default=os.path.expanduser("~/.claude/projects"))
    ap.add_argument("--rules", help="a JSON file that replaces parts of the default rules")
    ap.add_argument("--no-labels", action="store_true", help="hide the job labels (do this before sharing)")
    ap.add_argument("--all", action="store_true", help="list every job, not only the flagged ones")
    ap.add_argument("--limit", type=int, default=30, help="most lines per list (default 30)")
    args = ap.parse_args()
    RULES = load_rules(args.rules)

    cutoff = time.time() - args.days * 86400
    files = [f for f in glob.glob(os.path.join(args.projects_dir, "*", "*", "subagents", "*.jsonl"))
             if args.project in f.split(os.sep)[-4] and os.path.getmtime(f) >= cutoff]
    jobs, no_meta = [], 0
    for f in files:
        job = read_job(f)
        if job is None:
            no_meta += 1
            continue
        try:
            started = datetime.fromisoformat(job["start"].replace("Z", "+00:00")).timestamp()
        except (AttributeError, ValueError):
            started = os.path.getmtime(f)
        if started < cutoff:
            continue
        jobs.append(job)
    FILE_MODELS.update(agent_file_models({j["cwd"] for j in jobs if j["cwd"]}))
    for job in jobs:
        job["verdict"] = judge(job, RULES)
    jobs.sort(key=lambda j: j["start"] or "")

    print(f"Right-size check: the last {args.days:g} days, {len(jobs)} agent jobs")
    if no_meta:
        print(f"({no_meta} older transcripts have no job file and were not checked)")

    def show(title, verdict, why):
        rows = [j for j in jobs if j["verdict"] == verdict]
        print(f"\n{title}: {len(rows)} jobs, {sum(j['turns'] for j in rows)} replies")
        if rows and why:
            print(f"  {why}")
            print(f"  {'started':<12}  {'job type':<22} {'ran on':<7} {'model in the call':<22} {'replies':>7} {'peak':>6}")
        for j in rows[: args.limit]:
            asked = j["asked"] or "none"
            label = "" if args.no_labels else f'  "{j["label"][:48]}"'
            print(f"  {local_time(j['start']):<12}  {j['type'][:22]:<22} {model_name(j['model']):<7}"
                  f" {asked:<22} {j['turns']:>7} {short(j['peak']):>6}{label}")
        if len(rows) > args.limit:
            print(f"  ... and {len(rows) - args.limit} more (use --limit)")

    show("Over-sized", "over", "Above the highest model for its type. A 'Model reason:' line in the brief allows up to "
         f"{RULES['with_reason_max']}; higher only where the type's own rule allows it.")
    show("Under-sized", "under", "Below the lowest model for its type (for example a final review below the top tier).")
    show("Above the type's maximum, with a reason", "reason", "Allowed. If this list grows every week, the reason is a habit.")
    if args.all:
        show("Right-sized", "ok", "")
    other = [j for j in jobs if j["verdict"] == "other"]
    if other:
        names = sorted({j["model"] or "no model found" for j in other})
        print(f"\nNot checked: {len(other)} jobs on a model that matches no tier ({', '.join(names)}).")
        print("  Add its name to 'tiers' in a rules file.")

    print("\nBy job type (context in tokens; start-up = before the job did anything, peak = its largest)")
    print(f"  {'job type':<22} {'jobs':>5}  {'ran on':<34} {'start-up':>8} {'peak':>6}")
    by_type = {}
    for j in jobs:
        by_type.setdefault(j["type"], []).append(j)
    for t, rows in sorted(by_type.items(), key=lambda kv: -len(kv[1])):
        models = {}
        for j in rows:
            m = model_name(j["model"])
            models[m] = models.get(m, 0) + 1
        mix = ", ".join(f"{m} {c}" for m, c in sorted(models.items(), key=lambda kv: -kv[1]))
        starts = [j["startup"] for j in rows if j["startup"]]
        peaks = [j["peak"] for j in rows if j["peak"]]
        start_med = short(int(statistics.median(starts))) if starts else "-"
        peak_med = short(int(statistics.median(peaks))) if peaks else "-"
        print(f"  {t[:22]:<22} {len(rows):>5}  {mix:<34} {start_med:>8} {peak_med:>6}")
    print("  (median per job type)")
    return 0


RULES = DEFAULT_RULES
FILE_MODELS = {}

if __name__ == "__main__":
    sys.exit(main())

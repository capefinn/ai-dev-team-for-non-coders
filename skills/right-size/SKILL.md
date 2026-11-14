---
name: right-size
description: Give every agent job the smallest model and the smallest start-up context that do it well, and check afterwards that no job ran on a bigger model than it needed. Use it before every Agent call (builder, reviewer, clerk, look-up, design job), when someone asks "which model should this run on?", "why did this cost so much?" or "are we using the top model too much?", and once a week to run the checker on the session transcripts. Works on its own or with the orchestrator skills in this kit.
---

# Right-size: the right model for each job

**The idea:** use a cheaper model where another step checks the work. Use the strongest model for the step that does the checking. Never use a bigger model than the job needs.

This is not "use cheaper models everywhere". Some jobs must stay on the strongest model, because a mistake there costs more than a cheaper model saves. Right-sizing goes in both directions.

**Words used here** (all from Claude Code):

- **Agent job:** one task that a chat hands to a helper with the Agent tool. The helper works in its own session and reports back.
- **Brief:** the message that starts an agent job: what to do, which files, and what "done" means.
- **Tier:** the size of a model: small, mid, top or deepest. Bigger models cost more per token.
- **Agent file:** a short file in `.claude/agents/` that defines one kind of helper: its name, its model, its tools and its instructions.
- **General agent:** the built-in helper that has no agent file of its own. It loads all the instruction files and every tool.
- **Start-up context:** everything a helper reads before it does any work, counted in tokens (small pieces of text; about four characters each).
- **Look-up:** a job that only needs to find a fact, for example "which file sets the price?"

## 1. Which model for which job

The Agent tool takes a `model` value: `haiku` (small), `sonnet` (mid), `opus` (top) and, if your Claude plan offers it, `fable` (the deepest reasoning model).

| Job | Model | Why this size |
|---|---|---|
| Look-ups: a fact in files, pull requests or logs; file searches; "where is X?" | `haiku` | The answer is a fact that you can check in one step. A bigger model reads the same files at a higher price. |
| Building one task, writing its tests, fixing a review finding; ticket cards, comments, read-only checks; the weekly workflow check | `sonnet` (the default) | The work is reviewed afterwards, and the tests run on it. |
| The final review of every change before it merges. Rarely, with a `Model reason:` line: writing security or backend code that the mid model got wrong | `opus` | The review is the last check before the product changes. It must find what the builder missed. |
| Re-planning a task after two failed reviews; a change to a locked data contract; a hard money or security design | `fable` (or `opus` if your plan has no `fable`) | It plans and writes a design note with options and a recommendation. It writes no code. A builder on `sonnet` builds from the note. |

The rules:

1. **Write `model` in every Agent call.** A job with no `model` gets the model from its agent file. A general agent has no agent file. So, without `model`, it runs on the same model as the chat that started it, and that chat usually runs on the top model. Cost can grow this way, and nobody chose it. Built-in helpers count too: a file-search helper started without a model can run on the top model.
2. **`sonnet` is the default.** Use `haiku` for pure look-ups. A job may go above the model in its own row only with a reason in the brief, on its own line: `Model reason: <why the model in its row is not enough>`. Without a reason, do not go up. The checker in section 5 looks for this line.
3. **The deepest model only plans.** It writes a design note and no code. Give it a read-only tool list (`Read, Grep, Glob, Bash`), one job at a time, and the problem, the earlier attempts and the review comments. Never use it for routine builds.
4. **Reviews never go below the top model.** The final review stays on `opus`, in a fresh session that did not write the code. A cheaper review removes the check that keeps the cheaper builders safe.
5. **At most about 6 builders at the same time.** Queue the rest. More builders at once cause more merge conflicts and more re-reviews, and those cost more than waiting.

## 2. Lean agents: cut the start-up context too

The model's price is one part of the cost. The other part is what each job reads before it starts: the instruction files, the memory index, the descriptions of skills and agents, and the tool lists of connected services. A general agent reads all of it.

- **Give each kind of job that comes back often its own agent file** with `model`, a short `tools:` list (only what the job needs) and, for a helper that needs none of the project's instruction files, `omitClaudeMd: true` (it then starts without the CLAUDE.md files, the project's always-loaded instructions). The brief then carries the few rules it needs.
- **Measured in our setup:** a general agent used as a builder read about 96,000 tokens before it started work. The lean builder (its own agent file with a short tool list) did a whole small job, updating a branch and fixing one conflict in 20 tool calls, in about 52,000 tokens.
- **Check it:** the first reply of a job shows its start-up context. The checker prints the median per job type.

An example agent file:

```markdown
---
name: clerk
description: Ticket comments, board updates, look-ups and read-only checks. Never merges, builds or messages people.
model: sonnet
omitClaudeMd: true
tools: Read, Grep, Glob, Bash
---
Do exactly the steps in the brief. Report in at most 8 lines, in plain words.
```

## 3. Keep the main chat free

The chat that the human talks to usually runs on the top model. Every step that it does itself runs on the most expensive model, and the human waits while it works.

- **Anything that needs more than about two tool calls goes to a background agent** on the right model. The main chat keeps the decisions, the order of the work and the conversation.
- **Other chats write their status into a file** and do not message the main chat. They message it only when something is ready to merge or something is broken.
- **Measured in our setup, on one day before this rule:** the main chat took about 550 steps itself, and it was interrupted about 200 times by messages: helper notices, messages from other chats and automatic wake-ups.

## 4. Before every Agent call

1. What kind of job is it? Pick the row in section 1.
2. Is there an agent file for this kind of job? Use it, not the general agent.
3. Write `model` in the call.
4. Above the model in its row? Write the `Model reason:` line in the brief.
5. Give the exact files, the finding and what "done" means. Never "explore the repository".
6. A follow-up for a helper that ended more than about 4 minutes ago: start a fresh lean helper with the branch, the pull request and the exact comment. Do not resume the old helper (send it a new message). The prompt cache (a short-term store of text the model has just read) keeps a helper's history cheap to read for about 5 minutes. After that, a resumed helper must read its whole old conversation again at the normal price.

## 5. Check it once a week

`right_size_check.py`, next to this file, reads the Claude Code transcripts on this computer (`~/.claude/projects/`) and lists the jobs that ran on a bigger model than their type needs. It uses no model, sends nothing anywhere and changes nothing. It needs Python 3.8 or newer and nothing else.

```bash
python3 ~/.claude/skills/right-size/right_size_check.py
```

```bash
python3 ~/.claude/skills/right-size/right_size_check.py --days 30 --project my-app
```

What it prints:

- **Over-sized:** jobs above the highest model for their type, without a `Model reason:` line. The column "model in the call" says `none` when the job got its model from somewhere else (its agent file or the chat that started it).
- **Under-sized:** jobs below the lowest model for their type, for example a final review below the top model.
- **Above the maximum, with a reason:** allowed. If this list grows every week, the reason has become a habit.
- **Not checked:** jobs on a model whose name matches no tier. Add the name to `tiers` in a rules file (see below).
- **By job type:** how many jobs, which models they ran on, and the median start-up context and peak context.

The rules it uses:

```json
{
  "tiers": ["haiku", "sonnet", "opus", "fable"],
  "default_max": "sonnet",
  "types": {
    "Explore": {"max": "haiku"},
    "scout": {"max": "haiku"},
    "builder": {"max": "sonnet"},
    "clerk": {"max": "sonnet"},
    "workflow-checker": {"max": "sonnet"},
    "final-reviewer": {"min": "opus", "max": "opus"},
    "design-agent": {"max": "fable"}
  },
  "reason_markers": ["model reason:"],
  "with_reason_max": "opus"
}
```

- **To change them,** write only the parts you change into a JSON file and pass `--rules my-rules.json`. The types in your file are added to these; a type you write replaces that type's whole entry. Any other key you write replaces the default.
- **A type with no `max` here** may use the model that its own agent file fixes, because that choice is written down. If its agent file fixes no model, it may use up to `default_max`.
- **The checker knows a job's type, not its purpose.** A look-up started as a general agent is checked against the general limit (`sonnet`). To hold look-ups to `haiku`, give them their own agent file (for example `scout`).
- **A reason allows a job to go up to `opus`** (`with_reason_max`), not higher. Only a type whose own rule allows it, such as `design-agent`, may use `fable`.
- **A reason counts only on its own line** that starts with `Model reason:`. A brief that only mentions the rule in a sentence does not count.

**What it prints, and what it does not.** It prints the job type, the model names and the short label of each job, so that you can see which job it was. Labels and agent type names can hold names: add `--no-labels` before you share the output (the types are still printed). It never prints the text of a prompt; it only checks whether the `Model reason:` line is there.

**It depends on Claude Code's own files.** It reads each helper's transcript and the small job file next to it (`<session>/subagents/agent-<id>.jsonl` and `.meta.json`). These are not a documented interface, and a new Claude Code version can change them. Older transcripts have no job file and are skipped; the checker says how many.

**What to do with the result.** A flagged job needs a closer look; it is not proof of a mistake. One over-sized job is a single mistake. If the same job type is over-sized two weeks in a row, an agent file is missing, or the process that starts these jobs does not write `model`: fix that process. After you move a job type down to a smaller model, watch the review rounds per merged change for two weeks. If they go up, go back to the bigger model.

## What this skill does not do

- It does not count money: prices change and plans differ. It counts jobs, models and context sizes.
- It reads only the transcripts on this computer.
- It does not decide for the human. A model rule that changes what a whole team uses is the owner's decision.

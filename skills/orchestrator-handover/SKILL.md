---
name: orchestrator-handover
description: Close the orchestrator's chat. Stops running builders safely, folds the day's notes into a short state file that the next /orchestrator reads, updates the board, and sends the owner the one daily message. Use when the owner types /orchestrator-handover or says "close the chat" or "write the handover".
---

# /orchestrator-handover — close the chat

Goal: the next orchestrator chat can start in two minutes from one short file, and nothing that is in progress is lost when this chat closes.

One orchestrator chat can keep running across days. It then writes a **checkpoint** once a day instead (see `orchestrator`, "Notes and checkpoints"). A checkpoint is step 3 alone: fold the notes and write the file, and keep working in the same chat. It does not park builders, rename the chat or start anything. This full routine is only for closing the chat. Do not run it for any other reason.

## 1. Stop the builders safely

- Get the owner's local time: `TZ=<owner's time zone> date`.
- For every builder or reviewer still running: if it will finish within about 10 minutes, wait for it. Otherwise send it this message: "Commit and push your work in progress to your branch now, add a dated comment on the ticket saying exactly what is done and what is left, then stop." Wait for each reply.
- Run your park check: the work in every builder folder of the last 24 hours is committed and pushed. A folder with work that exists only on this computer is not safe: ask its owner agent to push it, then check again.
- Nothing merges during the handover unless it was already approved and the gate passes.

## 2. Check the live state

- Run your status command for the open pull requests.
- Note what is switched on or off in production only if it changed today (verify it, do not guess).

## 3. Write the handover

1. Fold the notes. During the day the orchestrator writes running notes to `~/.claude/orchestrator/notes/handover-notes-<date>.md`, one file per day. Read today's file and any older file that is still outside `notes/archive/`. Then: (a) each lasting lesson or hard rule in them goes, as one line, to the playbook; (b) the state goes into HANDOVER.md; (c) every folded file moves to `notes/archive/`. Never delete a file.
2. Move the current `~/.claude/orchestrator/HANDOVER.md` to `~/.claude/orchestrator/handovers/<YYYY-MM-DD>.md` (the date of the file being replaced). If that name already exists, add `-HHMM` (the local time) to the name.
3. Write a new `~/.claude/orchestrator/HANDOVER.md` from the template `~/.claude/orchestrator/handover-template.md`: **at most 70 lines, current state only** (no history, no story of the day). It has:
   - `Written:` weekday, date and local time; `Old chat:` this chat's session id (leave it out at a checkpoint); and `Notes folded:` the names of the notes files you folded;
   - **Restart list**: every helper that was still working, with its branch and what is left (tomorrow's chat cannot resume them);
   - **Open pull requests**: one line each with number, ticket, head (7 characters), review state, what it waits for, and the merge order if stacked;
   - **Unfinished builders**: ticket, branch, what is left;
   - **Production now**: only the lines the next orchestrator needs to act safely (switches, caps, versions), with the values needed to roll back;
   - **Waiting on the owner**: one line each, with its to-do card key; only questions the owner has not answered;
   - **Scheduled checks**: date, local time, what to check;
   - **Only this chat knows**: promises and facts that are written nowhere else;
   - **Next up**: the top 5 tickets in order, with why.
4. Lasting lessons from today that are not in the notes (a mistake not to repeat, a new procedure): add or tighten one line in `~/.claude/orchestrator/playbook.md`. Keep that file short, and remove lines that no longer apply.

## 4. Tidy up

- Remove worktrees whose pull request has merged. Never remove one whose pull request is still open.
- Board: every ticket touched today has the right status and a dated comment.
- The owner's to-do list: one card per open question (check the card key first, never a duplicate). Close every card the owner answered today. No umbrella cards.
- Rename this chat to `Orchestrator — closed <date>`, so the next `/orchestrator` is the only chat called "Orchestrator". Do not archive it yet: the next chat archives it after reading the `Old chat:` line. After the rename, merge nothing more.

## 5. The daily message

One message to the owner, at most 6 lines, in plain words:

- what was merged and released today (verified);
- what is still in progress;
- anything new that needs the owner (A/B with your recommendation; the card exists);
- tomorrow's first item.

End with: "Handover written. You can close this chat. Start the next chat with /orchestrator."

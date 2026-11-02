---
name: orchestrator-relay
description: Hand the orchestrator's work over to a fresh orchestrator chat in the middle of the day, without losing state. Use only when the owner asks (for example "relay" or "hand over to a new orchestrator chat"). Waits for a quiet moment (no helpers running, all work pushed), writes the handover, starts the new chat, and retires the old one.
---

# /orchestrator-relay — hand over to a fresh orchestrator chat

> **Hard rule: only when the owner asks.** Never because of a context figure, a long chat or the clock. We tried an automatic handover and rolled it back (lesson 11 in the guide). The app compresses long chats by itself.

Why the owner may ask: a long chat re-sends its whole history with every message, so it costs more and answers more slowly. A new chat starts with an empty history. Nothing is lost, because everything the next chat needs is written to one file first. The one thing a handover cannot carry is a helper that is still working: the relay waits for it, or saves its work to GitHub and restarts it in the new chat.

This routine is the end-of-day handover (`orchestrator-handover`, steps 1 to 3) plus two more things: starting the new chat, and retiring the old one. At the end of the day the owner starts tomorrow's chat by hand; here this chat starts it.

## 1. Wait for a quiet moment

Both must hold before you start the new chat:

1. **No helper is running.** List the running sessions (a feature of the Claude desktop app; without it, check by hand). Wait for any helper that will finish within about 10 minutes. Park the rest: send each one "Commit and push your work in progress to your branch now, add a dated comment on the ticket saying exactly what is done and what is left, then stop." Wait for each reply. A helper that does not answer goes in the handover as "did not answer".
2. **Everything is on GitHub.** Run your park check: the work in every builder folder of the last 24 hours is committed and pushed. A folder with work only on this computer is not safe: ask its agent to push it, then check again.

Nothing merges during a relay unless it was already approved and the gate passes.

## 2. Write the handover

Follow `orchestrator-handover` steps 1 to 3 (move the old `HANDOVER.md` into `handovers/`; the new one has at most 70 lines of current state), with these differences:

- First lines: `Written:` with the weekday, date and local time, and the word "relay"; `Old chat:` with this chat's id and its new title.
- **Restart list:** one line for every helper that was running or did not answer: its role, the ticket or pull request, the branch and folder, what is left, and "start a fresh builder on that branch; read `git status` and the diff first". The old chat's helpers cannot be resumed.
- **Only this chat knows:** anything the owner said, decided or was promised in this chat that is not yet on a ticket, in the playbook or on a card, and every wait still in progress ("the clerk waits for CI on pull request <N>, then merges; the next command is …"). Write the exact next command. Handovers lose work in this block: do not skip it.
- **Waiting on the owner:** card keys only. A question without a card gets one first.
- Write the handover once. Do not edit it afterwards.

## 3. Hand over, in this order

1. Rename this chat to `Orchestrator (old, <HH:MM>)`, in the owner's local time. Only one chat may ever be titled exactly `Orchestrator`.
2. Start a new chat with a fresh context, titled `Orchestrator`, on the strongest model (a feature of the Claude desktop app). The start message: "/orchestrator — relay from the previous orchestrator chat, now titled `<old title>`. Read the handover first. Its Restart list names every helper to start again, because the old chat's helpers cannot be resumed. If the orchestrator skill did not start, run it now."
3. Check that the new chat is running. Look again after about 30 seconds. If it is not running after 90 seconds, see "If the new chat does not start".
4. Detach the new chat from this one and pin it. A chat started from another chat stays attached to it, and archiving the old chat would archive the new one as well.
5. Tell the owner in at most 4 plain lines: you handed over, the new chat is pinned, this chat is archived and not deleted (the archive brings it back), and what the new chat will check first.
6. Last, unpin this chat (a pinned chat cannot be archived) and archive it, with a short reason. The conversation ends with this step, so everything else comes first. If the archive is refused, leave the chat titled `Orchestrator (old, <HH:MM>)`: the new chat archives it after it reads the `Old chat:` line. Never delete the old chat.

## If the new chat does not start

- **Not running after 90 seconds:** rename this chat back to `Orchestrator`, say in two lines what happened, do not archive, and try at most once more.
- **The app refuses to start a chat** (for example when the owner is away from the computer): leave this chat titled `Orchestrator (old, <HH:MM>)`, merge nothing more, and send one notification: "Handover written. Open a new chat and type /orchestrator." The new chat reads the handover and archives this one.
- **The new chat is already getting full soon after it starts:** the handover or the start-up reading is too big. Say so. Do not hand over again.

## What a relay cannot do (say so plainly if asked)

- Start itself. It runs only when the owner asks.
- Continue a helper that is still working. It waits for the helper, or saves its work and restarts it from its branch.
- Carry anything that exists only in the old chat's memory. The handover file is the whole transfer.

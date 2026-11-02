---
name: send-to-orchestrator
description: Hand build work to the orchestrator through the build board. Use whenever the owner or any chat says "send this to the orchestrator" or "queue this for the orchestrator", or when a chat has written or found tickets (a new screen, a bug, a fix) that should be built under the orchestrator. It finds or creates each ticket, makes it buildable, ticks the "Orchestrator" box, leaves a dated comment, and tells the orchestrator chat. It never builds anything itself.
---

# Send to the orchestrator

The orchestrator (see `skills/orchestrator`) takes work only from the tickets on the build board that have the **Orchestrator** box ticked. This skill puts work into that queue. A ticket is **buildable** when a builder can start it without asking anyone.

- Board data source: `<board data source>`.
- The orchestrator's queue (saved view): `<queue view>`. All open tickets (saved view): `<all open view>`.
- Read rows through those saved views, not with SQL-style queries (rule 3 in `templates/notion-setup.md`).

## Steps

1. **List what is being sent.** One line per item: an existing ticket (its Ticket ID or link), or new work described in the chat. If it is unclear what should be sent, ask once, with labelled options (A, B, …).

2. **Existing ticket.** Fetch it and make sure the orchestrator can build it without asking:
   - **Properties:** Ticket ID, Status, Priority, Size, Area, Touch area, Merge risk, Depends on. Fill in any that are missing with your best reading, and say in the comment that you did.
   - **Body:** it needs a plain "Why", a "Done when" list, and any decision the owner already made, with its date. Add the missing parts at the end of the page. Never use the command that replaces the page content: it wipes the whole page.

3. **New work.**
   - **Check for a duplicate first.** Search the board for the subject and for likely ticket IDs.
   - **Pick the Ticket ID:** the next free number in the right area. Confirm it is unused by searching for the exact ID. Done tickets keep their numbers too.
   - **Create the ticket** with the properties above and Status "New". Use this body:
     ```
     ## Why
     <one or two plain sentences: what is wrong or missing, and who it affects>
     ## What we want
     <bullets>
     ## Done when
     <bullets the orchestrator can check>
     ## Notes for the builder
     <files, related tickets, limits, areas not to touch>
     ```

4. **Tick the Orchestrator box.** Leave the Status alone if the ticket is already "In progress".

5. **Add a dated comment to each ticket:**
   > **Sent to the orchestrator** (<chat name>, <date>): <one line: what the orchestrator should do>. Decided by the owner: <only what the owner actually said, with the date, or "nothing yet">. Needs the owner: <only if it touches one of the owner's areas, written as "A: … / B: …", or "no">.

   The owner's areas are: money (a higher cap, a new paid supplier, an amount above the owner's limit); what customers see (new features or definitions, pricing, scope); locked contracts; customer data that cannot be undone; keys, access and anything sent outside the company. Never write an interpreted answer as the owner's decision.

6. **Tell the orchestrator chat.** List the running sessions. If a chat titled **Orchestrator** is running, send it one message. Its first line is "New in the orchestrator's queue: <Ticket IDs>", then one line per item. If more than one session has that title, send the message to the live interactive chat. If the message is held for approval, tell the person who asked that the owner must approve it in the orchestrator chat. If no orchestrator chat is running, do nothing more: the orchestrator reads the queue when it starts.

7. **Report back** to the person who asked: the Ticket IDs with their links, and anything marked "Needs the owner".

## Never

- Build, branch, review or merge. That is the orchestrator's work.
- Put these tickets on the owner's decision list. That list holds only decisions the owner must make, one card each (`templates/todo-card.md`).
- Tick the Orchestrator box on a ticket that belongs to another person's lane, unless the owner says so.
- Use slang or idioms in ticket text. Other people read the board, and some of them are not native English speakers.

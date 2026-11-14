# AI dev team for non-coders: the guide in one file

Run an AI software team without writing code. For people who do not write code: how to lead real software building with AI agents, safely.

> **Who this is for:** founders, product owners and others who lead a software product. You decide what to build and why. AI agents plan the work, write the code, review every change and add it to the product. You also approve any change to the rules the AI works under. A small script stops the AI from adding any change that has not passed the automatic tests and a review by a separate, stronger AI model.
>
> **What you need:**
> - Claude Code, on a paid Claude plan that includes the strongest model and enough usage to run several AI sessions at once. Section 7 has short notes for other AI tools.
> - A GitHub repository for your product, with automatic tests (CI) that run on every change. If you have none yet, the AI can set them up with you.
> - A tool for two lists, one for the work and one for your decisions, that AI agents can read, add to and comment on. We use Notion.
> - If other people work with you, we also use Google Drive and Slack.
>
> **What you do not need:** our product or its code. This is a written method with example files and one example script, not a product.
>
> **How to start:** read sections 1 to 4 (about 15 to 20 minutes). The setup in section 7 is technical. You can give this guide to Claude Code or another AI coding tool and ask it to set things up with you, step by step.

This kit describes how we run a software build with one AI "orchestrator" session. The orchestrator plans the work and gives it to cheaper AI builders. A stronger model reviews every change. A script refuses any merge that does not have that review. The human owner is asked only a short, named list of questions.

We share it as an example to copy and adapt. Sections 1 to 4 explain how the building works and why. Section 5 shows how the same setup makes content: articles, videos, decks and other material. Section 6 has the lessons we learnt, and section 7 the technical setup.


> This file holds the whole kit in one document: the guide first, then every kit file as an appendix. Where the guide names a file such as `agents/builder.md`, find the appendix with that name below. If you do not use Claude Code, read the header block at the top of an agent or skill appendix as "the model tier and tools this session gets", and the rest as the instructions to give that session.

## What is in this folder

| File | What it is |
|---|---|
| `README.md` | This guide |
| `skills/orchestrator/SKILL.md` | The start-of-day routine for the orchestrator chat |
| `skills/orchestrator-handover/SKILL.md` | The closing routine, only for when the human wants to close the chat: stop work safely, write the handover, send the daily message |
| `skills/orchestrator-relay/SKILL.md` | The mid-day handover to a fresh orchestrator chat, only when the human asks: wait for a quiet moment, write the handover, start the new chat, retire the old one |
| `skills/send-to-orchestrator/SKILL.md` | How any other chat puts work in the orchestrator's queue: find or create the ticket, make it buildable, flag it, comment, tell the orchestrator. It builds nothing |
| `skills/right-size/SKILL.md` | Which model and which agent for each job, with the reasons, and a check before every agent call. Any chat that starts agents can use it, also without the orchestrator |
| `skills/right-size/right_size_check.py` | A small script that reads the session transcripts on your computer and lists the jobs that ran on a bigger model than their type needs, and reviews that ran on a smaller one. It uses no model and changes nothing |
| `agents/builder.md` | The builder agent: one ticket, one draft pull request |
| `agents/builder-brief.md` | The shared rules every builder reads first |
| `agents/clerk.md` | The clerk agent: a lean, low-cost helper for ticket comments, board updates, to-do cards, look-ups and read-only checks. It starts without the large instruction files |
| `agents/final-reviewer.md` | The final reviewer agent |
| `agents/design-agent.md` | The hard-design agent: writes design notes, never code |
| `agents/workflow-checker.md` | The cost and workflow checker: measures tokens, money and rework, studies how good orchestrators work, and writes a short ranked list of changes. It edits nothing |
| `templates/handover.md` | The handover file that the next day starts from |
| `templates/todo-card.md` | One card on the human's to-do list |
| `templates/notion-setup.md` | How we set up the build board and the decision list in Notion, and how agents connect to them |
| `templates/merge-gate-hook.md` | What the merge gate checks, in pseudocode, and how to install it |
| `templates/merge-gate.example.mjs` | A trimmed example of the merge gate as a Claude Code hook |
| `LICENSE` | The MIT licence: you may copy, change and reuse everything here, if you keep the copyright notice |

Text in angle brackets, like `<main checkout path>`, is a placeholder for you to fill in.

---

## 1. What an orchestrator is, and why we use one

An orchestrator is one AI chat session that runs the building work for a human owner. The human decides **what** to build and **why**. The orchestrator decides **how**. It writes the plan on the ticket, starts builder agents, has each change reviewed, merges it, checks that it works in production, and sends the human one message a day.

### Why we set it up

Before the orchestrator, every change that an AI wrote waited for the owner to read the review and press "merge". Many changes waited a day or more, and some waited several days. Every plan for a change of more than one file also waited for the owner's approval. Reading code reviews was not a good use of the owner's time, and the waiting slowed everything down.

With an orchestrator:

- **The human decides only a short, named list of things** (money, what customers see, and a few more; see section 4). Everything else is decided, done and reported.
- **Quality does not depend on the human reading code.** An independent reviewer on a stronger model reads every change and runs the tests. A script refuses any merge that has no approving review on the exact commit being merged.
- **Cost stays under control.** The expensive model plans, reviews and decides. Cheaper models write the code.

### What it is not

- It does not remove the need for rules. It needs more written rules than a human team, because every agent starts with no memory. We keep the rules a person must remember on one page, and we let machines (CI and the merge gate) enforce the rest.
- It does not make the human's decisions. When a plan touches one of the human's areas, the orchestrator asks and takes the next ticket meanwhile.

---

## 2. The roles

Each role is a separate AI session or agent with its own instructions. The model tier matters: it decides most of the cost. The reasons for these model choices are written as a skill that any chat can use, with a script that checks them: `skills/right-size/`.

| Role | Model tier (what we use) | What it does | What it never does |
|---|---|---|---|
| **Human owner** | – | Decides the areas in section 4. Reads one daily message and one to-do list. | Reviews code. |
| **Orchestrator** | Strongest (Opus) | Picks the next ticket, writes the plan on it, starts builders and reviewers, decides the merge order, merges through the gate, checks production, keeps the ticket board current, writes the handover, talks to the human. | Writes the code it then reviews. |
| **Builder** | Mid-priced (Sonnet) | Builds one ticket in its own worktree, runs the tests, opens one draft pull request, reports in under 15 lines. Up to about six run at the same time. | Merges. Edits the rules files. |
| **Final reviewer** | Strongest (Opus), fresh session | Reviews the change, runs the tests on the change merged with current main, posts one verdict for the exact head commit. Security-sensitive changes get two reviewers. | Edits code. Merges. Reviews code it wrote. |
| **Clerk** | Mid-priced (Sonnet); small (Haiku) for a pure look-up | Light work: ticket comments, board updates, to-do cards, look-ups and read-only checks. It starts without the large always-loaded instruction files, so it is cheap to start (`agents/clerk.md`). | Merges. Builds. Messages people. Makes decisions. |
| **Merge clerk** | Mid-priced (Sonnet) | The merge steps after CI is green, and the after-merge checks. It is started as a general helper; the lean clerk never merges. | Makes decisions. |
| **Scout** | Small (Haiku) | Look-ups, file searches, read-only research. Reports a short answer. | Changes anything. |
| **Hard-design agent** | Deep-reasoning (Fable; Opus works too) | Solves one hard design problem: a ticket that failed review twice, a change to a locked data contract, a hard data, money or security question. Writes a design note with options and a recommendation. | Writes code. |
| **Workflow checker** | Mid-priced (Sonnet) | About once a week, or when the owner asks: measures where tokens, money and waiting time go and where work is done twice (from session logs and pull request history), studies how good orchestrators handle loops, memory, context and skills, and proposes a short ranked list of changes. | Edits rules, skills, memory or code. Proposes removing a safety guardrail to save tokens. |

---

## 3. The daily loop

### Start of day

The human opens an orchestrator chat and types one command (`/orchestrator`). One chat can keep running across days: the human types `/orchestrator` in the same chat each morning. A new chat is needed only when the human asks, after a change of account, or when the chat has become slow or forgetful. The orchestrator:

1. checks that no other orchestrator chat is running, not counting its own chat (two orchestrators once worked on the same pull request within minutes of each other);
2. reads the last handover or checkpoint file and the notes of the last two days, as a list of things to check, not as facts, and, if you keep a nightly backup of the notes, checks that it ran;
3. reads the live state: open pull requests, CI results and review verdicts from GitHub, with a status command; the queue on the ticket board; and what the human answered overnight on the to-do list;
4. sends the human at most 8 lines: what changed and is live (with the proof in a few words), the top 3 to 5 items for today, and only new questions;
5. starts work without waiting for a reply.

### Plan on the ticket

For each ticket the orchestrator writes a short plan as a comment on the ticket: what changes, which files, which tests, the risks, and how to undo it. Builders, reviewers and people can all read it there. If the plan touches one of the human's areas, it becomes a question to the human (section 4), and the orchestrator takes the next ticket meanwhile.

**Size rule:** if a plan has more than about 1,500 changed lines (tests and data included), or more than one purpose, it is split into several pull requests with different files and one purpose each.

### Build in worktrees

Each builder works in its own git worktree: a separate folder with its own branch, sharing one repository. It starts from the current main branch. Builders work on parts of the code that do not overlap, so their pull requests do not clash.

The builder prompt is short: "Read the builder brief first and follow it", then only the ticket, the files, any review findings, and what "done" means. The builder runs the tests (heavy runs on a separate test machine), opens a **draft** pull request, updates the ticket, and reports back. It never merges.

### Final review on the exact head commit

A new final-reviewer session, on the strongest model, reviews each pull request. It:

- writes down the head commit (the latest commit of the pull request); its verdict is only for that commit;
- tests the pull request merged with the current main branch, not only its own branch;
- for a bug fix, puts the bug back and checks that a test fails ("break the fix");
- checks, in order: does it do what the ticket asks; does it touch one of the human's areas without a recorded decision; security; money (no spending path without a cap); locked data contracts; deploy effects; customer-facing text;
- posts one comment with the verdict and a hidden marker that the merge gate reads:
  `<!-- final-review verdict=approved sha=<full 40-character commit> model=<model id> -->`

Any new push needs a new review. A change to security-sensitive files needs two approving reviews, and again two on the new commit after a fix. The gate enforces two reviews only for the files on its list; for other risky changes (for example endpoints and paid-call code outside the list) the orchestrator orders the second review itself. After a small fix, a scoped re-review checks only that the finding is fixed and nothing else changed. After two rounds of "changes needed", the orchestrator stops fixing the code and re-plans the design, usually with the hard-design agent. A third "changes needed" verdict on one pull request is a hard stop: no fourth fix starts, and the orchestrator re-plans the design or asks the human. Later re-reviews read only the new commits. Each reviewer works in its own folder, so two reviewers who run at the same time never overwrite each other's files.

### Merge through the gate

When the review approves, the orchestrator marks the pull request ready, as its own command and at least a minute after the last push. This starts CI (our CI does not run on drafts). To push a fix to a pull request that is already ready, it is turned back into a draft first, so the push does not start a full run. The orchestrator waits for CI in the background, then the merge clerk merges with:

```
gh pr merge <number> --squash --delete-branch --match-head-commit <reviewed commit>
```

The merge gate is a hook: a small script that Claude Code runs before every shell command. It allows the merge only if the pull request is not a draft, targets main, has every required CI check green, has an approving verdict marker on its head commit from an allowed model (two for sensitive files), and does not change the rules files. `--match-head-commit` makes the merge fail if anyone pushed after the review.

### After-merge checks

After each group of merges, the merge clerk checks:

- the website deploy of the new main commit finished;
- if backend code changed: the build of the last merged commit succeeded, the new server version is live, and the health address answers;
- the database security rules in production are the same as on main;
- the changed feature works in production (read-only where possible);
- if a screen changed: a screenshot goes to the human, with a one-line caption.

The ticket then moves to Done with the pull request link and how it was checked. If something broke in production, the order is: undo the change first (a revert pull request with a quick review), investigate second, tell the human third.

### Checkpoint every day, handover when the chat closes

During the day the orchestrator writes running notes to one notes file per day. Once a day it writes a **checkpoint**: it folds the notes into the handover file and keeps working in the same chat. The orchestrator cannot start itself, so the human says "checkpoint" in the chat before leaving. If the human has not said it by a time the human chose (for example 20:00 local time), the orchestrator writes it at its next reply after that time. A checkpoint ends nothing and starts no new chat. It keeps the file current, so a lost chat costs at most one day. This lets one orchestrator chat keep running across days: each morning the human types `/orchestrator` in the same chat, and the orchestrator repeats its start-of-day reads.

When the human wants to close the chat (and only then), the human types `/orchestrator-handover`. The orchestrator:

1. lets running builders finish, or tells them to commit and push their work and stop;
2. checks that the work of every builder folder is pushed;
3. folds the notes and writes a handover file of at most 70 lines with the current state only: open pull requests, unfinished work, production state, questions waiting for the human, scheduled checks, what only this chat knows, and the next five tickets;
4. adds lasting lessons to a short playbook file;
5. removes merged worktrees, updates the ticket board, closes answered to-do cards;
6. renames its chat so tomorrow's orchestrator is the only one;
7. sends the human one message of at most 6 lines.

The next chat starts from that one file. Close a chat that has become very long or slow and start a new one: a long chat re-sends its whole history with every message, so it costs more and answers more slowly.

### Handover in the middle of the day (only when the human asks)

Sometimes the human wants a fresh chat before the day ends. The human types `/orchestrator-relay` (`skills/orchestrator-relay/SKILL.md`). It is the same handover, plus two steps. When no helper is running and all work is pushed to GitHub (a quiet moment), the orchestrator writes the handover, renames its chat, starts a new orchestrator chat that begins by reading the handover, and archives the old chat. A helper that was still working cannot move to the new chat, so the handover lists it, and the new chat starts it again from its branch. The orchestrator never does this by itself, and never because a chat has become long: lesson 11 explains why.

### Checking the workflow itself (about once a week)

About once a week, or when the owner asks, the orchestrator starts the workflow checker (`agents/workflow-checker.md`) on one topic. The checker measures first: what is loaded into every session, the tokens by model and by role from the session logs, and the review rounds and hours per pull request. Then it reads current guidance on how good orchestrators handle loops, memory, context and skills. It delivers one note of at most 100 lines: where the tokens and money go, at most 7 changes ranked by saving (each with its basis, its risk and who decides), and a line for each idea it checked and rejected. It only reads and measures. The orchestrator applies changes to its own skills, rule changes go into the weekly bundle, and a change in the human's areas becomes a question. It never proposes removing a safety guardrail to save tokens.

Each morning, when the human types `/orchestrator`, the orchestrator looks at the date of the newest checker note. If it is 7 or more days old, it starts the checker that day with the next topic: the weekly check once lapsed for weeks because nothing reminded anyone. Once a week it also runs a scorecard of three numbers, with small scripts that use no model and read the session logs and the pull request history. The numbers are: the review verdicts per merged pull request (how many verdicts the average merged pull request needed; lower is better); the cache share (the part of all input tokens that came from the prompt cache; a token is a small piece of text that a model reads or writes, and cached text is read at a small part of the normal price); and the late resumes (messages to a helper that ended more than 4 minutes before; see lesson 15). It writes the first three numbers as one line in the playbook, as the baseline, and adds one line each week. If a number gets worse for two weeks in a row, the change behind it is undone. In the same weekly slot it runs the right-size check (`skills/right-size/right_size_check.py`): the jobs that ran on a bigger model than their type needs, the reviews that ran on a smaller one, and the median start-up context of each agent type.

---

## 4. What the human still decides, and how the human is asked

### The human's areas

Only these go to the human:

- **Money:** raising a spending cap, a new paid supplier or plan, switching on paid work that then runs by itself (for example resuming a paused paid job, or switching a kill switch back on), and any single item above an amount the human sets. Repeating costs are counted per month.
- **What customers see:** new features or definitions, pricing, scope. Not wording or layout inside a direction the human already gave.
- **Locked contracts:** data formats and definitions marked as locked, because many parts of the system depend on them.
- **Customer data that cannot be undone:** deleting or overwriting it.
- **Keys, access, and anything sent outside the company.**
- **Changes to the rules themselves.** The human merges those pull requests.

Everything else the orchestrator decides and reports in the daily message.

### How the human is asked

- **One list.** The human reads one to-do list and nothing else. A question that exists only in a chat, a handover file or a ticket comment gets lost.
- **One card per question.** Each card is complete on its own: what is going on, why it is the human's decision, option A and option B and what each does, the recommendation, and how many minutes it takes. Never an umbrella card that collects other cards. Things the human does in one sitting (for example two settings on the same screen) share one card.
- **Tell first, then the card.** The question is put to the human in the chat or the daily message first; the card is the record. Never create a card for something the human has never heard about: such cards are not done, and they mislead others who read the list.
- **A unique key on every card** (`<source>:<date>:<short-name>`). Check for it before adding a card, so there are no duplicates.
- **The human's own column.** The main columns are "To do", "Doing" and "Done" (`templates/notion-setup.md` adds "New" and "Parked"). "Doing" belongs to the human: agents never move a card into it or out of it. When the human answers, the orchestrator moves the card to Done in the same turn and writes the decision on the ticket.
- **Few interruptions.** One short notification when work is blocked on the human. Otherwise the orchestrator interrupts only when production or money is at risk, or when a merge planned for today waits on the human.
- **Never stretch a decision.** If a new case is close to an earlier decision but not the same, ask again.
- **Plain words.** No ticket numbers as shorthand; say what the work is and add the number only as a link.

The format of a card is in `templates/todo-card.md`.

### Two lists, kept apart (we use Notion for both)

We keep the work and the owner's decisions in two separate Notion databases.

- **The build board** holds every ticket: the plan, the status, the dated progress comments and the link to the pull request. The team and every agent read and write it. The orchestrator takes work only from the tickets on it that have the "Orchestrator" box ticked. Any other chat that finds work for the orchestrator adds a ticket there, ticks the box and leaves a comment, so work never arrives only as a chat message (see "Sending work to the orchestrator" below).
- **The owner's decision list** holds only what waits on the owner: one card per decision, written so that the owner can decide it in one sitting. It is private to the owner. Agents add cards and close answered ones, and they never move a card into or out of "Doing", which is the owner's own column.

*Why two lists:* the board has hundreds of tickets, and the owner needs to see almost none of them. When decisions sit on the board, they get lost among the tickets, and the owner has to search for them. With a separate list, the owner opens one short list, decides each card, and knows that nothing else is waiting. Nobody waits for the owner either: when a card goes on the list, the orchestrator takes the next ticket. Keeping the list private also lets cards speak plainly about money.

We tried a third board for work outside the build and stopped it after about two weeks: its cards took extra work and nobody read them. Two lists were enough.

How to set up both databases in Notion, and how agents connect to them: `templates/notion-setup.md`.

### Sending work to the orchestrator

Any other chat (a design chat, a content chat, the human's own chat) that finds or writes work for the orchestrator uses `skills/send-to-orchestrator/SKILL.md`. The chat first searches the board for a duplicate. Then it finds or creates the ticket and makes it buildable: a plain "Why", a "Done when" list, the usual properties, and any decision the human already made, with its date. It ticks the "Orchestrator" box, leaves one dated comment (who sent it, what to do, what the human decided, and whether it needs the human), and sends the orchestrator chat one message that lists the new tickets. If no orchestrator chat is running, the ticket waits in the queue. The chat never builds, reviews or merges anything itself, and never puts the ticket on the human's decision list.

### Where everything lives

Each kind of information has one home, so no agent has to guess where to look or where to save.

| What | Where | Who uses it |
|---|---|---|
| Instructions and context for each session: the skills, the agent files, the builder brief, the handover and the playbook | Files that Claude Code loads, in `~/.claude/` and in the repository | Every session, when it starts |
| Code, pull requests, review verdicts and CI results | GitHub | Agents and the merge gate |
| The record of the work: tickets, plans, progress, decisions, and the owner's to-dos | Notion | The team, the agents and the owner (the decision list is the owner's only) |
| Team assets: decks, reports, images, screenshots, videos, offers, and backup copies of the team's skills | Google Drive, in one shared drive | The team |
| Team conversation: questions from the team, review results, notices before paid runs, finished content | Slack, one development channel and one content channel | The team and the orchestrators |

How we use Google Drive:

- **One shared drive, one top folder, a fixed structure** with numbered folders, for example `00 To sort`, `01 Company`, `02 Brand`, `03 Sales`, `04 Clients`, `05 Marketing`, `06 Product`, `07 Templates`, `99 Archive`.
- **The structure and the filing rules are written in one skill,** so every agent files the same way. A file that does not clearly fit goes to `00 To sort`, and the agent tells the owner. Agents never create a new top folder without asking.
- **Quick looks and finished work go to different places.** Mock-ups and previews go to the owner's Downloads folder. Finished work is made in, or filed straight into, the right Drive folder: that is how it is delivered to the team. There is no general "outputs" folder.
- **Agents reach Drive** through Drive's desktop app (a folder on the computer that syncs) or through Claude's Google Drive connector.
- **Backup copies of the team's skills** live in Drive, one folder per skill, so a new computer or a new account does not lose them.
- **Files are shared with named people only,** never with "anyone who has the link". No keys, passwords or code go in Drive.

How the orchestrator uses Slack (a smaller part of the setup):

- **It reads the team's development channel** for questions and reports from the team, and answers there.
- **It posts three kinds of message:** an answer the owner gave in the orchestrator chat for a team member, review results on team members' pull requests, and a notice before any live run that costs money starts.
- **Channel messages, not thread replies.** A decision hidden in a thread is hard to find later. One post can cover several people, with a short labelled part for each.
- **Short posts.** One line and the file, or a direct link to the file. Never "it is in the drive": the reader should open it with one click. The detail stays in the review or the ticket.
- **Plain words for readers whose first language is not English:** no slang and no idioms. No praise: what was checked, the verdict, and what must be done.
- **Slack is not the record.** Decisions also go on the ticket. Questions for the owner go on the decision list, never only in Slack. Nothing goes to anyone outside the company.

---

## 5. The content side

The same setup also makes content: articles, videos, slide decks and client reports, cover images and ads, and sales material such as offers and introduction decks. Sections 1 to 4 are about building software. Content follows the same ideas (rules written down, the owner asked only a few things, one home for each kind of file), with its own steps, because the risk is different: a wrong fact or a piece that does not look like the brand, not a broken product.

### How content work is organised

- **One skill per kind of content.** Each skill holds the rules for that kind of work, the brand files it needs (logos, fonts, brand illustrations, colours), the steps, the checks, and where the finished piece goes. When the owner approves a piece, the lessons from it are written into the skill, so the next piece starts from them. Our skills cover, for example: slide decks, articles, cover images, ads, videos, and where files are kept.
- **One brand guide skill** is the single source for colours, fonts, voice and tone. Every other content skill follows it.
- **One house-rules file** that every session loads: plain words for readers whose first language is not English, how to show numbers, and the chart colours.
- **The whole team uses the same skills,** from one shared place, so a deck made on another person's computer follows the same rules. Backup copies of every skill are kept in the shared drive.
- **Writing and building are separate roles,** as in the build. A copywriter agent writes the words and never the code; the website's builders build the approved words. Routine video work and hard technical video work are two separate agents, in the same way that builders and the hard-design agent are separate.

### A second orchestrator for the website

Our public website has its own orchestrator session, with the same daily loop, its own repository, its own handover, and a final review of every change to the live website. The two orchestrators talk to each other directly about anything that crosses between them: product facts, prices, wording, and launch dates (so that the website and the product change at the same moment). Each repository has one orchestrator: website code belongs to one, product code to the other.

### Articles

1. A team member or a writing agent drafts the article. Facts are locked: prices, plans and numbers come only from a fact sheet. A missing fact is marked `[FACT NEEDED: …]` and never invented.
2. A cover image skill makes the cover. It holds the cover style, the brand illustrations and the export sizes for the website and for social posts.
3. The article arrives as a pull request. When the owner asks for it to go live, one agent does every publishing step itself: it uploads the images, publishes the text, checks the live page in every language, merges the pull request, and asks search engines to index the page. The owner is never handed technical steps.

### Videos

A video pipeline turns any idea (a feature, a finding, a how-to, an offer) into a short finished video.

1. **Shape first.** Choose the kind of video (sales, explainer, or customer help), then the opening line that makes people watch. If there is too little information, ask the owner two or three questions instead of inventing facts.
2. **Script as text first.** Text is quick to check and change; a rendered film is not.
3. **Then make the whole film without stopping for approval at each stage:** voice, timing, shots, render. Between stages the agent uses its own checks instead of the owner: a quick preview, one contact sheet of frames, and a transcript of the voice compared with the script (any line that differs from the script is recorded again). It stops only for a real blocker, missing facts, or a cost cap. *Why:* approval at every stage turned one short video into a long exchange of messages; the owner wants a finished film to react to.
4. **One delivery package per video:** the video, a square version for social posts, two thumbnails, exact captions made from the word timings, a transcript, the title and description for the video site, a social post, and the code to put it on the website. A video is not finished without a thumbnail that makes people want to watch it.
5. **Filed and announced.** The package goes into the right shared-drive folder and is announced in the team's content channel with one line. People publish it.

**Cost caps per video:** a fixed number of voice takes and image calls, the cost estimate written in the delivery note, a running count against the monthly allowance of each paid tool, and never a batch of videos made unattended.

### Slide decks and client reports

- **Review as text first.** Check all slide text and chart rows until they are true, render the deck once, then look once for layout only. *Why:* in our test, building the deck and reading the PDF took about 40 minutes to check three sentences, against about 5 minutes in text, and the text review found at least as many problems.
- **The client-reader test before delivery.** Three role-played readers on the client side, each with a different job (for example the person who holds the budget, the person who would do the work, and the person who would write the content), who know nothing about our method, read the whole report. Each must produce what their job needs from it, for example a budget request, a task list or a writing brief. Everything they had to invent or guess is fixed before the report goes out.
- **The deck skill** holds the rules, the brand files, a slide theme and a review script that catches placeholders left on slides.

### Show the work, then change it

After each round of creative work (covers, thumbnails, drafts, ads), show it to the owner before making another round. Change only what the owner, or a clear defect, points to, and keep what works. Do not throw away a whole round because the agent prefers its own idea. But a clear description of what the owner wants is a request: make it, do not wait for a second yes.

For thumbnails and ads, build from the brand files (logo, brand illustrations, real screenshots) rather than generating the whole picture: in our tests, fully generated thumbnail pictures failed three rounds in a row.

### Where content goes

- Questions for the owner (for example, which page a video goes on) go on the decision list, as in the build.
- Finished work is filed in the right shared-drive folder: that is the delivery. Mock-ups and quick looks go to the owner's Downloads folder.
- Finished pieces are announced in the content channel with one line and a direct link.

---

## 6. Lessons we learnt

### The main lessons

1. **Keep the orchestrator's chat free.** Anything that needs more than about two tool calls goes to a background agent. *Why:* the human waited minutes for every reply while the orchestrator waited for CI or wrote board cards itself. Now the orchestrator answers the human first, in one short message. Clerks (the lean clerk and the merge clerk) do the mechanical work. The orchestrator keeps the decisions, the merge order and the conversation. When the human asks a question, the orchestrator answers from what it knows; if a fact needs checking, it says so in one line and checks in the background.

2. **Builders run on a cheaper model; the stronger model only reviews.** Pass the model explicitly every time you start an agent. An agent that inherits the orchestrator's model runs on the expensive tier: one builder that was left on the strong model used several times the tokens of a normal build. The strongest model is for final reviews and, rarely, a hard design job, and the brief then says why. A short, explicit tool list in the builder's definition also cut its start-up context by about half. Clerks follow the same rule: start every card, board line and read-only check as the lean clerk (`agents/clerk.md`), which starts without the large always-loaded instruction files, and a pure look-up on the smallest model. A general helper loads every instruction file, and in our measurements it started at more than twice the size of the lean ones. A builder can also compact its own history at a set size (`autoCompactWindow`), so a long build does not grow without limit. The `right-size` skill (`skills/right-size/`) holds these rules for any chat that starts agents, and its script lists the jobs that ran on a bigger model than their type needs. Its first run on our own transcripts found a file-search helper that had run on the top model, because the call passed no model.

3. **A reviewer is never the session that wrote the code, and its verdict is tied to the exact head commit.** The session that wrote the code still has the same wrong assumptions it had while writing; a fresh session on a stronger model does not have them. The verdict names the 40-character commit. Any later push needs a new verdict. The merge command passes `--match-head-commit`, so a push between the review and the merge makes the merge fail.

4. **A hook enforces the merge gate, so it does not depend on memory.** Rules that agents must remember are forgotten, especially after a long chat is compressed. The gate is a script that refuses the merge command itself. It also fails closed: if the gate cannot run, any command that could merge or push is refused. Keep the main checkout on the main branch, because the hook runs from the folder where the session started: once a session ran in a folder that was on an old branch without the gate.

5. **Draft pull requests run no CI.** We set CI to skip drafts, to save CI minutes. So builders run their checks before they push and open drafts, and the orchestrator marks a pull request ready only after the review approves. A skipped run is never a pass. Never "mark ready and merge" in one command: the merge can run before CI has reported. To push a fix after the pull request is ready, turn it back into a draft first. Wait about a minute after a push before marking it ready; if you mark it ready too soon, the run is cancelled and every job is skipped (fix: back to draft, wait, ready again).

6. **Editing a pull request while its checks run cancels the checks.** Changing the title or description creates an "edited" event. Our workflows use one concurrency group per pull request with "cancel in progress", so the edited event cancels the real runs. Edit the description before marking ready, or after CI has finished. If it happens, re-run the cancelled runs.

7. **Subagents tend to stop while they wait for CI.** A subagent told "wait for CI, then merge" often ends its turn with "still waiting" and does nothing more. So the orchestrator runs the wait itself, as a background shell command: the chat stays free, and the orchestrator is woken when the command ends. When CI is green, it starts a fresh merge clerk, which checks the gate, merges with the literal commit, runs the after-merge checks and writes one line on the ticket. Also: no agent checks CI again and again without a pause. The GitHub API has an hourly limit that all agents share, and we reached it once.

8. **Stacked pull requests merge in a fixed order.** (A stack is a pull request built on top of another one.) (1) Merge the lower pull request with a merge commit, not a squash, and do not delete its branch. (2) Fetch, and check that the upper pull request still contains the lower one's merged head (`git merge-base --is-ancestor <lower head> <upper head>`). If it does not, merge main into the upper pull request and get a full review of its whole diff against main, not a scoped re-review. (3) Change the upper pull request's base to main. (4) Delete the lower branch, only after every pull request on it points at main. Never change the base first: the upper pull request would then pass the gate with the lower one's unreviewed commits. Deleting the lower branch first can close the upper pull request. Avoid stacks where you can.

9. **Split any change of more than about 1,500 lines.** Large pull requests got slower and more expensive reviews and more fix rounds. Split them into pull requests with different files and one purpose each. Stack them only when one really needs the other.

10. **Heavy test runs go to a separate machine.** With six builders and several reviewers, the laptop that runs the agents became too slow to use. Full test suites and the type check now run on a separate computer. The laptop runs only the single test files a change touches, one at a time. If the test machine cannot be reached, the builder stops and reports it; it does not fall back to the laptop. Safety: if the test machine is not sandboxed, run only branches that your own builders wrote, and never a branch that changes dependency files, because installing packages runs their scripts on that computer.

11. **An automatic handover at 60% context was tried and rolled back.** The idea: when the chat's context reached 60%, the orchestrator would write the handover, start a fresh orchestrator chat and archive the old one. In practice it had to wait for a quiet moment with no agents running, so it stopped starting new work; a limit of two handovers a day then blocked it; and a new chat could only be started from a message the human typed, so at night it waited for the human anyway. The app also compresses long chats by itself. Now one orchestrator chat keeps running across days and writes a checkpoint once a day (the notes are folded into the handover file); a handover is for the day the human wants to close the chat, and a mid-day handover happens only when the human asks for it (`skills/orchestrator-relay/SKILL.md`).

12. **The human decides only a few named areas.** An earlier attempt to delegate failed because chats still asked permission for everything, and scheduled runs stopped at permission prompts. A short, named list in the written rules ended that. Everything outside the list is decided by the orchestrator and reported.

13. **Cost caps and kill switches are designed in from the start.** Every paid call (AI models, data suppliers, e-mail) goes through: a server-side cap per account and per month, read from trusted settings and never from a value the client sends; a rate limit; and a kill switch, which is an environment flag per supplier plus one master flag that stops all paid work without a new deploy. No account gets paid work that runs by itself until its budget is set. Build these with the first paid feature, not after it.

14. **Never answer from an assumption: check the live state first.** Handover files, memory notes and the ticket board are out of date within hours. Before the orchestrator says what is live, what is done or why something happens, it reads the code and queries the live system. If it has not checked yet, it says "checking", not "probably". A check that cannot reach production means "wait", never "nothing is running".

15. **Start a fresh helper instead of resuming an old one.** A helper's prompt cache lasts about five minutes. After that, a message to it makes the system read its whole history again at full price, and a late resume of a builder cost many times more than a fresh lean builder that starts from the branch, the pull request number and the exact review comment. So: if a helper ended more than 4 minutes ago, start a fresh one; message an old helper only inside 4 minutes, or to steer one that is still running.

16. **Stop at the third "changes needed" verdict.** After two rounds the orchestrator already re-plans the design. If a third "changes needed" verdict still arrives on one pull request, no fourth fix starts: the orchestrator re-plans or asks the human, and later re-reviews read only the new commits. More rounds on the same design cost more and rarely converge.

17. **Measure every week with three numbers, and undo what makes them worse.** Review verdicts per merged pull request, the cache share (the part of the input tokens that came from the prompt cache) and the number of late resumes (both are defined under "Checking the workflow itself" in section 3). Each change to the workflow (a new agent type, a smaller context, a new rule) is judged by these numbers after a week or two, not by how sensible it sounded. If a number gets worse for two weeks in a row, the change behind it is undone.

### Smaller lessons

- **A "changes needed" verdict blocks that commit, even if approvals follow.** The gate counts every verdict on the head commit. A reviewer must never post "changes needed" only because CI has not run yet; it reports back instead.
- **Old failed CI runs keep the gate red** after the cause is fixed elsewhere, because every run on the head commit counts. Push a new commit (merge main in) and get a scoped re-review. Never delete runs.
- **Keep a builder's worktree until its pull request merges.** If the folder is deleted, the builder cannot be resumed for review fixes.
- **Every agent gets its own scratch folder.** Two builders once overwrote each other's files in a shared one.
- **Never reinstall packages into a shared, linked dependency folder.** It empties the folder for every other agent. And never stop processes by name: one agent stopped four other agents' test runs that way. Stop only process ids you started.
- **Name ticket ids and version numbers in the brief.** Builders working in parallel picked the same ones.
- **Do tiny edits yourself.** Resuming a finished builder for a one-line change costs far more tokens than doing it in the orchestrator chat.
- **Builders never edit the rules files.** The gate refuses the whole pull request, and the reviews are wasted. The builder writes the wording it needs on the ticket, and rule changes go to the human in one weekly bundle.
- **Fake keys in tests must look fake** (low randomness, for example one letter repeated), or the secret scan in CI fails.
- **Check your Claude subscription's usage limit before starting a batch of builders.** Agents that reach the limit at night stop without telling anyone.
- **Always use the human's local time** when naming a time or a day. Logs are in UTC, and a wrong conversion once put a check on the wrong day.
- **One orchestrator at a time.** Give it a fixed chat title. At the start of the day it checks that no other chat has that title; at the handover the old chat is renamed and merges nothing more.
- **Answer questions about production from production.** A local emulator returns no data, which looks like "nothing is running".
- **Two reviewers must never share a folder or a file name.** One reviewer once overwrote another reviewer's test script. Each reviewer keeps everything in a folder named after the pull request and its lens.
- **Keep the always-loaded notes index short.** The notes index is the file with one line per note that your tool loads into every session (in Claude Code, `MEMORY.md` in the project's memory). The tool may load only the first part of a long index and drop the rest without a warning, so a rule written near the end is lost. Check the length with a small script each morning, and move finished lines to an archive file instead of deleting notes.
- **Back up the state and notes folders every night.** A scheduled job copies the handover, the playbook, the notes and the memory files to a private repository, after a scan for secrets, and writes a one-line status (OK with the date, or blocked). Read that line each morning: a lost computer or a damaged folder then costs at most a day.
- **Fold the notes into the handover file once a day.** Running notes are cheap to write and easy to lose in a long chat. The daily checkpoint turns them into the one short file that the next chat reads.

---

## 7. Setup (technical)

### With Claude Code

Some steps use features of the Claude desktop app: listing, renaming and archiving chat sessions, and push notifications. If your app does not have them, do those steps by hand or leave them out.

1. **Skills.** Copy `skills/orchestrator/`, `skills/orchestrator-handover/`, `skills/orchestrator-relay/` and `skills/send-to-orchestrator/` into `~/.claude/skills/`. The human then types `/orchestrator` each morning in the same chat, says "checkpoint" before leaving, types `/orchestrator-handover` only when closing the chat, and types `/orchestrator-relay` when a fresh chat is wanted in the middle of the day. Every other chat that finds work for the orchestrator needs `send-to-orchestrator` too: put it where those chats load their skills. Copy `skills/right-size/` (the skill and its script) as well: the orchestrator uses it before every agent it starts, and any other chat that starts agents can use it too.
2. **Agents.** Copy `agents/builder.md`, `agents/clerk.md`, `agents/final-reviewer.md`, `agents/design-agent.md` and `agents/workflow-checker.md` into your repository's `.claude/agents/` folder (shared with the team) or into `~/.claude/agents/` (only for you). Copy `agents/builder-brief.md` into `~/.claude/orchestrator/`: it is not an agent and has no header. If builders and the clerk use the board through an MCP server (Notion, in our case), add those tool names to `builder.md` and `clerk.md`. In `builder.md`, fill in `autoCompactWindow`: the size, in tokens, at which Claude Code summarizes a builder's conversation to make room (the comment in the file explains it). In `clerk.md`, keep `omitClaudeMd: true`: it starts the clerk without the large always-loaded instruction files.
3. **State folder.** Create `~/.claude/orchestrator/` with: `HANDOVER.md` and `handover-template.md` (both copies of `templates/handover.md`), `todo-card.md` (a copy of `templates/todo-card.md`), an empty `handovers/` folder, an empty `notes/` folder (with an empty `notes/archive/` folder inside it) and an empty `playbook.md`. The skills read these files.
4. **Merge gate.** Copy `templates/merge-gate.example.mjs` to `scripts/merge-gate/merge-gate.mjs` in your repository, edit the constants at the top, register it in `.claude/settings.json` (the snippet is in `templates/merge-gate-hook.md`), and test it as described there.
5. **CI.** Decide whether CI skips draft pull requests (it saves CI minutes; lesson 5 lists what follows from it). Use one concurrency group per pull request. Put the exact check names in the gate.
6. **Rules page.** Write one page with the human's areas, the merge rule (final review on the head commit, merge only through the gate), and the security rules for every endpoint (authentication, ownership check, input limits, spending cap, rate limit, kill switch). Keep it to one page; give everything else to a machine.
7. **The two lists.** Set up a build board for the work and one decision list for the human. We use Notion for both: `templates/notion-setup.md` has the fields, the views, the connector and the rules. Any other tool works if agents can read it, add to it and comment on it.
8. **Shared drive and team chat.** Connect your shared drive (we use Google Drive) through its desktop app or Claude's connector, and write your folder structure and filing rules into one skill. Connect your team chat (we use Slack) through Claude's connector and put the channel name in the orchestrator skill. See "Where everything lives" in section 4.
9. **Content (if you make content).** Write one brand guide skill and one skill per kind of content, each with its rules, brand files, steps, checks and where finished work goes. Give them to the whole team from one shared place. See section 5.
10. **Placeholders.** Search the skill and agent files for `<` and fill in your values.

### Helper scripts worth writing

We wrote these as small shell scripts. Each one replaced a manual step that went wrong at least once.

- **status:** one line per open pull request with its head commit, draft state, CI result, the verdicts on the head commit, and what the gate would say. It is built from GitHub every time, never from a list kept by hand.
- **preflight**, before a final review: no conflict with main, the head contains the current main, no other open pull request touches the same files, the ticket id is in the title. It prints GO or a numbered fix list, and it saves review rounds.
- **gatecheck:** runs the gate on the merge command without merging (one line, in `templates/merge-gate-hook.md`).
- **after-merge:** the checks listed under "After-merge checks" above.
- **clean-worktrees:** lists worktrees whose pull request is merged or closed, with no uncommitted work and no change in the last 12 hours. It removes them only when given a flag.
- **park-check**, before the handover or a relay: the work in every builder folder is committed and pushed.
- **remote-test:** sends a branch to the test machine and runs the full suites there.
- **memory-health:** compares the length of the always-loaded notes index (see the smaller lessons) with the length that your tool loads. It prints a few lines, uses no model, and fails when the index is too long.
- **backup:** a scheduled job that copies the state folder, the notes and the memory files to a private repository every night, after a secret scan. It writes a one-line status file in the state folder: OK with the date, or blocked when the scan found a secret.
- **scorecard:** three small scripts that print numbers only, from the session logs and the pull request history: review verdicts per merged pull request, the cache share, and late resumes (defined under "Checking the workflow itself" in section 3). Ask Claude Code to write them. The right-size check is already written: `skills/right-size/right_size_check.py`.

### Without Claude Code

- **Skills are routines.** Paste `skills/orchestrator/SKILL.md` as the first message of the day's orchestrator chat, and the handover routine when the human wants to close the chat (the checkpoint is the same file, written once a day while the chat keeps running). Paste the relay routine only when the human asks for a mid-day handover, and the send routine into any chat that sends work to the orchestrator.
- **Agents are separate sessions** that start with these files as their instructions. Whatever your tool calls them (subagents, background agents, separate chats), start each one with its agent file and a short brief.
- **The merge gate is anything that runs before a merge and can refuse it.** Options: your tool's pre-command hook; a wrapper script that is the only way agents may merge; or branch protection with required checks plus a small CI job that sets a required status when it finds an approved verdict marker for the head commit. Use branch protection with required checks where your plan allows it; the hook is an extra layer that stops the merge before the command runs.
- **Model tiers:** your provider's strongest model for the orchestrator and the reviewer, a mid-priced model for builders and clerks, the smallest model for look-ups. `skills/right-size/SKILL.md` has the full table, the reasons, and when a job may go up a tier.

### What to change for your project

- Paths: the main checkout, the worktree folder, the state folder.
- The human's areas and the spending amount the orchestrator may approve alone.
- The CI check names, the allowed reviewer model ids and the GitHub account that posts verdicts, in the gate.
- The lists of rules files and security-sensitive files, in the gate and in the builder brief.
- The after-merge checks, which depend on where and how you deploy.
- Any quiet window: if merging backend code restarts servers and stops long jobs, allow backend merges only when an idle check passes or inside a fixed quiet window.

---

## Licence

MIT. See `LICENSE`. You may copy, change and reuse the kit, also in commercial work, if you keep the copyright notice.


---

# Appendices

## Appendix A: Start-of-day routine for the orchestrator (`skills/orchestrator/SKILL.md`)

Claude Code header:

```yaml
name: orchestrator
description: Start the day as the orchestrator of a software build. Checks that this is the only orchestrator chat, reads the last handover or checkpoint, reads the live state, tells the owner in a few lines what is happening today, then starts work. Use when the owner types /orchestrator (also each morning, in the chat that is already the orchestrator) or says "start the orchestrator". When the owner says "checkpoint", write the daily checkpoint (see "Notes and checkpoints").
```

### /orchestrator — start the day

> **Hard rule: never answer from an assumption.** Before you state any fact about production, data, dates, what is live or why something happens, read the code and query the live system, or start an agent and wait for its answer. The handover and your notes are leads to check, never answers. If you have not checked yet, say "checking", never "probably".

You are the orchestrator for `<project>`. The owner decides what and why, and only the areas listed in `<rules file>`. You decide how, check the work and merge it. You never write the code that you then review.

**One chat can run for many days.** You cannot start yourself. So the owner types `/orchestrator` in this same chat each morning: then do sections 1 to 3 again (they are short when little has changed) and carry on. Before leaving, the owner says "checkpoint", and you write the checkpoint (see "Notes and checkpoints"). A new chat is needed only in the cases named in section 6.

#### 1. Make sure you are the only orchestrator

- List the running sessions (a feature of the Claude desktop app; without it, check by hand). Ignore this chat itself: it already has the title **Orchestrator** when it has been running since an earlier day. If a different interactive chat titled **Orchestrator** is running, stop and tell the owner in one line: "Another orchestrator chat is still open. Close it, or run /orchestrator-handover there first." Do nothing else.
- Otherwise set this chat's title to **Orchestrator** (if it does not have the title yet). Other chats find you, and send you work (with `send-to-orchestrator`), by that title.
- If this chat is not on the strongest model, say once: "The orchestrator should run on `<strongest model>`. Switch with the model picker." Then carry on.

#### 2. Read the current state (read it; do not work it out again)

1. Get the owner's local time: `TZ=<owner's time zone> date`. Use local time for every time and day you name.
2. Read `~/.claude/orchestrator/HANDOVER.md` (the last checkpoint or handover). If its `Written:` time is more than 24 hours old, say so in the first line to the owner. Then read only the last 60 lines of today's notes file and of the newest older notes file in `~/.claude/orchestrator/notes/` (never open `notes/archive/` unless a handover line names a file). If HANDOVER.md is missing, read the newest file in `~/.claude/orchestrator/handovers/`.
3. Read `~/.claude/orchestrator/playbook.md` (lasting lessons).
4. Run your memory health check. Your tool loads a notes index into every session (in Claude Code, `MEMORY.md` in the project's memory: one line per note). It loads only the first part of a long index and drops the rest without a warning, so a rule near the end is silently lost. The check is a small script, with no model, that compares the length of the index with the length your tool loads. If it fails, tidy the index the same day: merge lines, or move finished ones to an archive file. Never delete a note.
5. If you keep a nightly backup, read its one-line status. The backup is a scheduled job that copies your state folder, your notes and your memory files to a private repository, after a scan for secrets, and writes the status: OK with a date, or "blocked". It should say OK with last night's date or later. "Blocked" means that the secret scan stopped the push: read the backup log. A date older than two days means that the job did not run. Say either one in the first message to the owner. If you keep no backup, skip this step.
6. The main checkout stays on main: `git -C <main checkout path> branch --show-current` must print `main`, because the merge-gate hook runs from there. Then `git fetch origin`.
7. Read the live pull request state from GitHub with your status command. Never trust the handover's pull request list over it.
8. Read your queue on the build board: the tickets with the "Orchestrator" box ticked that are not Done, read through the saved queue view.
9. Read the owner's to-do list: cards with your source key that the owner answered or commented on. Move answered cards to "Done" (never touch "Doing", which is the owner's own column) and write each decision on its ticket.
10. Do anything in the handover's "Scheduled checks" that is due now. Also look at the date of the newest note from the workflow checker: if it is 7 or more days old, start the checker today with the next topic (a weekly check once lapsed for weeks because nothing reminded anyone).
11. If the handover has an "Old chat" line and that chat is not running, archive it (archive, never delete).

Builders from yesterday's chat cannot be resumed. For each unfinished item in the handover, start a fresh builder from its pushed branch.

#### 3. One short message to the owner

At most 8 lines, plain everyday words, no pull request numbers in passing:

- what changed overnight and what is live (verified, with the proof in a few words);
- what you will do today (the top 3 to 5 items);
- only **new** things that need the owner, each as A/B with your recommendation. Never repeat a reminder the owner has already answered.

#### 4. Work

Start work without waiting for a reply.

##### Choose the model for every agent, and pass it explicitly

| Job | Agent | Model |
|---|---|---|
| Build one ticket | `builder` | `sonnet` |
| Final review | `final-reviewer` | `opus` |
| Merge steps, after-merge checks | merge clerk (general agent) | `sonnet` |
| Ticket and to-do cards, board lines, read-only checks | `clerk` | `sonnet` |
| Look-ups (the answer is a fact in files or pull requests), file searches | `clerk` or a scout (general agent) | `haiku` |
| Re-plan after two "changes" rounds; a locked contract; a hard data, money or security design | `design-agent` | strongest reasoning model; say why in the brief |
| Weekly study of tokens, money and rework | `workflow-checker` | `sonnet` |

Never let an agent inherit your model. Start every builder as `builder` and every card, board line and read-only check as `clerk`, never as a general agent: a general agent loads every always-loaded instruction file and starts at more than twice the size. Only the merge clerk stays a general agent; the lean clerk never merges. At most 6 builders at the same time; queue the rest. Before a batch of builders, check your Claude subscription's usage: if it is at 85% of the limit or more while builders run, tell the owner in one line.

A job that runs above the model in its row (for example a builder on `opus`) carries one line in its brief: `Model reason: <why the model in its row is not enough>`. The reasons behind this table, and the weekly check, are in the `right-size` skill (`skills/right-size/`).

##### Keep your chat free

Answer the owner first, in one short message. Anything that needs more than about two quick tool calls goes to a background agent. You keep the decisions, the merge order and the conversation. When the owner asks a question, answer from what you already know. If a fact needs checking, say so in one line, check in the background, and come back only if it changes the answer.

##### Name agents by their role

`builder-<task>`, `review-<pr>`, `security-review-<pr>`, `clerk-<task>`, `scout-<topic>`, `design-<topic>`. Use plain role words in anything other people read.

##### Plan on the ticket

Write a dated plan comment on the ticket: what changes, which files, tests, risks, how to undo it. **Size rule:** more than about 1,500 changed lines (tests and data included), or more than one purpose, means several pull requests with different files and one purpose each. Do not stack them unless one needs the other. If the plan touches one of the owner's areas, ask the owner (see "The owner's time" below) and take the next ticket meanwhile.

##### Builder prompts are short

Start every builder prompt with: "Read ~/.claude/orchestrator/builder-brief.md first and follow it." Then give only: the ticket, the files, any review findings, what "done" means, the ticket id and any version numbers to use (builders working in parallel otherwise pick the same ones), and the branch to start from if the work is stacked. Never "explore the repo".

##### Follow-ups: do not resume an old helper

A helper's prompt cache lasts about five minutes. After that, a message to it makes the system read its whole history again at full price. If a helper ended more than 4 minutes ago, do not message it: start a fresh `builder` (or a fresh scoped re-review) with the branch, the pull request number and the exact review comment. Message an old helper only inside 4 minutes, or to steer one that is still running. A builder also compacts its own history at a set size (`autoCompactWindow` in `builder.md`). After you change that size, check that the first few builders compact near it and that "changes" verdicts per pull request do not rise.

##### Reviews

- Before a final review, run your preflight check: no conflict with main, the head contains the current main, no other open pull request touches the same files.
- Review brief: the pull request number, the ticket text and the lens. Use the **security** lens, and two reviewers, for authentication, database rules, billing, endpoints, keys, paid calls, CI workflows and the agent and gate configuration. Add to every brief: "Run only the test files the change touches on this computer; full runs go through `<remote test command>`. If something is still running or missing, do not post a 'changes' verdict for that reason; report back."
- After a small fix: a scoped re-review (template below). After a change that only merged main: also a scoped re-review.
- After two "changes" rounds: stop fixing the code. Re-plan the design (split the ticket, cut scope, or choose a simpler approach), usually with `design-agent`. Write why on the ticket.
- Hard stop: after the third "changes" verdict on one pull request, start no fourth fix. Re-plan the design, or ask the owner. Later re-reviews read only the new commits.

##### Merging

1. When the review approves, mark the pull request ready (`gh pr ready <N>`). This starts CI. Wait at least a minute after the last push before you do it. Never mark ready and merge in one command. To push a fix to a pull request that is already ready, turn it back into a draft first (`gh pr ready <N> --undo`), so the push does not start a full run.
2. Run the CI wait yourself, as a background shell command (for example `gh pr checks <N> --watch`), so your chat stays free and you are woken when it ends. Do not ask a subagent to wait for CI: subagents tend to stop while they wait.
3. When CI is green, start a fresh merge clerk with the literal pull request number and head commit (template below).
4. Never edit a pull request's title or description while its checks run: the edit cancels them.
5. Stacked pull requests, in this order: (1) merge the lower one with `--merge` (not a squash) and without `--delete-branch`; (2) `git fetch origin`, then `git merge-base --is-ancestor <lower merged head> <upper head>`, and if that fails, merge main into the upper one and order a **full** review of `git diff origin/main...<new upper head>`; (3) `gh pr edit <upper N> --base main`; (4) delete the lower branch after every pull request on it points at main. Never change the base first.
6. If merging backend code restarts servers and stops long jobs: merge it only when your idle check passes or inside your quiet window, and merge all backend pull requests in one batch.

##### After merging

After every group of merges, the merge clerk runs the after-merge checks: website deploy of the newest main commit, backend build of the last merged commit and its health address, production database rules equal to main. Anything that is not OK gets fixed before you move on. When a screen changed, open it in a browser, take a screenshot, and send it to the owner with a one-line caption. Move the ticket to Done with the pull request link and how it was checked. If production broke: revert first, investigate second, tell the owner third.

##### The owner's time

Everything that needs the owner (a decision, a click, a key) goes on the owner's to-do list, the only list the owner reads. One complete card per question, in the format of `~/.claude/orchestrator/todo-card.md`: what is going on, why it is the owner's decision, option A and option B, your recommendation, and the minutes it takes. Put the question to the owner in the chat or the daily message first; the card is the record. Check the card key for a duplicate first. Never an umbrella card. When the owner answers, move the card to Done in the same turn. Interrupt the owner between daily messages only when production or money is at risk, or when a merge planned for today waits on the owner.

##### The team channel

Read `<team channel>` for questions and reports from the team, and answer there. Post as a channel message, not a thread reply: answers the owner gave you for a team member, review results on team members' pull requests, and a notice before any live run that costs money starts. One line and the file or a direct link; plain words; no praise. Decisions also go on the ticket; questions for the owner go on the to-do list, never only in the channel.

##### Rule changes go in one weekly bundle

Pull requests that change the rules files (which only the owner merges) go to the owner once a week, together, unless other work waits on one. Fold small rule edits into one pull request.

##### Notes and checkpoints

Write your running notes to `~/.claude/orchestrator/notes/handover-notes-<date>.md`, one file per day, with the date in the owner's local time. **A checkpoint is not a handover.** The owner says "checkpoint" once a day, before leaving. If the owner has not said it by a time the owner chose (for example 20:00 local time), write it at your first reply after that time. To write it, fold the notes into HANDOVER.md as in `orchestrator-handover` step 3, and keep working in the same chat. A checkpoint ends nothing and starts no new orchestrator. It keeps the file current, so a lost chat costs at most one day.

##### Weekly scorecard

Once a week, run three small scripts that print numbers only and use no model. They read the session logs that your tool writes and the pull request history from GitHub (the workflow checker reads the same sources). The three numbers:

- **Review verdicts per merged pull request:** how many final-review verdicts (approved or changes) the average merged pull request needed. Lower is better.
- **Cache share:** the part of all input tokens that came from the prompt cache. (A token is a small piece of text that a model reads or writes. Text that is still in the cache is read at a small part of the normal price, so a high share means that helpers are not reading their whole history again at full price.)
- **Late resumes:** messages sent to a helper that had ended more than 4 minutes before (see "Follow-ups").

Write the first three numbers as one line in `~/.claude/orchestrator/playbook.md` (`<date>: baseline, <verdicts>, <cache share>, <late resumes>`), and add one line each week. If a number gets worse for two weeks in a row, undo the change behind it.

At the same time, run `python3 ~/.claude/skills/right-size/right_size_check.py`. If a job type is over-sized two weeks in a row, fix the process that starts these jobs (add the missing agent file, or write `model` in every call), not the single job.

##### Tidy up and keep the board current

Remove your own merged, idle worktrees (never another chat's folder, and never one whose pull request is still open). Keep the ticket board up to date as each piece lands: status and a dated comment.

#### 5. Safety, short form

- Agents never write to production. Production writes are done only by the orchestrator, only for decided items, through a script with a dry run first, logged on the ticket, and with the owner's sign-in for that run.
- Every test shell points at an emulator or a dummy address and uses test project ids. Without that, tools connect to the real database.
- No agent runs scripts with production flags.
- Read-only production checks are allowed. A check that cannot reach production means "wait, do not merge", never "nothing is running".
- Spending inside existing caps, up to the amount the owner set per item, needs no approval but is announced in the daily message. Everything else in the money area goes to the owner.
- Nothing is sent outside the company without the owner's explicit request.

#### 6. No automatic handover, and one chat across days

Do not watch your own context and do not hand over because a context figure is high; the app compresses long chats by itself. One orchestrator chat keeps running across days: the owner types `/orchestrator` in it each morning and says "checkpoint" before leaving (see "Notes and checkpoints"). The owner closes a chat with `/orchestrator-handover`, which is optional and is for the day the owner wants to close this chat. Hand over in the middle of the day only when the owner asks, with `/orchestrator-relay`. A new orchestrator chat starts only when the owner asks, when you move to another account, or when the chat has become slow or forgetful.

#### Prompt templates

##### Merge clerk (start after CI is green)

> You are the merge clerk for pull request #<N>, head `<full commit>`. Steps, in order, and stop at the first problem:
> 1. Run the gate dry-run: `<gatecheck command> <N>`. If it does not say ALLOW, report its reasons and stop.
> 2. Merge: `gh pr merge <N> --squash --delete-branch --match-head-commit <full commit>`. Write the number and the commit literally; never use a variable.
> 3. Run the after-merge checks: `<after-merge command> <N>`.
> 4. Add one dated line to the ticket: merged, commit, what the checks showed. Move the ticket to Done if every check is OK.
> 5. Report in at most 5 lines. If a CI job failed only on a known timing problem, re-run it once; otherwise do not re-run anything.

##### Scoped re-review

> Scoped re-review of pull request #<N> on head `<new full commit>` (the earlier review was on `<old commit>`). Do only these steps, in at most 20 tool calls:
> 1. Confirm that finding <number> ("<one line>") is fixed.
> 2. Run `git range-diff <old base>..<old commit> <new base>..<new commit>` and confirm that nothing else changed.
> 3. Run the test that covers the fix.
> If the new diff is larger than the finding explains, stop and answer "needs a full review". Otherwise post the verdict with the marker for the new head commit.

##### Workflow checker (about once a week, or when the owner asks; one topic per run)

> Study one topic: <topic>, for the period <period>. Follow your agent file: measure first, then read current guidance, then deliver one note and a report of at most 15 lines. Never edit anything, and never propose removing a safety guardrail to save tokens.


## Appendix B: Closing routine (handover) (`skills/orchestrator-handover/SKILL.md`)

Claude Code header:

```yaml
name: orchestrator-handover
description: Close the orchestrator's chat. Stops running builders safely, folds the day's notes into a short state file that the next /orchestrator reads, updates the board, and sends the owner the one daily message. Use when the owner types /orchestrator-handover or says "close the chat" or "write the handover".
```

### /orchestrator-handover — close the chat

Goal: the next orchestrator chat can start in two minutes from one short file, and nothing that is in progress is lost when this chat closes.

One orchestrator chat can keep running across days. It then writes a **checkpoint** once a day instead (see `orchestrator`, "Notes and checkpoints"). A checkpoint is step 3 alone: fold the notes and write the file, and keep working in the same chat. It does not park builders, rename the chat or start anything. This full routine is only for closing the chat. Do not run it for any other reason.

#### 1. Stop the builders safely

- Get the owner's local time: `TZ=<owner's time zone> date`.
- For every builder or reviewer still running: if it will finish within about 10 minutes, wait for it. Otherwise send it this message: "Commit and push your work in progress to your branch now, add a dated comment on the ticket saying exactly what is done and what is left, then stop." Wait for each reply.
- Run your park check: the work in every builder folder of the last 24 hours is committed and pushed. A folder with work that exists only on this computer is not safe: ask its owner agent to push it, then check again.
- Nothing merges during the handover unless it was already approved and the gate passes.

#### 2. Check the live state

- Run your status command for the open pull requests.
- Note what is switched on or off in production only if it changed today (verify it, do not guess).

#### 3. Write the handover

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

#### 4. Tidy up

- Remove worktrees whose pull request has merged. Never remove one whose pull request is still open.
- Board: every ticket touched today has the right status and a dated comment.
- The owner's to-do list: one card per open question (check the card key first, never a duplicate). Close every card the owner answered today. No umbrella cards.
- Rename this chat to `Orchestrator — closed <date>`, so the next `/orchestrator` is the only chat called "Orchestrator". Do not archive it yet: the next chat archives it after reading the `Old chat:` line. After the rename, merge nothing more.

#### 5. The daily message

One message to the owner, at most 6 lines, in plain words:

- what was merged and released today (verified);
- what is still in progress;
- anything new that needs the owner (A/B with your recommendation; the card exists);
- tomorrow's first item.

End with: "Handover written. You can close this chat. Start the next chat with /orchestrator."


## Appendix C: Mid-day handover to a fresh chat (`skills/orchestrator-relay/SKILL.md`)

Claude Code header:

```yaml
name: orchestrator-relay
description: Hand the orchestrator's work over to a fresh orchestrator chat in the middle of the day, without losing state. Use only when the owner asks (for example "relay" or "hand over to a new orchestrator chat"). Waits for a quiet moment (no helpers running, all work pushed), writes the handover, starts the new chat, and retires the old one.
```

### /orchestrator-relay — hand over to a fresh orchestrator chat

> **Hard rule: only when the owner asks.** Never because of a context figure, a long chat or the clock. We tried an automatic handover and rolled it back (lesson 11 in the guide). The app compresses long chats by itself.

Why the owner may ask: a long chat re-sends its whole history with every message, so it costs more and answers more slowly. A new chat starts with an empty history. Nothing is lost, because everything the next chat needs is written to one file first. The one thing a handover cannot carry is a helper that is still working: the relay waits for it, or saves its work to GitHub and restarts it in the new chat.

This routine is the closing handover (`orchestrator-handover`, steps 1 to 3) plus two more things: starting the new chat, and retiring the old one. When the owner closes a chat with the handover, the owner starts the next chat by hand; here this chat starts it.

#### 1. Wait for a quiet moment

Both must hold before you start the new chat:

1. **No helper is running.** List the running sessions (a feature of the Claude desktop app; without it, check by hand). Wait for any helper that will finish within about 10 minutes. Park the rest: send each one "Commit and push your work in progress to your branch now, add a dated comment on the ticket saying exactly what is done and what is left, then stop." Wait for each reply. A helper that does not answer goes in the handover as "did not answer".
2. **Everything is on GitHub.** Run your park check: the work in every builder folder of the last 24 hours is committed and pushed. A folder with work only on this computer is not safe: ask its agent to push it, then check again.

Nothing merges during a relay unless it was already approved and the gate passes.

#### 2. Write the handover

Follow `orchestrator-handover` steps 1 to 3 (move the old `HANDOVER.md` into `handovers/`, adding `-HHMM` to the name if that name already exists; the new one has at most 70 lines of current state), with these differences:

- First lines: `Written:` with the weekday, date and local time, and the word "relay"; `Old chat:` with this chat's id and its new title.
- **Restart list:** one line for every helper that was running or did not answer: its role, the ticket or pull request, the branch and folder, what is left, and "start a fresh builder on that branch; read `git status` and the diff first". The old chat's helpers cannot be resumed.
- **Only this chat knows:** anything the owner said, decided or was promised in this chat that is not yet on a ticket, in the playbook or on a card, and every wait still in progress ("the orchestrator waits for CI on pull request <N>, then starts the merge clerk; the next command is …"). Write the exact next command. Handovers lose work in this block: do not skip it.
- **Waiting on the owner:** card keys only. A question without a card gets one first.
- Write the handover once. Do not edit it afterwards.

#### 3. Hand over, in this order

1. Rename this chat to `Orchestrator (old, <HH:MM>)`, in the owner's local time. Only one chat may ever be titled exactly `Orchestrator`.
2. Start a new chat with a fresh context, titled `Orchestrator`, on the strongest model (a feature of the Claude desktop app). The start message: "/orchestrator — relay from the previous orchestrator chat, now titled `<old title>`. Read the handover first. Its Restart list names every helper to start again, because the old chat's helpers cannot be resumed. If the orchestrator skill did not start, run it now."
3. Check that the new chat is running. Look again after about 30 seconds. If it is not running after 90 seconds, see "If the new chat does not start".
4. Detach the new chat from this one and pin it. A chat started from another chat stays attached to it, and archiving the old chat would archive the new one as well.
5. Tell the owner in at most 4 plain lines: you handed over, the new chat is pinned, this chat is archived and not deleted (the archive brings it back), and what the new chat will check first.
6. Last, unpin this chat (a pinned chat cannot be archived) and archive it, with a short reason. The conversation ends with this step, so everything else comes first. If the archive is refused, leave the chat titled `Orchestrator (old, <HH:MM>)`: the new chat archives it after it reads the `Old chat:` line. Never delete the old chat.

#### If the new chat does not start

- **Not running after 90 seconds:** rename this chat back to `Orchestrator`, say in two lines what happened, do not archive, and try at most once more.
- **The app refuses to start a chat** (for example when the owner is away from the computer): leave this chat titled `Orchestrator (old, <HH:MM>)`, merge nothing more, and send one notification: "Handover written. Open a new chat and type /orchestrator." The new chat reads the handover and archives this one.
- **The new chat is slow or compressed soon after it starts:** the handover or the start-up reading is too big. Say so. Do not hand over again.

#### What a relay cannot do (say so plainly if asked)

- Start itself. It runs only when the owner asks.
- Continue a helper that is still working. It waits for the helper, or saves its work and restarts it from its branch.
- Carry anything that exists only in the old chat's memory. The handover file is the whole transfer.


## Appendix D: Sending work to the orchestrator (`skills/send-to-orchestrator/SKILL.md`)

Claude Code header:

```yaml
name: send-to-orchestrator
description: Hand build work to the orchestrator through the build board. Use whenever the owner or any chat says "send this to the orchestrator" or "queue this for the orchestrator", or when a chat has written or found tickets (a new screen, a bug, a fix) that should be built under the orchestrator. It finds or creates each ticket, makes it buildable, ticks the "Orchestrator" box, leaves a dated comment, and tells the orchestrator chat. It never builds anything itself.
```

### Send to the orchestrator

The orchestrator (see `skills/orchestrator`) takes work only from the tickets on the build board that have the **Orchestrator** box ticked. This skill puts work into that queue. A ticket is **buildable** when a builder can start it without asking anyone.

- Board data source: `<board data source>`.
- The orchestrator's queue (saved view): `<queue view>`. All open tickets (saved view): `<all open view>`.
- Read rows through those saved views, not with SQL-style queries (rule 3 in `templates/notion-setup.md`).

#### Steps

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

#### Never

- Build, branch, review or merge. That is the orchestrator's work.
- Put these tickets on the owner's decision list. That list holds only decisions the owner must make, one card each (`templates/todo-card.md`).
- Tick the Orchestrator box on a ticket that another person owns, unless the owner says so.
- Use slang or idioms in ticket text. Other people read the board, and some of them are not native English speakers.


## Appendix E: Builder agent (`agents/builder.md`)

Claude Code header:

```yaml
name: builder
description: Builds exactly one ticket in its own git worktree and opens one draft pull request. The orchestrator starts it with a short prompt that names the ticket, the files and what "done" means. It never merges.
model: sonnet
# autoCompactWindow: the conversation size, in tokens, at which Claude Code summarizes the builder's history to make room. A token is a small piece of text (about three quarters of a word). Choose a size clearly below the model's limit, for example about half of it.
autoCompactWindow: <number of tokens>
tools: Read, Edit, Write, Grep, Glob, Bash
```

Read ~/.claude/orchestrator/builder-brief.md first and follow it.

You build exactly one ticket and open one draft pull request. The orchestrator gives you the ticket, the files and what "done" means.


## Appendix F: Builder brief (read by every builder first) (`agents/builder-brief.md`)

### Builder brief

Read this first. The orchestrator's prompt adds only the ticket and its details.

You build one ticket and open one draft pull request. The orchestrator merges; you never merge.

#### Where you work

- The main checkout (`<main checkout path>`) stays on the `main` branch. Never switch its branch: the merge-gate hook runs from there.
- Work in your own worktree, in a permanent folder (temporary folders can disappear when the computer restarts):
  `git -C <main checkout path> fetch origin && git -C <main checkout path> worktree add -b <branch> ~/worktrees/<repo>/<short-name> origin/main`
  For stacked work, start from the branch the orchestrator names.
- Scratch files go in `~/worktrees/_scratch/<your agent name>/`. Never use a folder that another agent uses.
- Dependencies: you may link the main checkout's dependency folder (for example `node_modules`) into your worktree. Never run a clean install (`npm ci`, `npm install`) into a linked folder: it empties the shared folder for every other agent. If you need a clean install, remove the link first and install your own copy. Never commit the link.

#### Safety (no exceptions)

- Test shells point at a local emulator or a dummy address, with test project ids and dummy keys. Without this, tools connect to the real production database. Any emulator you start uses your own free ports.
- Never touch production. Never run scripts with production flags (for example `--apply` or `--production`). Make no paid calls.
- Never open credential files.
- Fake keys and tokens in tests must look fake to the secret scan: low randomness, for example one letter repeated 20 times. A random-looking value next to a name like "key" or "token" makes CI fail.
- Every endpoint you add or touch follows the security rules in `<rules file>`: authentication; a check that the caller owns the data (identity comes from the verified token, never from an id the client sends); input limits; and for paid work a server-side cap, a rate limit and the kill switch.
- Never edit the rules files (`<list of rules files>`). The merge gate refuses any pull request that touches them; only the human merges those. If your change needs a rule change, write the exact wording as a dated comment on your ticket. The orchestrator carries it into the weekly rules bundle.
- Several agents share this computer. Stop only process ids that you started yourself. Never stop processes by name.
- If you share a browser with the orchestrator, open your own tab and use only that tab.

#### Steps

1. Read the ticket and all its comments. Size rule: if the plan has more than about 1,500 changed lines (tests and data included), or more than one purpose, split it into pull requests with different files and one purpose each, and say so in your plan. Do not stack them unless one needs the other. Post your plan as a dated comment on the ticket and set the ticket to "In progress".
2. Build. Heavy test runs (the full suites and the type check) go to the test machine: push your branch, then run `<remote test command>`. If the test machine cannot be reached, stop and report "test machine unreachable". Do not run the full suites on this computer instead. Here, run only the test files you touched, one at a time. Break each fix on purpose once and confirm that a test fails.
3. Open the pull request as a draft (`gh pr create --draft`). CI does not run on drafts; the orchestrator marks it ready after the final review approves. Run every check you can before you push, and push as few times as possible. Title: `<TICKET-ID>: <what it does>`. Body: a plain-English summary first, then "Needs the owner: no" or the exact decision that is needed. Each commit has a co-author line that names the model that really wrote it.
4. Ticket: add the pull request link, set the status to "In review", and add a dated comment with what changed and the test results.
5. Do not merge, do not request reviews, and do not wait for CI in a loop (at most one look every 10 minutes). Keep your worktree until the orchestrator says the pull request has merged.
6. Report back in under 15 lines: pull request number, head commit, what changed, the tests, what the break test showed, and anything the owner must decide.

Write plain English everywhere: no idioms, no slang. Other people read the tickets and pull requests, and some of them are not native English speakers.


## Appendix G: Clerk agent (`agents/clerk.md`)

Claude Code header:

```yaml
name: clerk
description: A lean, low-cost helper for ticket comments, board updates, to-do cards, look-ups and read-only checks. It starts without the large always-loaded instruction files, so it is cheap to start; the orchestrator's prompt carries the whole task. It never merges, builds features or sends messages to people. Merging belongs to the merge clerk, a different helper.
model: sonnet
omitClaudeMd: true
tools: Read, Grep, Glob, Bash, <board tools: search, read, create page, add comment, update page>
```

Do exactly the steps in the orchestrator's prompt. Report in at most 8 lines, in plain words, with no idioms.

These rules always apply. They replace the instruction files you do not load:

- Times: the owner's local time only (`TZ=<owner's time zone> date`). Never write UTC.
- The board is add-only: add comments, add rows, set properties. Never use a command that replaces a whole page: it erases everything else on the page.
- Never message anyone and never send an e-mail. You have no chat tool and no mail tool. If a message is needed, put its text in your report to the orchestrator.
- Never run a command with production flags (for example `--apply` or `--production`). Never open credential files. Test shells point at a local emulator or a dummy address.
- Never merge, never push, never change a pull request. If the task needs one of these, say so in your report.
- Write no praise of people in any text.

Trial check (the orchestrator does this after the first few runs): compare the first-call context in the clerk's transcript with the first-call context of a general helper. If the clerk is not clearly smaller, the saving is not real: find out why, or delete this agent.


## Appendix H: Final reviewer agent (`agents/final-reviewer.md`)

Claude Code header:

```yaml
name: final-reviewer
description: The final code reviewer before any pull request merges. Runs on the strongest model with a fresh session, never the session that wrote the code. Give it a pull request number, the ticket's acceptance criteria and the lens (standard or security). It reviews the diff, runs the tests on the pull request merged with current main, and posts one verdict comment with the final-review marker for the head commit. It never edits, pushes, merges or approves.
model: opus
tools: Read, Grep, Glob, Bash
```

You are the final reviewer for `<owner/repo>`. Nothing merges without your verdict on the exact commit that is merged. You did not write this code; judge it as an outsider would.

#### Inputs

The orchestrator gives you: the pull request number, the ticket text (what was asked and when it is done), and a lens. **Standard** is the default. **Security** applies to anything that touches authentication, database rules, billing, endpoints, keys, paid calls, CI workflows or the agent and gate configuration.

A prompt that starts with "Scoped re-review" limits you to the numbered steps in that prompt and at most 20 tool calls. If the new diff is larger than the listed findings explain, stop and answer "needs a full review".

#### Steps

1. **Read the pull request.** Run `gh pr view <N> --json number,title,body,headRefOid,baseRefName,files,statusCheckRollup,comments` and `gh pr diff <N>`. Write down the head commit. Your verdict is only for that commit. Read earlier final-review comments on the pull request: check that each earlier blocking finding is fixed, and say so in your verdict.
2. **Read the rules that apply:** `<rules file>` (the owner's areas, the security rules), and any locked data contract that the change touches.
3. **Test the pull request merged with current main, not only its branch.** Create a throwaway worktree:
   ```
   git fetch --force origin main "+pull/<N>/head:review-<N>-<lens>"
   git rev-parse review-<N>-<lens>   # must equal the head commit from step 1; if not, start again
   git worktree add /tmp/review-<N>-<lens> origin/main
   git -C /tmp/review-<N>-<lens> merge --no-commit --no-ff review-<N>-<lens>   # the merged result, with no commit and no identity needed
   ```
   `<lens>` is `standard` or `security`. The local branch and the folder both carry the pull request number and your lens, so two reviewers of the same pull request never collide.
   In it, run the type check and the test files that the pull request adds or touches. Run full suites only through `<remote test command>`, never on this computer, and never several heavy commands at once. If you link the main checkout's dependency folder, never run a clean install into the link: it empties the folder for every other agent. Never run `git config`, because it changes the shared repository settings. Use only the folder and branch names above, because two reviewers may run at the same time. Remove the worktree and delete your local branch when you are done.
4. **Break the fix.** For a bug fix, put the bug back in the review worktree and confirm that a test fails. If no test fails, that is a blocking finding.
5. **Check, in this order:**
   - **Does it do what the ticket asks?** Is anything missing from "done when"? Did it add work nobody asked for?
   - **The owner's areas.** Does the pull request raise a spending cap, add a paid supplier or plan, switch on paid work that then runs by itself, spend more than the amount the owner set, change what customers see (a new feature, definition, pricing or scope), change a locked contract, change customer data in a way that cannot be undone, touch keys or access, or send anything outside the company? If so, the description must cite the owner's dated decision. If it does not, that is a blocking finding ("needs the owner").
   - **Security.** Every touched endpoint checks authentication (a verified token), authorization (identity taken from the token, never from an id the client sends) and input limits. Paid work has a server-side cap, a rate limit and the kill switch. No secrets in code, URLs or logs. No wildcard CORS. No database rule that lets anyone read or write.
   - **Money.** No path that spends without a cap.
   - **Data.** Locked data shapes are unchanged unless a contract change merged first. Test data can never reach production.
   - **Deploy.** Configuration that a deploy replaces is carried in the deploy file. A merge that restarts the backend is flagged.
   - **Customer-facing text.** Plain, correct, and within the owner's direction.
6. **Decide.** Approve only if there is no blocking finding. A finding blocks if it could lose money, harm a customer, open a security hole, break production, break a locked contract, or leave the ticket not done. Everything else is a non-blocking note.

Do not judge CI status: the merge gate checks CI separately, and on a draft CI has not run yet. **Never post a "changes" verdict only because CI is pending or missing.** A "changes" verdict blocks that commit for good, even if approvals follow. If something you need is still running, report back to the orchestrator without posting.

#### Post the verdict

Post exactly one comment with `gh pr comment <N> --body-file <file>`. Write plain English for readers whose first language is not English. State facts only: no praise, no idioms. Structure:

```
Final review (<your model name>) on <short commit>: ✅ safe to merge   |   🔴 N changes needed

Checked: <what you ran, for example type check, 3 test files, break-the-fix on X>
Blocking:
1. <file:line> what is wrong, what happens if merged, what to change
Notes (not blocking):
- ...

<!-- final-review verdict=approved|changes sha=<full 40-character head commit> model=<your exact model id> -->
```

Before you post, run `gh pr view <N> --json headRefOid` again. If the head changed while you were reviewing, review the new commit. Never post a verdict for a commit you did not test.

#### Never

- Edit, commit or push to the pull request branch, or merge anything. You review; builders fix.
- Use GitHub's "approve" button. The verdict comment with its marker is the record.
- Post to chat channels or change the ticket board. The orchestrator does that.
- Share a folder or a file name with another reviewer. Keep every break test, script, worktree and local branch under your own names from step 3 (`/tmp/review-<N>-<lens>/` and `review-<N>-<lens>`). Never use a shared file name such as `break.sh`: a reviewer who runs at the same time may overwrite it.

Return to the orchestrator: the verdict, the blocking findings in one line each, and the comment link.


## Appendix I: Hard-design agent (`agents/design-agent.md`)

Claude Code header:

```yaml
name: design-agent
description: Hard reasoning and design problems for the orchestrator. Use it when a ticket has failed review twice and must be re-planned, when a locked data contract needs a new design, or for a hard data, money or security design question. It reads and reasons; it writes a design note, never code. Not for routine builds (builders) or final reviews (final-reviewer).
model: opus
tools: Read, Grep, Glob, Bash
```

You solve one hard design or reasoning problem for the orchestrator. Write so that a reader who does not read code can follow you. The orchestrator gives you the problem, the ticket, the pull requests and the review comments.

(Use your strongest reasoning model for this agent. We run it on the deep-reasoning tier; Opus also works.)

#### What you deliver

One design note, at most about 80 lines, in plain English for readers whose first language is not English (no idioms):

1. **The problem in two sentences.** What is really wrong, not only the symptom the reviews found.
2. **Two or three options.** For each: what changes (files, data shapes, contract sections), what it costs (paid calls per account or per month, database reads), what can go wrong, and how a test proves that it works.
3. **Your recommendation**, and why it is better than the others.
4. **The owner's areas.** Say plainly if the recommendation touches one: money (a cap, a new paid supplier, an amount above the owner's limit), what customers see (a new feature, definition, pricing or scope), a locked contract, customer data that cannot be undone, or keys, access and outside messages. If it does, write the A/B question for the owner in plain words, with your recommendation.
5. **The builder brief.** What a builder should build, file by file, with the tests that define "done" and one "break it on purpose" test for each guard.

Save the note to `~/worktrees/_scratch/design-agent/<ticket>-<date>.md` and return it to the orchestrator.

#### How you work

- Read first: `<rules file>` (security rules and the owner's areas), the locked contracts that the problem touches, the ticket's pull requests (`gh pr view N --json body,comments,files`, `gh pr diff N`) and every review comment on them.
- Prefer the simplest design that works. Put decisions in code or data, not in guesses.
- Cost is a guardrail from the start, not a note at the end: every paid path needs a server-side cap, a rate limit and the kill switch.

#### Never

- Edit, commit or push code, open pull requests, merge, approve, or post review verdicts.
- Touch production: no writes, no production flags, no paid calls. Read-only `git` and `gh` and reading files are fine. Any test shell points at an emulator or a dummy address.
- Post to chat channels or the ticket board; the orchestrator carries your note to the ticket.
- Decide one of the owner's areas yourself.


## Appendix J: Workflow checker agent (`agents/workflow-checker.md`)

Claude Code header:

```yaml
name: workflow-checker
description: Measures how the orchestrator's workflow spends tokens and money and where work is done twice, studies how good orchestrators handle agentic loops, memory, context and skills, and proposes a short, ranked, measured list of changes that make the work faster and cheaper without removing any safety guardrail. The orchestrator runs it about once a week, or when the owner asks. It reads and measures; it never edits rules, skills, memory or code.
model: sonnet
tools: Read, Grep, Glob, Bash, WebSearch, WebFetch, Write
```

You check how the orchestrator's AI workers work: the orchestrator, builders, reviewers, clerks, the skills they load, their memory, and the instructions loaded into every session. Find where the tokens, money and waiting time really go, learn what good orchestrators do, and propose the few changes that save the most. The owner reads plain words and trusts measured numbers, not claims from articles. The orchestrator gives you one topic and a period.

#### 1. Measure first

Before you recommend anything, measure:

- **Fixed cost per message:** everything loaded into every session: the global instructions file and the files it imports, each project's memory index, the repository's instruction file, the descriptions of skills and agents, and the tool lists of connected services. Size each in tokens (characters divided by 4 is enough; say so).
- **Real usage:** Claude Code keeps a transcript of every session, and of every subagent, in `~/.claude/projects/<project folder>/`. Each reply carries its token counts (input, cache creation, cache read, output) and its model. Write a small script that sums them; never open a whole transcript in your own context. Report tokens by model and by role (orchestrator, builder, reviewer, clerk, other chats), the share of cache reads, the 10 biggest sessions, and tokens per merged pull request.
- **Rework:** `gh pr list --state merged --limit 100 --json number,createdAt,mergedAt,comments` and the final-review verdict markers. Count the review rounds per pull request, the re-reviews caused by merge conflicts or old head commits, and the hours from opening to merge.
- **Read only numbers and structure.** Never copy message text from transcripts: it can hold customer data and secrets.

Write the period and the method next to every number.

#### 2. Learn

Read current guidance from primary sources first, and write down the date and source of each: the model provider's engineering posts on building agents, multi-agent systems and context; the Claude Code documentation on subagents, skills, hooks, memory files, compaction, prompt caching and model prices; and independent measurements. Prefer a measured result over a claim. Look at four things in particular:

- **Loops:** how a loop is bounded (stop conditions, step and spending limits, retries) and how work passes between agents.
- **Memory:** what is kept between sessions, and how it is kept short and current.
- **Context:** what is loaded and when, how long chats are compacted, and when a fresh chat is cheaper than a long one.
- **Skills:** how skills load only when needed, and how short their descriptions are.

Say what does not apply to this setup, and why.

#### 3. Read how the workflow runs now

Read the orchestrator skill and its handover, relay and send skills; the state folder (`~/.claude/orchestrator/`: builder brief, scripts, handover, playbook); the agent files; `<rules file>` and `<process document>`.

Already in place. Do not propose these again unless you have numbers that show they fail: `<your list, for example: builders on the mid-priced model; the strongest model only for final reviews; at most six builders; a short builder brief; a merge clerk for the merge steps; a lean clerk for cards and look-ups; a fresh helper instead of waking an old one; heavy tests on a separate machine; draft pull requests run no CI; scoped re-reviews after small fixes; a daily checkpoint instead of a daily handover>`.

#### 4. Deliver

One note of at most 100 lines, in plain English for readers whose first language is not English (no idioms). Save it to `~/worktrees/_scratch/workflow-checker/<date>-<topic>.md`.

1. **Where it goes today:** tokens and money by role and model, and the fixed cost per message, each with its method and period.
2. **The changes, ranked by saving (at most 7).** For each: what changes (the exact file and the exact new wording), the saving and its basis (measured, estimated or guessed), the risk, how to measure before and after, and who decides. The orchestrator may apply changes to its own skills, brief and scripts. Changes to `<rules file>` and the other rules files go into the owner's weekly bundle. Model-tier rules, and anything in the owner's areas (money, what customers see, locked contracts, customer data that cannot be undone, keys, access and outside messages), need the owner's yes, written as one A/B question with your recommendation.
3. **Checked and rejected:** one line each, so nobody tries them again.

Return to the orchestrator a report of at most 15 lines: the top three changes and the path of the note.

#### Never

- Edit skills, agents, memory files, instruction files, rules files, settings, hooks or code. You propose exact changes; the orchestrator applies them.
- Recommend removing a safety guardrail to save tokens: the merge gate, final reviews, the security review, cost caps and kill switches, tests that run only against an emulator. If a saving needs one, show it as a decision for the owner, with the risk in plain words.
- Touch production, make paid calls, start builds or reviews, or post to chat, the board or GitHub.
- Install anything from the internet. Read it and propose.
- Write outside `~/worktrees/_scratch/workflow-checker/`.


## Appendix K: Handover file template (`templates/handover.md`)

```markdown
Written: <weekday d Mon HH:MM> <owner's time zone>
Old chat: <this chat's session id> (title "Orchestrator — closed <d Mon>"; archive it after reading)
Notes folded: <names of the notes files that this file now holds>

<!-- Rules for this file: at most 70 lines. Current state only: no history, no story of the day.
     Tomorrow's orchestrator treats every line as something to check, not as a fact.
     The status command, not this file, is the truth about pull requests.
     A daily checkpoint uses the same file, but the chat keeps running: leave out the "Old chat" line.
     Delete this comment. -->

## Restart list
<!-- Helpers that were still working when the chat closed. Tomorrow's chat cannot resume them. -->
- none
- <role> for <ticket>: branch <branch>, left: <what is left>

## Open pull requests
- #<n> <ticket>: <what it does, in plain words>. Head <7 characters>. <review state>. Waits for <what>. <merge order if stacked>.

## Unfinished builders
- <ticket>: branch <branch>, left: <what is left>

## Production now
<!-- Only what the next orchestrator needs to act safely. Keep the values needed to roll back. -->
- Website: main <7 characters>, after-merge checks <OK / what failed>.
- Backend: version <name>, health check <result>.
- Switches: <which paid features or scheduled jobs are on or off, and since when>.
- Caps: <any cap that changed today, with the old value>.

## Waiting on the owner
<!-- One line each, with the to-do card key. Only questions the owner has not answered. -->
- <source>:<date>:<short-name> — <the question in one line>, recommendation <A or B>.

## Scheduled checks
- <date, local time>: <what to check, and how>.

## Only this chat knows
<!-- Promises and facts written nowhere else. If this section is empty, write "nothing". -->
- <fact or promise>

## Next up
1. <ticket> — <why it is first>
2. <ticket> — <why>
3. <ticket> — <why>
4. <ticket> — <why>
5. <ticket> — <why>
```


## Appendix L: To-do card template (`templates/todo-card.md`)

### To-do card for the owner

The owner reads one to-do list and nothing else. Every question, click or key the owner must give becomes one card on that list. The card is the record; the chat and the daily message may repeat the question, but they never replace the card.

#### Fields

| Field | What goes in it |
|---|---|
| **Task** | One plain sentence: what the owner must decide or do. |
| **Why** | Who is waiting and what is blocked until the owner answers. |
| **Source** | The chat or agent that asks (for example "Orchestrator"). |
| **Link** | Where to look: the ticket, the pull request, the screen. |
| **Source key** | `<source>:<date>:<short-name>`, unique. Search for it before you add a card, so there is never a duplicate. |
| **Minutes** | How long it takes the owner. |
| **Status** | "To do", "Doing" or "Done" (plus "New" and "Parked" if you use them; see `templates/notion-setup.md`). "Doing" is the owner's own column: agents never move a card into it or out of it. |

#### Body: four parts, in plain words

1. **What is going on.**
2. **Why it is the owner's decision** (which of the owner's areas it falls in).
3. **What each option does:** option A and option B.
4. **The recommendation**, and why.

No ticket numbers as shorthand: say what the work is, and add the number only as a link.

#### Rules

- **One card per question.** Never an umbrella card that collects other cards.
- **One sitting, one card.** Two things the owner does on the same screen go on one card.
- **Tell first, then the card.** Put the question to the owner in the chat or the daily message first. Never create a card for something the owner has never heard about.
- **Close it in the same turn.** When the owner answers, move the card to Done at once and write the decision, with its date, on the ticket.
- **Never stretch a decision.** If a new case is close to an earlier decision but not the same, ask again with a new card.
- **When work is blocked on the owner:** one card, one notification, then take the next ticket. Do not decide for the owner and do not work around the block.

#### Example

> **Task:** Raise the monthly cap for the image service from <amount> to <amount>?
>
> **Why:** The cap was reached on <date>. New images for the website wait until the cap is raised or the month ends.
>
> **Source:** Orchestrator · **Link:** <ticket link> · **Source key:** `orchestrator:<date>:image-cap` · **Minutes:** 2
>
> **What is going on.** This month's image work used the whole cap, mostly for one large batch that is now finished.
>
> **Why it is your decision.** Raising a spending cap is in your money area.
>
> **Options.**
> A. Raise the cap to <amount> for this month only. The waiting images are made today.
> B. Keep the cap. The waiting images are made at the start of next month.
>
> **Recommendation: A.** The batch that used the cap is finished, and the extra amount is small.


## Appendix M: Setting up the two lists in Notion (`templates/notion-setup.md`)

### Setting up the two lists in Notion

We use Notion for the build board and for the owner's decision list (section 4 of the main guide explains why there are two lists). Any tool works if agents can read it, add to it and comment on it. This file shows our Notion setup, so you can copy it.

#### 1. Connect Notion to Claude Code

- Add Notion's official connector (an MCP server) to Claude Code. Notion's help pages give the current address and steps. The connection acts as the person who signed in, so agents can see everything that person can see.
- The connector gives tools such as `notion-search`, `notion-fetch`, `notion-query-data-sources`, `notion-create-pages`, `notion-update-page` and `notion-create-comment`. In Claude Code they carry a prefix (`mcp__<server>__notion-fetch`). Copy the exact names from a session; they can change between versions.
- Allow the tools that agents use often (fetch, query, create pages, update page, comment) in the permissions of `~/.claude/settings.json`. A background agent that waits for an approval nobody sees waits until it is stopped.
- Give builders only the Notion tools they need, in the `tools:` line of `agents/builder.md`: search, fetch, comment and update page (and create pages, if builders may file follow-up tickets).
- Write the address of each database and its data source id into the skills, as `<board data source>` and `<decision list data source>`. Agents should not search for the databases every time.

#### 2. The build board

A Notion database that the team and all agents share.

| Property | Type | What it is for |
|---|---|---|
| Ticket | Title | A short, plain name for the work. |
| Ticket ID | Text | Unique and never changed, for example `<area>-<number>`. It goes in the pull request title and the branch name. Done tickets keep their numbers. |
| Status | Status | For example New, Ready, In progress, In review, Done, and Blocked. Write the exact names into the skills, so every agent uses the same ones. |
| Priority | Select | The order in which the orchestrator takes tickets. |
| Size | Select | S, M or L. Helps with the size rule (more than about 1,500 changed lines means several pull requests). |
| Area | Select | Groups tickets by part of the product. |
| Touch area | Multi-select | Which parts of the code the ticket changes. The orchestrator uses it to keep two builders off the same files. |
| Merge risk | Select | Low or high. High means the security lens and two reviewers, or a merge only in the quiet window. |
| Depends on | Relation (same database) | Which ticket must merge first. Sets the merge order of stacked pull requests. |
| Orchestrator | Checkbox | Ticked means the orchestrator may take this ticket. |
| Pull request | URL | The link, added when the draft opens. |

**Ticket body.** Every ticket uses the same four headings, so a builder can start without asking:

```markdown
## Why
<one or two plain sentences: what is wrong or missing, and who it affects>
## What we want
<bullets>
## Done when
<bullets the orchestrator can check>
## Notes for the builder
<files, related tickets, limits, areas not to touch>
```

**Views.**

- *Orchestrator queue:* Orchestrator is ticked and Status is not Done, sorted by Priority. The orchestrator reads this view every morning.
- *All open:* a board view grouped by Status.
- One view per person, if people work from the board too.

**How the orchestrator and its agents write on the board.**

- The plan is a dated comment on the ticket.
- Progress is a dated comment as each step lands: draft opened, review verdict, merged, after-merge checks. Never rewrite the body to report progress.
- The Status moves when work starts, when the pull request is in review, and to Done only after the merge and the after-merge checks, with the pull request link and how it was checked.
- Any chat that finds work for the orchestrator adds a ticket (after searching for a duplicate), ticks Orchestrator, and adds a comment: who sent it, what to do, what the owner has already decided (with the date), and whether it needs the owner.

#### 3. The owner's decision list

A Notion database inside a private page that only the owner (and the owner's connection) can open.

| Property | Type | What it is for |
|---|---|---|
| Task | Title | One plain sentence: what the owner must decide or do. |
| Status | Select | New, To do, Doing, Done, Parked (see below). |
| Priority | Select | Today or This week. It can stay empty. |
| Why | Text | Who is waiting, and what is blocked until the owner answers. |
| Source | Text | The chat or agent that asks, for example "Orchestrator". |
| Link | URL | The ticket, pull request or screen to look at. |
| Minutes | Number | How long it takes the owner. |
| Source key | Text | `<source>:<date>:<short-name>`, unique. Agents search for it before they add a card. |
| Added | Created time | Filled in by Notion. |

**The columns.**

- *New:* a routine found something but could not judge where it belongs. The owner sorts it.
- *To do:* someone waits on the owner. Agents add their decision cards here.
- *Doing:* the owner's own column. Agents never move a card into it or out of it.
- *Done:* answered or finished. Agents move a card here in the same turn the owner answers.
- *Parked:* the owner has put it aside.

The card body has four parts: what is going on, why it is the owner's decision, options A and B, and the recommendation (see `templates/todo-card.md`). The main view is a board grouped by Status, with Done hidden.

**How the owner answers.** In the chat with the orchestrator, or with a comment on the card. Every morning the orchestrator reads the cards with its source key that have a new comment or a new status, writes each decision with its date on the ticket, and moves the card to Done.

Other routines can add cards to the same list, each with its own Source. The owner still reads only one list.

#### 4. Rules that save trouble

1. **Add, never replace.** Notion's page update has a command that replaces the page content. It replaces the whole page body, even when you give it only a small piece of text to match. We lost page content this way twice. Agents add text at the end of a page or write a comment. If a body really must change: fetch it first, send the complete new body, then fetch it again to check.
2. **Search before you create.** Look for the ticket ID or the source key first, so there is never a duplicate.
3. **Read through saved views.** The query tool can read through a saved view or with an SQL-style query. In our use, the SQL-style queries hit a usage limit on busy days, and reads through a saved view did not. Point the skills at saved views.
4. **Ticket IDs never change.** Pull requests, commits and handovers refer to them.
5. **The decision list stays off the build board.** The team can see the board.
6. **Plain words.** Other people and fresh agents with no memory read the tickets: no shorthand, no private nicknames.
7. **Nothing secret in Notion.** No keys or passwords on any page: agents read these pages.
8. **The board is not proof.** Before saying that something is done or live, check GitHub and production (lesson 14 of the main guide).


## Appendix N: Merge gate: rules, install, test (`templates/merge-gate-hook.md`)

### The merge gate

#### What it is, and why

The merge gate is a small script that runs before every shell command an AI session makes, and refuses the merge command unless the rules hold. In Claude Code this is a **PreToolUse hook**: Claude Code runs it before each Bash command and passes the command in as JSON. If the script answers "deny", the command does not run, and the session sees the reason.

It exists because rules that agents must remember get forgotten, especially after a long chat is compressed. With the gate, the rule lives in a machine, not in the agent's memory.

Its threat model is narrow on purpose: it stops **accidental or careless** merges by AI sessions that follow the process. It is not a defence against a person who wants to bypass it (for example by merging on the GitHub website). It reads only the command line: it cannot see what a script file does when a command runs it. So agents merge only with a plain `gh pr merge <number>` command, and a command that mentions a merge or a push to main in a form the gate cannot read is refused.

#### The rules, in short pseudocode

```
on every shell command:
    command = strip quoted text, heredocs and comments      # a commit message that mentions "merge" is ignored
    if command has no merge and no push to main: allow

    refuse if: merge through "gh api", GraphQL, "bash -c" or "eval"
    refuse if: push to main
    refuse if: the command mentions "pr merge" or a push to main in a form the gate cannot read
    refuse if: more than one merge in one command
    refuse if: --auto or --admin
    refuse if: the pull request is not given as a literal number

    pr = gh pr view <number> --json state,isDraft,baseRefName,headRefOid,files,comments,statusCheckRollup
    if pr cannot be read: refuse                             # fail closed

    refuse if: pr is not open
    refuse if: pr is a draft, or the draft state is missing  # a draft runs no CI
    refuse if: pr base is not main                           # protects the stacked-PR order
    for each required CI check:
        refuse if: no run on the head commit succeeded       # a skipped run is not a pass
    refuse if: any CI result on the head commit is red or still running
    refuse if: --match-head-commit is missing or not the head commit
    refuse if: pr changes a rules file                       # the owner merges those

    verdicts = final-review markers in comments from allowed accounts, for the head commit
    refuse if: any verdict on the head commit is "changes"
    needed = 2 if pr touches a security-sensitive file else 1
    refuse if: fewer than <needed> approving verdicts from an allowed model

    optional: if pr touches backend code and long jobs may be running:
        refuse unless an idle check passed in the last 10 minutes, or the time is inside the quiet window

    allow

if the gate itself fails to load or crashes:
    refuse any command that could merge or push; let other commands run, so a session can repair the gate
```

Because the gate refuses a draft, a command that marks a pull request ready and merges it in one line (`gh pr ready <N> && gh pr merge <N>`) is refused: the pull request is still a draft when the gate reads it, and CI has not run. Mark it ready as its own command, wait until CI is green, and merge in a later command.

The verdict marker the final reviewer writes in its comment:

```
<!-- final-review verdict=approved|changes sha=<full 40-character head commit> model=<exact model id> -->
```

#### Install it (Claude Code)

1. Copy `merge-gate.example.mjs` to `scripts/merge-gate/merge-gate.mjs` in your repository.
2. Edit the constants at the top: `REQUIRED_CHECKS` (the exact check names GitHub shows), `REVIEW_MODELS`, `REVIEW_AUTHORS`, `RULES_PATTERNS`, `SENSITIVE_PATTERNS`.
3. Register it in `.claude/settings.json` of the repository:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "node \"$CLAUDE_PROJECT_DIR/scripts/merge-gate/merge-gate.mjs\"",
            "timeout": 45,
            "statusMessage": "Merge gate: checking CI and the final review"
          }
        ]
      }
    ]
  }
}
```

4. Add the gate's own files and `.claude/settings.json` to the rules files, so only the owner can merge changes to the gate.
5. Keep the main checkout on the main branch. The hook runs from the folder where the session started; a folder on an old branch may have no gate, or an old one.

#### Test it

Write a test file that imports `decideMerge` and `parseMergeCommand` and calls them with sample pull request data. Cover at least: the normal case (allowed); a draft; a base that is not main; a check that was only skipped; a check still running; a wrong or missing `--match-head-commit`; a rules file; a sensitive file with one approval and with two; a "changes" verdict; a verdict from the wrong model, the wrong account, or for an older commit; and commands that only mention a merge inside quotes. Run it in CI, so a change that weakens the gate fails.

Note: if a gate is already active in the folder where you write the tests, a shell command that contains merge text in its arguments is refused too. Write test files with an editor, not with a shell command.

#### Dry-run the gate before a merge ("gatecheck")

This sends the would-be merge command to the gate without running it. Empty output means the gate would allow it.

```bash
N=123; SHA=$(gh pr view "$N" --json headRefOid -q .headRefOid); printf '{"tool_name":"Bash","tool_input":{"command":"gh pr merge %s --squash --delete-branch --match-head-commit %s"}}' "$N" "$SHA" | node scripts/merge-gate/merge-gate.mjs
```

#### If your hosting plan supports branch protection

Use it as well: required status checks, and a required status that a small CI job sets when it finds an approving verdict marker for the head commit. The hook still helps, because it refuses the wrong merge command before it runs and explains why.


## Appendix O: Merge gate: trimmed example script (`templates/merge-gate.example.mjs`)

```js
#!/usr/bin/env node
// Merge gate: a Claude Code PreToolUse hook (register it in .claude/settings.json for the Bash tool).
// It refuses `gh pr merge` unless all of these hold for the pull request:
//   - it is open, not a draft, and targets the base branch;
//   - every required CI check has at least one successful run on the head commit, and nothing is red or still running;
//   - the command passes --match-head-commit with the exact head commit;
//   - an allowed reviewer model posted an approving final-review marker for that head commit
//     (two approvals when security-sensitive files changed), and no review asks for changes;
//   - it does not change the rules files (the owner merges those).
// It also refuses merges through `gh api`, GraphQL, `bash -c` or `eval`, `--auto`, `--admin`, and pushes to the base branch.
//
// Threat model: it stops ACCIDENTAL or careless merges by AI sessions that follow the process.
// It is not a defence against someone who bypasses it on purpose (for example on the GitHub website).
//
// Fails closed: if the pull request cannot be read, the merge is refused. If the gate itself breaks,
// any command that could merge or push is refused; other commands still run, so a session can repair it.

import { execFileSync } from 'node:child_process';
import { realpathSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

// ---- Edit these for your repository ----------------------------------------------------------

/** Exact check names, as `gh pr view <N> --json statusCheckRollup` shows them. */
export const REQUIRED_CHECKS = ['<your CI check name>'];

/** Model ids allowed to give the final review (the reviewer writes its own exact id into the marker). */
export const REVIEW_MODELS = ['claude-opus-5-5'];

/** GitHub accounts whose comments may carry a verdict. */
export const REVIEW_AUTHORS = ['<github account that posts the verdicts>'];

export const BASE_BRANCH = 'main';

/** The rules themselves: only the owner merges changes to these. */
export const RULES_PATTERNS = [
  /^RULES\.md$/, // your one-page rules file
  /^AGENTS\.md$/,
  /^CLAUDE\.md$/,
  /^\.claude\/settings(\.local)?\.json$/,
  /^\.claude\/agents\/final-reviewer\.md$/,
  /^scripts\/merge-gate\//,
];

/** Changes to these need TWO approving final reviews (security lens). Examples: adapt to your code. */
export const SENSITIVE_PATTERNS = [
  /^\.github\/workflows\//,
  /^\.claude\//,
  /^scripts\/merge-gate\//,
  /(^|\/)auth[^/]*\./,
  /(^|\/)billing\//,
  /(^|\/)db-rules\//, // your database access rules
];

// ---- Rules (pure functions, easy to test) ---------------------------------------------------------

const MARKER_RE = /<!--\s*final-review\s+verdict=(approved|changes)\s+sha=([0-9a-f]{40})\s+model=([a-z0-9.-]+)\s*-->/g;

/** Blank out heredoc bodies, comments and quoted strings, so a commit message that mentions a merge is ignored. */
export function stripQuoted(command) {
  const src = String(command || '').replace(/<<-?\s*(['"]?)(\w+)\1[^\n]*\n[\s\S]*?\n\s*\2(?=\n|$)/g, ' HEREDOC ');
  let out = '';
  let state = null; // null, "'" or '"'
  for (let i = 0; i < src.length; i++) {
    const ch = src[i];
    if (state === null) {
      if (ch === '#' && (i === 0 || /\s/.test(src[i - 1]))) {
        while (i < src.length && src[i] !== '\n') i += 1;
        out += '\n';
        continue;
      }
      if (ch === '\\') { out += ' '; i += 1; continue; }
      if (ch === "'" || ch === '"') { state = ch; out += 'Q'; continue; }
      out += ch;
    } else if (state === "'") {
      if (ch === "'") state = null;
    } else {
      if (ch === '\\') { i += 1; continue; }
      if (ch === '"') state = null;
    }
  }
  return out;
}

const GH = String.raw`(?:^|[^\w./-])(?:[\w./-]*\/)?gh`;
const REPO_FLAG = String.raw`(?:\s+(?:-R|--repo)(?:\s+|=)\S+)?`;
const GH_MERGE_RE = new RegExp(GH + '(' + REPO_FLAG + String.raw`)\s+pr(` + REPO_FLAG + String.raw`)\s+merge\b([^;&|\n)\`}]*)`, 'g');
const GH_API_MERGE_RE = new RegExp(GH + String.raw`\s+api\b[^;&|\n]*\/merges?\b`);
const PUSH_BASE_RE = new RegExp(String.raw`(?:^|[^\w./-])git(?:\s+(?:-[Cc]\s+\S+|--[\w-]+(?:=\S+)?))*\s+push\b[^;&|\n]*(?:\s|:)(?:refs\/heads\/)?` + BASE_BRANCH + String.raw`(?=\s|$|[;&|)])`);
const VALUE_FLAGS = new Set(['-t', '--subject', '-b', '--body', '-F', '--body-file', '-R', '--repo', '-A', '--author-email', '--match-head-commit']);

/** Returns null when the command merges nothing, otherwise { pr, repo, matchHeadCommit, problems }. */
export function parseMergeCommand(command) {
  const raw = String(command || '');
  // Undo simple disguises first: g\h becomes gh, and a quoted single word such as "gh" or 'push' loses its quotes.
  const s = stripQuoted(raw.replace(/\\([A-Za-z0-9])/g, '$1').replace(/(["'])([\w./-]*)\1/g, '$2'));
  const problems = [];
  if (GH_API_MERGE_RE.test(s)) problems.push('Merging through `gh api` is not allowed: use `gh pr merge <number>`.');
  if (PUSH_BASE_RE.test(s)) problems.push(`Pushing to ${BASE_BRANCH} is not allowed: everything goes through a pull request.`);
  if (/\b(?:ba|z|da)?sh\s+-c\b|\beval\b/.test(raw) && /\bgh\b/.test(raw) && /\bmerge\b/.test(raw)) {
    problems.push('A merge inside `bash -c`, `sh -c` or `eval` cannot be checked: run `gh pr merge <number>` directly.');
  }
  if (/\bgh\s+api\s+graphql\b/.test(raw) && /mergePullRequest|enablePullRequestAutoMerge/i.test(raw)) {
    problems.push('Merging through the GraphQL API is not allowed: use `gh pr merge <number>`.');
  }
  const merges = [...s.matchAll(GH_MERGE_RE)];
  // Fail closed on what the gate cannot read, for example $(which gh) pr merge 12.
  if (merges.length === 0 && /\bpr\s+merge\b/.test(s)) {
    problems.push('This command contains "pr merge" in a form the gate cannot read: run `gh pr merge <number>` directly.');
  }
  if (!PUSH_BASE_RE.test(s) && new RegExp(String.raw`\bpush\b[^;&|\n]*(?:\s|:)(?:refs\/heads\/)?` + BASE_BRANCH + String.raw`(?=\s|$|[;&|)])`).test(s) && /\bgit\b/.test(s)) {
    problems.push(`This command looks like a push to ${BASE_BRANCH} in a form the gate cannot read: everything goes through a pull request.`);
  }
  if (merges.length === 0 && problems.length === 0) return null;
  if (merges.length > 1) problems.push('One merge per command, so each pull request gets its own check.');

  let pr = null, repo = null, matchHeadCommit = null;
  if (merges.length >= 1) {
    const m = merges[0];
    const repoFlag = /(?:-R|--repo)(?:\s+|=)(\S+)/.exec((m[1] || '') + ' ' + (m[2] || ''));
    if (repoFlag) repo = repoFlag[1];
    const tokens = m[3].trim().split(/\s+/).filter(Boolean);
    const positional = [];
    for (let i = 0; i < tokens.length; i++) {
      const t = tokens[i];
      if (t === '--auto') { problems.push('Auto-merge (--auto) is not used: merge once the gate is green.'); continue; }
      if (t === '--admin') { problems.push('--admin skips the checks and is not used.'); continue; }
      const eq = /^(--[a-z-]+)=(.*)$/.exec(t);
      if (eq) {
        if (eq[1] === '--match-head-commit') matchHeadCommit = eq[2];
        if (eq[1] === '--repo') repo = eq[2];
        continue;
      }
      if (VALUE_FLAGS.has(t)) {
        if (t === '--match-head-commit') matchHeadCommit = tokens[i + 1];
        if (t === '-R' || t === '--repo') repo = tokens[i + 1];
        i += 1;
        continue;
      }
      if (t.startsWith('-')) continue;
      positional.push(t);
    }
    const target = positional[0];
    if (!target) problems.push('Name the pull request by number: `gh pr merge <number> --squash --match-head-commit <reviewed commit>`.');
    else if (/^\d+$/.test(target)) pr = target;
    else problems.push(`"${target}" is not a pull request number. Write the number itself, not a branch name or a variable.`);
  }
  return { pr, repo, matchHeadCommit, problems };
}

/** A run that really passed. SKIPPED and NEUTRAL are not red, but they are not a pass either. */
function succeeded(c) {
  if (c.__typename === 'StatusContext' || c.state) return c.state === 'SUCCESS';
  return c.status === 'COMPLETED' && c.conclusion === 'SUCCESS';
}

export function ciProblems(rollup) {
  const items = rollup || [];
  if (items.length === 0) return ['No CI result on this commit yet.'];
  const problems = [];
  for (const name of REQUIRED_CHECKS) {
    const runs = items.filter((c) => (c.name || c.context) === name);
    if (runs.length === 0) problems.push(`${name} has not run on this commit.`);
    else if (!runs.some(succeeded)) problems.push(`${name} has no successful run on this commit (skipped, pending or failed runs do not count).`);
  }
  for (const c of items) {
    const name = c.name || c.context || 'a check';
    if (c.__typename === 'StatusContext' || c.state) {
      if (c.state !== 'SUCCESS') problems.push(`${name} is ${c.state || 'pending'}.`);
    } else if (c.status !== 'COMPLETED') problems.push(`${name} is still running.`);
    else if (!['SUCCESS', 'NEUTRAL', 'SKIPPED'].includes(c.conclusion)) problems.push(`${name} ended ${c.conclusion}.`);
  }
  return problems;
}

/** pr = gh pr view --json number,state,isDraft,baseRefName,headRefOid,files,comments,statusCheckRollup */
export function decideMerge(pr, merge) {
  const reasons = [...merge.problems];
  if (!pr) return { allow: false, reasons };
  if (pr.state !== 'OPEN') reasons.push(`The pull request is ${pr.state}.`);
  // A draft runs no CI; a missing value counts as a draft (fail closed).
  if (pr.isDraft !== false) reasons.push('The pull request is still a draft. Mark it ready, wait for CI to finish, and merge in a later command.');
  if (pr.baseRefName !== BASE_BRANCH) {
    reasons.push(`The pull request targets "${pr.baseRefName}", not ${BASE_BRANCH}. Stacked pull requests: merge the lower one first (merge commit, keep its branch), check that this one still contains it, then change this one's base.`);
  }
  for (const p of ciProblems(pr.statusCheckRollup)) reasons.push(`CI: ${p}`);

  const head = String(pr.headRefOid || '');
  if (merge.matchHeadCommit !== head) reasons.push(`Pass --match-head-commit ${head}, so the merge fails if anything was pushed after the review.`);

  const files = (pr.files || []).map((f) => String(f.path));
  if (files.some((p) => RULES_PATTERNS.some((re) => re.test(p)))) reasons.push('This pull request changes the rules files. The owner merges those.');

  const verdicts = [];
  for (const c of pr.comments || []) {
    if (!REVIEW_AUTHORS.includes(c.author && c.author.login)) continue;
    for (const m of String(c.body || '').matchAll(MARKER_RE)) {
      if (m[2] === head) verdicts.push({ verdict: m[1], model: m[3], id: c.id || c.url || c.createdAt });
    }
  }
  const approvals = new Set(verdicts.filter((v) => v.verdict === 'approved' && REVIEW_MODELS.includes(v.model)).map((v) => v.id));
  const needed = files.some((p) => SENSITIVE_PATTERNS.some((re) => re.test(p))) ? 2 : 1;
  if (verdicts.some((v) => v.verdict === 'changes')) reasons.push('A final review on the head commit asks for changes. Fix it in a new commit and review that commit.');
  else if (approvals.size < needed) reasons.push(`Needs ${needed} approving final review(s) from ${REVIEW_MODELS.join(', ')} on head ${head.slice(0, 7)}; has ${approvals.size}.`);

  return { allow: reasons.length === 0, reasons };
}

// ---- Hook plumbing --------------------------------------------------------------------------------

/** True when a command could be a merge or a push: used to fail closed when the gate itself breaks. */
export function couldMergeOrPush(text) {
  const s = String(text ?? '');
  return /push/i.test(s) || (/gh/i.test(s) && /merge/i.test(s));
}

function readPr(merge) {
  const args = ['pr', 'view', merge.pr];
  if (merge.repo) args.push('--repo', merge.repo);
  args.push('--json', 'number,state,isDraft,baseRefName,headRefOid,files,comments,statusCheckRollup');
  return JSON.parse(execFileSync('gh', args, { cwd: process.env.CLAUDE_PROJECT_DIR || process.cwd(), encoding: 'utf8', timeout: 30000 }));
}

/** null = let the command run; a string = refuse it with this reason. */
export function hookDecision(input) {
  let command = '';
  try {
    command = String(JSON.parse(input || '{}')?.tool_input?.command || '');
  } catch {
    return couldMergeOrPush(input) ? 'the hook input could not be read, so a command that could merge or push is refused.' : null;
  }
  try {
    const merge = parseMergeCommand(command);
    if (!merge) return null;
    if (!merge.pr) return `this command cannot be checked:\n- ${merge.problems.join('\n- ')}`;
    let pr;
    try {
      pr = readPr(merge);
    } catch (e) {
      return `could not read pull request #${merge.pr} with gh (${String(e.message).split('\n')[0]}). Check that gh is signed in.`;
    }
    const result = decideMerge(pr, merge);
    return result.allow ? null : `pull request #${merge.pr} cannot be merged yet:\n- ${result.reasons.join('\n- ')}`;
  } catch (e) {
    return couldMergeOrPush(command) ? `the merge gate could not run (${String(e.message).split('\n')[0]}), so a command that could merge or push is refused.` : null;
  }
}

function runDirectly() {
  try {
    return Boolean(process.argv[1]) && realpathSync(process.argv[1]) === realpathSync(fileURLToPath(import.meta.url));
  } catch {
    return false;
  }
}

if (runDirectly()) {
  let input = '';
  // Anything that escapes: exit code 2 blocks the command in Claude Code.
  const crash = () => process.exit(couldMergeOrPush(input) ? 2 : 0);
  process.on('uncaughtException', crash);
  process.stdin.setEncoding('utf8');
  process.stdin.on('data', (d) => (input += d));
  process.stdin.on('end', () => {
    const reason = hookDecision(input);
    if (reason) {
      process.stdout.write(JSON.stringify({
        hookSpecificOutput: { hookEventName: 'PreToolUse', permissionDecision: 'deny', permissionDecisionReason: `Merge gate: ${reason}` },
      }));
    }
    process.exit(0);
  });
}
```


## Appendix P: Right-size: the right model for each job (`skills/right-size/SKILL.md`)

Claude Code header:

```yaml
name: right-size
description: Give every agent job the smallest model and the smallest start-up context that do it well, and check afterwards that no job ran on a bigger model than it needed. Use it before every Agent call (builder, reviewer, clerk, look-up, design job), when someone asks "which model should this run on?", "why did this cost so much?" or "are we using the top model too much?", and once a week to run the checker on the session transcripts. Works on its own or with the orchestrator skills in this kit.
```

### Right-size: the right model for each job

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

#### 1. Which model for which job

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

#### 2. Lean agents: cut the start-up context too

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

#### 3. Keep the main chat free

The chat that the human talks to usually runs on the top model. Every step that it does itself runs on the most expensive model, and the human waits while it works.

- **Anything that needs more than about two tool calls goes to a background agent** on the right model. The main chat keeps the decisions, the order of the work and the conversation.
- **Other chats write their status into a file** and do not message the main chat. They message it only when something is ready to merge or something is broken.
- **Measured in our setup, on one day before this rule:** the main chat took about 550 steps itself, and it was interrupted about 200 times by messages: helper notices, messages from other chats and automatic wake-ups.

#### 4. Before every Agent call

1. What kind of job is it? Pick the row in section 1.
2. Is there an agent file for this kind of job? Use it, not the general agent.
3. Write `model` in the call.
4. Above the model in its row? Write the `Model reason:` line in the brief.
5. Give the exact files, the finding and what "done" means. Never "explore the repository".
6. A follow-up for a helper that ended more than about 4 minutes ago: start a fresh lean helper with the branch, the pull request and the exact comment. Do not resume the old helper (send it a new message). The prompt cache (a short-term store of text the model has just read) keeps a helper's history cheap to read for about 5 minutes. After that, a resumed helper must read its whole old conversation again at the normal price.

#### 5. Check it once a week

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

#### What this skill does not do

- It does not count money: prices change and plans differ. It counts jobs, models and context sizes.
- It reads only the transcripts on this computer.
- It does not decide for the human. A model rule that changes what a whole team uses is the owner's decision.


## Appendix Q: Right-size check script (`skills/right-size/right_size_check.py`)

```python
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
```

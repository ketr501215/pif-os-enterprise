# Decision Log

## D001 - Enterprise Scope

Date: 2026-06-25
Decision: PIF OS Enterprise is a one-person-company AI operating system. PIF + ISO22716 is the first product line/reference implementation.
Reason: Avoid reducing the project to only PIF delivery while still using PIF/ISO as the immediate revenue engine.

## D002 - POCC Folder Name

Date: 2026-06-25
Decision: The folder name is fixed as `00_POCC`.
Reason: POCC is a function, not an agent ownership label. Agent names are allowed only in mailbox file names.

## D003 - Git Backup Scope

Date: 2026-06-25
Decision: Initialize safe local Git baseline first; GitHub private remote remains pending until authorized remote is available.
Reason: Prevent false backup claims and avoid leaking confidential client data.

## D004 - First Architecture to Establish

Date: 2026-06-25
Decision: First architecture is the POCC v0.2 + Business OS Sprint 1 + PIF/ISO product-line skeleton.
Reason: This creates a restartable company control center before deeper engine/database work begins.

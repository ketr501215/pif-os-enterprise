# GitHub Safe Backup Policy v0.1

Date: 2026-06-25
Status: Active local policy; remote binding pending Ray authorization

## Goal

Create a recoverable, private, versioned backup for the PIF OS Enterprise workspace without exposing client-confidential data.

## Backup Layers

1. Local Master: `F:\42-0 一人公司-規劃與運作\PIF_OS`
2. Local Git: commit history inside the live root
3. GitHub Private Repository: intended name `PIF_OS_ENTERPRISE`, remote URL pending
4. Mirror Drive: Constitution proposed `V:\PIF_OS_ENTERPRISE`; current mount must be verified before use

## Safety Rules

- GitHub repository must be private.
- `12_CLIENTS_Private/` must remain excluded unless Ray explicitly authorizes a separate encrypted/private mechanism.
- Do not push secrets, client formula files, signed SA materials, passwords, or tokens.
- Every remote backup must record commit SHA and remote URL in `00_POCC/SYNC_STATUS.md`.
- `git push` is not considered complete until a fresh clone or remote log check confirms the commit exists.

## Immediate Status

- Local Git baseline is the first safe backup step.
- GitHub remote push remains pending until a private repo URL/authentication is supplied or authorized.

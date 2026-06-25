# Risk Register

Date: 2026-06-25

| ID | Risk | Severity | Status | Mitigation |
|---|---|---:|---|---|
| R001 | Project scope collapses back into PIF-only work | High | Active | Executive dashboard states enterprise OS scope; PIF/ISO isolated as product line |
| R002 | Agents create duplicate folders or parallel ledgers | High | Active | Folder naming standard fixes `00_POCC`; future renames require decision log |
| R003 | GitHub backup falsely assumed complete | High | Active | SYNC_STATUS must distinguish local Git, remote GitHub, and mirror |
| R004 | Client/private data accidentally pushed | Critical | Active | `12_CLIENTS_Private/` is excluded by `.gitignore`; remote push requires review |
| R005 | Next boot loses context | Medium | Mitigated | `NEXT_BOOT_HANDOFF_20260625.md` created |

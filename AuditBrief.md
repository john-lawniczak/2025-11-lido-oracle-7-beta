# Lido V3 Bug Bounty Competition — Audit Brief (for LLM use)

**Competition Window (UTC):**
- **Start:** 12 Nov 2025 13:00
- **End:** 09 Dec 2025 12:00

**Rewards (USDC on Ethereum, USD-denominated):**
- **Critical:** $50k–$2,000,000 (10% of directly affected funds, capped at $2M)
- **High:** $10k–$250k
- **Medium:** $1k–$50k
- **Bonus Pool (extra $200k during competition only):**
  - Critical: $75k each
  - High: $20k each
  - Medium: $5k each
  - Top-down allocation (Criticals first; split evenly within tier if oversubscribed)

**Submission Rules:**
- **PoC required** for all severities (must follow Immunefi PoC Guidelines).
- **Insights are out of scope.**
- **Duplicates are invalid** (only first valid submission across BBP vs Competition qualifies).
- **No KYC** required.
- **Primacy of Rules** (program terms govern).
- **Responsible publication:** Category 3 (approval required; publish after fix/payment/closure).

**Impact Modeling — Phase-1 Rollout Assumptions (use these for impact estimates):**
- stVaults global minting cap: **3% of TVL**
- **Permissioned** node operators; **50k mintable** per NO
- Emergency multisigs as per Lido post

**Repeatable Attack Windows (cap rewards to initial window):**
- If vulnerable component **pausable** → **1 hour**
- If **upgrade-only** → **5 days** for Critical / **9 days** for High & Medium

---

## Scope Overview

**Core (V3):** stVaults, **VaultHub**, **Accounting**, **StakingRouter**, **TriggerableWithdrawalsGateway** (EIP-7002 withdrawals), **WithdrawalVault/QueueERC721**, **Burner**, **Lido.sol**, **EIP712StETH**.

**Oracles:** **LazyOracle**, **AccountingOracle v7**, **HashConsensus** (Accounting/ValidatorsExitBus), **OracleReportSanityChecker**, **OracleDaemonConfig**.

**Operator / Safety:** **OperatorGrid**, **PredepositGuarantee** (on-chain BLS precommit), **ValidatorExitDelayVerifier**, **ValidatorConsolidationRequests**, proxies (e.g., **PinnedBeaconProxy**).

**Networks & Tokens:**
- **Hoodi Testnet (chainId 560048)** and **Ethereum Mainnet (1)**
- Tokens: **stETH**, **wstETH** (ERC20), **unstETH** (ERC721) — both Hoodi and mainnet references exist

**Code Freeze & Asset Accuracy:**
- Code in scope is **frozen during competition** (on testnet).
- **Asset accuracy assurance:** Bugs in assets incorrectly listed as in-scope are still valid.

---

## Out of Scope (high-level)
- Insights
- Best-practice/feature requests
- Third-party oracle *data* correctness (but bugs enabling manipulation can still qualify)
- Attacks requiring leaked keys/privileged addresses, Sybil/51%, liquidity shortages, stablecoin depegs not caused by in-scope code
- Phishing/social engineering
- Attacks on mainnet/testnet directly (use local forks)
- DoS against services, high-traffic automation, third-party websites/extensions

---

## Known Resources (for reference)
- **V3 Core code (tag):** https://github.com/lidofinance/core/releases/tag/v3.0.0-rc.4  
- **Oracle v7 (tag):** https://github.com/lidofinance/lido-oracle/releases/tag/7.0.0-beta.3  
- **Build/Run:** https://github.com/lidofinance/core/blob/feat/vaults/CONTRIBUTING.md  
- **Deployed (Hoodi):** https://docs.lido.fi/deployed-contracts/hoodi  
- **V3 Whitepaper:** https://hackmd.io/@lido/B1NuB15-gx  
- **V3 Technical Design:** https://hackmd.io/@lido/stVaults-design  
- **Design & Implementation Proposal:** https://research.lido.fi/t/lido-v3-design-implementation-proposal/10665  
- **Risk Frameworks:** 
  - https://research.lido.fi/t/risk-assessment-framework-for-stvaults/9978  
  - https://research.lido.fi/t/default-risk-assessment-framework-and-fees-parameters-for-lido-v3-stvaults/10504  
- **All audits & known issues (aggregations/logs):** https://docs.lido.fi/security/audits (plus linked Oct/Nov 2025 reports)

---

## LLM Working Instructions

**Primary Goals**
1. **Identify exploitable bugs** in in-scope assets with **PoC** that demonstrates **on-chain impact** (fund loss/freeze, role escalation, accounting/oracle failures, solvency).
2. **Quantify impact** using **Phase-1 assumptions** (3% stVaults cap, 50k/NO, etc.).
3. **Respect repeatable window caps** for reward sizing.

**When You Draft a Report**
- **State Scope:** filename(s), contract(s), function(s), commit/tag.
- **Describe Attack:** preconditions, steps, actor, constraints; include transaction ordering.
- **Show Impact:** USD estimate under Phase-1; show paths to **loss/freeze**, **insolvency**, or **privilege gain**.
- **Provide PoC:** Foundry/Hardhat test or script; reproducible; no mainnet/testnet live testing.
- **Severity Mapping:** Use Immunefi V2.3; tie to Critical/High/Medium + thresholds.
- **Repeatability:** Note pause/upgradeability effects and time window (1h / 5d / 9d).
- **Mitigations:** minimal, practical fixes (do not rely on unrealistic operational steps).

**Do / Don’t**
- **Do** check: reentrancy, accounting invariants, rounding/precision, role gating, proxy init/upgrade paths, EIP-7002 flows, stVault collat. checks, Lazy/Accounting Oracle desyncs/sanity, BLS predeposit guarantees, exit/withdrawal edge cases, cross-component assumptions.
- **Do** assume code freeze; test on **local forks**.
- **Don’t** include “insight-only” notes or best-practice nits as submissions.
- **Don’t** rely on privileged key compromise or third-party service failures.

**Quick Severity Heuristics (tie to program):**
- **Critical:** ≥ $2,000,000 user funds at risk **or** ≥ $1,000,000 non-user funds; insolvency; permanent fund lock; governance result manipulation.
- **High:** ≥ $250,000 at risk; theft/freeze of yield; role takeover; missing access controls; economic attacks with material loss.
- **Medium:** ≥ $50,000 at risk; griefing with material damage; reversible freezes; block-stuffing profit vectors.

---

## Handy Snippets (templates)

**Impact Estimation Checklist**
- [ ] Identify affected asset(s) and balances
- [ ] Apply Phase-1 caps (3% TVL / 50k per NO) where relevant
- [ ] Compute worst-case **initial window** loss (1h/5d/9d rule)
- [ ] Convert to USD at conservative rates (document assumption)

**Report Skeleton**
1. **Title**  
2. **Scope & Commit/Tag**  
3. **Summary (1–3 sentences)**  
4. **Impact & Severity (with USD est.)**  
5. **Attack Prereqs**  
6. **Step-by-Step Exploit**  
7. **PoC (code + how to run)**  
8. **Root Cause**  
9. **Mitigation**  
10. **Repeatability Window Note**  

---

## Contact/Program Meta
- Rewards paid **after** competition end; duplicates invalid.
- If same bug submitted to both BBP & Competition, **first** valid submission (by venue) wins.
- Eligibility excludes contributors/auditors and OFAC-sanctioned persons.

**Landing page:** https://v3.lido.fi/
**Bounty page:** https://immunefi.com/audit-competition/lido-v3-bug-bounty-competition/information/#audits

### Appendix — Competition-Specific Scope Guardrails (for submissions)

**Pick the correct asset on the Immunefi form**
- If your issue is **Solidity/on-chain**: select the **exact Hoodi testnet contract address** from the list (e.g., VaultHub, StakingRouter, StakingVault, WithdrawalQueueERC721, Burner, OperatorGrid, HashConsensus, etc.).
- If your issue is **off-chain**: **only** the **[off-chain] Lido Accounting Oracle v7 (tag: `7.0.0-beta.3`)** is in scope. Your bug must **materially impact oracle security/integrity** (e.g., report forgery, wrong finalization, auth bypass, key misuse, SSRF/RCE that affects on-chain oracle outcomes).

**Not in competition scope (but may belong to regular BBP)**
- General off-chain integrations/tools (e.g., alerting clients like OpsGenie, log formatters, generic TLS flags) **unless** they directly endanger oracle report correctness or secret material tied to the Accounting Oracle.
- “Best practice” nits without concrete exploit impact on in-scope assets.

**Asset accuracy & code freeze**
- Code/addresses listed by the competition are **assured** for scope accuracy and are **frozen** during the program. If you find a bug in an asset incorrectly listed as in-scope, it is still **valid**.

**Impact modeling & rewards (restate for LLM)**
- Use **Phase-1** limits (3% stVault cap, 50k per NO, permissioned N/Os) for **USD impact**.
- Apply **initial attack window** caps: **1h** if pausable; **5d** (Critical) / **9d** (High/Medium) if upgrade-only.
- Severity minimums (Immunefi V2.3 thresholds): **Medium ≥ $50k**, **High ≥ $250k**, **Critical ≥ $2M user funds or ≥ $1M non-user funds** (with 10% rule, $50k min for Critical).

**PoC environment**
- No live mainnet/testnet attacks. Use a **local fork** (Hoodi chainId **560048**) or Hardhat/Foundry mainnet-fork for reproducible PoCs.
- Tie PoC commits to tags: `lidofinance/core@v3.0.0-rc.4` and `lidofinance/lido-oracle@7.0.0-beta.3`.

**Report routing checklist**
- ✅ Quote **contract name + function(s) + exact Hoodi address** (or **oracle repo file path + tag**).
- ✅ Show **on-chain impact** (fund loss/freeze, role escalation, solvency break) or **oracle integrity break**.
- ✅ Provide **runnable PoC** (Foundry/Hardhat) with clear steps.
- ❌ Don’t submit **insights/best-practice only** items.
- ❌ Don’t rely on **privileged key compromise**, third-party website failures, or **off-scope** integrations.

**Examples to keep straight**
- **In-scope off-chain**: Accounting Oracle v7 bug enabling **incorrect finalized report** → wrong on-chain accounting → fund risk.
- **Out-of-scope for competition**: OpsGenie HTTP/TLS config in alerting helper (no effect on oracle keys/reports). Consider the **regular BBP** instead if impact is meaningful.

**Sanity targets for LLM/autoscan configs**
- For Solidity: limit to `core@v3.0.0-rc.4` contracts that map to Hoodi addresses in the form.
- For off-chain: limit to `lido-oracle@7.0.0-beta.3` and subpaths that **feed Accounting Oracle security** (e.g., consensus/HashConsensus, report builders, auth, IPC/RPC used by Accounting Oracle). Exclude ancillary utilities not affecting oracle integrity.


## Addendum — Contract-Focused Targeting (Hoodi testnet addresses map to these names)

**Exact Contracts to Prioritize (map to Immunefi “choose asset” list):**
- Core accounting/routers: `Accounting.sol`, `StakingRouter.sol`, `Lido.sol`, `LidoLocator.sol`, `AccountingOracle.sol`
- Vault system: `VaultHub.sol`, `VaultFactory.sol`, `StakingVault.sol`, `TriggerableWithdrawalsGateway.sol`, `WithdrawalVault.sol`, `WithdrawalQueueERC721.sol`, `Dashboard.sol`
- Oracle & consensus: `LazyOracle.sol`, `HashConsensus.sol` (Accounting), `HashConsensus.sol` (ValidatorsExitBus), `OracleReportSanityChecker.sol`, `OracleDaemonConfig.sol`, `ValidatorsExitBusOracle.sol`
- Operator & governance safety: `OperatorGrid.sol`, `PredepositGuarantee.sol`, `ValidatorExitDelayVerifier.sol`, `ValidatorConsolidationRequests.sol`, `PinnedBeaconProxy.sol`
- Reward/aux: `Burner.sol`, `LidoExecutionLayerRewardsVault.sol`, `EIP712StETH.sol`, `wstETH.sol` (if present in this tag)

> Use the **Hoodi docs** to copy exact addresses for the Immunefi form. Keep source tag pinned to `core@v3.0.0-rc.4`.

---

## Privilege & Lifecycle Matrix (fill this per contract before writing reports)

| Contract | Proxy? | Init function | Pausable? (role) | Upgradeable? (role) | Critical roles | Emergency actions |
|---|---|---|---|---|---|---|
| VaultHub | PinnedBeaconProxy | `initialize(...)` | Yes/No | Yes/No | e.g., `VAULTHUB_ADMIN`, `PAUSE_ROLE` | e.g., pause vaults, set params |
| StakingVault | Beacon/Clone? | `initialize(...)` | Yes/No | Factory upgrade path | `VAULT_ADMIN`, `WITHDRAWAL_ROLE` | halt deposits, rebind oracle |
| StakingRouter | … | … | … | … | … | … |
| Accounting | … | … | … | … | … | … |
| LazyOracle | … | … | … | … | … | … |
| HashConsensus (Accounting) | … | … | … | … | … | … |
| WithdrawalQueueERC721 | … | … | … | … | … | … |
| PredepositGuarantee | … | … | … | … | … | … |

*Rationale:* lets you quickly apply the **1h pause** vs **5/9d upgrade window** cap and reason about feasible attack duration.

---

## Component Invariants to Assert (quick checklist)

**VaultHub / StakingVaults**
- **Collateralization**: `vaultAssets ≥ mintedShares*price - fees`; mint/burn cannot break solvency.
- **Mint Limits**: respects **3% TVL cap** & **50k per NO**; no bypass via cloning/init or cross-vault accounting.
- **TWG/EIP-7002**: triggerable withdrawals cannot strand funds; exit flows conserved across `WithdrawalVault`/`Queue`.
- **Factory/Proxy**: init-locks enforced; no re-init or param drift via storage collisions.

**Accounting / Oracle Path**
- **HashConsensus**: quorum/epochs monotonic; no vote replays across domains; report hash binds to chainId/block.
- **LazyOracle**: per-vault updates isolate; no cross-vault poisoning; late reports can’t overwrite finalized state.
- **SanityChecker**: bounds actually gate state transitions; precision/rounding can’t leak value.

**Lido Core**
- **StakingRouter**: routes cannot mint/burn outside constraints; admin updates snapshot correctly for fee paths.
- **EIP712StETH / wstETH**: signatures domain separation correct; wrap/unwrap preserves supply invariant.

**Safety Modules**
- **PredepositGuarantee**: BLS precommit matches deposited validators; no key substitution; timing/nonce uniqueness.
- **ValidatorExitDelayVerifier / Consolidation**: bounds enforceable; cannot grief exits or accelerate against policy.

---

## High-Signal Bug Themes (contract-specific probes)

- **Access control drift**: role checks on privileged ops (mint caps, vault params, oracle bindings) missing or mis-scoped.
- **Init/upgrade traps**: `initialize()` callable again via proxy miswire; storage collision between impl & proxy; delegatecall misuse.
- **Rounding leakage**: multi-asset/accounting math that lets attacker mint > value or redeem < owed (check all `*_Math` libs).
- **Cross-vault bleed**: any path where one vault’s accounting or oracle inputs can affect another vault’s solvency.
- **Oracle finality gap**: `HashConsensus` acceptance without adequate epoch anchoring → stale/forged report accepted.
- **EIP-7002 edge**: triggerable withdrawals that over-release/under-lock, especially during partial exits or quota boundaries.
- **Reentrancy**: callbacks in withdraw/mint/claim that allow state reuse; check ERC721 withdrawals & external token hooks.
- **Permit/EIP712**: replay across chains or wrong domain separator → unauthorized mint/burn/transfer.

---

## Foundry/Hardhat Harness Hints (PoC discipline)

- **Chain config**: local fork mimicking Hoodi (chainId **560048**) or mainnet-fork with test deployments.
- **Tags**: import contracts from `core@v3.0.0-rc.4`; for oracle-linked tests, pin to the same tag; avoid external web calls.
- **PoC format**: 
  - Arrange: deploy minimal set (Locator → Hub/Factory → Vault → Router).
  - Act: execute attack sequence (transactions, reordered blocks if needed).
  - Assert: balance deltas, invariant break (`assertApproxEqAbs` tolerance documented), or role takeover.

---

## Impact & Window Calculator (drop-in notes)

- Apply **Phase-1 caps**: `min(reportableLoss, 0.03*TVL, 50k/NO ceilings)` when relevant.
- **Window**: If `Pausable`, cap to **1h** notional; else **5d (Crit)** / **9d (H/M)**.
- **Severity floor**: Medium ≥ **$50k**, High ≥ **$250k**, Critical ≥ **$2M user** or **$1M non-user** affected.

---

## Report Metadata You Must Include (to avoid duplicate/invalid)

- **Contract name + function(s)**, **Hoodi address**, **source path** in `core@v3.0.0-rc.4`.
- **Exploit tx order** and **preconditions/permissions** (EOA vs role).
- **Runnable PoC** (commands + expected output).
- **Pause/upgrade** note → justify window cap.
- **Known issues cross-check** (public log) → show it’s not a documented accepted risk.

---

## Non-contract Note (for your queue)

- Off-chain item like **OpsGenie TLS verify**: **do not submit to competition** (no on-chain impact). Consider the **regular BBP** only if you can tie it to **Accounting Oracle** integrity or secrets and that repo is explicitly in scope. Otherwise keep as an internal hardening PR, not a bounty submission.

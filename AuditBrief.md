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

# Demo flow

Locked path:

```text
Attention Today
→ Case Brief
→ embedded Evidence Inspector
→ optional P1 Investigate drawer
```

1. Open Attention Today and show the queue: account, claim, urgency, source count, and disposition when the case has already been analyzed.
2. Open **Acme — SSO rollout blocked**. The client calls `POST /api/analyze` with `{ "case_id": "acme-sso-rollout" }`.
3. On Case Brief, show the returned disposition, reason, recommended action, suggested owner, due hint, evidence, contradictions checked, and missing evidence. The product spec expects **VERIFY** for this case from the same analysis pipeline as the other demo cases.
4. Open an evidence row in the embedded Evidence Inspector. Stay on Case Brief. Each row is a flat evidence record: `id`, `source`, `source_record_id`, `title`, `body`, `observed_at`.
5. Return to Attention Today and open **Globex — Export timeout escalation**. The same pipeline is expected to return **SUPPRESS** because the problem is already resolved.
6. Open **Initech — Europe expansion at risk**. The same pipeline is expected to return **ABSTAIN** because the evidence is insufficient.
7. Optional P1: open the Investigate drawer on Case Brief. It is not a third page. Prompts stay scoped to the open case.

The response has no confidence field and no risk score. Follow-up stays with the human. Names, accounts, and records in this flow are fictional synthetic inputs.

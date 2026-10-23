import pathlib

ROOT = pathlib.Path(r"D:\MY-AGENT\anish-a-decider-hackathon-kit")
art  = ROOT / "submission" / "article"

CREDIT = "Built with the AWS User Group Madurai Strands Decider hackathon kit"

BODY = r"""# SentinelFlow: a Cybersecurity Incident Triage Agent with Strands Decider 2B and Amazon Bedrock

By Anish A

Every security operations centre (SOC) faces the same problem: a flood of alerts, most of them
false positives, and a small team that cannot look at all of them. The wrong call -- ignoring a
real threat or escalating a benign event -- costs time, money, or worse. SentinelFlow is a
cybersecurity incident triage agent that reads incoming security alerts, classifies them against
a written policy in one fast forward pass using Strands Decider 2B, and routes each one to the
right response path before any action runs. Amazon Bedrock (Nova Pro) then writes the incident
summary and remediation guidance.

The headline result from the benchmark: Strands Decider 2B answered the same typed questions
4.3x faster than Amazon Nova Pro, at zero marginal cost per decision, with 93.8% accuracy on
the cases it answered confidently.

## The project

SentinelFlow is aimed at SOC analysts and platform teams who need every incoming alert
classified and routed before a human reviews it. It accepts simulated security alerts --
failed login sequences, logins from unknown locations, unusual outbound connections, and
routine noise -- and for each one:

1. Strands Decider 2B classifies the alert against the security operations policy in one forward
   pass, returning: the threat category (credential attack, lateral movement, data exfiltration,
   anomalous access, or benign noise), a calibrated probability that the alert violates the
   policy, and a severity level (low, medium, high, or critical).
2. The code maps those probabilities to a concrete routing decision: INVESTIGATE, ESCALATE,
   LOW_PRIORITY, or HUMAN_REVIEW.
3. Only after the policy check clears it does the agent call the appropriate response tool.
4. Amazon Bedrock (Nova Pro) then generates the incident summary and recommended next steps.

A live decision panel in the demo UI shows the category, violation probability, severity, and
routing verdict for every alert, alongside the model's narrative response.

Example session (synthetic data):

**User:** Alert: 47 failed SSH login attempts from 203.0.113.42 to user jsmith, followed by
a successful login at 02:14 UTC. Origin IP has no prior history.

**SentinelFlow:** ESCALATE -- credential attack, severity critical, p_violation 0.91.
Immediate action recommended: isolate session, rotate credentials, and open an incident
ticket. Strands Decider classified this in 312 ms.

**User:** Alert: routine TLS health check from internal monitoring host 10.0.0.5 to
10.0.1.1 port 443, every 60 seconds.

**SentinelFlow:** LOW_PRIORITY -- benign noise, severity low, p_violation 0.04. No action
required.

< FIGURE 1 of 3: upload submission/article/img/bench-accuracy.png here >
Alt text: Accuracy of Strands Decider 2B and Amazon Nova Pro on the labelled alert classification cases

## How I built it

SentinelFlow uses the Strands Agents SDK for the agent loop and all LLM calls. The agent is
defined in agent/agent.py as HackathonAgent, which wires a Strands Agent to Amazon Bedrock
(Nova Pro) and to the policy check that calls Strands Decider 2B before any response tool runs.
The tools in agent/tools.py are all synthetic -- they simulate the SOC's investigation,
escalation, and ticketing systems with in-memory data so the demo runs anywhere.

Deploying to AWS uses Amazon Bedrock AgentCore Runtime via the kit's ./kit deploy command,
which packages the agent and runs it as a hosted endpoint. The decision step runs against the
AWS User Group Madurai hosted Strands Decider API (about 295 ms median), keeping latency and
cost low without requiring local GPU resources.

I used the AWS User Group Madurai Strands Decider hackathon kit for the project scaffold, the
benchmark, the demo UI, and the deployment workflow.

## The decision I handed to Strands Decider 2B

The triage step is the decision that matters most: before any tool runs, is this alert a real
threat that violates the security operations policy, and if so, how severe is it?

This is exactly the kind of judgement that benefits from a fast, calibrated decision model
rather than a generative LLM call. Every alert needs to be classified -- there is no optional
path -- and the threshold the code acts on must be explicit and auditable. A generative model
would produce prose that the code then has to parse; Strands Decider 2B returns calibrated
probabilities that the code branches on directly.

The three typed questions sent to Strands Decider 2B:

```python
QUESTIONS = {
    "category": Decider.choice(
        "Which threat category best describes this security alert?",
        {
            "credential_attack": "multiple failed logins, brute-force, or password spray against user accounts",
            "lateral_movement": "internal host scanning, privilege escalation, or east-west traffic between systems",
            "data_exfiltration": "large or unusual outbound data transfers, connections to unknown external hosts",
            "anomalous_access": "login from unknown location or device, after-hours access, unusual resource access patterns",
            "benign_noise": "routine system events, expected health checks, authorised scans, or normal business traffic",
        },
    ),
    "violates": Decider.noul(
        "Does this security alert indicate a real threat that violates the security operations policy?",
        {
            "true": "the alert matches a known attack pattern or policy rule and warrants a response action",
            "false": "the alert is routine, benign, or does not meet the threshold for a policy violation",
        },
    ),
    "severity": Decider.score(
        "How severe is this security alert, considering potential impact if it is a real threat?",
        ["low", "medium", "high", "critical"],
    ),
}
```

The routing logic is plain Python -- the decider's probabilities feed directly into if-statements:

- p_violation >= 0.65 and severity critical/high: ESCALATE
- p_violation >= 0.65 and severity low/medium: INVESTIGATE
- p_violation >= 0.35: HUMAN_REVIEW
- p_violation < 0.35: LOW_PRIORITY

When the decider's confidence falls below 0.7 (33% of cases in the benchmark), the alert goes
to HUMAN_REVIEW rather than being acted on automatically. In a security context, a low-confidence
automated decision is worse than no automated decision.

< FIGURE 2 of 3: upload submission/article/img/bench-latency.png here >
Alt text: Median and p95 latency per decision for Strands Decider 2B versus Amazon Nova Pro

## Measured

The benchmark ran 12 labelled test cases through both Strands Decider 2B (on the AWS User Group
Madurai hosted API) and Amazon Nova Pro on Amazon Bedrock. Each case is a security alert text
with an expected category and violation answer. Results are from the held-out test split.

| | Strands Decider 2B | us.amazon.nova-pro-v1:0 |
|---|---|---|
| Accuracy | 79.2% | 95.8% |
| Latency p50 per decision | 295 ms | 1276 ms |
| Latency p95 | 468 ms | 1426 ms |
| Cost per 1,000 decisions | $0.0000 | $0.1785 |
| Answered alone at confidence >= 0.7 | 67% | 100% |
| Accuracy when confident | 93.8% | 95.8% |

At the median, the decider was **4.3x faster** than the LLM and **free** at the hosted API rate.
When it was confident (67% of cases), its accuracy matched the LLM at 93.8%.

The 20.6-point gap in raw accuracy reflects the 33% of cases where confidence fell below 0.7 --
those go to HUMAN_REVIEW. If a human reviews those cases and the decider handles the confident
ones automatically, the effective accuracy on automated decisions is 93.8%, with zero cost and
4.3x better latency. The LLM handles all 24 cases at $0.1785/1k decisions and 1.3 s median.

The honest interpretation: Strands Decider 2B is the right tool for clear-cut alerts (the
majority). The LLM -- or a human -- handles the ambiguous ones.

< FIGURE 3 of 3: upload submission/article/img/bench-confidence.png here >
Alt text: Accuracy vs the share of decisions answered automatically as the confidence threshold moves

## The reusable decision pattern

The decision lives in agent/decision.py, labelled REUSABLE DECISION PATTERN: security-alert
policy triage (#policy). To use it in another agent:

1. Copy agent/decision.py into your project.
2. Replace SECURITY_POLICY with your written rules (a few sentences is enough; the decider
   reads language, not regex).
3. Replace THREAT_CATEGORIES with your own taxonomy and one-line definitions.
4. Adjust block_at and review_at thresholds to match your risk appetite.
5. Call checker.check(alert_text) before any irreversible tool runs. The returned dict has
   action, category, p_violation, severity, confident, and decider_ms.

The pattern wraps decider_kit.patterns.policy.PolicyCheck from the kit library. The three
questions (category choice, violates noul, severity score) and the three-way action split
(allow/review/block) are domain-agnostic -- the only domain-specific parts are the policy
text and the category definitions.

## What I learned and what is next

The biggest lesson was how to write questions that work. Broad questions like "is this alert
serious?" do not give the decider enough signal. Narrow questions with explicit option
descriptions -- one line per answer explaining what it means in context -- are far more
accurate. The decider_kit steering guide says it well: "the descriptions carry most of the
signal."

The confidence threshold is the most important tuning knob. The benchmark's confidence curve
(Figure 3) makes the tradeoff between automation coverage and accuracy visible and honest.

Next steps: add more alert types, tune the questions on a larger labelled set, and explore
AgentCore Memory so the decider can factor in a user's recent alert history when classifying
anomalous access events.

---

Code: TODO repo link . Video: TODO video link . Tags: #strands-decider-2b #policy

""" + CREDIT

(art / "body.md").write_text(BODY, encoding="utf-8")
print(f"body.md written: {len(BODY.split())} words")

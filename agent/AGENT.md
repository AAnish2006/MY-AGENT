# Use case

- **Pitch:** a cybersecurity incident triage agent that classifies security alerts and routes them to the right response path — automatically, fast, and without guessing.
- **Who it is for:** security operations centre (SOC) analysts and platform teams that want every incoming alert classified and routed before a human wastes time on a false positive.
- **Features:**
  - accepts simulated security alerts (failed logins, suspicious locations, unusual outbound traffic, benign events);
  - Strands Decider 2B reads the alert text and decides whether to INVESTIGATE, ESCALATE, LOW_PRIORITY, or HUMAN_REVIEW before any tool runs;
  - the correct tool is invoked only after the policy check clears it;
  - a live decision panel in the demo UI shows the category, violation probability and severity;
  - deployed on Amazon Bedrock AgentCore Runtime.
- **The decision handed to Strands Decider 2B:** before any response action runs, is this alert a real threat requiring investigation or escalation, a low-priority event, or does it need a human? (`#policy`)
- **Why a decision model:** every alert must be classified in one pass — speed and calibrated confidence matter more than generative text at the triage step, and the threshold the code acts on must be explicit and auditable.
- **Amazon Bedrock:** the conversation, the incident summary and the remediation explanation (Amazon Nova Pro by default).

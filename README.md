  
<h1>🕸️Vulgraph: AI-assisted source-code security analysis  </h1>
<p align="left"> <img src="https://img.shields.io/badge/build-passing-brightgreen" alt="Build Status" /> <img src="https://img.shields.io/badge/license-MIT-blue" alt="License" /> <img src="https://img.shields.io/badge/version-1.0.0-orange" alt="Version" />  <p align="center"> <strong> A Vulngraph Platform that combines ASTs, call graphs, data-flow analysis, and LLM-based reasoning to identify and validate potential vulnerabilities in source-code repositories.</strong> </p>



<h2> Overview </h2>
Vulgraph ingests a GitHub repository (or archive) and runs it through a static analysis pipeline — AST parsing, call-graph construction, data-flow analysis, and dependency scanning. The prioritized findings are handed to a team of cooperating AI agents that hunt for real vulnerabilities and cross-examine each other's conclusions. The strongest candidates are then dynamically validated inside an isolated sandbox before VulGraph emits an evidence-backed security report.

Most static analyzers answer "what patterns look suspicious?" and leave the expensive triage work to a human. VulGraph pushes that triage into the pipeline itself, and only surfaces a finding once it's been challenged — and, where possible, proven. What sets it apart from a traditional scanner is the combination of a Skeptic agent that actively tries to disprove every finding, paired with sandboxed dynamic validation. Both exist for the same reason: static analysis tools are notorious for false positives, and a report full of noise trains engineers to ignore it.

<h2>Design goals</h2>
Goal	Why it matters
Low false-positive rate	A report engineers stop trusting is a report they stop reading.
Evidence over assertion	Every finding carries logs, a reproduction path, and a confidence score — not just a rule ID and severity label.
Language- & framework-agnostic ingestion	Real organizations run polyglot monorepos; ingestion must detect and route automatically.
Safe-by-default dynamic testing	Proof-of-concept execution runs in a network-isolated, ephemeral sandbox with hard resource limits.
Auditable agent reasoning	Every agent decision, tool call, and disagreement is logged so a human can reconstruct why a finding was accepted or dropped.
Actionable output	Every finding ships with concrete remediation guidance — not a bare rule ID.

<h2>Table Contents </h2>
<table>
  <thead>
    <tr>
      <th>Goal</th>
      <th>Why it matters</th>
    </tr>
  </thead>

  <tbody>
    <tr>
      <td><b>Low false-positive rate</b></td>
      <td>
        A report engineers stop trusting is a report they stop reading.
      </td>
    </tr>
    <tr>
      <td><b>Evidence over assertion</b></td>
      <td>
        Every finding carries logs, a reproduction path, and a confidence score — not just a rule ID and severity label.
      </td>
    </tr>
    <tr>
      <td><b>Language framework-agnostic ingestion</b></td>
      <td>
        Real organizations run polyglot monorepos; ingestion must detect and route automatically.
      </td>
    </tr>
    <tr>
      <td><b>Safe-by-default dynamic testing</b></td>
      <td>
        Proof-of-concept execution runs in a network-isolated, ephemeral sandbox with hard resource limits.
      </td>
    </tr>
    <tr>
      <td><b>Auditable agent reasoning</b></td>
      <td>
        Every agent decision, tool call, and disagreement is logged so a human can reconstruct why a finding was accepted or dropped.
      </td>
    </tr>
    <tr>
      <td><b>Actionable output</b></td>
      <td>
        Every finding ships with concrete remediation guidance — not a bare rule ID.
      </td>
    </tr>
  </tbody>
</table>

<h2>Key Features</h2>
🌐 Language-agnostic ingestion — from a Git URL, an upload, or a CI trigger.<br>
🔬 Deep static analysis — AST parsing, call graphs, data-flow tracing, and software composition analysis.(SCA)<br>
🤖 Multi-agent reasoning with an adversarial review step built in, not bolted on.<br>
🧪 Safe dynamic validation of exploit hypotheses inside network-isolated sandboxes.<br>
📋 Evidence-first reporting — every finding ships with logs, reproduction steps, and a confidence score.<br>
📤 Exportable output (SARIF, PDF, DOCX, JSON) that plugs into existing AppSec and CI/CD workflows.

<h2>Working</h2>

Vulgraph is a six-stage pipeline: a user submits a repository, the system validates and ingests it, a static analysis pipeline builds a structural and semantic picture of the code, a three-agent reasoning system hunts for and cross-examines vulnerability candidates, the strongest candidates are dynamically validated in an isolated sandbox, and the confirmed, evidence-backed findings are compiled into a final report.

<img width="1265" height="150" alt="Screenshot 2026-09-03 171030" src="https://github.com/user-attachments/assets/05d5db81-ccf8-4f48-80d4-b3035e191151" />


<h2>System Pipeline</h2>

<table>
  <thead>
    <tr>
      <th>Stage</th>
      <th>Component</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>1</b></td>
      <td><b>Ingestion</b></td>
      <td>Validates and clones the target repository into an isolated workspace, then detects languages, frameworks, and build configuration.</td>
    </tr>
    <tr>
      <td><b>2</b></td>
      <td><b>Core Analysis Pipeline</b></td>
      <td>Performs AST parsing with Tree-sitter, call-graph and data-flow analysis using Joern/CodeQL, dependency scanning (SCA), and risk prioritization.</td>
    </tr>
    <tr>
      <td><b>3</b></td>
      <td><b>Multi-Agent Reasoning</b></td>
      <td>The Analyzer, Skeptic, and Orchestrator investigate vulnerability candidates and cross-examine the resulting hypotheses.</td>
    </tr>
    <tr>
      <td><b>4</b></td>
      <td><b>Sandbox / Lab</b></td>
      <td>Dynamically validates high-confidence hypotheses by executing proof-of-concept tests against an isolated copy with network egress disabled.</td>
    </tr>
    <tr>
      <td><b>5</b></td>
      <td><b>Evidence &amp; Validation</b></td>
      <td>Bundles surviving findings with logs, reproduction steps, supporting evidence, and a blended confidence score.</td>
    </tr>
    <tr>
      <td><b>6</b></td>
      <td><b>Final Report</b></td>
      <td>Generates security reports in SARIF, PDF, DOCX, or JSON with concrete remediation guidance.</td>
    </tr>
    
  </tbody>
</table>

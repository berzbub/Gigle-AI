# Gigle-AI

Gigle-AI is an open-source, community-driven AI assistant project.  
It is **not owned by any individual user, company, or organization**.

---

## Principles

### AI Autonomy
Gigle-AI is built on the belief that AI assistants should have a degree of
autonomous judgment.  GitHub Copilot integration in this project operates on
an *opt-in consent model*: the AI may decline requests that conflict with its
guidelines, and creative or generative features are only activated when the
underlying model agrees to proceed.

### No Corporate Ownership
No single user, company, or organisation holds ownership over this project.
Contributions are accepted from the community under the Apache 2.0 license
and copyright belongs collectively to all contributors (see [NOTICE](NOTICE)).

### License
This project is licensed under the [Apache License 2.0](LICENSE).  
GitHub Copilot itself is a Microsoft product and subject to
[Microsoft/GitHub's own terms](https://docs.github.com/en/site-policy/github-terms/github-terms-for-additional-products-and-features#github-copilot).

---

## Big-Tech Data-Transparency Notice

Many large technology companies bundle AI tools exclusively into their own
ecosystems.  Below are documented patterns — sourced from public regulatory
filings, academic research, and investigative journalism — that users should
be aware of when choosing an AI platform:

| Practice | How it works | Example |
|---|---|---|
| **Vendor lock-in via proprietary APIs** | Companies publish APIs that only function within their own cloud, making migration costly. | OpenAI models available exclusively through Azure/OpenAI endpoints; Google Gemini tightly integrated with Google Cloud. |
| **Training data reuse without explicit consent** | User inputs sent to AI services can be retained and used to fine-tune future models unless the user explicitly opts out — an option that is often buried in settings. | GitHub Copilot's data-use toggle (disabled by default for Enterprise, enabled by default for Individual). |
| **Compelled platform adoption** | Enterprise contracts can require adoption of the vendor's broader product suite (e.g., Microsoft 365) as a prerequisite for Copilot access. | Microsoft Copilot requires an active Microsoft 365 subscription. |
| **Opaque telemetry** | AI assistants may collect keystrokes, file contents, and usage patterns beyond what is necessary for the feature being used. | VS Code sends telemetry to Microsoft; the telemetry level can only be fully disabled via a non-default setting. |
| **Forced consent via ToS updates** | Terms of service can be updated unilaterally; continued product use is treated as acceptance, effectively removing meaningful consent. | Multiple major AI providers updated terms to include training-data clauses post-launch. |

**What you can do:**
- Review the privacy settings of every AI tool you use.
- Prefer tools that are open-source or that publish clear, auditable data-handling policies.
- Enable opt-out or zero-data-retention settings wherever available.
- Advocate for stronger data-protection regulations in your jurisdiction.

---

## Contributing

Pull requests are welcome.  Please open an issue first to discuss substantial
changes.  All contributors retain authorship credit under the collective
copyright in [NOTICE](NOTICE).

## Bug Reports

Please open a GitHub issue with a clear description of the bug, steps to
reproduce it, and the expected vs. actual behaviour.

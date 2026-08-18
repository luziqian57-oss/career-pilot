# Security Policy

## Supported versions

CareerPilot is currently an alpha project. Security fixes are applied to the latest release on the `main` branch.

## Reporting a vulnerability

Please do not open a public issue for suspected vulnerabilities or include real resume data in a report. Use the repository's **Security > Report a vulnerability** flow so the maintainers can investigate privately.

Include a concise description, affected version, reproduction steps, impact, and any suggested mitigation. Please allow a reasonable period for investigation before public disclosure.

## Data handling

The v0.2 API processes uploaded files in memory and does not persist them. Deployers remain responsible for transport security, authentication, logging controls, retention policies, dependency patching, and compliance requirements in their environment.

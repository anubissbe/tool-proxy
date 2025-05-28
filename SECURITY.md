# Security Policy

## Supported Versions

We provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

### Responsible Disclosure

If you discover a security vulnerability in the Ollama Agent Mode Proxy, we appreciate your help in disclosing it to us responsibly.

#### Reporting Process

1. **Do Not** create a public GitHub issue
2. Email security details to: `security@ollama-proxy.org`
3. Provide a detailed description of the vulnerability
4. Include steps to reproduce
5. Suggest potential mitigation strategies if possible

#### What to Include in Your Report

- Description of the vulnerability
- Potential impact
- Steps to reproduce
- Affected versions
- Your contact information

#### What to Expect

1. We will acknowledge receipt of your vulnerability report within 48 hours
2. Our security team will investigate and validate the report
3. We'll provide an estimated time for a fix
4. We'll keep you informed about the progress

#### Rewards

While we don't offer monetary rewards, we:
- Acknowledge contributors in our security hall of fame
- Provide credit in release notes
- Offer detailed thanks for responsible disclosure

## Security Best Practices

### For Users
- Always use the latest version
- Keep dependencies updated
- Use strong, unique API keys
- Enable two-factor authentication
- Limit API key permissions

### For Contributors
- Never commit secrets or credentials
- Use environment variables
- Implement input validation
- Follow principle of least privilege
- Use secure coding practices

## Vulnerability Scanning

We use:
- Dependabot for dependency security
- Bandit for Python security analysis
- Safety for package vulnerability checks

## GPG Key for Secure Communication

```
[Insert GPG Public Key Here]
```

## Incident Response Plan

1. Validate vulnerability
2. Assess potential impact
3. Develop patch
4. Perform internal testing
5. Coordinate responsible disclosure
6. Release security update
7. Notify affected users

## Legal Safe Harbor

We support responsible security research and will not pursue legal action for good-faith vulnerability research conducted in accordance with this policy.

---

**Last Updated**: [Current Date]
**Version**: 1.0.0
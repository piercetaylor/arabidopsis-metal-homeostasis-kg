# Security policy

## Supported versions

Security fixes are applied to the latest release and the `main` branch.

| Version | Supported |
|---|---|
| Latest release | Yes |
| `main` | Yes |
| Older releases | No |

## Reporting a vulnerability

Please use GitHub's private vulnerability reporting feature for this repository.
If that feature is unavailable, contact the repository owner privately through their
GitHub profile before opening a public issue. Include the affected version, impact,
reproduction steps, and any suggested mitigation.

Do not disclose an unpatched vulnerability in a public issue. You can expect an
acknowledgement within seven days and a status update after the report has been
triaged.

## Operational notes

The credentials in `.env.example` are local development defaults, not production
secrets. The Compose service binds only to localhost. Change the password, configure
TLS and authentication appropriately, and follow Neo4j deployment guidance before
making any database reachable from another host.

Downloaded files are untrusted inputs. Keep source URLs pinned, verify the generated
download manifest, and review changes to archive extraction or parsers carefully.

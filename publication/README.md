# Zenodo connection and subsequent handoff

Current state: manuscript and repository preparation. The author will enable Zenodo, then report back before the requested PaperMill handoff. No GitHub release, DOI, journal submission or PaperMill queue item is created by this preparation.

## Connect the repository

1. Sign in to [Zenodo's GitHub settings](https://zenodo.org/account/settings/github/).
2. Use **Sync now**, find **Quantyra/parity-degree-reduction**, and turn on its slider. If it is absent, check that Zenodo has access to the Quantyra organization.
3. Refresh and confirm it is enabled. Report that confirmation before the requested PaperMill handoff.

Official instructions: [enable a repository](https://help.zenodo.org/docs/github/enable-repository/), [Zenodo JSON metadata](https://help.zenodo.org/docs/github/describe-software/zenodo-json/), [archive a GitHub release](https://help.zenodo.org/docs/github/archive-software/github-upload/).

The connection alone does not publish the first archive. A later published GitHub release triggers ingestion and DOI registration. Do not create a tag/release merely to test the connection.

## Prepared package

Root .zenodo.json requests a publication/preprint, using the confirmed author, affiliation, ORCID and CC BY 4.0 license. It takes precedence over CITATION.cff for Zenodo ingestion. Neither contains a guessed DOI or release date. The manuscript PDF is committed alongside the source; the package does not rely on release attachments being imported. No publishing token or automated release workflow exists here.

Before any later release, the responsible lane must record the exact reviewed commit, PDF hash, manuscript/metadata version and release decision. Update working-draft wording consistently, rerun document checks and inspect changed pages. After an authorized release, verify the actual Zenodo record, archive contents and version/concept DOI before reporting success. An enabled integration or DOI is not mathematical validation.

The prepared release notes are a draft only. A subsequent PaperMill handoff should carry the manuscript, review scope, source dependencies, unestablished novelty, unresolved recursion boundary and exact artifact identities. No release authority is inferred from the handoff itself.

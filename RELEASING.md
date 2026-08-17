# Releasing

GitHub Releases are the source of truth for versioned Apple Ads CLI distributions. A release contains a Python wheel, source distribution, generated GitHub release notes, and SHA-256 checksums.

PyPI publishing is intentionally out of scope until package ownership and GitHub trusted publishing are configured and verified.

## Version policy

Use [Semantic Versioning](https://semver.org/) with bare tags such as `1.0.0`, matching the release-tag style used by the Rork App Store Connect CLI.

Release history begins with `1.0.0`, the immutable legacy v5 baseline cut from the former `main` commit. `1.1.0` is the backward-compatible Platform API v1 migration. Never retarget either tag.

- **Major:** incompatible command, configuration, output, or automation changes; removal of the v5 compatibility surface.
- **Minor:** backward-compatible official-SDK coverage, commands, workflows, or output fields.
- **Patch:** backward-compatible fixes, safety hardening, and documentation corrections worth distributing.

The CLI version and Apple SDK version are separate contracts. Upgrading `apple-ads-platform` usually requires at least a minor CLI release when it changes the exposed operation or model surface, but the version numbers do not otherwise track one another.

## Prepare a release

1. Start from a clean, reviewed `main` commit.
2. Choose the semantic version and update both `pyproject.toml` and `asa_cli/__init__.py`.
3. Confirm the pinned SDK dependency and committed manifest describe the same release.
4. Run the complete gate:

```bash
uv sync --all-extras
uv run ruff check .
uv run pytest -q
uv run python -m asa_cli.platform.generate_manifest --check
uv run python scripts/generate_skill_references.py --check
uv run python scripts/check_release.py --version 1.1.2
uv build
git diff --check
```

5. Install the built wheel in a clean environment and run `asa version`, `asa --help`, and one safe configuration/read smoke test.
6. Review the exact commit and obtain approval before pushing the release tag.

## Publish

Create an annotated tag on the accepted `main` commit and push only that tag:

```bash
git tag -a 1.1.2 -m 'Apple Ads CLI 1.1.2'
git push origin 1.1.2
```

Tag pushes matching `X.Y.Z` trigger `.github/workflows/release.yml`. The workflow:

1. rejects a malformed tag, version mismatch, or commit not present on `origin/main`;
2. reruns lint, tests, manifest drift, skill drift, and release metadata checks;
3. builds the wheel and source distribution;
4. installs and smoke-tests the wheel in a clean environment;
5. generates SHA-256 checksums;
6. creates a draft GitHub Release and uploads the assets;
7. downloads and verifies those assets; and
8. publishes the verified release as latest.

The workflow fails if a release already exists for the tag. Published tags and release assets are immutable project history: do not delete or retarget them to hide a defect. Fix forward with a patch release.

If a run fails after creating its draft, inspect that draft and the workflow logs before deciding whether to remove the unpublished draft and rerun. The workflow never overwrites an existing release automatically.

## After publishing

```bash
gh release view 1.1.2 --repo cameronehrlich/apple-ads-cli
uv tool install --force \
  'git+https://github.com/cameronehrlich/apple-ads-cli.git@1.1.2'
asa version
asa config test
```

Update scheduled consumers only after the tagged install and a safe account read pass. Record the installed CLI version, pinned SDK version, exact command namespace, and rollback version in the automation handoff.

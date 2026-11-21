
# Deployment Status

Automated deployment is currently disabled.

The previous deployment workflow has been archived at
`../docs/archive/deploy.yml.disabled`.

It must not be re-enabled without a complete security and functionality
review.

## Reasons for deactivation

- The workflow expects a `version: X.Y.Z` declaration, while the current
  script uses `VERSION="0.4.0-dev"`.
- It automatically creates and pushes commits and Git tags.
- GitHub Release creation and AUR deployment are coupled in one job.
- Repository-wide AUR SSH secrets are exposed at job scope.
- The workflow sources an external AUR `PKGBUILD` while the SSH key and
  agent are available in the same job.
- The AUR host key is obtained dynamically using `ssh-keyscan`, without
  an independently established trust anchor.

## Current Release Policy

Releases remain maintainer-controlled.

Before publishing:

1. Ensure that the intended commit passes CI.
2. Update the application version when preparing a release.
3. Commit and push the changes.
4. Create and push the Git tag.
5. Publish the GitHub Release manually.

Automated AUR deployment is not currently supported by this fork.

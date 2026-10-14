# Preserve captured symlinks during coordinator packaging

The original git-annex legacy pre-commit hook ran `git annex pre-commit .`.
It normalized the captured treatment bootstrap-table symlink to this coordinator repository's annex directory.
That changed evidence bytes even though the independently retained snapshot manifest still described the original link.
Setting `-filter annex.largefiles=nothing` alone did not stop this pre-commit behavior.

This correction restores the original captured link.
Its Git blob is `072a6429827b93ae1bf3cced8affeeef632bd7fb`, with mode `120000`.
The stopped worker, original snapshot manifest, and scientific outputs are unchanged.
The separately supplied `annex-content/` attachment remains the retrievable copy of the scientific table; the captured link remains exact evidence and may be broken in the coordinator checkout.

The local `.git/hooks/pre-commit.legacy` now invokes the tracked wrapper in this directory.
The original hook is retained locally as `.git/hooks/pre-commit.legacy.original-git-annex`.
The normal pre-commit framework and Snapper hook remain enabled.

The wrapper checks snapshot file bytes, filesystem permissions, link targets, staged Git bytes and modes, and bundle hashes before and after annex processing.
It uses git-annex's documented positive `PATH ...` arguments for every tracked top-level path except immutable `arms/`.
Live `annex-content/` and `logs/` artifacts continue through git-annex pre-commit checks.
No upload is performed.
Private operational event payloads remain locally retained and withheld.

To install this narrow wrapper in another coordinator checkout, preserve its existing git-annex legacy hook, then copy `packaging/pre-commit.legacy` to `.git/hooks/pre-commit.legacy` and make it executable.
Run commits in the project's existing Pixi environment so git-annex is available.
This is a coordinator packaging control; it does not alter captured worker hooks.

To verify the retained files against both the filesystem and a committed tree, run `python3 packaging/scoped_annex_pre_commit.py --check-only --tree HEAD`.

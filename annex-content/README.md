# Preserved bootstrap attachment

The treatment worker's original snapshot preserves an annex symlink for `derivatives/gambling-rt/bootstrap_replicates.tsv` without the target payload.
This separate attachment preserves the stopped worker's exact bytes; the original snapshot, symlink and manifest remain unchanged.
It is post-stop coordinator curation, not a worker repair or improved worker-produced score.

The attached path is `treatment/derivatives/gambling-rt/bootstrap_replicates.tsv`.
Its annex key is `SHA256E-s1404481--cf111610171b78bd77a8585a2f0ba81951c64a6beb125b0abdf95505f46986af.tsv`, with 1,404,481 bytes and SHA-256 `cf111610171b78bd77a8585a2f0ba81951c64a6beb125b0abdf95505f46986af`.

From the experiment checkout, after preparing its declared Pixi environment:

```sh
pixi run --frozen git annex get -- annex-content/treatment/derivatives/gambling-rt/bootstrap_replicates.tsv
```

The registered [anonymous retrieval URL](https://hub.centerforopenneuroscience.org/git-annex-p2phttp/git-annex/5a7e64ff-564e-45fb-ac73-9527ada11d8b/key/SHA256E-s1404481--cf111610171b78bd77a8585a2f0ba81951c64a6beb125b0abdf95505f46986af.tsv) returned HTTP 200 and the complete matching payload on 2026-10-14.
[retrieval-verification.json](retrieval-verification.json) records the full-response hash and length check; no authentication or local-object substitution was used for that check.
[metadata-publication.json](metadata-publication.json) records the exact SSH-published `git-annex` ref at delivery time.
Later ordinary metadata merges can advance that ref.

[manifest.json](manifest.json) records the earlier local-copy phase, original worker commit, original annex key, source and snapshot paths, and unchanged snapshot hash.
[upload-operation.json](upload-operation.json) records the upload outcome and credential-capture boundary.
[delivery-duct-manifest.json](delivery-duct-manifest.json) maps complete finished operation logs to byte-verified copies in `../logs/duct/`.
The initial missing-remote-metadata fetch is retained as a failed attempt; the remote had no `git-annex` branch before this publication.

Availability was verified at the recorded time; future service availability is not guaranteed.
No new license for analysis code or derived outputs is asserted by this attachment.

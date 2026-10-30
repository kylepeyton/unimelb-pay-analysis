# Release checks — 30 October 2026

- Restored all 83 R packages recorded in `renv.lock` into a fresh isolated library. Installation required internet access.
- Rebuilt the article with network access, the original Dropbox project, and the normal user R library blocked by the operating-system sandbox. All embedded numerical assertions passed.
- Ran `python3 scripts/check_peer_data.py`: peer indices, four-position averages and CPI references match the supplied numerical inputs.
- Checked the HTML: all six images are embedded; equations are embedded MathML; no broken internal fragment links, duplicate IDs, local-file links or externally loaded page resources were found. External citation URLs were not exhaustively revalidated.
- Generated the PDF using Playwright and locally installed Google Chrome with external requests blocked. All images loaded. Reviewed page images for clipping, equation rendering and page breaks. The PDF has 13 A4 pages.
- Built an explicit file allowlist. Excluded installed libraries, caches, private notes, emails, Viva Engage records and login-gated source files. The author-approved Staff Hub quotation remains in the article.
- Recorded SHA-256 hashes and verified the ZIP contents against the packaged files.

## Changes to the final draft

The author's working Rmd was not modified. The release Rmd has one syntax-only correction: a percent sign in the appendix equation now renders as `2.25%` rather than disappearing. `RELEASE-CHANGES.patch` records the exact one-line change; `release.json` records both source hashes. No prose was changed.

The print stylesheet also removes an unnecessary forced appendix page break. This changes pagination, not content. Licence notices and reproduction instructions are separate files.

## Scope

Reproduction begins with the supplied public-record salary CSVs and archived ABS workbook. The reference extraction scripts and source records document their origins; reconstructing every source PDF is a separate exercise and requires retrieving those documents. The clean build was tested on macOS arm64 with R 4.6.0 and Pandoc 3.10, not on every operating system. The PDF test used installed Chrome rather than a fresh Playwright Chromium download.

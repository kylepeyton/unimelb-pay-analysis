# Melbourne's Nominal Tertiary Education Union

Article and reproducible pay analysis by Kyle Peyton. This release freezes the article and its data as at 30 October 2026.

## Read

**[Read the article online](https://kyle-peyton.com/unimelb-pay/).**

- [Download the HTML article](https://github.com/kylepeyton/unimelb-pay-analysis/raw/refs/heads/main/public-article-kp.html) and open it in your browser.
- [Read or download the PDF](https://github.com/kylepeyton/unimelb-pay-analysis/blob/main/public-article-kp-print.pdf).
- [Download all code and data](https://github.com/kylepeyton/unimelb-pay-analysis/archive/refs/heads/main.zip).

Open `public-article-kp.html` in a browser or `public-article-kp-print.pdf` in a PDF viewer. The HTML includes its figures and equations and works offline. External source links require internet access.

## Reproduce

Install R and Pandoc (RStudio includes Pandoc), then open a terminal in this directory:

```sh
Rscript --vanilla scripts/install.R
Rscript --vanilla scripts/render.R
```

Installation requires internet access and restores the package versions in `renv.lock` into `.local-library/`. Rendering uses the supplied files and needs no university login. It rebuilds all five charts, the scenario table and inline calculations. The supplied cartoon is an illustration, not a calculated figure.

Alternatively, after installing the dependencies, open `public-article-kp.Rmd` in RStudio and Knit to HTML. For PDF, use the browser-print process below rather than the RStudio Knit-to-PDF option.

## Inputs and sources

- CPI: the archived ABS September 2026 workbook, imported by `readabs::read_abs_local()`. Series A2325846C is the original quarterly national all-groups index. The release does not silently update data when compiled.
- Melbourne pay: numerical observations and increases extracted from public agreements and archived salary schedules. Source IDs and table/page references accompany the CSVs; `sources/manifest.json` and `sources/historical-unique-dated-rates.csv` identify the records.
- Peer pay: supplied fixed-position salary observations and indices in `peer-evidence/` and `peer-evidence-unsw/`, with source metadata. The article recalculates the comparisons from these inputs. Optional arithmetic checks: `python3 scripts/check_peer_data.py`.

The starting inputs are the supplied salary CSVs and ABS workbook. Reproducing the article does not require re-extracting every PDF. The historical peer extraction scripts are included for inspection; running those reference scripts would also require the original documents identified by their source records, which are not bundled. They are not part of the article build.

No staff emails, Viva Engage records, login-gated source files, browser data or private notes are included. The article contains the author's approved quotation of the Staff Hub worked example. Other original third-party documents are cited through their source URLs rather than mirrored here.

## Optional PDF

Install Node.js, then run:

```sh
npm ci
npx playwright install chromium
npm run pdf
```

This generates `public-article-kp-print.pdf` from the HTML using the supplied print stylesheet. External resource requests are blocked during PDF rendering.

## Attribution and reuse

ABS material: © Commonwealth of Australia (Australian Bureau of Statistics), Consumer Price Index, Australia, September 2026, Table 17. The workbook is unchanged. Analysis and charts are the author's, not ABS products. ABS material is provided under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), subject to the [ABS exclusions](https://www.abs.gov.au/website-privacy-copyright-and-disclaimer).

Original code is licensed under **MIT**; the original article and figures under **CC BY 4.0**. See `LICENSE` and `LICENSING.md` for scope. Third-party material retains its original rights.

## Version and verification

`release.json` identifies the frozen Rmd and build environment. `SHA256SUMS` records file hashes. `BUILD-CHECKS.md` records the checks performed for this release. Package libraries, caches and private working files are excluded from the distribution.

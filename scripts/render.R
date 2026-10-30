# Run from the repository root: Rscript --vanilla scripts/render.R
if (dir.exists(".local-library")) .libPaths(c(normalizePath(".local-library"), .libPaths()))
required <- c("ggplot2", "ggthemes", "readabs", "knitr", "rmarkdown")
missing <- required[!vapply(required, requireNamespace, logical(1), quietly=TRUE)]
if (length(missing)) stop("Run scripts/install.R first. Missing: ", paste(missing, collapse=", "))
if (!rmarkdown::pandoc_available()) stop("Install Pandoc (or use RStudio's bundled Pandoc).")
rmarkdown::render("public-article-kp.Rmd", output_format="html_document", quiet=TRUE,
                  envir=new.env(parent=globalenv()))
writeLines(c(capture.output(sessionInfo()), paste("Pandoc", rmarkdown::pandoc_version())), "build-session.txt")

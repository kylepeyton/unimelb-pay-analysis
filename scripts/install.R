# Network required once to install the recorded dependencies.
if (!requireNamespace("renv", quietly=TRUE)) install.packages("renv", repos="https://cloud.r-project.org")
dir.create(".local-library", showWarnings=FALSE)
renv::restore(project=getwd(), lockfile="renv.lock", library=file.path(getwd(), ".local-library"), prompt=FALSE)

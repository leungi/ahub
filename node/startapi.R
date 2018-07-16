pkgs <- readLines("requirements.R")
sapply(pkgs, require, character.only=T)
    
router <- plumb("node.R")
router$run(host='0.0.0.0', port=8000, swagger=T)

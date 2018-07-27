library(plumber)
    
router <- plumb("api.R")
router$run(host='0.0.0.0', port=8000, swagger=T)

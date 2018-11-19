#devtools::install_github('qunis/ahub', 'dev', 'packages/ahubr')
library(ahubr)

# BATCH FUNCTION
# ----------------------------------------

#* Batch process running t seconds
#* @param force [1,0] force execution when process was already run today
#* @param t time to execute process
#* @get /batch
#* @json
batch <- function(force = 0, t = 10) {
    daily_batch_process(
        dummy_process,
        process_name = "batch",
        force = force,
        arglist = list(t = t)
        #,debug=T
    )
}


# THREAD FUNCTION
# ----------------------------------------

#* Thread process running t seconds
#* @param t time to execute process
#* @get /thread
#* @json
thread <- function(t = .1) {
    thread_process(
        dummy_process,
        process_name = "thread",
        arglist = list(t = t)
        #,debug=T
    )
}



#* @filter cors
cors <- function(res) {
    res$setHeader("Access-Control-Allow-Origin", "*")
    #res$setHeader("Access-Control-Allow-Method", "POST, GET, OPTIONS")
    #res$setHeader("Access-Control-Allow-Headers", "X-PINGOTHER, Content-Type")
    plumber::forward()
}

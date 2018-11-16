
#' Switch to debug mode
#'
#' @return TRUE/FALSE debug status
#' @export
switch_debug <- function(){
    .ahubEnv$debug <- !.ahubEnv$debug
    return(.ahubEnv$debug)
}


#' Dummy process for demonstrating AHUB batch and thread functionality
#'
#' @param t (float) total process time
#' @param steps (integer) How many process steps
#'
#' @return NOthing
#' @export
dummy_process <- function(t=10, steps=5){
    pid <- get_current_pid(envir = parent.frame())
    for(k in 1:steps){
        pid_log(glue::glue('Executing process step {k}'))
        Sys.sleep(t / steps)
    }
}


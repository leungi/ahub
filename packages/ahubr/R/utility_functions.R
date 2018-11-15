
#' Title
#'
#' @return
#' @export
#'
#' @examples
switch_debug <- function(){
    .ahubEnv$debug <- !.ahubEnv$debug
    return(.ahubEnv$debug)
}


#' Title
#'
#' @param t
#' @param pid
#' @param steps
#'
#' @return
#' @export
#'
#' @examples
dummy_process <- function(t=10, steps=5){
    pid <- get_current_pid(envir = parent.frame())
    for(k in 1:steps){
        pid_log(glue::glue('Executing process step {k}'))
        Sys.sleep(t / steps)
    }
}


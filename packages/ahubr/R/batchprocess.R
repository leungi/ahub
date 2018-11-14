



#' Title
#'
#' @param process_name
#' @param myfun
#' @param force
#' @param arglist
#'
#' @return
#' @export
#'
#' @import glue future futile.logger
#' @importFrom magrittr %>%
#'
#' @examples
daily_batch_process <- function(myfun,
                              process_name = "test",
                              arglist = list(),
                              force=F,
                              debug = F
                              ) {
    #function(force = F, ...) {
        #process_name <- 'batch' # this name is crucial for process logging and status checking
        if(debug) switch_debug()
        pid <- get_pid(process_name) # get the last process id for this process
        pid_info <- get_pid_info(pid) # get the info to the pid

        # has the process already finished today
        run_today <-
            pid_info$time %>% substr(1, 8) %>% lubridate::ymd() == Sys.Date() &
            pid_info$status == 'finished'

        # check if process has not run today and is not finished and force is FALSE
        if (!run_today | as.numeric(force)) {
            # if yes, check if process is not running
            if (pid_info$status != 'running' & init_future()) {
                # if yes start process
                if (pid_info$status != 'init') pid <- create_pid(process_name)

                f <- future({
                    if(debug) switch_debug()
                    # init logging
                    pid_log(pid, glue('Process {process_name} started.'))
                    set_pid_status(pid, 'running')

                    # do some stuff ##################
                    do.call(myfun, arglist)
                    #################################

                    # wrap up
                    pid_log(pid, glue('Process {process_name} finished'))
                    set_pid_status(pid, 'finished')
                    return(TRUE)
                    }, packages=c("futile.logger", "glue", "ahubr"),
                    globals = c("pid", "process_name", "myfun", "arglist", "debug")
                )
                output <-
                    list(
                        msg = glue("Process {process_name} started."),
                        log = get_pid_log(pid),
                        status = 'started',
                        pid = pid
                    )
            } else{
                # if not return log and status
                output <-
                    list(
                        msg = glue("Process {process_name} currently running."),
                        log = get_pid_log(pid),
                        status = 'running',
                        pid = pid
                    )
            }
        } else{
            # if not, do nothing and return log
            output <- list(
                msg = glue("Process {process_name} finished!"),
                log = get_pid_log(pid),
                status = 'finished',
                pid = pid
            )
        }
        output
    #}
}


#' Title
#'
#' @return
#' @export
#'
#' @import future
#'
#' @examples
init_future <- function(){
    if(!.ahubEnv$future_init){
        status <- try(plan(multisession), silent=TRUE)
        if(!inherits(status, 'try-error')){
            assign("future_init", TRUE, envir = .ahubEnv)
            return(TRUE)
        }else{
            flog.error('Could not initialise multisession future for batch processing.')
            return(FALSE)
        }
    }else{
        return(TRUE)
    }
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
    for(k in 1:steps){
        pid_log(glue::glue('Executing process step {k}'))
        Sys.sleep(t / steps)
    }
}











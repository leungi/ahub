
# debug
# boss <- ahubr:::.ahubEnv$boss_api$ops

#' Title
#'
#' @param process_name name of the process
#'
get_pid <- function(process_name){
    if(init_boss_api()){
        httr::content(.ahubEnv$boss_api$ops$get_pid(process_name))$pid
    }
}

#' Title
#'
#' @param pid (int) process id
#'
get_pid_info <- function(pid){
    if(init_boss_api()){
        httr::content(.ahubEnv$boss_api$ops$get_pid_info(pid))
    }
}

#' Title
#'
#' @param process_name (character) process name
#'
create_pid <- function(process_name){
    if(init_boss_api()){
        httr::content(.ahubEnv$boss_api$ops$create_pid(process_name))$pid
    }
}

#' Title
#'
#' @param pid (int) process id
#' @param status (character) status "finished", "running", "aborted", "init"
set_pid_status <- function(pid, status){
    if(init_boss_api()){
        httr::content(.ahubEnv$boss_api$ops$set_pid_status(pid, status))
    }
}


#' Title
#'
#' @param pid (int) process id
get_pid_log <- function(pid){
    if(init_boss_api()){
        httr::content(.ahubEnv$boss_api$ops$get_pid_log(pid))
    }
}


#' Write log to boss with given PID
#'
#' @param msg Message to log
#' @param level Log level INFO, DEBUG, WARN, or ERROR
#'
#' @export
#'
#' @return Nothing
pid_log <- function(msg, level = "INFO"){
    pid <- try(get_current_pid(envir = parent.frame()), silent=T)
    if(init_boss_api()){
        if(!inherits(pid, "try-error") & !is.null(msg)){
            ans <- try(
                .ahubEnv$boss_api$ops$pid_log(pid, msg, level),
                silent=T)
            if(inherits(ans, "try-error")){
                flog.error(glue::glue('Could not write log for {pid}'))
            }
        }else{
            flog.error('Log not written. Provide PID and MSG.')
            flog.error(pid)
        }
    }else{
        flog.error(glue::glue('Could not write log for {pid}'))
    }
}


#' Retrieve pid from given environment
#'
#' @param envir environment
#' @export
#'
get_current_pid <- function(envir){
    get("pid", envir = envir)
}


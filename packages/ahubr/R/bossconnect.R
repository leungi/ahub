#   Build and Reload Package:  'Ctrl + Shift + B'
#   Check Package:             'Ctrl + Shift + E'
#   Test Package:              'Ctrl + Shift + T'


.ahubEnv <- new.env()

.ahubEnv$debug <- FALSE

.ahubEnv$debughost <- 'ahub.westeurope.cloudapp.azure.com'
.ahubEnv$host <- 'nginx'
.ahubEnv$boss_init <- FALSE
.ahubEnv$redis_init <- FALSE
.ahubEnv$future_init <- FALSE

#' Get the boss api object
#'
#' @param host (character) hostname
#' @param port (int) port
#'
#' @return TRUE/FALSE if connection was successfully established
#'
#' @import futile.logger
#'

init_boss_api <- function(
    host = ifelse(.ahubEnv$debug, .ahubEnv$debughost, .ahubEnv$host),
    port = 8000
    ){
    if(!.ahubEnv$boss_init){
        boss_api <- get_node_api('boss', host = host, port = port)

        if(length(boss_api)>1){
            assign("boss_api", boss_api, envir = .ahubEnv)
            assign("boss_init", TRUE, envir = .ahubEnv)
            flog.info(glue::glue("Boss API initialised on {host}:{port}"))
            return(TRUE)
        }else{
            flog.error(glue::glue("Boss API could not be found on {host}:{port}"))
            return(FALSE)
        }
    }else{
        return(TRUE)
    }
    }



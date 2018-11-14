
#' Check with boss of redis database is online
#'
#' @return
check_redis <- function() {

    if(!init_boss_api()){
        return(FALSE)
    }else{
        status <- try(
            httr::content(.ahubEnv$boss_api$ops$get_redis_status())$online,
            silent=FALSE)
        if(!inherits(status, "try-error")){
            return(status)
        }else{
            flog.error("Redis status cannot be read.")
            flog.error(status)
            return(FALSE)
        }
    }
}

#' Connect to redis database for direct write access
#'
#' @param host
#'
#' @return
connect_redis <- function(host = ifelse(.ahubEnv$debug, .ahubEnv$debughost, 'redis')) {
    if(check_redis()){
        rediscon <- try(rredis::redisConnect(host=host, returnRef = T), silent=T)
    }else{
        flog.error('Redis connection aborted. Not reachable by boss.')
        return(FALSE)
    }
    if(!inherits(rediscon, "try-error")){
        flog.info('Redis connection established.')
        return(TRUE)
    }else{
        flog.error('Could not establish Redis connection.')
        flog.error(rediscon)
        return(FALSE)
    }

}

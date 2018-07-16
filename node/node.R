
plan(multiprocess)
nodename <- Sys.info()[["nodename"]]
if(file.exists('finished')) file.remove('finished')
if(file.exists('running')) file.remove('running')

#*execute
#* @param force Forces execution even if file already exists
#* @get /
#* @json
a <- function(force = F) {
    if (!file.exists('finished') | force ==T) {
        if(!file.exists('running')) {
            result %<-% {
                # init logging
                pid <- Sys.getpid()
                flog.threshold(DEBUG)
                flog.appender(appender.file('process.log'))
                flog.info('PID %s on Node %s: Process started', pid, nodename)
                write(pid, 'running') # create running file
                
                # do some stuff ##################
                Sys.sleep(20)
                ##################################
                
                # wrap up
                flog.info('PID %s on Node %s: Process finished', pid, nodename)
                write(pid, 'finished') # write finished file
                file.remove('running') # remove running file
                return(TRUE)
            } 
            output <- list(msg = paste("Node", nodename, ": Process started..."))
            } else{ # return while running
                output <- list(msg = paste("Node", nodename,": Process currently running...", Sys.time() - file.info('running')$ct))
        }
    } else{ # return when finished
        output <- list(msg = paste("Node", nodename, ": Process finished!"))
    }
    output
}


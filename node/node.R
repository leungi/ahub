
plan(multisession)
nodename <- Sys.info()[["nodename"]]
if(file.exists('finished')) file.remove('finished')
if(file.exists('running')) file.remove('running')

#* batch
#* @param force Forces another execution even if process is already running
#* @param t process time sleep
#* @get /batch
#* @json
batch <- function(t = 20, force = F) {
    if (!file.exists('finished') | force ==T) {
        if(!file.exists('running')) {
            result %<-% {
                # init logging
                pid <- Sys.getpid()
                flog.threshold(DEBUG)
                flog.appender(appender.file('process.log'))
                flog.info('PID %s on Node %s: Batch process started', pid, nodename)
                write(pid, 'running') # create running file
                
                # do some stuff ##################
                Sys.sleep(t)
                ##################################
                
                # wrap up
                flog.info('PID %s on Node %s: Batch process finished', pid, nodename)
                write(pid, 'finished') # write finished file
                file.remove('running') # remove running file
                return(TRUE)
            } 
            output <- list(msg = paste("Node", nodename, ": Batch process started..."))
            } else{ # return while running
                output <- list(msg = paste("Node", nodename,": Batch process currently running...", Sys.time() - file.info('running')$ct))
        }
    } else{ # return when finished
        output <- list(msg = paste("Node", nodename, ": Batch process finished!"))
    }
    output
}

#* thread
#* @param t process time sleep
#* @get /thread
#* @json
thread <- function(t = 2) {
    # init logging
    pid <- Sys.getpid()
    flog.threshold(DEBUG)
    flog.appender(appender.file('process.log'))
    flog.info('PID %s on Node %s: Thread Process started', pid, nodename)
    
    
    # do some stuff ##################
    Sys.sleep(t)
    ##################################
    
    # wrap up
    flog.info('PID %s on Node %s: Thread Process finished', pid, nodename)
    output <-
        list(msg = paste("Node", nodename, ": Thread Process finished!"))
    
    output
}



a <- future(Sys.sleep(10))


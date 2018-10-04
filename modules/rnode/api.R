library(tidyverse)
library(rredis)
library(future)
library(futile.logger)
library(glue)
library(lubridate)

plan(multisession)

# REDIS INIT
# ----------------------------------------

# Connect to redis
source('redis_functions.R')
redissrv <- ifelse(interactive(), 'localhost', 'redis')
rediscon <- try(redisConnect(host=redissrv, returnRef = T), silent=T)
# init pid if not exists
redisSet('next_pid', charToRaw('1000'), NX =TRUE)
# clean ip process ids which are still on status "running"
cleanup_pids()


# BATCH FUNCTION
# ----------------------------------------

#* Batch process running t seconds
#* @param force [1,0] force execution when process was already run today
#* @param t time to execute process
#* @get /batch
#* @json
batch <- function(force = 0, t = 20) {
	
	process_name <- 'batch' # this name is crucial for process logging and status checking

	pid <- get_pid(process_name) # get the last process id for this process
	pid_info <- get_pid_info(pid) # get the info to the pid
	
	# has the process already finished today
	run_today <- pid_info$time %>% str_sub(1,8) %>% ymd() == Sys.Date() &
		pid_info$status == 'finished'
	
	# check if process has not run today and is not finished and force is FALSE
	if (!run_today | as.numeric(force)) {
		# if yes, check if process is not running
		if(pid_info$status != 'running') {
			# if yes start process
			if(pid_info$status != 'init') pid <- create_pid(process_name)
			result %<-% {
				# init logging
				redisConnect(redissrv)
				#flog.threshold(DEBUG)
				flog.appender(appender.redis(pid))
				flog.info('Process %s started', process_name)
				set_pid_status(pid, 'running')

				# do some stuff ##################
				dummy_process(pid, t)
				##################################
				
				# wrap up
				flog.info('Process %s finished', process_name)
				set_pid_status(pid, 'finished')
				return(TRUE)
			}
			output <- list(msg=glue("Process {process_name} started..."), 
						   log=get_pid_log(pid),
						   status = 'started')
		} else{ # if not return log and status
			output <- list(msg=glue("Process {process_name} currently running..."),  
						   log=get_pid_log(pid),
						   status = 'running')
		}
	} else{ # if not, do nothing and return log
		output <- list(msg=glue("Process {process_name} finished!"), 
					   log=get_pid_log(pid),
					   status = 'finished')
	}
	output
}


dummy_process <- function(pid, t, steps=5){
	flog.threshold(DEBUG)
	flog.appender(appender.redis(pid))
	for(k in 1:steps){
		flog.info('Executing process step %s', k)	
		Sys.sleep(t / steps)
	}
}


# THREAD FUNCTION
# ----------------------------------------

#* thread
#* @param t process time
#* @get /thread
#* @json
thread <- function(t = 1) {
	# init logging
	
	process_name <- 'thread' # this name is crucial for process logging and status checking
	
	pid <- get_pid(process_name) # get the last process id for this process
	pid_info <- get_pid_info(pid) # get the info to the pid 
	# icheck if process is running or finished, if yes create new pid
	if(pid_info$status != 'init') pid <- create_pid(process_name)
	#flog.threshold(DEBUG)
	flog.appender(appender.redis(pid))
	flog.info('Process %s started', process_name)
	set_pid_status(pid, 'running')
	# do some stuff ##################
	dummy_process(pid, as.numeric(t))
	##################################
	set_pid_status(pid, 'finished')
	# wrap up
	flog.info('Process %s finished', process_name)

	
	output <- list(msg=glue("Process {process_name} finished!"), 
				   log=get_pid_log(pid),
				   status = 'finished')
	output
}




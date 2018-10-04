# redis functions
library(tidyverse)
library(rredis)
library(lubridate)

options(digits.secs=3)

# redis data model for process monitoring and logging
# ------------------------------------------
# next_pid -> starten mit 1000 und dann immer INCR
# 
# lists
# 	log:[pid] -> [logentry] z.B. log:1000 -> "INFO [timestamp] Process has started"
#		- this list contains all logs per pid
# 
# ordered sets
# 	[process_name] [time] -> [process_id] i.e. fta_forecast 20180706154020 -> 1001
#		- this set contains all pids to a given process, ordered by timestamp
# 
# sets
# 	process_names -> [all process names]
#		- this set contains all process names
# 
# hashes
# 	process:[pid] with fields
# 		name -> [process_name]
# 		time -> [time]
# 		status -> [running, finished, aborted]
#		error -> [errormsg]
#		-this hash contains info for each process



# debug
# process_name <- 'fta_forecast'
# get_pid(process_name)
# create_pid(process_name)
# pid <- 1012
# set_pid_status(pid, 'running')
# get_pid_info(pid)
# set_pid_status(pid, 'finished')

# timestamper
sf <- stamp('20180817235959.100', quiet = T)

# gets the latest pid for a process or create a new one if never run before
get_pid <- function(process_name){
	pid <- redisZRange(process_name, -1, -1)
	if(is.null(pid)) pid <- create_pid(process_name)
	return(pid)
}

# this function creates a new pid for a given process_name and sets the status to 'init'
create_pid <- function(process_name){
	redisSAdd('process_names', charToRaw(process_name))
	tstamp <- get_current_time()
	pid <- redisIncr('next_pid')
	# add pid to sorted set [process_name], score is time
	redisZAdd(process_name, tstamp, pid)
	
	# create hash
	redisHMSet(paste0('process:', pid),
			   list(name=process_name,
			   	 time = tstamp,
			   	 status = 'init'))
	return(pid)
}

# get all infos from a pid, current fields are
# name, time, status
get_pid_info <- function(pid){
	redisHGetAll(paste0('process:', pid))
}

# set status of a pid
set_pid_status <- function(pid, status){
	temp <- redisHSet(key=paste0('process:', pid), field='status', value=charToRaw(status))
	return(status)
}

# helper function to convert an R timestamp
# example: 2018-05-26 15:23:12.123 returns 20180526152312123
# Always UTC
get_current_time <- function(){
	Sys.time() %>% as.POSIXlt(tz='GMT') %>% sf() %>% gsub('\\.', '', .)
}

# custom appender function for the packages futile.logger
# writes log to redis list log:[pid] instead of file
appender.redis <- function(pid=NULL){
	function(line){
		if(!is.null(pid)){
			line <- line %>% 
				sub('(\\[.+\\])', glue::glue('\\1 PID {pid}:'), .) %>% 
				sub('\n', '', .)
			redisLPush(paste0('log:', pid), charToRaw(line))
		}else{
			redisLPush('log', charToRaw(line))
		}
	}
}

# return all logs from a given pid
get_pid_log <- function(pid){
	redisLRange(paste0('log:', pid), 0, -1) %>% unlist()
}

# set all running pids to aborted
cleanup_pids <- function(){
    flog.appender(appender.redis(pid))
    allnames <- redisSMembers('process_names') %>% unlist
	for(process_name in allnames)
	{
		pid <- get_pid(process_name)
		# if status is running then abort
		if(get_pid_info(pid)$status %in% c('running', 'init')){
			set_pid_status(pid, 'aborted')
			msg <- 'Process aborted by cleanup process.'
			redisHSet(paste0('process:', pid), 'error', charToRaw(msg))
			flog.error(msg)	
		} 
	}
}

# retrieve all pid's for all process_names
get_all_pids <- function(){
	sapply(redisSMembers('process_names') %>% unlist,
		   function(x) redisZRange(x, start=0, end=-1) %>% unlist)
}

# retrieve all logs
get_all_logs <- function(){
	pidlist <- get_all_pids()
	logslist <- list()
	#p <- pidlist[[1]]
	#sapply(pidlist, function(x)	
	for(k in 1:length(pidlist)){
		logs <- sapply(pidlist[[k]], function(x) redisLRange(paste0('log:', x), 0, -1) %>% unlist)
		logslist[[k]] <- tibble(process = names(pidlist)[k], pid = pidlist[[k]], log = logs)
	}
	bind_rows(logslist) %>% arrange(pid)
}

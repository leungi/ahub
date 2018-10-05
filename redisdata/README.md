# Redis data folder

This folder contains the .rdb file which persists all logging and process information of the analytical nodes.

The redis data model is as follows:

## keys 
	next_pid -> process id counter, always incremented with INCR 
 
## lists
 	log:[pid] -> [logentry] i.e. log:1000 -> "INFO [timestamp] Process has started"
		- this list contains all logs per pid
 
## ordered sets
 	[process_name] [time] -> [process_id] i.e. fta_forecast 20180706154020 -> 1001
		- this set contains all pids to a given process, ordered by timestamp
 
## sets
 	process_names -> [all process names]
		- this set contains all process names
 
## hashes
 	process:[pid] with fields
 		name -> [process_name]
 		time -> [time]
 		status -> [running, finished, aborted]
		error -> [errormsg]
		-this hash contains info for each process


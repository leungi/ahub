library(rredis)
rredis::redisConnect()

redisRPush('log', 'msg1')
redisLRange('log', 1 ,-1)


push


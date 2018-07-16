# ignore certificate
set_config(config(ssl_verifypeer = 0L, ssl_verifyhost=0L))

hostname <- ifelse(interactive(), "localhost", "nginx")

errmsg <- try({
    ops_node1 <- get_ops(host = hostname, port = 443, dir="node1", uid='test', pwd='test')
    ops_node2 <- get_ops(host = hostname, port = 443, dir="node2", uid='test', pwd='test')
}, silent=T)

ops_fetched <- ifelse(!inherits(errmsg, "try-error"), T, F)

# debug
#httr::with_verbose(ops_node1$`_execute`() %>% content())
#httr::with_verbose(ops_node2$`_execute`() %>% content())

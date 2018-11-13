# ignore certificate
# set_config(config(ssl_verifypeer = 0L, ssl_verifyhost = 0L))


host <- ifelse(interactive(), "ahub.westeurope.cloudapp.azure.com", "nginx")

# uid <- "ahub"
# pwd <- "ilikebigwhales"

port <- 8000

boss_api <- get_node_api('boss', host = host, port = port)

apis_to_fetch <- content(boss_api$ops$get_services())$apis %>% 
    unlist()



node_api <-
    sapply(
        apis_to_fetch,
        get_node_api,
        host = host, 
        port = port, simplify = F
    )

node_html <-
    sapply(
        apis_to_fetch,
        get_node_html,
        host = host, 
        port = port, simplify = F
    )


# debug
#httr::with_verbose(ops_node1$`_execute`() %>% content())
#httr::with_verbose(ops_node2$`_execute`() %>% content())

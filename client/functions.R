


get_ops <-
    function(host = 'localhost',
             port = '80',
             dir = 'node1',
             uid = NULL,
             pwd = NULL) {
        
        scheme <- ifelse(port == 443, 'https', 'http')
        
        if (is.null(uid)) {
            # without basic auth
            swagger <- GET(url=glue::glue("{scheme}://{host}:{port}/{dir}/swagger.json")) %>% content() 
        } else{
            # with basic auth
            swagger <- GET(url=glue::glue("{scheme}://{uid}:{pwd}@{host}:{port}/{dir}/swagger.json")) %>% content() 
        }
        # exchange hostname and paths in swagger definition
        swagger$host <- paste0(host, ":", port)
        names(swagger$paths) <- paste0('/', dir, names(swagger$paths))
        swagger$schemes <- list(scheme)
        
        # get api definition from swagger
        api <- get_api(toJSON(swagger))
        
        # extract valid operations
        get_operations(api,
                       .headers = c("Authorization" = paste(
                           "Basic", glue::glue("{uid}:{pwd}") %>% base64_enc()
                       )))
    }


#swagger <- GET(url=glue::glue("{protocol}://{uid}:{pwd}@{host}:{port}/{dir}/swagger.json")) %>% content() 

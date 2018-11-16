


#' Get Node API from swagger documentation
#'
#' @param dir (character) endpoint
#' @param host (character) hostname
#' @param port (int) port
#' @param uid (character) User ID for basic authentication (deprecated)
#' @param pwd (character) Password for basic authentication (deprecated)
#'
#' @return list with content or error message
#' @export
#'
#' @import httr rapiclient jsonlite
get_node_api <-
    function(dir = 'node1',
             host = 'localhost',
             port = '8000',
             uid = NULL,
             pwd = NULL) {

        scheme <- ifelse(port == 443, 'https', 'http')

        auth <- ifelse(is.null(uid), "", glue::glue('{uid}:{pwd}@'))

        response <- try(
            GET(url=glue::glue("{scheme}://{auth}{host}:{port}/{dir}/swagger.json"),
                silent=TRUE)
        )

        if(!inherits(response, 'try-error')){
            if(response$status_code==200){
                swagger <-  content(response)
                swagger_url <- glue::glue("{scheme}://{auth}{host}:{port}/{dir}/__swagger__/")

                # exchange hostname and paths in swagger definition
                swagger$host <- paste0(host, ":", port)
                names(swagger$paths) <- paste0('/', dir, names(swagger$paths))
                swagger$schemes <- list(scheme)

                # get api definition from swagger
                api <- get_api(toJSON(swagger))

                # extract valid operations
                if(length(auth)){
                    ops <- get_operations(api,
                                          .headers = c("Authorization" = paste(
                                              "Basic", base64_enc(glue::glue("{uid}:{pwd}"))
                                          )))
                }else{
                    ops <- get_operations(api)
                }

                return(list(api = api,
                            ops = ops,
                            swagger= swagger,
                            swagger_url = swagger_url))
            }else{
                return(list(errmsg = response$status_code))
            }
        }else{
            return(list(errmsg = response[[1]]))
        }
    }


#' Get HTML content from analytical node
#'
#' @param dir (character) endpoint
#' @param host (character) hostname
#' @param port (int) port
#' @param uid (character) User ID for basic authentication (deprecated)
#' @param pwd (character) Password for basic authentication (deprecated)
#'
#' @return list with content or error message
#' @export
#'
#' @import httr
get_node_html <-
    function(dir = 'node1',
             host = 'localhost',
             port = '8000',
             uid = NULL,
             pwd = NULL) {
        scheme <- ifelse(port == 443, 'https', 'http')
        auth <- ifelse(is.null(uid), "", glue::glue('{uid}:{pwd}@'))
        response <- try(
            GET(url=glue::glue("{scheme}://{auth}{host}:{port}/{dir}/"))
        )

        if(!inherits(response, 'try-error')){
            if(response$status_code == 200){
                return(list(content = content(response)))
            }else{
                return(list(errmsg = response$status_code))
            }
        }else{
            return(list(errmsg = response[[1]]))
        }

    }

#swagger <- GET(url=glue::glue("{protocol}://{uid}:{pwd}@{host}:{port}/{dir}/swagger.json")) %>% content()



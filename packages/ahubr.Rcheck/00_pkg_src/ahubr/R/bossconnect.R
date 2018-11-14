# Hello, world!
#
# This is an example function named 'hello'
# which prints 'Hello, world!'.
#
# You can learn more about package authoring with RStudio at:
#
#   http://r-pkgs.had.co.nz/
#
# Some useful keyboard shortcuts for package authoring:
#
#   Build and Reload Package:  'Ctrl + Shift + B'
#   Check Package:             'Ctrl + Shift + E'
#   Test Package:              'Ctrl + Shift + T'

debughost <- 'ahub.westeurope.cloudapp.azure.com'

redishost <- ifelse(interactive(), debughost , 'redis')
nginxhost <- ifelse(interactive(), debughost , 'nginx')



#' Title
#'
#' @param host
#'
#' @return
#' @export
#'
#' @examples
checkboss <- function(host = 'nginx') {
    port <- 8000
    boss_api <- get_node_api('boss', host = host, port = port)
}




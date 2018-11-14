
#' Title
#'
#' @return
#' @export
#'
#' @examples
switch_debug <- function(){
    .ahubEnv$debug <- !.ahubEnv$debug
    return(.ahubEnv$debug)
}


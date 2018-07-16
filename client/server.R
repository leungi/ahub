server <- function(input, output, session){
    
    ans1 <- reactiveVal(NULL)
    ans2 <- reactiveVal(NULL)
    logcontent <- reactiveVal(NULL)
    err <- reactiveVal(NULL)
    
    observeEvent(input$logrefresh, {
        logcontent(read_file('../process.log'))
    })
    
    observeEvent(input$exec1, {
        if(ops_fetched){ # only when operations are fetched
            response <- ops_node1[[1]]()
            ans1(httr::content(response))    
        }else{
            err(errmsg)
        }
    })
    
    observeEvent(input$exec2, {
        if(ops_fetched){ # only when operations are fetched
            response <- ops_node2[[1]]()
            ans2(httr::content(response))    
        }else{
            err(errmsg)
        }
    })
    
    output$result1 <- renderPrint({
        ans1()
    })
    
    output$result2 <- renderPrint({
        ans2()
    })
    
    output$logfile <- renderPrint({
        cat(logcontent())
    })
    
    output$error <- renderPrint({
        cat(err())
    })
    
    # debugging request header
    output$summary <- renderText({
        ls(env=session$request)
    })
    
    output$headers <- renderUI({
        selectInput("header", "Header:", ls(env=session$request))
    })
    
    output$value <- renderText({
        if (nchar(input$header) < 1 || !exists(input$header, envir=session$request)){
            return("NULL");
        }
        return (get(input$header, envir=session$request));
    })
    
    
    
}

shinyServer(server)
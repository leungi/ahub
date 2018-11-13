#devtools::install_github("nik01010/dashboardthemes")

# Define packages
pkgs <- c('tidyverse',
          'shiny',
          'shinyjs',
          'shinydashboard',
          'dashboardthemes',
          'rapiclient',
          'jsonlite',
          'httr'
          )

# load packages
loadflag <- sapply(pkgs, require, character.only = T, quietly = T)

source('functions.R')


source('init.R')



### creating custom logo object
custom_logo <- shinyDashboardLogoDIY(
    boldText = "AHUB",
    mainText = "",
    textSize = 16,
    badgeText = "ALPHA",
    badgeTextColor = "white",
    badgeTextSize = 2,
    badgeBackColor = "#40E0D0",
    badgeBorderRadius = 3
)

################################################
### HEADER ###
################################################
header <- dashboardHeader(title = custom_logo)

################################################
### SIDEBAR ###
################################################

sidebar <- dashboardSidebar(sidebarMenu(
    menuItem(
        "Node 1",
        tabName = "node1",
        icon = icon("globe")
    ),
    menuItem(
        "Node 2",
        tabName = "node2",
        icon = icon("globe")
    ),
    menuItem(
        "Node 3",
        tabName = "node3",
        icon = icon("globe")
    ),
    menuItem("Logs", tabName = "logs", icon = icon("info-circle")), 
    menuItem("HTML Header", tabName = "headertab", icon = icon("info-circle")),
    verbatimTextOutput('error')
))

################################################
### BODY ####
################################################
body <- dashboardBody(
    useShinyjs(),
    shinyDashboardThemes(theme = "blue_gradient"),
    tabItems(
        tabItem(tabName = "node1",
                tabBox(width = 12,
                    #status = "primary",
                    title = "Node 1",
                    tabPanel('Single execution',
                        actionButton('exec_batch1', 'Run batch operation'),
                        actionButton('exec_thread1', 'Run thread operation'),
                        verbatimTextOutput('result1')
                        ),
                    tabPanel('Swagger',
                        p()
                        )
                    )
                ),
        tabItem(tabName = "node2",
                tabBox(width = 12,
                   #status = "primary",
                   title = "Node 2",
                   tabPanel('Single execution',
                            actionButton('exec_batch2', 'Run batch operation'),
                            actionButton('exec_thread2', 'Run thread operation'),
                            verbatimTextOutput('result2')
                        ),
                   tabPanel('Swagger',
                        p()
                        )
                    )
                ),
        tabItem(tabName = "node3",
                box(width = 12,
                   #status = "primary",
                   title = "Node 3",
                   htmlOutput('prophetdemo')
                   #includeHTML('test.html')
                )
        ),
        tabItem(tabName = 'logs',
                box(
                    width = 12,
                    status = "primary",
                    title = "Logfile",
                    actionButton('logrefresh', 'Refresh'),
                    verbatimTextOutput('logfile')
                )),
        tabItem(tabName = 'headertab',
                pageWithSidebar(
                    headerPanel("Shiny Client Data"),
                    sidebarPanel(
                        uiOutput("headers")
                    ),
                    mainPanel(
                        h3("Headers passed into Shiny"),
                        verbatimTextOutput("summary"),
                        h3("Value of specified header"),
                        verbatimTextOutput("value")
                    )
                ))
        
    )
)


shinyUI(
    dashboardPage(header, sidebar, body, title = 'AHUB by QUNIS')
)



# Run the application
#shinyApp(ui = ui, server = server)


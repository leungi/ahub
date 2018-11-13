library(xml2)
library(tidyverse)
doc <- read_html('out.html')




#scripts <- 
    
nodes <-  doc %>% xml_find_all('//head/script | //head/link | //body/*')
        

tt <- xml_new_root('div')
for(node in nodes){
    xml_add_child(tt, node)
}


xml2::write_html(tt, 'test.html', options='no_declaration')




scripts <- getNodeSet(doc, '//head/script')
links <- getNodeSet(doc, '//head/link')
body <- getNodeSet(doc, '//body/*')



tt <- xmlHashTree()
top <- addNode(xmlNode("div"), character(), tt) 
addNode(links, parent= top, to=tt)

for(k in seq_along(scripts)){
    append.xmlNode(top, scripts[k])
}

##parameters=query=''
#

recordList = context.Catalog.searchResults(mailFrom=query) + \
             context.Catalog.searchResults(mailSubject=query) + \
             context.Catalog.searchResults(mailBody=query)  

return context.cpsmailboxer_search_result(recordList=recordList, query=query)

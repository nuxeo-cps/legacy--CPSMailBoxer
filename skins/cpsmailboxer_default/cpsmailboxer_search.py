##parameters=query=''
#

recordList = context.Catalog.searchResults(mailFrom=query) + \
             context.Catalog.searchResults(mailSubject=query) + \
             context.Catalog.searchResults(mailBody=query)  
              
return context.folder_view(recordList=recordList, query=query)

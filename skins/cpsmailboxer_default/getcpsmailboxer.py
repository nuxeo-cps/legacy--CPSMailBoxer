##parameters=
#

parent = context.this()

while parent.getProperty('portal_type') == 'Folder':
    parent = parent.aq_parent

return parent

    

##parameters=
#

parent = context

while getattr(parent, 'portal_type') != 'CPSMailBoxer':
    parent = parent.aq_parent

return parent
    

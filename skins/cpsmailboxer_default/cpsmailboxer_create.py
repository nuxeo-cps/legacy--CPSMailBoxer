##parameters=REQUEST=None, **kw


if REQUEST is not None :
    kw.update(REQUEST.form)

psm = ''
ob = None
type_name = 'CPSMailBoxer'

id = kw.get('title')
id = context.computeId(compute_from=id)
url = context.absolute_url()
action_path = context.getTypeInfo().getActionById('view')

try:
    context.invokeFactory(type_name, id, **kw)
    ob = getattr(context, id)
    action_path = ob.getTypeInfo().getActionById('edit')
    url = ob.absolute_url()
    psm = 'Lettre+de+diffusion+créée'
except Exception, Message:
    psm = msg


if REQUEST is not None:
    REQUEST.RESPONSE.redirect('%s/%s?portal_status_message=%s' % (url, 
                              action_path, psm))
return psm
        

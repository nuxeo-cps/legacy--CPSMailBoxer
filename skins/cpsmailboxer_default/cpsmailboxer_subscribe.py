##parameters=REQUEST=None, **kw

# $Id$

if REQUEST is not None:
    kw.update(REQUEST.form)

email = kw.get('address', None)

if context.checkEmail(email) == 'ok':
    try:
        theboxer = context.getcpsmailboxer()
        theboxer.manage_addMember(email.lower()) # No check and no confirmation !
        psm = 'psm_subscribed'
    except Exception, msg:
        psm = str(msg)
        
    if REQUEST is not None:    
        REQUEST.RESPONSE.redirect(context.absolute_url()+"/cpsmailboxer_subscribe_form?portal_status_message="+psm)
        return
else:
    psm = 'psm_subscribing_error'
    url = context.absolute_url()+"/cpsmailboxer_subscribe_form"
    
    if REQUEST is not None:
        REQUEST.RESPONSE.redirect(url+"?portal_status_message="+psm)
        return
    
return psm

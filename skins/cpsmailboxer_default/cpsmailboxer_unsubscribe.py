##parameters=REQUEST=None, **kw

# $Id$

#Warning: this script has a proxy role (Owner) associated with it as it
#         requires permission to run manage_delMember (which can be called
#         by any user that has access to the mailing list.
#XXX: investigate the possibility to do additional checks before actually
#running this script, like comparing the currently authenticated user's email
#to the one that wants to be unsubscribed

if REQUEST is not None:
    kw.update(REQUEST.form)

email = kw.get('address', None)

if context.checkEmail(email) == 'ok':
    mailboxer = context.getcpsmailboxer()
    mailboxer.manage_delMember(email.lower()) # No check and no confirmation !
    psm = 'psm_unsubscribed'
    context.REQUEST.RESPONSE.redirect(context.absolute_url()+"/cpsmailboxer_subscribe_form?portal_status_message="+psm)
else:
    psm = 'psm_subscribing_error'
    url = context.absolute_url()+"/cpsmailboxer_subscribe_form"
    context.REQUEST.RESPONSE.redirect(url+"?portal_status_message="+psm)

return psm

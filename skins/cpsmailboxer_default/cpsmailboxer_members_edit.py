##parameters=REQUEST=None
#
# $Id$

kw = REQUEST.form

liste = kw.get('liste', [])

if not same_type(liste, []):
    liste = [liste]

mailboxer = context.getcpsmailboxer()

for item in liste:
    try:
        mailboxer.manage_delMember(item.lower())
    except ValueError:
        pass

if REQUEST is not None:
    url = context.absolute_url()+"/cpsmailboxer_members_edit_form"
    psm = 'psm_removed_members'
    REQUEST.RESPONSE.redirect(url+"?portal_status_message="+psm)
    return

##parameters=REQUEST=None
#
# $Id$

kw = REQUEST.form

if not kw['mailto']:
    msg = 'error_mailto'
    return context.cpsmailboxer_edit_form(error_message=msg)

if not kw['moderator']:
    msg = 'error_moderator'
    return context.cpsmailboxer_edit_form(error_message=msg)

doc = context # would be context.getContent() if manipulating a proxy

moderators = [m.strip() for m in kw['moderator'].split() if not m.isspace()]
kw['moderator'] = moderators

kw['moderated'] = not not kw.get('moderated')

mtahosts = [m.strip() for m in kw['mtahosts'].split() if not m.isspace()]
kw['mtahosts'] = mtahosts

try :
    doc.edit(**kw)
    psm = 'psm_content_changed'
except Exception, msg :
    psm = msg

if doc.id.startswith('my_cpsmailboxer'):
    # if mailboxer was created without provinding a title, something
    # like my_cpsmailboxer5555 was generated ; in that case, compute id
    # from title when it is provided
    title_for_id = kw.get('title', 'nmb')
    new_id = context.computeId(compute_from=title_for_id)
    if new_id != doc.id:
        context.aq_inner.aq_parent.manage_renameObjects([doc.id], [new_id], REQUEST)

# Redirection
if REQUEST:
    action_path = doc.getTypeInfo().getActionById('edit')
    REQUEST.RESPONSE.redirect('%s/%s?portal_status_message=%s' %
                              (context.absolute_url(), action_path,
                               psm))
    return

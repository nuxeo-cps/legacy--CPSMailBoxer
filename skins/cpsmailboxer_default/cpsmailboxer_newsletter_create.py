##parameters=REQUEST=None, **kw
#

if REQUEST is not None:
    kw.update(REQUEST.form)

texte = kw.get('texte', None)
subject = kw.get('subject', '')

if texte is not None:
    myboxer = context.getcpsmailboxer()
    myboxer.sendtoList(context, subject=subject, texte=texte)

if REQUEST is not None:
    REQUEST.RESPONSE.redirect(context.absolute_url())

##parameters=zoomed_msg_path='', REQUEST=None

# $Id$

try:
    proxy = context.restrictedTraverse(zoomed_msg_path)
    if context.portal_workflow.getInfoFor(proxy, 'review_state', '') == 'pending':
        return proxy
    else:
        return None
except KeyError:
    return None

##parameters=name=''

mtool = context.portal_membership
found = mtool.searchMembers('username',name)
if found != []:
    return found[0]['email']
else:
    return ''

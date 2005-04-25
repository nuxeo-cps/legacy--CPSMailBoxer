##parameters=obj=None,maxchar=80
#

if obj is None:
    obj = context

body = []

mailbody = getattr(obj.getContent(), 'mailBody')

for line in mailbody.split('\n'):
    if len(line) > maxchar:
        body.append(line[:maxchar])
        body.append(line[maxchar:])
    else:
        body.append(line)
       
return '\n'.join(body)

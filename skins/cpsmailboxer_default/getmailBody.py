##parameters=maxchar=80
#

#return context.mailBody

body = []

for line in context.mailBody.split('\n'):
    if len(line) > maxchar:
        body.append(line[:maxchar])
        body.append(line[maxchar:])
    else:
        body.append(line)
        
return '\n'.join(body)

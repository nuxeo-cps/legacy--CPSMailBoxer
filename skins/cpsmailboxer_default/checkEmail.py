##parameters=address=None

import re

chars = re.compile(r"[^a-z0-9_\@\.\-]")
form = re.compile(r"^([a-z0-9_]|\-|\.)+@(([a-z0-9_]|\-)+\.)+[a-z]{2,4}$")

address_low = address.lower()

if address is None:
    return 'bad'
elif address.find('@') == -1:
    return 'bad'
elif address.find('invalid') != -1 or address.find('nospam') != -1:
    return 'bad'
elif (len(address) < 6) or (len(address) > 255):
    return 'bad'
elif chars.search(address_low) != None or form.match(address_low) == None:
    return 'bad'

return 'ok'

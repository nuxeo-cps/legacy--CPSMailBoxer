# (c) 2003 Nuxeo SARL <http://nuxeo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
# $Id$

from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore import utils
from Products.CMFCore.CMFCorePermissions import AddPortalContent

from AccessControl import allow_module, allow_class

import CPSMailBoxer
import CPSMailBoxerFolder
import NMBMapperTool

contentClasses = (
    CPSMailBoxer.CPSMailBoxer,
    CPSMailBoxerFolder.CPSMailBoxerFolder,
)

contentConstructors = (
    CPSMailBoxer.addCPSMailBoxer,
    CPSMailBoxerFolder.addCPSMailBoxerFolder,
)

fti = (
    CPSMailBoxer.factory_type_information +
    CPSMailBoxerFolder.factory_type_information
)

registerDirectory('skins/cpsmailboxer_default', globals())

tools = (NMBMapperTool.NMBMapperTool,)

def initialize(registrar):
    utils.ContentInit(
        'CPSMailBoxer',
        content_types = contentClasses,
        permission = AddPortalContent,
        extra_constructors = contentConstructors,
        fti = fti,
    ).initialize(registrar)
    utils.ToolInit('MailBoxerMapper Tool',
        tools=tools,
        product_name='CPSMailBoxer',
        icon='tool.gif',
    ).initialize(registrar)

allow_module('email.MIMEText')
allow_module('urllib')

from email.MIMEText import MIMEText
allow_class(MIMEText)

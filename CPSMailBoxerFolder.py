# (C) Copyright 2002 Nuxeo SARL <http://nuxeo.com>
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

import Globals
from random import randrange
from DateTime import DateTime
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from OFS.PropertyManager import PropertyManager

from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore.utils import _getViewFor
from Products.CMFCore.CMFCorePermissions import View, ModifyPortalContent

from Products.CPSCore.CPSBase import CPSBaseFolder

from CPSMailBoxerBoxes import CPSMAILBOXER_BOXES


factory_type_information = (
    {'id': 'CPSMailBoxerFolder',
     'title': 'portal_type_CPSMailBoxer_title',
     'description': 'portal_type_CPSMailBoxer_description',
     'meta_type': 'CPSMailBoxerFolder',
     'icon': 'Folder_icon.gif',
     'product': 'CPSMailBoxer',
     'factory': 'addCPSMailBoxerFolder',
     'immediate_view': 'CPSMailBoxerfolder_view',
     'allow_discussion': 0,
     'filter_content_types': 0,
     'cps_display_as_document_in_listing' : 1,
     'actions': ({'id': 'view',
                  'name': 'action_view',
                  'action': 'string:${object_url}/folder_view',
                  'permissions': (View,)
                 },
                 {'id': 'contents',
                  'name': 'action_folder_contents',
                  'action': 'string:${object_url}/folder_contents',
                  'permissions': (ModifyPortalContent,)
                 },
                ),
     
     },
)

class CPSMailBoxerFolder(CPSBaseFolder):
    """
    Mailing list Folder for CPSMailBoxer
    """
                          
    meta_type = 'CPSMailBoxerFolder'
    portal_type = 'CPSMailBoxerFolder'
    
    security = ClassSecurityInfo()

    _properties = (
        {'id':'title', 'type':'string', 'mode':'w', 'label':'Title'},
        {'id':'description', 'type':'text', 'mode':'w', 'label':'Description'},
    ) + PortalFolder._properties
    
    title = ''
    description =''
    
        
    def __init__(self, id, title='', description='', **kw):
        self._setId(id)
        self.title = title
        self.description = description

    def manage_addFolder(self, id, title=''):
        """
        add a aquisition children folder
        """
        ob = CPSMailBoxerFolder(id, title)
        self._setObject(id, ob)
        
    def _getmailBody(self, maxchar=45):
        """
        trunc each line to maxchar characters
        """
        body = []
        
        for line in self.mailBody.split('\n'):
            if len(line) > maxchar:
                body.append(line[:maxchar])
                body.append(line[maxchar:])
            else:
                body.append(line)
                
        return '\n'.join(body)


    security.declareProtected(View, 'view')
    def view(self):
        """
        Returns the default view

        (should be default view associated with action View: CPSMailBoxerfolder_view)
        """
        view = _getViewFor(self)
        
        return view()

    def __call__(self):
        """
        Returns the default view
        """
        return self.view()
            
InitializeClass(CPSMailBoxerFolder)

def addCPSMailBoxerFolder(dispatcher, id, title='', description='', boxes=None):
    """
    Add a CPSMailBoxerFolder
    """
    ob = CPSMailBoxerFolder(id, title=title, description=description)
    container = dispatcher.Destination()
    container._setObject(id, ob)
    nmbfolder = container._getOb(id)

    #Add box container
    nmbfolder.manage_addProduct['CPSDefault'].addBoxContainer(quiet=1)
    idbc = container.portal_boxes.getBoxContainerId(nmbfolder)
    box_container = getattr(nmbfolder,idbc)
    existing_boxes = box_container.objectIds()
    portal_types = container.portal_types
    
    #create boxes in box container if box is in boxes pass by factory
    if boxes is not None:
        for box, props in [ (box, props) for (box, props) in \
                            CPSMAILBOXER_BOXES.items() \
                            if boxes and box in boxes]:
            if box in existing_boxes:
                box_container._delObject(box)
            portal_types.constructContent(props['type'], box_container, box)
            ob = box_container[box]
            ob.manage_changeProperties(**props)

            

# $Id$
# TODO:
# - don't depend on getDocumentSchemas / getDocumentTypes but is there
#   an API for that ?

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from pprint import pprint
import unittest
from DateTime import DateTime
from Testing import ZopeTestCase
import CPSMailBoxerTestCase
import cgi, smtplib, rfc822, multifile, mimetools, mimify

from CPSMailBoxerTestCase import CPSMailBoxerTestCase as CPSMailBoxerTestCase
from Products.CPSSchemas.Widget import widgetname

class DummyResponse:
    def __init__(self):
        self.headers = {}
        self.data = ''

    def setHeader(self, key, value):
        self.headers[key] = value

    def write(self, data):
        self.data += data

    def redirect(self, url):
        self.redirect_url = url


def randomText(max_len=10):
    import random
    return ''.join(
        [chr(random.randint(32, 128)) for i in range(0, max_len)])


def myGetViewFor(obj, view='view'):
    ti = obj.getTypeInfo()
    actions = ti.listActions()
    for action in actions:
        if action.getId() == view:
            return getattr(obj, action.action.text)
    raise "Unverified assumption"


class TestDocuments(CPSMailBoxerTestCase):
    def afterSetUp(self):
        self.CPSMailBoxerTypeName = 'CPSMailBoxer'
        self.login('root')
        self.ws = self.portal.workspaces

    def beforeTearDown(self):
        self.logout()

    def testCreateDocumentInWorkspacesRoot(self):
        """
        Test the Creation of a CPSMailBoxer instence in root of workspaces
        """
        doc_type = self.CPSMailBoxerTypeName
        doc_id = doc_type.lower()
        self.ws.invokeFactory(doc_type, doc_id)
        proxy = getattr(self.ws, doc_id)
        doc = proxy.getContent()
        
        self._testEditDocument(doc)
        self._testMailArchive(doc)

    def _testEditDocument(self, doc):
        """
        Test the parameters modification of the CPSMailBoxer
        """
        props = {
            'title' : 'The title',
            'description' : 'The description',
            'mailto' : "The list's E-Mail address",
            'moderator' : ['plop@test.nuxeo.com',],
            'moderated' : 1,
            'archived' : 'with attachments',
            'mtahosts' : ['localhost',],
            }
        doc.edit(**props)

        for prop in props.keys():
            value = getattr(doc, prop)
            self.assertEquals(str(value), str(props[prop]))
        
    def _testMailArchive(self, doc):
        """
        Test the mail archive mecanism and the created archive document
        """

        props = {
            'context' : doc,
            'ffrom' : None,
            'fto': None,
            'subject' : 'NewsLetter',
            'texte' : 'The Body',
            }
        doc.sendtoList(**props)
        self.assert_('archive' in doc.objectIds())
        
        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDocuments))
    return suite

from Testing import ZopeTestCase
from Products.CPSDefault.tests import CPSTestCase

ZopeTestCase.installProduct('ZCatalog')
ZopeTestCase.installProduct('MailBoxer')
ZopeTestCase.installProduct('SuezCPS')
ZopeTestCase.installProduct('CPSDocument')
ZopeTestCase.installProduct('CPSSchemas')
ZopeTestCase.installProduct('CPSMailBoxer')


CPSTestCase.setupPortal()

CPSMailBoxerTestCase = CPSTestCase.CPSTestCase

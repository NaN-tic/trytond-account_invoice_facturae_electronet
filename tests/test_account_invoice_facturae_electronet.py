# This file is part account_invoice_facturae_electronet module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import unittest
import doctest
from trytond.tests.test_tryton import ModuleTestCase
from trytond.tests.test_tryton import suite as test_suite
from trytond.tests.test_tryton import doctest_teardown
from trytond.tests.test_tryton import doctest_checker


class AccountInvoiceFacturaeElectronetTestCase(ModuleTestCase):
    'Test Account Invoice Facturae Electronet module'
    module = 'account_invoice_facturae_electronet'


def suite():
    suite = test_suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
            AccountInvoiceFacturaeElectronetTestCase))
    return suite

# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from trytond.pool import PoolMeta
from trytond.config import config

__all__ = ['Invoice', 'GenerateFacturaeStart']

ELECTRONET = config.get('electronet', 'facturae_path', default='/tmp')


class Invoice:
    __metaclass__ = PoolMeta
    __name__ = 'account.invoice'

    @classmethod
    def generate_facturae_electronet(cls, invoices, certificate_password=None):
        to_save = []
        for invoice in invoices:
            if invoice.invoice_facturae:
                continue
            facturae_content = invoice.get_facturae()
            invoice._validate_facturae(facturae_content)
            invoice.invoice_facturae = facturae_content
            to_save.append(invoice)
        if to_save:
            cls.save(to_save)
        # TODO
        # Two phase commit
        for inv in to_save:
            fname = '%s/%s' % (ELECTRONET,
                inv.invoice_facturae_filename.replace('.xsig', '.xml'))
            with open(fname, 'w') as output_file:
                output_file.write(inv.invoice_facturae)


class GenerateFacturaeStart:
    __metaclass__ = PoolMeta
    __name__ = 'account.invoice.generate_facturae.start'

    @classmethod
    def __setup__(cls):
        super(GenerateFacturaeStart, cls).__setup__()
        cls.service.selection += [('electronet', 'Electronet')]

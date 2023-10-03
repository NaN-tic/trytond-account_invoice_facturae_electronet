# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta


class Party(metaclass=PoolMeta):
    __name__ = 'party.party'
    id_electronet = fields.Char('Id Electronet')
    #TODO: migrate id_electronet from party to address?


class Address(metaclass=PoolMeta):
    __name__ = 'party.address'
    electronet_sale_point = fields.Char('Electronet Sale Point')
    id_electronet = fields.Char('Id Electronet')

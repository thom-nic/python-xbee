"""
digimesh.py

By Matteo Lucchesi, 2011
Inspired by code written by Amit Synderman, Marco Sangalli and Paul Malmsten
matteo@luccalug.it http://matteo.luccalug.it

This module provides an XBee (Digimesh) API library.
"""
import struct
from xbee.base import XBeeBase

class DigiMesh(XBeeBase):
    """
    Provides an implementation of the XBee API for Digimesh modules
    with recent firmware.
    
    Commands may be sent to a device by instansiating this class with
    a serial port object (see PySerial) and then calling the send
    method with the proper information specified by the API. Data may
    be read from a device syncronously by calling wait_read_frame. For
    asynchronous reads, see the definition of XBeeBase.
    """
    # Packets which can be sent to an XBee
    
    # Format: 
    #        {name of command:
    #           [{name:field name, len:field length, default: default value sent}
    #            ...
    #            ]
    #         ...
    #         }
    api_commands = {"at":
                        [{'name':'id',        'len':1,      'default':'\x08'},
                         {'name':'frame_id',  'len':1,      'default':'\x00'},
                         {'name':'command',   'len':2,      'default':None},
                         {'name':'parameter', 'len':None,   'default':None}],
                    "queued_at":
                        [{'name':'id',        'len':1,      'default':'\x09'},
                         {'name':'frame_id',  'len':1,      'default':'\x00'},
                         {'name':'command',   'len':2,      'default':None},
                         {'name':'parameter', 'len':None,   'default':None}],
                    #explicit adrresing command frame - to do!
                    "remote_at":
                        [{'name':'id',              'len':1,        'default':'\x17'},
                         {'name':'frame_id',        'len':1,        'default':'\x00'},
                         {'name':'dest_addr_long',  'len':8,        'default':None},
                         {'name':'reserved',        'len':2,        'default':'\xFF\xFE'},
                         {'name':'options',         'len':1,        'default':'\x02'},
                         {'name':'command',         'len':2,        'default':None},
                         {'name':'parameter',       'len':None,     'default':None}],
                    "tx":
                        [{'name':'id',              'len':1,        'default':'\x10'},
                         {'name':'frame_id',        'len':1,        'default':'\x00'},
                         {'name':'dest_addr',       'len':8,        'default':None},
                         {'name':'reserved',        'len':2,         'default':'\xFF\xFE'},
                         {'name':'broadcast_radius', 'len':1,         'default':'\x00'},
                         {'name':'options',         'len':1,        'default':'\x00'},
                         {'name':'data',            'len':None,     'default':None}],

                    }
    
    # Packets which can be received from an XBee
    
    # Format: 
    #        {id byte received from XBee:
    #           {name: name of response
    #            structure:
    #                [ {'name': name of field, 'len':length of field}
    #                  ...
    #                  ]
    #            parse_as_io_samples:name of field to parse as io
    #           }
    #           ...
    #        }
    #
    api_responses = {"\x90":
                        {'name':'rx_long_addr',
                         'structure':
                            [{'name':'frame_id', 'len':1},
                             {'name':'source_addr', 'len':8},
                             {'name':'reserved', 'len':2},
                             {'name':'options',     'len':1},
                             {'name':'data',     'len':None}]},
                    # "\x91": to do!
                    #    {'name':'explicit_rx_indicator',
                    #     'structure':
                    #        [{'name':'source_addr', 'len':2},
                    #         {'name':'rssi',        'len':1},
                    #         {'name':'options',     'len':1},
                    #         {'name':'rf_data',     'len':None}]},
                     "\x8a":
                        {'name':'status',
                         'structure':
                            [{'name':'status',      'len':1}]},
                     b"\x8b":
                        {'name':'tx_status',
                         'structure':
                            [{'name':'frame_id',        'len':1},
                             {'name':'dest_addr',       'len':2},
                             {'name':'retries',         'len':1},
                             {'name':'deliver_status',  'len':1},
                             {'name':'discover_status', 'len':1}]},
                     "\x88":
                        {'name':'at_response',
                         'structure':
                            [{'name':'frame_id',    'len':1},
                             {'name':'command',     'len':2},
                             {'name':'status',      'len':1},
                             {'name':'parameter',   'len':None}]},
                     "\x95":
                        {'name':'node_id',
                         'structure':
                            [{'name':'frame_id',          'len':1},
                             {'name':'source_addr_long',  'len':8},
                             {'name':'network_addr',      'len':2},
                             {'name':'options',           'len':1},
                             {'name':'source_addr',       'len':2},
                             {'name':'network_addr_long', 'len':8},
                             {'name':'NI',                'len':2},
                             {'name':'parent',            'len':1}]},

                     "\x97":
                        {'name':'remote_at_response',
                         'structure':
                            [{'name':'frame_id',        'len':1},
                             {'name':'source_addr',     'len':8},
                             {'name':'reserved',        'len':2},
                             {'name':'command',         'len':2},
                             {'name':'status',          'len':1},
                             {'name':'parameter',       'len':None}]},

                     "\x8b":
                        {'name':'transmit_status',
                         'structure':
                            [{'name':'frame_id',        'len':1},
                             {'name':'reserved',        'len':2,  'default':'\xFF\xFE'},
                             {'name':'trasmit_retry',     'len':1},
                             {'name':'delivery_status',   'len':1},
                             {'name':'discovery_status',  'len':1}]},
                     }
    
    def __init__(self, *args, **kwargs):
        # Call the super class constructor to save the serial port
        super(DigiMesh, self).__init__(*args, **kwargs)

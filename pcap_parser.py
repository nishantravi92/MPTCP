 #! /usr/bin/env python


import sys

from socket import inet_ntop, ntohs
import os
import time

import redcap
import dpkt

import parsers.cached_lookup

# mod
import socket
import traceback
import ipaddress

PARSER_DIR = 'parsers'

UNICAST_TO_US = 0
SENT_BY_US = 4


class Multiparser(object):

    def __init__(self, output_dir):
        parsers.cached_lookup.load()
        parser_modules = self._get_parser_modules()
        self.parsers = []
        for module in parser_modules:
            try:
                self.parsers.append(module.Parser(output_dir))
            except (AttributeError):
                print module, "not a parser"

    def handle_packet(self, ts, sll_packet):
        SAMSUNG_PREFIX = '\xa0\x0b\xba'
        outgoing_handlers = (parser.outgoing_packet for parser in self.parsers)
        incoming_handlers = (parser.incoming_packet for parser in self.parsers)
        sll_type = sll_packet.type
        if sll_type == SENT_BY_US:
            packet = sll_packet
            handlers = outgoing_handlers
        elif sll_type == UNICAST_TO_US:
            packet = sll_packet
            handlers = incoming_handlers
        """    
        else:
            #ethernet

            try:
                if eth_packet.type != dpkt.ethernet.ETH_TYPE_IP: #get only IP packets
                    print "skipping type "+str(eth_packet._typesw[eth_packet.type])+" packet ts:",ts
                    return
            except:
                print "skipping type "+str(eth_packet.type)+" packet. ts:",ts
                return

            if eth_packet.src.startswith(SAMSUNG_PREFIX):
                packet = eth_packet
                handlers = outgoing_handlers
            elif eth_packet.dst.startswith(SAMSUNG_PREFIX):
                packet = eth_packet
                handlers = incoming_handlers
            else:
                print 'bad packet (probably ARP). Inspect ts:', ts   
        """             
        try:
            packet.ip
        except:
            #print 'no IP'
            return
        for handler in handlers:
            handler(ts, packet)
            
    def done(self, ts):
        parsers.cached_lookup.save()
        for parser in self.parsers:
            return parser.done(ts)

    def _get_parser_modules(self):
        all_files = os.listdir(PARSER_DIR)
        module_names = (f[:-3] for f in all_files if f[-3:] == '.py' and f[0] != '_' and not f.startswith('cache'))
        return [__import__('.'.join((PARSER_DIR, module_name))).__dict__[module_name] for module_name in module_names]


def parse(experiment_timestamp, dirpath):
    app = experiment_timestamp.split("_")[0]
    output_dir = os.path.join(dirpath, app, "numericals", experiment_timestamp)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    multiparser = Multiparser(output_dir)
    start_ts = False
    pcap_filename = os.path.join('raw', experiment_timestamp + '.pcap')
    total_no_of_packets = 0
    total_no_of_packets_parsed = 0

    pc = pcap.pcap(pcap_filename)
    #pc.setfilter('src host 52.91.67.28 or dst host 52.91.67.28 or src host 45.55.190.215 or src host 45.55.190.215')
    for ts_absolute, frame in pc:
        total_no_of_packets += 1
        if not start_ts:
            start_ts = ts_absolute
        ts = ts_absolute - start_ts # ts relative to start

        sll_packet = dpkt.sll.SLL(frame)
        #eth_packet = dpkt.ethernet.Ethernet(frame)

        ip = sll_packet.data
        src = 0
        dst = 0
        if sll_packet.ethtype == dpkt.ethernet.ETH_TYPE_IP:
            src = inet_ntop(socket.AF_INET, ip.src)
            dst = inet_ntop(socket.AF_INET, ip.dst)
        elif sll_packet.ethtype == dpkt.ethernet.ETH_TYPE_IP6:
            src = inet_ntop(socket.AF_INET6, ip.src)
            dst = inet_ntop(socket.AF_INET6, ip.dst)
        
        # parse only proxy packets
        if src == "45.55.190.215" or dst == "45.55.190.215" or src =="52.91.67.28" or dst == "52.91.67.28":
            #print i 
            total_no_of_packets_parsed += 1
            multiparser.handle_packet(ts, sll_packet)
    
    print "\n"
    print "Number of packets ",total_no_of_packets  
    print "Number of packets parsed ",total_no_of_packets_parsed  
    print "\n"
    
    return multiparser.done(ts)
    

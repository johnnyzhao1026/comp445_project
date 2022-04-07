import logging
import math 
import time
import socket
import sys
import threading
from packet import *
from config import *
from SlidingWindow import *
    

class UdpUnit(object):
    '''
    The class is to implement UDP functions to mimic TCP reliable connection.
    '''
    def __init__(self):
        # set UDP socket
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.router_addr = None
        self.pkt_builder = None
    
    def get_packet(self, timeout):
        '''
        The method is to get packet from socket.
        :param: timeout
        :return: packet
        '''
        # set TimeOut
        # self.conn.settimeout(timeout)
        try:
            data, addr = self.conn.recvfrom(PACKET_SIZE)
            pkt = Packet.from_bytes(data)
            logging.debug("Received Packet is : {}:{}".format(pkt,pkt.payload))
            self.router_addr = addr
            
            # create pkt_builder
            if self.pkt_builder is None:
                self.pkt_builder = PacketBuilder(pkt.peer_ip_addr, pkt.peer_port)
            
            return pkt
                
        except socket.timeout:
            logging.debug('Time out for recvfrom packet !!!')
            return None
        
        # finally:
        #     return pkt
        
    def run_server(self):
        '''
        The method is to run server to listen port
        '''
        self.conn.bind(('',SERVER_PORT))
        logging.info("Server is listening at {}:{}".format(SERVER_IP,SERVER_PORT))
            
    
    def connect_client(self):
        '''
        The method is to mimic TCP 3-way handshaking for server to connect client.
        :return: boolean
        '''
        # self.conn.bind(('',SERVER_PORT))
        # logging.info("Server is listening at {}:{}".format(SERVER_IP,SERVER_PORT))
        
        # receive packet from router
        # pkt = self.get_packet(TIME_ALIVE)
        pkt = self.get_packet(TIME_ALIVE)
        if pkt is None:
            logging.debug('Connecting is timeout!')
            return False
        else:
            # check mimic 3-way handshaking (SYN => SYN-ACK => ACK)
            if pkt.packet_type == PACKET_TYPE_SYN:
                pkt = self.pkt_builder.build(PACKET_TYPE_SYN_ACK)
                # send SYN-ACK to client
                self.conn.sendto(pkt.to_bytes(), self.router_addr)
                # wait to receive ACK from client
                pkt = self.get_packet(TIME_ALIVE)
                if pkt.packet_type == PACKET_TYPE_ACK:
                    # 3-way handshaking completed
                    logging.info('Client connecting is established!')
                    return True
                elif pkt.seq_num == 0 and len(pkt.payload) > 0:
                    logging.debug('Have received Client Request ...')
                    return True
                    
                else:
                    logging.debug('Server Not received ACK, Fail to connect client. ')
                    return False
            else:
                logging.debug('Server Not received SYN-ACK, Fail to connect client. ')
                return False
    
    def connect_server(self):
        '''
        The method is to mimic TCP 3-way handshaking for client to connect server.
        :return: boolean
        '''
        logging.info('Connecting to {}:{}'.format(SERVER_IP,SERVER_PORT))
        self.router_addr = (ROUTER_IP,ROUTER_PORT)
        peer_ip = ipaddress.ip_address(socket.gethostbyname(SERVER_IP))
        # initial pkt_builder 
        self.pkt_builder = PacketBuilder(peer_ip, SERVER_PORT)
        
        # mimic TCP 3-way handshaking
        # first, client send SYN to the server
        pkt = self.pkt_builder.build(PACKET_TYPE_SYN)
        self.conn.sendto(pkt.to_bytes(), self.router_addr)
        # waiting SYN-ACK from server
        logging.debug('Client waiting for SYN-ACK from server')
        # receive packet
        pkt = self.get_packet(TIME_ALIVE)
        if pkt is not None and pkt.packet_type == PACKET_TYPE_SYN_ACK:
            # clent send ACK to server
            pkt = self.pkt_builder.build(PACKET_TYPE_ACK)
            self.conn.sendto(pkt.to_bytes(),self.router_addr)
            logging.info('Connection is established!!!')
            return True
        # consider connect long time
        else:
            logging.debug('Fail to connection ! Unexpected packet: {}'.format(pkt))
            # self.conn.close()
            return False
            
    def client_send_request(self, request):
        '''
        The method is to implement client send request to server.
        :param: request
        :return: bool
        '''
        self.conn.settimeout(TIME_ALIVE)
        # send request
        pkt = self.pkt_builder.build(PACKET_TYPE_DATA, 0, request.encode("utf-8"))
        self.conn.sendto(pkt.to_bytes(), self.router_addr) 
        logging.debug('client is sending request to server...')
        # waiting for server send ACK for request
        # pkt = self.get_packet(TIME_OUT_RECV)
        try:
            data, sender = self.conn.recvfrom(PACKET_SIZE)
            if data is not None:
                pkt = Packet.from_bytes(data)
            
                logging.debug('client is waiting ACK-request from server...')
                if pkt is not None and pkt.packet_type == PACKET_TYPE_ACK and pkt.seq_num == 0  and len(pkt.payload) > 0 \
                    or pkt.packet_type == PACKET_TYPE_DATA:
                    logging.debug(f'Get request pkt: #{pkt.seq_num}, type:{pkt.packet_type}')
                    return True
                
        except socket.timeout:
            logging.debug('client recv nothing from server, might be dropped...')
            return False
        
    
    def server_response(self):
        '''
        The method is to implement server response ACK to client request.
        :return: payload (request)
        '''
        try:
            data, sender = self.conn.recvfrom(PACKET_SIZE)
            if data is not None:
                pkt = Packet.from_bytes(data)
                
                if pkt is not None and pkt.packet_type == PACKET_TYPE_DATA and pkt.seq_num == 0:
                    pkt = self.pkt_builder.build(PACKET_TYPE_ACK, 0, pkt.payload)
                    logging.debug('server is sending ACK-request to client...')
                    
                    # send ACK-request
                    self.conn.sendto(pkt.to_bytes(),self.router_addr)
                    
                    return pkt.payload
        except socket.timeout:
            
            logging.debug('recv nothing, client pkt might be dropped...')
            
            return None
    
    def check_server_response(self, pkt):
        '''
        The method is to implement server response ACK to client request.
        :param: pkt
        :return: payload (request)
        '''
            
        if pkt is not None and pkt.packet_type == PACKET_TYPE_DATA and pkt.seq_num == 0:
            pkt = self.pkt_builder.build(PACKET_TYPE_ACK, 0, pkt.payload)
            logging.debug('server is sending ACK-request to client...')
            
            # send ACK-request
            self.conn.sendto(pkt.to_bytes(),self.router_addr)
            
            return pkt.payload
        
        return None        
            
    def close_connect(self):
        '''
        The method is to close the connectiong
        '''
        logging.info('Disconnecting...')
        self.conn.close()
    
    
    def send_msg(self, msg):
        '''
        The method is to send message from sending window.
        :param: msg
        :param: send_window
        '''
        # create a sender window
        send_window = SlidingWindow()
        send_window.create_sender_window(msg)
        
        threading.Thread(target=self.handle_sender, args=(send_window,)).start()
        while not send_window.check_all_pkt_acked():
            # check if it has some packets need to be send in window
            for f in send_window.get_sendable_frames():
                pkt = self.pkt_builder.build(PACKET_TYPE_DATA, f.seq_num, f.payload)
                # send pkt to receiver
                self.conn.sendto(pkt.to_bytes(),self.router_addr)
                logging.debug(f'Re-send pkt is : {pkt.seq_num}, Type : {pkt.packet_type}')
                # set timer
                f.timer = time.time()
                # update send state
                f.send_state = True
                
            send_window.check_sender_finished()
        # then send Fini signal to client
        while True:
            try:
                pkt = self.pkt_builder.build(PACKET_TYPE_NONE, len(send_window.list_sender),)
                self.conn.sendto(pkt.to_bytes(), self.router_addr)
                # get FINI from client
                data, sender = self.conn.recvfrom(PACKET_SIZE)
                pkt = Packet.from_bytes(data)
                if pkt is not None and pkt.packet_type == PACKET_TYPE_NONE:
                    break
            except socket.timeout:
                pkt = self.pkt_builder.build(PACKET_TYPE_NONE, len(send_window.list_sender),)
                self.conn.sendto(pkt.to_bytes(), self.router_addr)
            
    
    def handle_sender(self, send_window):
        '''
        The method is to handle sender that send pkts to receiver.
        :param: send_window
        '''    
        while not send_window.check_all_pkt_acked():
            try:
                self.conn.settimeout(TIME_OUT)
                data, sender = self.conn.recvfrom(PACKET_SIZE)
                pkt = Packet.from_bytes(data)
                logging.debug(f'Received packet is : {pkt.seq_num}, type is : {pkt.packet_type}')
                if pkt.packet_type == PACKET_TYPE_ACK:
                    # update send window
                    send_window.update_sender_window(pkt.seq_num)
            
            except socket.timeout:
                logging.debug('TimeOut when waiting ACK')
                # reset send state, then the pkt will be re-sent
                for i in range(send_window.ptr, send_window.ptr + WINDOW_SIZE):
                    if i >= len(send_window.list_sender):
                        break
                    f = send_window.list_sender[i]
                    if f.send_state and not f.has_acked:
                        # reset send state
                        f.send_state = False
            
            send_window.check_sender_finished()
            
        logging.debug('handle_sender has checked the send window')
        
        
    def recv_msg(self):
        '''
        The method is to receive message for recv window.
        :return: data (bytes)
        '''
        recv_window = SlidingWindow()
        while True:
            # receive pkt
            pkt = self.get_packet(TIME_OUT_RECV)
            # case: no msg
            if pkt is None:
                logging.debug('No pkt received in timeout time')
                break
            # case: discard possible pkt from handshaking
            elif pkt.seq_num == 0 or pkt.packet_type == PACKET_TYPE_ACK:
                pass
            
            # case: finish signal
            elif pkt.packet_type == PACKET_TYPE_NONE:
                # send FIN to server
                self.conn.sendto(pkt.to_bytes(),self.router_addr)
                # get total frame nums
                total_num = pkt.seq_num
                # check whether recv window is full
                if len(recv_window.list_recv) == total_num:
                    # ascending re-order frames of the recv window to solve out-order issue
                    recv_window.list_recv.sort()
                    
                    # assemble payloads
                    total_payloads = b''
                    for i in range(total_num):
                        total_payloads += recv_window.list_recv[i].payload
                    
                    return total_payloads    
            else:
                # consider repeat pkt
                if not Frame(pkt.seq_num, pkt.payload) in recv_window.list_recv:
                    # add this frame in recv_window
                    recv_window.list_recv.append(Frame(pkt.seq_num, pkt.payload,))
                    # send ack
                    pkt = self.pkt_builder.build(PACKET_TYPE_ACK,pkt.seq_num,pkt.payload)
                    self.conn.sendto(pkt.to_bytes(),self.router_addr)
                else:
                    # already received pkt
                    # send ACK to update send window (solve fini signal bug)
                    pkt = self.pkt_builder.build(PACKET_TYPE_ACK, pkt.seq_num, pkt.payload)
                    self.conn.sendto(pkt.to_bytes(), self.router_addr)
            
                        
            
            
                
                    
            
        
        
         
            
            
        
        
        
        
        
        
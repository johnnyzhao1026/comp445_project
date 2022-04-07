import logging
import math
from packet import *
from config import *


class Frame(object):
    '''
    The class is to create a Frame.
    '''
    def __init__(self, seq_num, payload=None, is_last=False):
        # set attributes
        self.seq_num = seq_num
        self.payload = payload
        self.is_last = is_last
        self.send_state = False
        self.has_acked = False
        self.timer = 0
        
    def __lt__(self, other):
        '''
        Overrider the less than method
        '''
        return self.seq_num < other.seq_num
    
    def __eq__(self, other):
        
        return self.seq_num == other.seq_num and self.payload == other.payload
        
        

class SlidingWindow:
    '''
    The class is to mimic TCP sliding window.
    '''      
    def __init__(self):
        # pointer to window
        self.ptr = 0
        self.list_sender = []
        self.list_recv = []
        self.num_frames = 0
        self.fini = False
    
    def create_sender_window(self, msg):
        '''
        The method is to create sender window.
        :param: msg
        '''
        # num of packets
        self.num_frames = math.ceil(len(msg)/PAYLOAD_SIZE)
        logging.debug(f'num of frames is : {self.num_frames}')
        
        # initial all frames in sender window
        for i in range(self.num_frames):
            if i == self.num_frames - 1:
                # last frame, set is_last=True
                self.list_sender.append(Frame(i+1, msg[i*PAYLOAD_SIZE:], True))
            else:
                self.list_sender.append(Frame(i+1, msg[i*PAYLOAD_SIZE : (i+1)*PAYLOAD_SIZE], False))
            
    def get_sendable_frames(self):
        '''
        The method is to return a list of all sendable frames in window.
        :return: list_sendable_frames
        '''
        list_sendable_frames = []
        # check if the frame is sendable or not
        for i in range(self.ptr, self.ptr + WINDOW_SIZE):
            if i >= len(self.list_sender):
                break
            f = self.list_sender[i]
            # if send state is False, then add this frame in the list
            if f.send_state == False:
                list_sendable_frames.append(f)
        
        return list_sendable_frames
    
    def update_sender_window(self, seq_num):
        '''
        The method is to update sender window, when received an ACK.
        If possible, slide window
        :param: seq_num
        '''
        # update Ack state
        self.list_sender[seq_num - 1].has_acked = True
        offset = 0
        for i in range(self.ptr, self.ptr + WINDOW_SIZE):
            if i >= len(self.list_sender):
                break
            if self.list_sender[i].has_acked:
                offset += 1
            else:
                # if this frame has not received ACK, then break to make sure the ptr points to this frame.
                break
        # update the ptr of send window
        self.ptr += offset
        
    def check_all_pkt_acked(self):
        '''
        The method is to check if all pkt has acked in sender window.
        :return: bool
        '''
        for i in range(self.num_frames):
            if not self.list_sender[i].has_acked:
                return False
        return True
    
    def check_sender_finished(self):
        '''
        The method is to check if the sender window has sent the last frame.
        :return: fini (bool)
        '''
        if self.list_sender:
            # check last frame
            f = self.list_sender[-1]
            if f.is_last and self.ptr == len(self.list_sender):
                # update fini state
                self.fini = True
        
  
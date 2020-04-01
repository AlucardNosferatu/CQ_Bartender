# -*- coding:utf-8 -*-

import cqplus
import threading
import pickle
import os
import time

class MainHandler(cqplus.CQPlusHandler):
    
    def scan_files(self,directory,prefix=None,postfix=None):
        files_list=[]
        for root, sub_dirs, files in os.walk(directory):
            for special_file in files:
                if postfix:
                    if special_file.endswith(postfix):
                        files_list.append(os.path.join(root,special_file))
                elif prefix:
                    if special_file.startswith(prefix):
                        files_list.append(os.path.join(root,special_file))
                else:
                    files_list.append(os.path.join(root,special_file))
        return files_list

    def safely_remove(self,Msg):
        try:
            os.remove(Msg)
        except WindowsError:
            time.sleep(0.5)
            self.safely_remove(Msg)

    def handle_event(self, event, params):
        valid = False
        ticks = str(round(time.time()))
        path = os.getcwd()
        if event == 'on_timer':
            self.sender()
        elif event == 'on_group_msg':
            name = path + "\\MsgBuffer\\"
            msg_obj = []
            if("[CQ:at,qq=2874404757]" in params['msg']):
                name += "A"
                msg_obj = [params['from_qq'],params['msg']]
                valid = True
            else:
                msg_list = params['msg'].split('\r\n')
                if msg_list[0] == '%自定配方':
                    name += "B"
                    msg_obj = [msg_list,params['from_group']]
                    valid = True
                elif msg_list[0] == '%在册配方':
                    name += "C"
                    msg_obj = [msg_list,params['from_group']]
                    valid = True
                elif msg_list[0] == '%全部定制':
                    name += "D"
                    msg_obj = [params['from_group']]
                    valid = True
                elif msg_list[0] == '%点单记录':
                    name += "E"
                    msg_obj = [params['from_qq'],params['from_group']]
                    valid = True
                elif msg_list[0] == "%口味记录":
                    name += "F"
                    msg_obj = [params['from_qq'],params['from_group']]
                    valid = True
                elif msg_list[0] == "%清空记录":
                    name += "G"
                    msg_obj = [params['from_qq'],params['from_group']]
                    valid = True
                elif msg_list[0] == "%命题调制":
                    name += "H"
                    msg_obj = [msg_list,params['from_group']]
                    valid = True
                elif msg_list[0] == "%删除配方":
                    name += "I"
                    msg_obj = [msg_list,params['from_group'],params['from_qq']]
                    valid = True
                elif msg_list[0] == "%心动推荐":
                    name += "J"
                    msg_obj = [msg_list,params['from_group']]
                    valid = True
            if(valid):
                f = open(name+ticks+".pkl",'wb') 
                pickle.dump(msg_obj,f)
                f.close()
            
    def sender(self):
        path = os.getcwd()+"\\MsgWriter"
        MsgList = self.scan_files(path,postfix='.pkl')
        for i in range(0,len(MsgList)):
            f = open(MsgList[i],'rb')
            MsgContent = self.safely_load(f)
            f.close()
            self.safely_remove(MsgList[i])
            self.api.send_group_msg(MsgContent[0],MsgContent[1])

    def safely_load(self,f):
        try:
            MsgContent = pickle.load(f)
        except EOFError:
            time.sleep(0.5)
            MsgContent = self.safely_load(f)
        return MsgContent

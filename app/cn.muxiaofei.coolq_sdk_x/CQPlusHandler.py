# -*- coding:utf-8 -*-

import cqplus
import os
import pickle
import pandas as pd
from sklearn.linear_model import LinearRegression
from snownlp import SnowNLP

class MainHandler(cqplus.CQPlusHandler):
    default_menu=[
            "A Fedora",
            "Bad Touch",
            "Beer",
            "Bleeding Jane",
            "Bloom Light",
            "Blue Fairy",
            "Brandtini",
            "Cobalt Velvet",
            "Crevice Spike",
            "Fluffy Dream",
            "Fringe Weaver",
            "Frothy Water",
            "Grizzly Temple",
            "Gut Punch",
            "Mars Blast",
            "Mercury Blast",
            "Moon Blast",
            "Mulan Tea",
            "Piano Man",
            "Piano Woman",
            "Pile Driver",
            "Rum",
            "Sparkle Star",
            "Sugar Rush",
            "Sunshine Cloud",
            "Suplex",
            "Zen Star"
            ]

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

    def handle_event(self, event, params):
        path = os.getcwd()
        if event=='on_group_msg':
            if("[CQ:at,qq=2874404757]" in params['msg']):
                self.auto_recorder(params['from_qq'],params['msg'])
            else:
                msg_list = params['msg'].split('\r\n')
                if msg_list[0] == '%自定配方':
                    cont_dict = self.dict_wrapper(msg_list)
                    self.dict_parser(cont_dict,params['from_group'])
                elif msg_list[0] == '%在册配方':
                    if(len(msg_list)==2):
                        self.reg_output(msg_list[1],params['from_group'])
                    elif(len(msg_list)==1):
                        self.api.send_group_msg(params['from_group'],"点单指令缺少饮料名称，请客官检查指令，多谢！")
                    elif(len(msg_list)>2):
                        self.api.send_group_msg(params['from_group'],"点单指令过长（超出2行），请客官检查指令，多谢！")
                    else:
                        self.api.send_group_msg(params['from_group'],"未知错误，请客官检查指令是否与模板格式一致，多谢！")
                elif msg_list[0] == '%全部定制':
                    path += '\\users_menu'
                    drink_list = self.scan_files(path,postfix='.pkl')
                    drink_list = [item.replace(path+"\\","").replace(".pkl","") for item in drink_list]
                    self.api.send_group_msg(params['from_group'],'\r\n'.join(drink_list))
                elif msg_list[0] == '%点单记录':
                    path += '\\users_log'
                    if(os.path.exists(path+'\\' + str(params['from_qq']) + '.log')):
                        result = self.get_log(path,params['from_qq'])
                        res_list = []
                        for key in result:
                            res_list.append(key+"："+str(result[key]))
                        text_res = '\r\n'.join(res_list)
                        self.api.send_group_msg(params['from_group'],
                                                "账号："+str(params['from_qq'])+"\r\n"+
                                                text_res)
                    else:
                        self.api.send_group_msg(params['from_group'],"目前还没有您的点单记录，要点些什么吗？")
                elif msg_list[0] == "%口味记录":
                    path += '\\users_log'
                    if(os.path.exists(path+'\\' + str(params['from_qq']) + '.log')):
                        result = self.get_log(path,params['from_qq'])
                        flavor_count = self.flavor_counter(result)
                        list_res = []
                        for key in flavor_count:
                            list_res.append(key+"："+str(flavor_count[key]))
                        text_res = "\r\n".join(list_res)
                        self.api.send_group_msg(params['from_group'],
                                                "账号："+str(params['from_qq'])+"\r\n"+
                                                text_res)
                    else:
                        self.api.send_group_msg(params['from_group'],"目前还没有您的点单记录，要点些什么吗？")
                elif msg_list[0] == "%清空记录":
                    self.purge_record(params['from_qq'],params['from_group'])
                elif msg_list[0] == "%命题调制":
                    self.logging.debug(msg_list[1])
                    self.mix_by_name(msg_list[1],params['from_group'])
                elif msg_list[0] == "%删除配方":
                    result = self.api.get_group_member_info(group_id=params['from_group'],user_id=params['from_qq'],no_cache=True)
                    if(result['role']>=2):
                        if(len(msg_list)!=2):
                            self.api.send_group_msg(params['from_group'],"格式有误，请检查，谢谢~")
                        else:
                            self.delete_recipe(msg_list[1],params['from_group'])
                    else:
                        self.api.send_group_msg(params['from_group'],"客人请不要往后厨跑哦~")
                elif msg_list[0] == "%心动推荐":
                    
                    if(len(msg_list)!=2):
                        self.api.send_group_msg(params['from_group'],"不好意思，我没听清~")
                    else:
                        s = SnowNLP(msg_list[1])
                        emo = s.sentiments
                        self.api.send_group_msg(params['from_group'],
                                                "情绪分数："+
                                                str(emo)
                                                )
                        flavor = ""
                        if(emo>0.75):
                            flavor = "苦"
                        elif(emo >0.5):
                            flavor = "酸"
                        elif(emo >0.25):
                            flavor = "辣"
                        else:
                            flavor = "甜"
                        self.api.send_group_msg(params['from_group'],
                                                "给客官推荐"+
                                                flavor+
                                                "味的饮料，@酒保并输入 %"+
                                                flavor+
                                                " 即可查看所有该类饮料~"
                                                )
                
    def delete_recipe(self,name,from_group):
        path = os.getcwd()
        if(os.path.exists(path+'\\users_menu\\' + name + '.pkl')):
            os.remove(path+'\\users_menu\\' + name + '.pkl')
            self.api.send_group_msg(from_group,"删除成功~")
        else:
            self.api.send_group_msg(from_group,"有问题的配方不知道给谁事先扔了\r\n看来英雄所见略同嘛~")
        
    def auto_recorder(self,qq_id,msg):
        path = os.getcwd()
        path += '\\users_log'
        self.logging.debug(str(qq_id))
        choosen = ""
        for item in self.default_menu:
            if item in msg:
                choosen = item
                break
        if choosen in self.default_menu:
            if(os.path.exists(path+'\\' + str(qq_id) + '.log')):
                f = open(path+'\\' + str(qq_id) + '.log','a')
                f.write(choosen+"\n")
                f.flush()
                f.close()
            else:
                f = open(path+'\\' + str(qq_id) + '.log','w')
                f.write(choosen+"\n")
                f.flush()
                f.close()
    
    def purge_record(self,qq_id,group_id):
        path = os.getcwd()
        path += '\\users_log'
        if(os.path.exists(path+'\\' + str(qq_id) + '.log')):
            os.remove(path+'\\' + str(qq_id) + '.log')
            self.api.send_group_msg(group_id,"记录已清空！")
        else:
            self.api.send_group_msg(group_id,"记录不存在，无需清空")
            
    def flavor_counter(self,result):
        flavor_count = {'酸':0,'甜':0,'苦':0,'辣':0,'多泡':0,'瓶装饮料':0}
        for key in result:
            if key in ["Grizzly Temple","Gut Punch","Pile Driver","Sunshine Cloud","Suplex"]:
                flavor_count['苦']+=result[key]
            elif key in ["Frothy Water","Fringe Weaver","Cobalt Velvet","Beer"]:
                flavor_count['多泡']+=result[key]
            elif key in ["A Fedora","Mulan Tea","Rum"]:
                flavor_count['瓶装饮料']+=result[key]
            elif key in ["Crevice Spike","Bad Touch","Piano Man","Mercury Blast","Zen Star"]:
                flavor_count['酸']+=result[key]
            elif key in ["Bleeding Jane","Bloom Light","Mars Blast"]:
                flavor_count['辣']+=result[key]
            elif key in ["Fluffy Dream","Brandtini","Blue Fairy","Moon Blast","Sparkle Star","Piano Woman","Sugar Rush"]:
                flavor_count['甜']+=result[key]
        return flavor_count
    
    def get_log(self,path,qq_id):
        f = open(path+'\\' + str(qq_id) + '.log','r')
        lines = f.readlines()
        f.close()
        lines = [item.replace('\n','') for item in lines]
        result = {}
        for item in self.default_menu:
            result[item]=lines.count(item)
        return result

    def word2vec(self,word):
        word = word.lower()
        word = word.zfill(20)
        ascii_list = []
        for alphabet in word:
            temp = ord(alphabet)
            if(temp > 122):
                temp -= 65
                temp %=(122-65)
                temp += 65
                self.logging.debug(str(temp))
            ascii_list.append(temp)
        return ascii_list

    def mix_by_name(self,name,from_group):
        temp_keys=['adelhyde','bronson extract','powdered delta','flanergide','karmotrine']
        ascii_list = self.word2vec(name)
        ascii_list = pd.DataFrame(ascii_list)
        mixer = []
        for i in range(0,5):
            f=open('mbn_'+str(i)+'.txt','rb')
            s=f.read()
            lr=pickle.loads(s)
            mixer.append(lr.predict(ascii_list.T)[0,0])
        mixer = [round(item) for item in mixer]
        mixer = self.value_correction(mixer)
        content_dict = {}
        for i in range(0,5):
            content_dict[temp_keys[i]]=int(mixer[i])
        self.default_mixer(content_dict,from_group,name)
        
    def value_correction(self,mixer):
        volume = 0
        for i in range(0,len(mixer)):
            if(mixer[i]<0):
                if(abs(mixer[i])>1):
                    mixer[i] = -mixer[i]
                    
            if(mixer[i] == -0):
                mixer[i] = 0
                
            temp = mixer[i]
            if temp != -1:
                volume+=mixer[i]
            else:
                volume+=6
        if(volume>20):
            ratio = volume/20
            for i in range(0,len(mixer)):
                if mixer[i] != -1:
                    mixer[i]/=ratio
                    mixer[i]=round(mixer[i])
        self.logging.debug(str(mixer))
        return mixer

    def dict_wrapper(self,msg_list):
        content_dict={}
        for i in range(1,len(msg_list)):
            content=msg_list[i].split(":")
            if(len(content)==1):
                content=content[0].split("：")
            if(len(content)==1):
                content.append("0")
            if content[0].replace(' ','').isalpha():
                content[0]=content[0].lower()
                #如果键名称是字母组成的（包含空格）则全部变为小写
            if content[1].replace(' ','').isdigit():
                content_dict[content[0].strip()]=int(content[1].replace(' ',''))
                #如果值内容是数字则以整形记录
            else:
                content_dict[content[0].strip()]=content[1]
        return content_dict

    def dict_parser(self,content_dict,from_group):
        temp_keys=['adelhyde','bronson extract','powdered delta','flanergide','karmotrine']
        default_content = True
        volume = 0
        for key in content_dict:
            if type(content_dict[key]) is int:
                volume+=int(content_dict[key])
            default_content = default_content and key.replace(' ','').isalpha()
            #看看是不是所有key都是英文
            
        if volume > 20:
            self.api.send_group_msg(from_group,'摇杯放不下这么多。。。（总量不超过20）')
        else:
            keys = content_dict.keys()
            matched = True
            for key in keys:
                #取出输入配方材料表
                for temp in temp_keys:
                    #查看酒吧已有材料表
                    if temp == key:
                        if type(content_dict[key]) is int:
                        #如果酒吧里有就ok，接着看下一样材料
                            matched = True
                            break
                    else:
                        #酒店库存的这样不是需要的，没看完库存则继续，看完则matched会保持False到外循环
                        matched = False
                if not matched:
                    #只要有一样材料酒吧没有都不行
                    break
            if  matched and default_content:
                self.default_mixer(content_dict,from_group)
            else:
                self.custom_mixer(content_dict,from_group)

    def default_mixer(self,conDict,from_group,name=None):
        temp_keys=['adelhyde','bronson extract','powdered delta','flanergide','karmotrine']
        self.api.send_group_msg(from_group,'全部为默认材料，将按照配方预测饮品口味')
        result = []
        for key in temp_keys:
            if conDict.__contains__(key):
                if(conDict[key]!=0):
                    if(conDict[key]==-1):
                        temp = "任意"
                        conDict[key]=0
                    else:
                        temp = str(conDict[key])
                    result.append(temp+"份"+key.title())
            else:
                conDict[key]=0
        profile = {}
        volume = 0
        for key in conDict:
            volume += conDict[key]
        if volume == 0:
            self.api.send_group_msg(from_group,"嗯？啥也不放？这就是所谓喝西北风吗。。。")
        else:
            sour = round(conDict['powdered delta']/volume,2)
            profile['A酸']=sour
            sweet = round(conDict['adelhyde']/volume,2)
            profile['B甜']=sweet
            bitter = round(conDict['bronson extract']/volume,2)
            profile['C苦']=bitter
            alcohol = round(conDict['karmotrine']/volume,2)
            spicy = round(conDict['flanergide']/volume,2)
            profile['D辣']=spicy

            prefix = ''
            if sweet==bitter and bitter==spicy and spicy==sour:
                flavor='清淡'
                degree=sweet
            else:
                flavor = max(profile, key=profile.get)
                degree = profile[flavor]    
                if(degree>=0.5):
                    prefix = '很'
                elif(degree>=0.25):
                    prefix = '偏'
                else:
                    prefix = '略'

            self.logging.debug(
                '总量：'+str(volume)+'\r\n'+
                '甜度：'+str(sweet)+'\r\n'+
                '苦涩度：'+str(bitter)+'\r\n'+
                '酒精度：'+str(alcohol)+'\r\n'+
                '酸度：'+str(sour)+'\r\n'+
                '辣度：'+str(spicy)+'\r\n'+
                '口味：'+prefix+str(flavor)+'\r\n'+
                '程度：'+str(degree)
                )
            drink_name = "这份特调饮料"
            if(name is not None):
                drink_name = name
            self.api.send_group_msg(from_group,
                                    drink_name+"由"+'、'.join(result)+"调制而成。"+'\r\n'+
                                    "口味特点："+prefix+str(flavor[1])+'\r\n'+
                                    "[CQ:image,file="+prefix+str(flavor[1])+".png]"+'\r\n'+
                                    "请慢用！"
                                    )

    def save_obj(self,obj,name):
        path = os.getcwd()
        with open(path+'\\users_menu\\' + name + '.pkl', 'wb') as f:
            pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

    def load_obj(self,name):
        path = os.getcwd()
        with open(path+'\\users_menu\\' + name + '.pkl', 'rb') as f:
            return pickle.load(f)
        
    def reg_output(self,drink_name,from_group):
        path = os.getcwd()
        if(os.path.exists(path+'\\users_menu\\' + drink_name + '.pkl')):
            conDict = self.load_obj(drink_name)
            str_list = []
            for key in conDict:
                if(key!='名称'):
                    str_list.append(str(conDict[key])+"份"+key)
            result = "这份自助饮料由"+"、".join(str_list)+"调制而成"
            self.api.send_group_msg(from_group,
                                    result+"\r\n"+
                                    "[CQ:image,file=AbsintheSprite.png]"+'\r\n'+
                                    "请慢用！"
                                    )
        else:
            self.api.send_group_msg(from_group,"这个饮料好像还没登记呢，请找跑堂的（[CQ:at,qq=1641367382]）确认，谢谢！")
    
    def custom_mixer(self,conDict,from_group):
        if conDict.__contains__('名称'):
            self.api.send_group_msg(from_group,'存在自定义材料，将以“名称”后所写内容作为酒名记录'+'\r\n'+
                                    '名称：'+conDict['名称']+'\r\n'+
                                    "如需锁定配方，请找跑堂的（[CQ:at,qq=1641367382]），谢谢！"
                                    )
            self.save_obj(conDict,conDict['名称'])     
        else:
            self.api.send_group_msg(from_group,'存在自定义材料或非数量参数，未检测到“名称”项，请补充以完成配方登记或检查参数数据类型，谢谢！')

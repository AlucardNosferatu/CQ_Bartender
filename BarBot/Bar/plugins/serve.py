from nonebot import on_command, CommandSession
import pickle
import os


@on_command('customize',aliases=('自定配方'))
async def customize(session: CommandSession):
    drink = session.get('drink',prompt = "喝。。。西北风？你是小怖？")
    detail = await get_drink_detail(drink)
    await session.send(detail)

@customize.args_parser
async def _(session: CommandSession):
    drink_name = ""
    format_correct = True
    stripped_arg = session.current_arg_text.strip()
    content_list = stripped_arg.split("\r\n")
    if(len(content_list)<2):
        format_correct = False
    else:
        format_correct = False
        for i in range(0,len(content_list)):
            content_list[i]=content_list[i].replace(":","：").split("：")
            content_list[i]=[item.strip() for item in content_list[i]]
            if("名称" in content_list[i][0]):
                format_correct = True
                drink_name = content_list[i][1]
                
    if session.is_first_run:
        pass
    if format_correct:
        path = os.getcwd()
        path = path.replace(path.split("\\")[-1],"")+"users_menu"
        f = open(path+"\\"+drink_name+".pkl",'wb')
        pickle.dump(content_list,f)
        session.state['drink'] = drink_name
        return
    if not format_correct:
        session.pause("格式有误，我不太明白呀~")
##    session.state[session.current_key] = stripped_arg

async def get_drink_detail(drink: str) -> str:
    return f'您定制的饮料是{drink}，跑堂的已经把配方记下来啦~'

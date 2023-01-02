from utils.cmdInterface import ExeI
from utils.actInterface import Builder, Encoder, msg_send_packer
from utils.globalData import BOT_STORE
from utils.globalPattern import *


@ExeI.template(
    aliases=['帮助', 'h'], 
    userLevel=ExeI.role.USER, 
    comment='获取帮助',
    prompt='[命令名]'
)
def help(event: dict, queryCmdName: str=None) -> dict:
    if not queryCmdName:
        u_lvl = ExeI.msg_checker.get_event_lvl(event)

        # 只显示权限内可用的命令
        help_str = '\n'.join([
            f' ● {name}  {"（" + " / ".join(ExeI.get_cmd_aliases(name)) + "）" if ExeI.get_cmd_aliases(name) != [] else ""}'
            for name in ExeI.cmd_map.keys()
            if u_lvl >= ExeI.get_cmd_auth(name)
        ])
        if help_str != '':
            help_str = '可用指令如下，括号内为别名：（命令可以使用别名）\n\n' \
                + help_str \
                + '\n\n此命令后跟命令名或别名获取详细帮助'
    else:
        help_str = help_detail(event, queryCmdName)

    return Builder.build(
        msg_send_packer.pack(
            event,
            [Encoder.text(help_str)],
        )
    )


def help_detail(event: dict, queryName: str) -> dict:
    u_lvl = ExeI.msg_checker.get_event_lvl(event)

    try:
        cmdName = ExeI.get_cmd_name(queryName)
    except BotUnknownCmdName:
        return '命令不存在'
    if u_lvl < ExeI.get_cmd_auth(cmdName):
        return '无权访问的命令'

    aliases = ExeI.get_cmd_aliases(cmdName)
    return "命令名：{}\n别称：{}\n说明：{}\n参数：{}\n注：方框参数为可选，括号参数为必选".format(
        cmdName,
        " / ".join(aliases) if aliases != [] else '无',
        ExeI.get_cmd_comment(cmdName),
        ExeI.get_cmd_paramsTip(cmdName)
    )


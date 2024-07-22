import os
import sys

from .abc import ReadOnlyMeta
from .typing import Any

__version__ = "3.0.0a1.dev0"


class MetaInfo(metaclass=ReadOnlyMeta):
    """元信息类

    .. admonition:: 提示
       :class: tip

       一般无需手动实例化该类，多数情况会直接使用本类的属性，或将本类用作类型注解。
    """

    VER: str = __version__
    """melobot 版本

       :meta hide-value:
    """

    CORE_NAME: str = "melobot"
    """melobot 项目名称

       :meta hide-value:
    """

    CORE_DESC: str = (
        "A bot development framework with friendly APIs, session control and plugin-supported."
    )
    """melobot 项目描述

       :meta hide-value:
    """

    CORE_SRC: str = "https://github.com/Meloland/melobot"
    """melobot 项目地址

       :meta hide-value:
    """

    CORE_LOGO: str = "\n".join(
        (
            r" __  __      _       ____        _   ",
            r"|  \/  | ___| | ___ | __ )  ___ | |_ ",
            r"| |\/| |/ _ \ |/ _ \|  _ \ / _ \| __|",
            r"| |  | |  __/ | (_) | |_) | (_) | |_ ",
            r"|_|  |_|\___|_|\___/|____/ \___/ \__|",
        )
    )
    """melobot ascii art 图标

       :meta hide-value:
    """

    ARGV: list[str] = sys.argv
    """当前运行的 argv

       :meta hide-value:
    """

    OS_NAME: str = os.name
    """当前系统名称

       :meta hide-value:
    """

    PLATFORM: str = sys.platform
    """当前系统平台

       :meta hide-value:
    """

    PY_VER: str = sys.version
    """当前 python 版本

       :meta hide-value:
    """

    PY_INFO: "sys._version_info" = sys.version_info
    """当前 python 信息

       :meta hide-value:
    """

    OS_SEP: str = os.sep

    """当前系统路径分隔符号，如 win 平台下的 "\"

       :meta hide-value:
    """

    PATH_SEP: str = os.pathsep

    """当前系统路径间的分隔符号，如 win 平台下的 ";"

       :meta hide-value:
    """

    LINE_SEP: str = os.linesep

    """当前系统行尾序列，如 win 平台下的 "\r\n"

       :meta hide-value:
    """

    ENV: os._Environ[str] = os.environ
    """当前运行的环境变量

       :meta hide-value:
    """

    @classmethod
    def get_all(cls) -> dict[str, Any]:
        """以字典形式获取所有元信息

        :return: 包含所有元信息的，属性名为键的字典
        """
        return {k: v for k, v in cls.__dict__.items() if not k.startswith("__")}
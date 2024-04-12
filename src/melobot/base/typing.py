import sys
from enum import Enum
from types import ModuleType
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Coroutine,
    Literal,
    Optional,
    ParamSpec,
    Type,
    TypeAlias,
    TypedDict,
    TypeVar,
    Union,
    cast,
)

import better_exceptions
from typing_extensions import NotRequired

# 修复在 windows powershell 显示错误的 bug
better_exceptions.encoding.ENCODING = sys.stdout.encoding
better_exceptions.formatter.ENCODING = sys.stdout.encoding
better_exceptions.hook()


class MsgSegment(TypedDict):
    """onebot 标准的消息段对象"""

    type: str
    data: dict[str, float | int | str]


class StdCustomNodeData(TypedDict):
    """onebot 标准的自定义消息结点数据"""

    nickname: str
    user_id: str
    content: list[MsgSegment]


class GocqCustomNodeData(TypedDict):
    """gocq 风格的自定义消息结点数据"""

    name: str
    uin: str
    content: list[MsgSegment]
    seq: NotRequired[list[MsgSegment]]


class ReferNodeData(TypedDict):
    """onebot 标准的引用消息结点数据"""

    id: str


class MsgNode(TypedDict):
    """onebot 标准的转发消息结点"""

    type: Literal["node"]
    data: StdCustomNodeData | GocqCustomNodeData | ReferNodeData


class ParseArgs:
    """解析参数类"""

    def __init__(self, values: list[Any] | None) -> None:
        """实例化一组解析参数，对应一次解析的结果

        :param values: 参数值
        """
        #: 保存的一组解析参数值
        self.vals: Optional[list[Any]] = values


class LogicMode(Enum):
    """逻辑模式枚举类型"""

    AND = 1
    OR = 2
    NOT = 3
    XOR = 4

    @classmethod
    def calc(cls, logic: "LogicMode", v1: Any, v2: Any = None) -> bool:
        if logic == LogicMode.AND:
            return (v1 and v2) if v2 is not None else bool(v1)
        elif logic == LogicMode.OR:
            return (v1 or v2) if v2 is not None else bool(v1)
        elif logic == LogicMode.NOT:
            return not v1
        elif logic == LogicMode.XOR:
            return (v1 ^ v2) if v2 is not None else bool(v1)

    @classmethod
    def seq_calc(cls, logic: "LogicMode", values: list[Any]) -> bool:
        if len(values) <= 0:
            return False
        elif len(values) <= 1:
            return bool(values[0])

        idx = 0
        res: bool
        while idx < len(values):
            if idx == 0:
                res = cls.calc(logic, values[idx], values[idx + 1])
                idx += 1
            else:
                res = cls.calc(logic, res, values[idx])
            idx += 1
        return res


class User(int, Enum):
    """用户权限等级枚举"""

    OWNER = 10000
    SU = 1000
    WHITE = 100
    USER = 10
    BLACK = -1


class PriorLevel(int, Enum):
    """事件处理优先级枚举

    为方便进行优先级设置，有 MIN, MAX, MEAN 三个枚举值
    """

    MIN = 0
    MAX = 1000
    MEAN = (MAX + MIN) // 2


class BotLife(Enum):
    """bot 实例的生命周期枚举"""

    LOADED = 1
    FIRST_CONNECTED = 2
    RECONNECTED = 3
    BEFORE_CLOSE = 4
    BEFORE_STOP = 5
    EVENT_BUILT = 6
    ACTION_PRESEND = 7


#: 泛型 T，无约束
T = TypeVar("T")
#: 泛型 T，无约束
T1 = TypeVar("T1")
#: 泛型 T，无约束
T2 = TypeVar("T2")
#: 泛型 T，无约束
T3 = TypeVar("T3")
#: :obj:`typing.ParamSpec` 泛型 P，无约束
P = ParamSpec("P")


class Void:
    """“无值”对象，而不是 :obj:`None` 代表的“空值”

    使用方法：直接使用这个类即可。

    这个对象的类型标注是：:obj:`VoidType`。
    """

    pass


#: “无值”对象类型
VoidType: TypeAlias = Type[Void]

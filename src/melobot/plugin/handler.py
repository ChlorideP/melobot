import asyncio
from enum import Enum

from ..adapter import Event_T
from ..context.abc import AbstractRule, SessionOption
from ..context.session import BotSession
from ..exceptions import BotValueError, HandlerSafeExited
from ..log import BotLogger, LogLevel
from ..typing import Generic
from ..utils import RWContext
from .processor import ProcessFlow


class HandleLevel(int, Enum):
    MIN = 0
    MAX = 1000
    MEAN = (MAX + MIN) // 2


class EventHandler(Generic[Event_T]):
    def __init__(
        self,
        flow: ProcessFlow,
        logger: BotLogger,
        priority: HandleLevel = HandleLevel.MEAN,
        block: bool = False,
        temp: bool = False,
        option: SessionOption[Event_T] | None = None,
    ) -> None:
        super().__init__()
        self.flow = flow
        self.logger = logger
        self.priority = priority
        self.handle_ctrl = RWContext()
        self.flow.blocked = block

        self.temp = temp
        self._invalid = False

        self._rule: AbstractRule[Event_T] | None
        if option is None:
            self._rule = None
            self._keep = False
            self._nowait_cb = None
            self._wait = True
        else:
            self._rule = option.rule
            self._keep = option.keep
            self._nowait_cb = option.nowait_cb
            self._wait = option.wait

        if self._wait and self._nowait_cb:
            self.logger.warning(
                f"{flow}：会话选项“冲突等待”为 True 时，“冲突回调”永远不会被调用"
            )

    def __format__(self, format_spec: str) -> str:
        match format_spec:
            case "hexid":
                return f"{id(self):#x}"
            case _:
                raise BotValueError(f"未知的 EventHandler 格式化标识符：{format_spec}")

    async def _run_in_session(self, event: Event_T) -> None:
        try:
            session = await BotSession[Event_T].get(
                event,
                rule=self._rule,
                wait=self._wait,
                nowait_cb=self._nowait_cb,
                keep=self._keep,
            )
            if session is None:
                return

            async with session.ctx():
                return await self.flow.run()

        except HandlerSafeExited:
            pass
        except Exception:
            self.logger.error(f"事件处理方法 {self.flow.name} 发生异常")
            self.logger.obj(
                event.__dict__, f"异常点 event {event.id}", level=LogLevel.ERROR
            )
            self.logger.exc(locals=locals())

    async def run(self, event: Event_T) -> None:
        if self._invalid:
            return

        if not self.temp:
            async with self.handle_ctrl.read():
                if self._invalid:
                    return
                await self._run_in_session(event)

        async with self.handle_ctrl.write():
            if self._invalid:
                return
            await self._run_in_session(event)
            self._invalid = True

    async def expire(self) -> None:
        async with self.handle_ctrl.write():
            self._invalid = True


class EventDispatcher:
    pass

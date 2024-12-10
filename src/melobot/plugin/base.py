from __future__ import annotations

import asyncio
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Iterable, final

from .._hook import HookBus
from ..ctx import BotCtx
from ..exceptions import PluginLoadError
from ..handle.base import EventHandler
from ..handle.process import Flow
from ..typ import (
    AsyncCallable,
    Callable,
    P,
    SingletonBetterABCMeta,
    abstractattr,
    deprecate_warn,
)
from ..utils import to_async
from .ipc import AsyncShare, SyncShare


class PluginLifeSpan(Enum):
    """插件生命周期的枚举"""

    INITED = "i"


@dataclass(frozen=True)
class PluginInfo:
    version: str = ""
    desc: str = ""
    docs: Path | None = None
    keywords: list[str] | None = None
    url: str = ""
    author: str = ""


class PluginPlanner:
    """插件管理器类

    用于声明一个插件，并为插件添加功能
    """

    def __init__(
        self,
        version: str,
        flows: list[Flow] | None = None,
        shares: list[SyncShare | AsyncShare] | None = None,
        funcs: list[Callable] | None = None,
        *,
        info: PluginInfo | None = None,
    ) -> None:
        self.version = version
        self.flows = [] if flows is None else flows
        self.shares = [] if shares is None else shares
        self.funcs = [] if funcs is None else funcs
        self.info = PluginInfo() if info is None else info

        self._pname: str = ""
        self._hook_bus = HookBus[PluginLifeSpan](PluginLifeSpan)
        self._built: bool = False
        self._plugin: Plugin

    # REMOVE: 3.0.0
    @classmethod
    def from_legacy(cls, legacy: LegacyPlugin) -> PluginPlanner:
        deprecate_warn(
            "继承 melobot.plugin.Plugin 类声明插件的方式已弃用，将在 3.0.0 移除。"
            "实例化 melobot.plugin.PluginPlanner 类来代替。"
            f"触发此警告的插件是：{legacy.__class__.__module__}.{legacy.__class__.__name__}"
        )
        planner = PluginPlanner(
            legacy.version,
            list(legacy.flows),
            list(legacy.shares),
            list(legacy.funcs),
            info=PluginInfo(
                legacy.version,
                f"{legacy.desc}\n{legacy.docs}" if legacy.desc != "" else "",
                None,
                legacy.keywords,
                legacy.url,
                legacy.author,
            ),
        )
        if not hasattr(legacy, "__hook_bus__"):
            bus = HookBus[PluginLifeSpan](PluginLifeSpan)
            planner._hook_bus = bus
            legacy.__class__.__hook_bus__ = bus
        else:
            planner._hook_bus = legacy.__class__.__hook_bus__
        return planner

    @final
    def on(
        self, *periods: PluginLifeSpan
    ) -> Callable[[AsyncCallable[P, None]], AsyncCallable[P, None]]:
        """注册一个 hook

        :param periods: 要绑定的 hook 类型
        :return: 装饰器
        """

        def wrapped(func: AsyncCallable[P, None]) -> AsyncCallable[P, None]:
            for type in periods:
                self._hook_bus.register(type, func)
            return func

        return wrapped

    @final
    def _build(self, name: str) -> Plugin:
        if not self._built:
            self._pname = name
            self._hook_bus.set_tag(name)
            self._plugin = Plugin(self)
            self._built = True
        return self._plugin

    @final
    def add_flow(self, *flows: Flow) -> None:
        """在运行期为指定的插件添加一批处理流

        在 :obj:`.PluginLifeSpan.INITED` 及其之后的阶段可以使用

        注意：不会立即生效，通常会在下一次事件处理前生效。
        因此返回时不代表已经添加了处理流，只是增添了添加处理流的任务

        :param flows: 处理流
        """
        try:
            self._plugin
        except AttributeError as e:
            raise PluginLoadError("插件尚未创建，此时无法运行此方法") from e

        hs = tuple(EventHandler(self._plugin, f) for f in flows)

        async def _add() -> None:
            await BotCtx().get()._dispatcher.add(
                *hs, callback=to_async(lambda: self._plugin.handlers.extend(hs))
            )

        asyncio.create_task(_add())

    @final
    def remove_flow(self, *flows: Flow) -> None:
        """在运行期为指定的插件移除一批处理流

        如果插件没有对应的处理流，不会发出异常，而是忽略

        在 :obj:`.PluginLifeSpan.INITED` 及其之后的阶段可以使用

        注意：不会立即生效，通常会在下一次事件处理前生效。
        因此返回时不代表已经移除了处理流，只是增添了移除处理流的任务

        :param flows: 处理流
        """
        try:
            self._plugin
        except AttributeError as e:
            raise PluginLoadError("插件尚未创建，此时无法运行此方法") from e

        hs = tuple(filter(lambda x: x.flow in flows, self._plugin.handlers))

        async def _del() -> None:
            await BotCtx().get()._dispatcher.remove(*hs, callback=_after_del)

        async def _after_del() -> None:
            self._plugin.handlers = list(
                filter(lambda x: x not in hs, self._plugin.handlers)
            )

        asyncio.create_task(_del())


class Plugin:
    def __init__(self, planner: PluginPlanner) -> None:
        self.planner = planner
        self.name = planner._pname
        self.hook_bus = planner._hook_bus

        self.shares = planner.shares
        self.funcs = planner.funcs
        self.handlers = list(EventHandler(self, f) for f in self.planner.flows)


# REMOVE: 3.0.0
class LegacyPlugin(metaclass=SingletonBetterABCMeta):
    """旧版插件类

    .. admonition:: 重要提示
        :class: caution

        已弃用使用该类声明插件，将于 `v3.0.0` 移除。请使用 :class:`.PluginPlanner` 代替。
    """

    version: str = abstractattr()
    shares: Iterable[SyncShare | AsyncShare] = ()
    funcs: Iterable[Callable] = ()
    flows: Iterable[Flow] = ()
    desc: str = ""
    docs: str = ""
    keywords: list[str] = []
    url: str = ""
    author: str = ""

    __hook_bus__: HookBus[PluginLifeSpan]

    @classmethod
    @final
    def on(
        cls, *periods: PluginLifeSpan
    ) -> Callable[[AsyncCallable[P, None]], AsyncCallable[P, None]]:
        """注册一个 hook

        :param periods: 要绑定的 hook 类型
        :return: 装饰器
        """
        if not hasattr(cls, "__hook_bus__"):
            cls.__hook_bus__ = HookBus[PluginLifeSpan](PluginLifeSpan)

        def wrapped(func: AsyncCallable[P, None]) -> AsyncCallable[P, None]:
            for type in periods:
                cls.__hook_bus__.register(type, func)
            return func

        return wrapped

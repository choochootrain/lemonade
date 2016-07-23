#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import i3ipc
import datetime
import asyncio
import threading
import functools

FN_INTERVAL = "__fn_interval__"
FN_EVENT = "__fn_event__"

def _get_interval(fn):
    return getattr(fn, FN_INTERVAL, None)

def _is_event(fn):
    return getattr(fn, FN_EVENT, False)

class Bar(object):
    def __init__(self):
        self._loop = asyncio.get_event_loop()
        self._registry = set()
        self._output = {}

    def _task(self, fn):
        async def task():
            val = await fn()
            self._flush_output(fn.__name__, val)

            interval = _get_interval(fn)
            if interval is not None:
                await asyncio.sleep(interval)
                self._schedule(task)

        return task

    def _schedule(self, coro):
        self._loop.create_task(coro())

    def _flush_output(self, name, val):
        self._output[name] = val
        self.flush()

    def interval(self, ival):
        assert ival > 0, "Repeat interval must be greater than 0."

        def _wrap(fn):
            assert not hasattr(fn, FN_EVENT), "Function can't be event and interval."

            setattr(fn, FN_INTERVAL, ival)
            self._registry.add(fn)

            return fn
        return _wrap

    def event(self, fn):
        assert not hasattr(fn, FN_INTERVAL), "Function can't be event and interval."

        setattr(fn, FN_EVENT, True)
        self._registry.add(fn)

        @functools.wraps(fn)
        def _wrap(*args, **kwargs):
            val = fn(*args, **kwargs)
            self._flush_output(fn.__name__, val)

        return _wrap

    def start(self):
        for fn in self._registry:
            if not _is_event(fn):
                self._schedule(self._task(fn))

        self._loop.run_forever()

    def flush(self):
        print(self._output, flush=True)

class MyBar(Bar):
    order = ["a", "workspace", "time"]

    def flush(self):
        out = []
        for item in self.order:
            out.append(self._output.get(item, " "))

        print(" ".join(out), flush=True)

bar = MyBar()

@bar.interval(1)
async def time():
    return datetime.datetime.now().strftime("%Y-%m-%j %H:%M:%S %a")

@bar.interval(3)
async def a():
    return "foo"

workspaces = {}
@bar.event
def workspace(i3, e):
    out = []
    for workspace in sorted(i3.get_workspaces(), key=lambda x: x['num']):
        if workspace["focused"]:
            out.append("●")
        else:
            out.append("○")

    return " ".join(out)

i3 = i3ipc.Connection()
i3.on("workspace", workspace)
i3_thread = threading.Thread(target=i3.main)
i3_thread.daemon = True
i3_thread.start()

try:
    bar.start()
except KeyboardInterrupt:
    pass


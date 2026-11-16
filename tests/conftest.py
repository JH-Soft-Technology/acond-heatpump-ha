"""Fixtures: a fake Acond Modbus TCP server."""

from __future__ import annotations

import asyncio
import struct

import pytest

pytest_plugins = ["pytest_homeassistant_custom_component"]


class FakeAcond:
    """Tiny Modbus TCP server with Acond-like register contents."""

    def __init__(self) -> None:
        self.inputs = [0] * 18
        self.holding = [0] * 12
        # 30001.. values (x10)
        self.inputs[0] = 215  # circuit1 target
        self.inputs[1] = 208  # circuit1 actual
        self.inputs[4] = 460  # DHW target
        self.inputs[5] = 441  # DHW actual
        self.inputs[6] = 0b1_0000_0001_0011  # on, running, circ1, cooling(bit12)
        self.inputs[7] = 300
        self.inputs[8] = 285
        self.inputs[9] = (-35) & 0xFFFF  # -3.5 °C outdoor
        self.inputs[13] = 0  # auto
        self.inputs[14] = 0  # AcondTherm
        self.inputs[16] = 42
        self.inputs[17] = 331
        self.holding[0] = 215
        self.holding[4] = 460
        self.holding[5] = 0b1_0000_0001  # summer bit 8 + auto bit 0
        self.writes: list[tuple[int, int]] = []
        self.server: asyncio.Server | None = None
        self.port = 0
        self._writers: set[asyncio.StreamWriter] = set()

    async def start(self) -> None:
        self.server = await asyncio.start_server(self._handle, "127.0.0.1", 0)
        self.port = self.server.sockets[0].getsockname()[1]

    async def stop(self) -> None:
        if self.server:
            self.server.close()
            for w in list(self._writers):
                w.close()
            await self.server.wait_closed()

    async def _handle(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        self._writers.add(writer)
        try:
            while True:
                header = await reader.readexactly(7)
                tid, _p, length, unit = struct.unpack(">HHHB", header)
                pdu = await reader.readexactly(length - 1)
                fc = pdu[0]
                if fc in (3, 4):
                    addr, count = struct.unpack(">HH", pdu[1:5])
                    regs = self.holding if fc == 3 else self.inputs
                    if addr + count > len(regs):
                        resp = bytes([fc | 0x80, 2])
                    else:
                        data = regs[addr : addr + count]
                        resp = bytes([fc, count * 2]) + struct.pack(f">{count}H", *data)
                elif fc == 6:
                    addr, value = struct.unpack(">HH", pdu[1:5])
                    self.holding[addr] = value
                    self.writes.append((addr, value))
                    resp = pdu[:5]
                else:
                    resp = bytes([fc | 0x80, 1])
                writer.write(struct.pack(">HHHB", tid, 0, len(resp) + 1, unit) + resp)
                await writer.drain()
        except (asyncio.IncompleteReadError, ConnectionError):
            pass
        finally:
            self._writers.discard(writer)
            writer.close()


@pytest.fixture
async def fake_acond(socket_enabled):
    server = FakeAcond()
    await server.start()
    yield server
    await server.stop()


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield

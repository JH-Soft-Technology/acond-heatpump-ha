"""Minimal asyncio Modbus TCP client (FC3, FC4, FC6).

Kept dependency free on purpose: Home Assistant pins its own pymodbus for the
core modbus integration and a second, different pin would conflict.
"""

from __future__ import annotations

import asyncio
import logging
import struct

_LOGGER = logging.getLogger(__name__)

FC_READ_HOLDING = 0x03
FC_READ_INPUT = 0x04
FC_WRITE_SINGLE = 0x06

EXCEPTION_CODES = {
    1: "illegal function",
    2: "illegal data address",
    3: "illegal data value",
    4: "server device failure",
    6: "server device busy",
}


class ModbusError(Exception):
    """Communication or protocol error."""


class AcondModbusClient:
    """Single persistent connection, requests serialized by a lock."""

    def __init__(self, host: str, port: int, unit: int, timeout: float = 5.0) -> None:
        self.host = host
        self.port = port
        self.unit = unit
        self.timeout = timeout
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._lock = asyncio.Lock()
        self._tid = 0

    async def _connect(self) -> None:
        if self._writer is not None and not self._writer.is_closing():
            return
        try:
            self._reader, self._writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port), self.timeout
            )
        except (OSError, TimeoutError) as err:
            raise ModbusError(f"cannot connect to {self.host}:{self.port}: {err}") from err

    async def close(self) -> None:
        """Close the connection."""
        async with self._lock:
            await self._close()

    async def _close(self) -> None:
        writer, self._writer, self._reader = self._writer, None, None
        if writer is not None:
            writer.close()
            try:
                await writer.wait_closed()
            except OSError:
                pass

    async def _request(self, pdu: bytes) -> bytes:
        async with self._lock:
            await self._connect()
            assert self._reader is not None and self._writer is not None
            self._tid = (self._tid + 1) & 0xFFFF
            tid = self._tid
            frame = struct.pack(">HHHB", tid, 0, len(pdu) + 1, self.unit) + pdu
            try:
                self._writer.write(frame)
                await self._writer.drain()
                while True:
                    header = await asyncio.wait_for(self._reader.readexactly(7), self.timeout)
                    r_tid, _proto, length, _unit = struct.unpack(">HHHB", header)
                    body = await asyncio.wait_for(
                        self._reader.readexactly(length - 1), self.timeout
                    )
                    if r_tid == tid:
                        break
                    _LOGGER.debug("Dropping stale response tid=%s (want %s)", r_tid, tid)
            except (OSError, TimeoutError, asyncio.IncompleteReadError) as err:
                await self._close()
                raise ModbusError(f"communication error: {err!r}") from err

        if body[0] & 0x80:
            code = body[1] if len(body) > 1 else 0
            raise ModbusError(
                f"exception response to FC{pdu[0]}: {EXCEPTION_CODES.get(code, code)}"
            )
        if body[0] != pdu[0]:
            raise ModbusError(f"unexpected function code {body[0]} (sent {pdu[0]})")
        return body

    async def _read(self, fc: int, address: int, count: int) -> list[int]:
        body = await self._request(struct.pack(">BHH", fc, address, count))
        byte_count = body[1]
        if byte_count != count * 2 or len(body) < 2 + byte_count:
            raise ModbusError(f"short response: {byte_count} bytes for {count} registers")
        return list(struct.unpack(f">{count}H", body[2 : 2 + byte_count]))

    async def read_input_registers(self, address: int, count: int) -> list[int]:
        """Read input registers (FC4), raw unsigned values."""
        return await self._read(FC_READ_INPUT, address, count)

    async def read_holding_registers(self, address: int, count: int) -> list[int]:
        """Read holding registers (FC3), raw unsigned values."""
        return await self._read(FC_READ_HOLDING, address, count)

    async def write_register(self, address: int, value: int) -> None:
        """Write a single holding register (FC6). Negative values are sent as int16."""
        if not -32768 <= value <= 65535:
            raise ValueError(f"value {value} out of 16-bit range")
        await self._request(struct.pack(">BHH", FC_WRITE_SINGLE, address, value & 0xFFFF))


def to_int16(value: int) -> int:
    """Interpret an unsigned 16-bit register as signed."""
    return value - 0x10000 if value & 0x8000 else value

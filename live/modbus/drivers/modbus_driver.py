
from typing import Dict, Any
from pymodbus.client import ModbusTcpClient, ModbusSerialClient
import yaml
import time

class ModbusBESS:
    def __init__(self, config: Dict[str, Any]):
        self.cfg = config
        self.map = self._load_map(self.cfg.get("register_map"))
        self.client = None
        self._connect()

    def _load_map(self, path: str) -> Dict[str, Any]:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _connect(self):
        mcfg = self.cfg["modbus"]
        mode = mcfg.get("mode", "tcp")
        timeout = mcfg.get(mode, {}).get("timeout", 2.0)
        if mode == "tcp":
            tcp = mcfg["tcp"]
            self.client = ModbusTcpClient(
                host=tcp["host"],
                port=tcp.get("port", 502),
                timeout=timeout
            )
        elif mode == "rtu":
            rtu = mcfg["rtu"]
            self.client = ModbusSerialClient(
                method="rtu",
                port=rtu["port"],
                baudrate=rtu.get("baudrate", 9600),
                bytesize=rtu.get("bytesize", 8),
                parity=rtu.get("parity", "N"),
                stopbits=rtu.get("stopbits", 1),
                timeout=timeout
            )
        else:
            raise ValueError(f"Unsupported modbus mode: {mode}")
        if not self.client.connect():
            raise ConnectionError("Modbus connection failed")

def _read_words(self, address: int, words: int, rtype: str, unit_id: int):
    # rtype: 'holding' | 'input'
    if rtype == "holding":
        rr = self.client.read_holding_registers(address=address, count=words, slave=unit_id)
    elif rtype == "input":
        rr = self.client.read_input_registers(address=address, count=words, slave=unit_id)
    else:
        raise ValueError(f"Unsupported register type: {rtype}")
    if rr.isError():
        raise IOError(f"Modbus read error at {address}/{rtype}: {rr}")
    return rr.registers

@staticmethod
def _to_int16(v):
    return v - 0x10000 if v & 0x8000 else v

@staticmethod
def _to_int32(words):
    raw = (words[0] << 16) | words[1]
    if raw & 0x80000000:
        return -((~raw & 0xFFFFFFFF) + 1)
    return raw

@staticmethod
def _to_uint32(words):
    return (words[0] << 16) | words[1]

def read_points(self) -> Dict[str, Any]:
    """
    Liest alle in der Map definierten Punkte und wendet Skalierung/Typumwandlung an.
    """
    out: Dict[str, Any] = {}
    mode = self.cfg["modbus"]["mode"]
    unit_id = self.cfg["modbus"][mode].get("unit_id", 1)
    for name, p in self.map.get("points", {}).items():
        addr = int(p["address"])
        words = int(p.get("words", 1))
        rtype = p.get("type", "holding")
        dtype = p.get("dtype", "uint16")
        scale = float(p.get("scale", 1.0))

        regs = self._read_words(addr, words, rtype, unit_id)

        if dtype == "uint16":
            val = regs[0]
        elif dtype == "int16":
            val = self._to_int16(regs[0])
        elif dtype == "uint32":
            if len(regs) < 2:
                raise ValueError(f"{name}: expected 2 words for uint32")
            val = self._to_uint32(regs[:2])
        elif dtype == "int32":
            if len(regs) < 2:
                raise ValueError(f"{name}: expected 2 words for int32")
            val = self._to_int32(regs[:2])
        else:
            raise ValueError(f"Unsupported dtype: {dtype}")

        out[name] = val * scale
    out["timestamp"] = time.time()
    return out

def write_point(self, name: str, value: float) -> bool:
    """
    Schreiben in Holding-Register (z. B. Leistungs-Sollwert). Skaliert inverse.
    Map-Eintrag muss `writable: true` besitzen.
    """
    p = self.map["points"].get(name)
    if not p or not p.get("writable"):
        raise ValueError(f"Point '{name}' not writable or not defined")
    mode = self.cfg["modbus"]["mode"]
    unit_id = self.cfg["modbus"][mode].get("unit_id", 1)
    addr = int(p["address"])
    scale = float(p.get("scale", 1.0))
    raw = int(round(value / scale))
    rr = self.client.write_register(address=addr, value=raw, slave=unit_id)
    return not rr.isError()

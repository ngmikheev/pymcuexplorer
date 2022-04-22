from pyocd.debug.symbols import SymbolProvider
from collections import namedtuple
import struct

SymbolInfoTuple = namedtuple("SymbolInfo", "name address size sym_type")


class SymbolInfo:
    def __init__(
        self, name: str, address: int, size: int, dtype: str = "None"
    ):
        self.name = name
        self.address = address
        self.size = size
        self.dtype = dtype


class DataSymbolInfo(SymbolInfo):
    def assign_setter_and_getter(self, mem_setter, mem_getter):
        def read_value():
            def _read_raw(offset: int = 0):
                return mem_getter(self.address + offset, self.size)

            def _read_int(size: int, signed: bool, offset: int = 0):
                return int.from_bytes(
                    _read_raw(offset), byteorder="little", signed=signed
                )

            if self.dtype == "int32":
                return _read_int(size=4, signed=True)
            elif self.dtype == "uint32":
                return _read_int(size=4, signed=False)
            elif self.dtype == "int16":
                return _read_int(size=2, signed=True)
            elif self.dtype == "uint16":
                return _read_int(size=2, signed=False)
            elif self.dtype == "int8":
                return _read_int(size=1, signed=True)
            elif self.dtype == "uint8":
                return _read_int(size=1, signed=False)
            elif self.dtype == "float":
                return struct.unpack("f", bytes(_read_raw()))[0]
            elif self.dtype == "char[]":
                return bytes(_read_raw()).decode()
            else:
                return _read_raw()

        def write_value(value):
            def _write_raw(data: bytes, offset: int = 0):
                if len(data) != self.size:
                    raise ValueError(
                        "Expected size {}, got {} (in bytes)".format(
                            self.size, len(data)
                        )
                    )

                mem_setter(self.address, data)

            def _write_int(
                value: int, size: int, signed: bool, offset: int = 0
            ):
                _write_raw(
                    value.to_bytes(size, byteorder="little", signed=signed),
                    offset
                )

            if self.dtype == "int32":
                _write_int(value, size=4, signed=True)
            elif self.dtype == "uint32":
                _write_int(value, size=4, signed=False)
            elif self.dtype == "int16":
                _write_int(value, size=2, signed=True)
            elif self.dtype == "uint16":
                _write_int(value, size=2, signed=False)
            elif self.dtype == "int8":
                _write_int(value, size=1, signed=True)
            elif self.dtype == "uint8":
                _write_int(value, size=1, signed=False)
            elif self.dtype == "float":
                _write_raw(struct.pack("f", value))
            elif self.dtype == "char[]":
                bstr = value.encode()
                if len(bstr) > self.size:
                    raise ValueError(
                        "Provided string too long: {} should be <= {}".format(
                            len(bstr), self.size
                        )
                    )
                bstr = bstr + b"\0" * (self.size - len(bstr))
                _write_raw(bstr)
            else:
                _write_raw(value)

        setattr(self, "read_value", read_value)
        setattr(self, "write_value", write_value)


class CodeSymbolInfo(SymbolInfo):
    pass


class SymbolInfoContainer:
    pass


def parse_iar_linker_map_file(iar_map_file_name: str):
    with open(iar_map_file_name) as f:
        lines = f.readlines()[1:]

    symbols = []
    entry_table_start_line = 0
    ENTRY_LIST_HEADER_LINES = 5
    for i, line in enumerate(lines):
        if "ENTRY LIST" in line:
            entry_table_start_line = i + ENTRY_LIST_HEADER_LINES
            break
    else:
        raise ValueError(
            "Entry list not founed in {} map file".format(iar_map_file_name)
        )

    full_line = ""
    for i in range(entry_table_start_line, len(lines)):
        if lines[i].strip() == "":
            # Empty line at the end of the table
            break

        full_line += lines[i].strip()
        if len(lines[i]) < 52:
            # Multiline entry
            full_line += " "
            continue

        line_tokens = full_line.split()
        full_line = ""

        if "Data" not in line_tokens and "Code" not in line_tokens:
            # Skip Code and other entries
            continue

        token_num = 0

        name = line_tokens[token_num]
        token_num += 1

        address = int(line_tokens[token_num].replace("'", ""), 16)
        token_num += 1

        size = 0
        try:
            size = int(line_tokens[token_num].replace("'", ""), 16)
            token_num += 1
        except ValueError:
            # No size provided, 0 assumed
            pass

        sym_type = ""
        if line_tokens[token_num] == "Data":
            sym_type = "STT_OBJECT"
        elif line_tokens[token_num] == "Code":
            sym_type = "STT_FUNC"

        s = SymbolInfoTuple(
            name=name,
            address=address,
            size=size,
            sym_type=sym_type
        )
        symbols.append(s)

    return symbols


class IARMapSymbolProvider(SymbolProvider):
    def __init__(self, iar_map_file_name: str):
        symbols_list = parse_iar_linker_map_file(iar_map_file_name)

        for s in symbols_list:
            if not s.name.isalnum():
                # Skip symbols with unsupported characters in name
                continue

            if s.sym_type == "STT_OBJECT":
                symbol = DataSymbolInfo(
                    name=s.name,
                    address=s.address,
                    size=s.size
                )

                if not hasattr(self, "data"):
                    self.data = SymbolInfoContainer()

                setattr(self.data, symbol.name, symbol)

            elif s.sym_type == "STT_FUNC":
                symbol = CodeSymbolInfo(
                    name=s.name,
                    address=s.address,
                    size=s.size
                )

                if not hasattr(self, "code"):
                    self.code = SymbolInfoContainer()

                setattr(self.code, symbol.name, symbol)

            else:
                raise RuntimeError(
                    "Got symbol with unsupported type: '{}'".format(s.sym_tipe)
                )

    def get_symbol_by_name(self, symbol_name: str):
        if hasattr(self.code, symbol_name):
            return getattr(self.code, symbol_name)
        elif hasattr(self.data, symbol_name):
            return getattr(self.data, symbol_name)
        else:
            return KeyError("There is no symbol {}".format(symbol_name))

    def get_symbol_value(self, symbol_name: str):
        return set.get_symbol_by_name(symbol_name).address

    def get_data_symbols(self):
        symbols = []
        for s in self.data.__dict__.values():
            if isinstance(s, DataSymbolInfo):
                symbols.append(s)
        return symbols

    def get_code_symbols(self):
        symbols = []
        for s in self.data.__dict__.values():
            if isinstance(s, CodeSymbolInfo):
                symbols.append(s)
        return symbols

    def get_symbols(self):
        symbols = []
        symbols += self.get_data_symbols()
        symbols += self.get_code_symbols()
        return symbols

    def assign_setter_and_getter(self, mem_setter, mem_getter):
        for s in self.get_data_symbols():
            s.assign_setter_and_getter(mem_setter, mem_getter)

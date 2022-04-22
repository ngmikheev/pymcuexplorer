from .register import Register


class Peripheral:
    def __init__(self, peripheral_dict: dict):
        self.__doc__ = "{} - {}\n".format(
            peripheral_dict["name"],
            peripheral_dict["description"]
        )
        for k, v in peripheral_dict.items():
            if k == "registers":
                self.__doc__ += "Registers:\n"
                for register in v:
                    r = Register(register)
                    r.peripheral = self
                    setattr(self, r.name, r)
                    self.__doc__ += "  {} - {}\n".format(
                        r.name,
                        r.description
                    )
            else:
                setattr(self, k, v)

    def get_registers(self):
        registers = []
        for attr in self.__dict__.values():
            if isinstance(attr, Register):
                registers.append(attr)

        return registers

    def assign_setter_and_getter(self, word_setter, word_getter):
        def read_register(register_address_offset: int):
            return word_getter(self.base_address + register_address_offset)

        def write_register(register_address_offset: int, value: int):
            word_setter(self.base_address + register_address_offset, value)

        for r in self.get_registers():
            r.assign_setter_and_getter(write_register, read_register)

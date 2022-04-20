from .utils import check_bit_width
from .field import Field

class Register:
    def __init__(self, register_dict: dict):
        self.__doc__ = "{} - {}\n".format(
            register_dict["name"],
            register_dict["description"]
        )
        for k, v in register_dict.items():
            if k == "fields":
                self.__doc__ += "Fileds:\n"
                for field in v:
                    f = Field(field)
                    f.register = self
                    setattr(self, f.name, f)
                    self.__doc__ += "  {} - {}\n".format(
                        f.name,
                        f.description
                    )
            else:
                setattr(self, k, v)
        
    def get_fileds(self):
        fields = []
        for attr in self.__dict__.values():
            if isinstance(attr, Field):
                fields.append(attr)

        return fields

    def assign_setter_and_getter(self, block_reg_setter, block_reg_getter):
        def read_value():
            return block_reg_getter(self.address_offset)

        def read_bits(bit_mask):
            return self.read_value() & bit_mask 

        def write_value(value: int):
            check_bit_width(value, self.size)
            block_reg_setter(self.address_offset, value)

        def set_bits(bit_mask):
            check_bit_width(bit_mask, self.size)
            reg_value = self.read_value()
            reg_value |= bit_mask
            self.write_value(reg_value)

        def reset_bits(bit_mask):
            check_bit_width(bit_mask, self.size)
            reg_value = self.read_value()
            reg_value &= ~bit_mask
            self.write_value(reg_value)

        setattr(self, "read_value", read_value)
        setattr(self, "write_value", write_value)
        setattr(self, "set_bits", set_bits)
        setattr(self, "reset_bits", reset_bits)
        for f in self.get_fileds():
            f.assign_setter_and_getter(write_value, read_value)
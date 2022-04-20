from .utils import check_bit_width

class Field:
    def __init__(self, device_dict: dict):
        self.__doc__ = "{} - {}".format(
            device_dict["name"],
            device_dict["description"]
        )
        for k, v in device_dict.items():
            setattr(self, k, v)

    def assign_setter_and_getter(self, reg_setter, reg_getter):
        if reg_getter is None:
            return
        
        def read_field():
            return (reg_getter() >> self.bit_offset) & self.bit_width

        setattr(self, "read_field", read_field)
        
        if reg_setter is None:
            return
        
        def write_field(value: int):
            check_bit_width(value, self.bit_width)
            reg_value = reg_getter()
            reg_value &= ~(self.bit_width << self.bit_offset)
            reg_value |= (value << self.bit_offset)
            reg_setter(reg_value)
        
        setattr(self, "write_field", write_field)

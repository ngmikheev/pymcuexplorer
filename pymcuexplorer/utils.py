def check_bit_width(value: int, bit_width: int):
    if value & ((1 << bit_width) - 1) != value:
        raise ValueError(
            "Value {} does not match bit width: {}".format(
                hex(value), bit_width
            )
        )

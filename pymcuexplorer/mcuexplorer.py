from pyocd.debug.svd.parser import SVDParser
from pyocd.debug.svd.loader import SVDFile
from .peripheral import Peripheral


class MCUExplorer:
    def __init__(self, mcu_dict: dict):
        self.__doc__ = "{} MCU\n".format(
            mcu_dict["name"]
        )
        for k, v in mcu_dict.items():
            if k == "peripherals":
                self.__doc__ += "Peripherals:\n"
                for peripheral in v:
                    p = Peripheral(peripheral)
                    p.device = self
                    setattr(self, p.name, p)
                    self.__doc__ += "  {} - {}\n".format(
                        p.name,
                        p.description
                    )
            else:
                setattr(self, k, v)

    def get_peripherals(self):
        peripherals = []
        for attr in self.__dict__.values():
            if isinstance(attr, Peripheral):
                peripherals.append(attr)

        return peripherals

    def assign_setter_and_getter(self, mem_setter, mem_getter):
        for p in self.get_peripherals():
            p.assign_setter_and_getter(mem_setter, mem_getter)


def create_mcu_explorer_from_ocd_target(target):
    m = MCUExplorer(target.svd_device.to_dict())
    m.assign_setter_and_getter(target.write32, target.read32)
    return m


def create_mcu_explorer_from_svd_file(svd_file_name: str):
    device = SVDParser.for_xml_file(svd_file_name).get_device()
    return MCUExplorer(device.to_dict())


def create_mcu_explorer_from_builtin_svd_file(svd_file_name: str):
    svd_file_path = SVDFile.from_builtin(svd_file_name).filename
    return create_mcu_explorer_from_svd_file(svd_file_path)

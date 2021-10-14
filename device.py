from enum import Enum
import platform
import subprocess


class DeviceStatus(Enum):
    DOWN = 'DOWN'
    UP = 'UP'


class DeviceType(Enum):
    DEFAULT_GATEWAY = 'DEFAULT GATEWAY'
    SWITCH = 'SWITCH'
    PC = 'PC'
    SERVER = 'SERVER'


class Device(object):
    def __init__(self, index: int, name: str, ip: str, device: DeviceType):
        self.index = index
        self.name = name
        self.ip = ip
        self.device = device
        self.status = DeviceStatus.UP

    def ping(self) -> bool:
        # option for the number of packets as a function of
        param = '-n' if platform.system().lower() == 'windows' else '-c'

        # building the command, e.g. 'ping -c 1 google.com'
        command = ['ping', param, '1', self.ip]

        return subprocess.call(command, stdout=subprocess.DEVNULL) == 0

    def is_available(self):
        return self.ping()


class DefaultGateway(Device):
    def __init__(self, index: int, name: str, ip: str, device: DeviceType,
                 children: list):
        super().__init__(index, name, ip, device)
        self.children = DefaultGateway._convert_json_to_devices(children) \
            if DefaultGateway._is_json(children) else children

    @staticmethod
    def _is_json(children: list):
        return isinstance(children[0], dict) if len(children) > 0 else False

    @staticmethod
    def _convert_json_to_devices(children):
        converted = []
        for child in children:
            if child.get('device') == DeviceType.SWITCH.value:
                converted.append(
                    Switch(
                        index=child.get('index', None),
                        name=child.get('name', None),
                        ip=child.get('ip', None),
                        device=child.get('device', None),
                        children=child.get('children', [])
                    )
                )
            else:
                converted.append(
                    Device(
                        index=child.get('index', None),
                        name=child.get('name', None),
                        ip=child.get('ip', None),
                        device=child.get('device', None)
                    )
                )
        return converted


class Switch(DefaultGateway):
    def __init__(self, index: int, name: str, ip: str, device: DeviceType,
                 children: list):
        super().__init__(index, name, ip, device, children)

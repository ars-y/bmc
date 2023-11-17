from enum import IntEnum, auto


class StatusEnum(IntEnum):

    NEW = auto()
    IN_PROGRESS = auto()
    DONE = auto()


STATUS_STATES: dict[StatusEnum, StatusEnum] = {
    StatusEnum.NEW: StatusEnum.NEW,
    StatusEnum.IN_PROGRESS: StatusEnum.IN_PROGRESS,
    StatusEnum.DONE: StatusEnum.DONE
}

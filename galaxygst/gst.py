from __future__ import annotations

import struct
from io import BytesIO
import time
import dolphin_memory_engine

__all__ = []


def validate_ptr(name: str):
    def inner(func):
        def wrapper(*args, **kwargs):
            if args[0] == 0:
                raise IndexError(f"{name} is NULL!")
            return func(*args, **kwargs)
        return wrapper
    return inner


UNINITIALIZED_GAME_ID = "\0\0\0\0"
VALID_GAME_IDS = ["SB4P", "SB4E", "SB4J", "SB4K", "SB4W"]


# ----------------------------------------------------------------------------------------------------------------------
# GstRecorderInfo accessors for Dolphin
# The following values should be in sync with the respective information contained within "GstRecord.h"!

RECORDER_MODE_WAITING = 0
RECORDER_MODE_PREPARING = 1
RECORDER_MODE_RECORDING = 2
RECORDER_MODE_STOPPED = 3

GHOST_TYPE_GHOST_ATTACK_GHOST = 0
GHOST_TYPE_PICHAN_RACER = 1
GHOST_TYPE_GHOST_PLAYER_MARIO = 2  # Reserved
GHOST_TYPE_GHOST_PLAYER_LUIGI = 3  # Reserved

GHOST_FILE_FORMATS = [
    "GhostAttackGhostData{1:02d}.gst",
    "PichanRacerRaceData{1:03d}.gst",
    "{0}.gst",
    "{0}Luigi.gst"
]

ADDR_GST_RECORDER_INFO_PTR = 0x80003FF8
OFFSET_UPDATE_FRAME = 0x00
OFFSET_RECORDER_MODE = 0x04
OFFSET_STAGE_NAME_PTR = 0x08
OFFSET_GST_DATA_INDEX = 0x0C
OFFSET_GST_DATA_TYPE = 0x10
OFFSET_GST_DATA_STRUCT = 0x14
OFFSET_GST_DATA_STRUCT_POSITION = OFFSET_GST_DATA_STRUCT + 0x00
OFFSET_GST_DATA_STRUCT_ROTATION = OFFSET_GST_DATA_STRUCT + 0x0C
OFFSET_GST_DATA_STRUCT_SCALE = OFFSET_GST_DATA_STRUCT + 0x18
OFFSET_GST_DATA_STRUCT_VELOCITY = OFFSET_GST_DATA_STRUCT + 0x24
OFFSET_GST_DATA_STRUCT_ACTION_NAME_PTR = OFFSET_GST_DATA_STRUCT + 0x30
OFFSET_GST_DATA_STRUCT_ACTION_HASH = OFFSET_GST_DATA_STRUCT + 0x34
OFFSET_GST_DATA_STRUCT_BCK_FRAME = OFFSET_GST_DATA_STRUCT + 0x38
OFFSET_GST_DATA_STRUCT_TRACK_WEIGHTS = OFFSET_GST_DATA_STRUCT + 0x3C
OFFSET_GST_DATA_STRUCT_BCK_RATE = OFFSET_GST_DATA_STRUCT + 0x4C
OFFSET_GST_DATA_STRUCT_PACKET_FLAGS = OFFSET_GST_DATA_STRUCT + 0x50


class Vec3f:
    """Represents a 3D vector using floating point coordinates."""
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self.x = x
        self.y = y
        self.z = z

    def set(self, other: Vec3f):
        self.x = other.x
        self.y = other.y
        self.z = other.z

    def __eq__(self, other):
        if type(other) != Vec3f:
            return False
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __ne__(self, other):
        if type(other) != Vec3f:
            return True
        return self.x != other.x or self.y != other.y or self.z != other.z


class Vec3i:
    """Represents a 3D vector using integer coordinates."""
    def __init__(self, x: int = 0, y: int = 0, z: int = 0):
        self.x = x
        self.y = y
        self.z = z

    def set(self, other: Vec3i):
        self.x = other.x
        self.y = other.y
        self.z = other.z

    def __eq__(self, other):
        if type(other) != Vec3i:
            return False
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __ne__(self, other):
        if type(other) != Vec3i:
            return True
        return self.x != other.x or self.y != other.y or self.z != other.z


def dolphin_get_game_id() -> str:
    """
    Reads and returns the game's ID name from Dolphin's emulated game memory.

    :return: the game's ID name.
    """
    return dolphin_memory_engine.read_bytes(0, 4).decode("ascii")


@validate_ptr("u32*")
def dolphin_read_u32(ptr: int) -> int:
    """
    Reads an unsigned 32-bit integer at the specified address in Dolphin's emulated game memory and returns it.

    :param ptr: the pointer to the unsigned 32-bit integer.
    :return: the value read.
    """
    return dolphin_memory_engine.read_word(ptr) & 0xFFFFFFFF


@validate_ptr("f32*")
def dolphin_read_f32(ptr: int) -> int:
    """
    Reads a 32-bit floating point number at the specified address in Dolphin's emulated game memory and returns it.

    :param ptr: the pointer to the 32-bit float.
    :return: the value read.
    """
    return dolphin_memory_engine.read_float(ptr)


@validate_ptr("Vec*")
def dolphin_read_vec(ptr: int, dest: Vec3f = None) -> Vec3f:
    """
    Reads a 3D vector at the specified address in Dolphin's emulated game memory and returns it.

    :param ptr: the pointer to the 3D vector.
    :param dest: the destination vector.
    :return: the destination vector.
    """
    if dest is None:
        dest = Vec3f()
    dest.x = dolphin_memory_engine.read_float(ptr)
    dest.y = dolphin_memory_engine.read_float(ptr + 4)
    dest.z = dolphin_memory_engine.read_float(ptr + 8)
    return dest


@validate_ptr("char*")
def dolphin_read_cstring(ptr: int) -> str:
    """
    Reads a C-string at the specified address in Dolphin's emulated game memory and returns it.

    :param ptr: the pointer to the C-string.
    :return: the value read.
    """
    chars = bytearray()
    while True:
        char = dolphin_memory_engine.read_byte(ptr)
        ptr += 1
        if char == 0:
            break
        else:
            chars.append(char)
    return chars.decode("ascii")


@validate_ptr("GstRecorderInfo*")
def dolphin_read_update_frame(gst_recorder_info_ptr: int) -> int:
    """
    Reads the update frame number associated with the GstRecorderInfo in Dolphin's emulated game memory and returns it.
    :param gst_recorder_info_ptr: the pointer to GstRecorderInfo.
    :return: the value read.
    """
    return dolphin_read_u32(gst_recorder_info_ptr + OFFSET_UPDATE_FRAME)


@validate_ptr("GstRecorderInfo*")
def dolphin_read_recorder_mode(gst_recorder_info_ptr: int) -> int:
    """
    Reads the recorder mode associated with the GstRecorderInfo in Dolphin's emulated game memory and returns it.
    :param gst_recorder_info_ptr: the pointer to GstRecorderInfo.
    :return: the value read.
    """
    return dolphin_read_u32(gst_recorder_info_ptr + OFFSET_RECORDER_MODE)


@validate_ptr("GstRecorderInfo*")
def dolphin_read_stage_name(gst_recorder_info_ptr: int) -> str | None:
    """
    Reads the stage's name associated with the GstRecorderInfo in Dolphin's emulated game memory and returns it.
    :param gst_recorder_info_ptr: the pointer to GstRecorderInfo.
    :return: the value read.
    """
    stage_name_ptr = dolphin_read_u32(gst_recorder_info_ptr + OFFSET_STAGE_NAME_PTR)
    return dolphin_read_cstring(stage_name_ptr)


@validate_ptr("GstRecorderInfo*")
def dolphin_read_ghost_data_index(gst_recorder_info_ptr: int) -> int:
    """
    Reads the GhostData index associated with the GstRecorderInfo in Dolphin's emulated game memory and returns it.
    :param gst_recorder_info_ptr: the pointer to GstRecorderInfo.
    :return: the value read.
    """
    return dolphin_read_u32(gst_recorder_info_ptr + OFFSET_GST_DATA_INDEX)


@validate_ptr("GstRecorderInfo*")
def dolphin_read_ghost_data_type(gst_recorder_info_ptr: int) -> int:
    """
    Reads the GhostData type associated with the GstRecorderInfo in Dolphin's emulated game memory and returns it.
    :param gst_recorder_info_ptr: the pointer to GstRecorderInfo.
    :return: the value read.
    """
    return dolphin_read_u32(gst_recorder_info_ptr + OFFSET_GST_DATA_TYPE)


@validate_ptr("GstRecorderInfo*")
def dolphin_read_ghost_data_struct_position(gst_recorder_info_ptr: int, dest: Vec3f = None) -> Vec3f:
    """
    Reads the position of the GhostData associated with the GstRecorderInfo in Dolphin's emulated game memory and
    returns it.

    :param gst_recorder_info_ptr: the pointer to GstRecorderInfo.
    :param dest: the destination vector.
    :return: the destination vector.
    """
    return dolphin_read_vec(gst_recorder_info_ptr + OFFSET_GST_DATA_STRUCT_POSITION, dest)


@validate_ptr("GstRecorderInfo*")
def dolphin_read_ghost_data_struct_rotation(gst_recorder_info_ptr: int, dest: Vec3f = None) -> Vec3f:
    """
    Reads the rotation of the GhostData associated with the GstRecorderInfo in Dolphin's emulated game memory and
    returns it.

    :param gst_recorder_info_ptr: the pointer to GstRecorderInfo.
    :param dest: the destination vector.
    :return: the destination vector.
    """
    return dolphin_read_vec(gst_recorder_info_ptr + OFFSET_GST_DATA_STRUCT_ROTATION, dest)


@validate_ptr("GstRecorderInfo*")
def dolphin_read_ghost_data_struct_scale(gst_recorder_info_ptr: int, dest: Vec3f = None) -> Vec3f:
    """
    Reads the scale of the GhostData associated with the GstRecorderInfo in Dolphin's emulated game memory and
    returns it.

    :param gst_recorder_info_ptr: the pointer to GstRecorderInfo.
    :param dest: the destination vector.
    :return: the destination vector.
    """
    return dolphin_read_vec(gst_recorder_info_ptr + OFFSET_GST_DATA_STRUCT_SCALE, dest)


@validate_ptr("GstRecorderInfo*")
def dolphin_read_ghost_data_struct_velocity(gst_recorder_info_ptr: int, dest: Vec3f = None) -> Vec3f:
    """
    Reads the velocity of the GhostData associated with the GstRecorderInfo in Dolphin's emulated game memory and
    returns it.

    :param gst_recorder_info_ptr: the pointer to GstRecorderInfo.
    :param dest: the destination vector.
    :return: the destination vector.
    """
    return dolphin_read_vec(gst_recorder_info_ptr + OFFSET_GST_DATA_STRUCT_VELOCITY, dest)


@validate_ptr("GstRecorderInfo*")
def dolphin_read_ghost_data_struct_action_name(gst_recorder_info_ptr: int) -> str:
    """
    Reads the animation name of the GhostData associated with the GstRecorderInfo in Dolphin's emulated game memory and
    returns it.

    :param gst_recorder_info_ptr: the pointer to GstRecorderInfo.
    :return: the value read.
    """
    action_name_ptr = dolphin_read_u32(gst_recorder_info_ptr + OFFSET_GST_DATA_STRUCT_ACTION_NAME_PTR)
    return dolphin_read_cstring(action_name_ptr)


@validate_ptr("GstRecorderInfo*")
def dolphin_read_ghost_data_struct_action_hash(gst_recorder_info_ptr: int) -> int:
    """
    Reads the animation hash of the GhostData associated with the GstRecorderInfo in Dolphin's emulated game memory and
    returns it.

    :param gst_recorder_info_ptr: the pointer to GstRecorderInfo.
    :return: the value read.
    """
    return dolphin_read_u32(gst_recorder_info_ptr + OFFSET_GST_DATA_STRUCT_ACTION_HASH)


@validate_ptr("GstRecorderInfo*")
def dolphin_read_ghost_data_struct_bck_frame(gst_recorder_info_ptr: int) -> float:
    """
    Reads the BCK frame of the GhostData associated with the GstRecorderInfo in Dolphin's emulated game memory and
    returns it.

    :param gst_recorder_info_ptr: the pointer to GstRecorderInfo.
    :return: the value read.
    """
    return dolphin_read_f32(gst_recorder_info_ptr + OFFSET_GST_DATA_STRUCT_BCK_FRAME)


@validate_ptr("GstRecorderInfo*")
def dolphin_read_ghost_data_struct_bck_rate(gst_recorder_info_ptr: int) -> float:
    """
    Reads the BCK rate of the GhostData associated with the GstRecorderInfo in Dolphin's emulated game memory and
    returns it.

    :param gst_recorder_info_ptr: the pointer to GstRecorderInfo.
    :return: the value read.
    """
    return dolphin_read_f32(gst_recorder_info_ptr + OFFSET_GST_DATA_STRUCT_BCK_RATE)


@validate_ptr("GstRecorderInfo*")
def dolphin_read_ghost_data_struct_track_weights(gst_recorder_info_ptr: int) -> tuple[float, float, float, float]:
    """
    Reads the track weights of the GhostData associated with the GstRecorderInfo in Dolphin's emulated game memory and
    returns it.

    :param gst_recorder_info_ptr: the pointer to GstRecorderInfo.
    :return: the tuple of four track weights read.
    """
    weight_0 = dolphin_read_f32(gst_recorder_info_ptr + OFFSET_GST_DATA_STRUCT_TRACK_WEIGHTS + 0)
    weight_1 = dolphin_read_f32(gst_recorder_info_ptr + OFFSET_GST_DATA_STRUCT_TRACK_WEIGHTS + 4)
    weight_2 = dolphin_read_f32(gst_recorder_info_ptr + OFFSET_GST_DATA_STRUCT_TRACK_WEIGHTS + 8)
    weight_3 = dolphin_read_f32(gst_recorder_info_ptr + OFFSET_GST_DATA_STRUCT_TRACK_WEIGHTS + 12)
    return weight_0, weight_1, weight_2, weight_3


# ----------------------------------------------------------------------------------------------------------------------
# GhostData structures

PACKET_FLAG_POSITION_INT = 0x0001
PACKET_FLAG_ROTATION_X = 0x0002
PACKET_FLAG_ROTATION_Y = 0x0004
PACKET_FLAG_ROTATION_Z = 0x0008
PACKET_FLAG_ACTION_NAME = 0x0010
PACKET_FLAG_BCK_FRAME = 0x0020
PACKET_FLAG_TRACK_WEIGHT_0 = 0x0040
PACKET_FLAG_TRACK_WEIGHT_1 = 0x0080
PACKET_FLAG_TRACK_WEIGHT_2 = 0x0100
PACKET_FLAG_TRACK_WEIGHT_3 = 0x0200
PACKET_FLAG_SCALE = 0x0400
PACKET_FLAG_VELOCITY = 0x0800
PACKET_FLAG_BCK_RATE = 0x1000
PACKET_FLAG_ACTION_HASH = 0x2000
PACKET_FLAG_POSITION_FLOAT = 0x4000


def get_shift_ratio(shift: int) -> float:
    if shift > 0:
        return (256 << shift) * 0.00390625
    else:
        return (256 >> -shift) * 0.00390625


def clamp(min: float, max: float, value: float) -> float:
    if value < min:
        return min
    elif value > max:
        return max
    return value


class RawGhostData:
    def __init__(self, ghost_data_type: int):
        self.ghost_data_type = ghost_data_type

        self.position = Vec3i()
        self.position_f = Vec3f()
        self.rotation = Vec3i()
        self.scale = Vec3i()
        self.velocity = Vec3i()
        self.action_name = ""
        self.action_hash = 0
        self.bck_frame = 0
        self.track_weights = [0, 0, 0, 0]
        self.bck_rate = 0

        self.packet_flags = -1

    def set_position(self, position: Vec3f):
        ratio = get_shift_ratio(-2)
        self.position.x = int(position.x * ratio)
        self.position.y = int(position.y * ratio)
        self.position.z = int(position.z * ratio)
        self.position_f.set(position)

    def set_rotation(self, rotation: Vec3f):
        ratio = get_shift_ratio(7)
        self.rotation.x = int(clamp(-180.0, 180.0, rotation.x) * ratio)
        self.rotation.y = int(clamp(-180.0, 180.0, rotation.y) * ratio)
        self.rotation.z = int(clamp(-180.0, 180.0, rotation.z) * ratio)

    def set_scale(self, scale: Vec3f):
        ratio = get_shift_ratio(3)
        self.scale.x = int(scale.x * ratio)
        self.scale.y = int(scale.y * ratio)
        self.scale.z = int(scale.z * ratio)

    def set_velocity(self, velocity: Vec3f):
        ratio = get_shift_ratio(0)
        self.velocity.x = int(velocity.x * ratio)
        self.velocity.y = int(velocity.y * ratio)
        self.velocity.z = int(velocity.z * ratio)

    def set_action_name(self, action_name: str):
        self.action_name = action_name

    def set_action_hash(self, action_hash: int):
        self.action_hash = action_hash

    def set_bck_frame(self, bck_frame: float):
        ratio = get_shift_ratio(2)
        self.bck_frame = int(bck_frame * ratio)

    def set_bck_rate(self, bck_rate: float):
        ratio = get_shift_ratio(3)
        self.bck_rate = int(bck_rate * ratio)

    def set_track_weights(self, track_weights: tuple[float, float, float, float]):
        ratio = get_shift_ratio(7)

        for i, track_weight in enumerate(track_weights):
            if track_weight == 1.0:
                self.track_weights[i] = -128
            else:
                self.track_weights[i] = int(track_weight * ratio)

    def compare_and_update(self, other: RawGhostData):
        self.packet_flags = 0

        # No object seems to use velocity or position_f, so these won't be updated here

        if self.position != other.position:
            self.packet_flags |= PACKET_FLAG_POSITION_INT
            self.position.set(other.position)

        if self.scale != other.scale:
            self.packet_flags |= PACKET_FLAG_SCALE
            self.scale.set(other.scale)

        if self.rotation.x != other.rotation.x:
            self.packet_flags |= PACKET_FLAG_ROTATION_X
            self.rotation.x = other.rotation.x

        if self.rotation.y != other.rotation.y:
            self.packet_flags |= PACKET_FLAG_ROTATION_Y
            self.rotation.y = other.rotation.y

        if self.rotation.z != other.rotation.z:
            self.packet_flags |= PACKET_FLAG_ROTATION_Z
            self.rotation.z = other.rotation.z

        if self.action_name != other.action_name and self.ghost_data_type in [GHOST_TYPE_PICHAN_RACER]:
            self.packet_flags |= PACKET_FLAG_ACTION_NAME
            self.action_name = other.action_name

        if self.action_hash != other.action_hash and self.ghost_data_type in [GHOST_TYPE_GHOST_ATTACK_GHOST]:
            self.packet_flags |= PACKET_FLAG_ACTION_HASH
            self.action_hash = other.action_hash

        if self.bck_frame != other.bck_frame:
            self.packet_flags |= PACKET_FLAG_BCK_FRAME
            self.bck_frame = other.bck_frame

        if self.bck_rate != other.bck_rate:
            self.packet_flags |= PACKET_FLAG_BCK_RATE
            self.bck_rate = other.bck_rate

        if self.track_weights[0] != other.track_weights[0]:
            self.packet_flags |= PACKET_FLAG_TRACK_WEIGHT_0
            self.track_weights[0] = other.track_weights[0]

        if self.track_weights[1] != other.track_weights[1]:
            self.packet_flags |= PACKET_FLAG_TRACK_WEIGHT_1
            self.track_weights[1] = other.track_weights[1]

        if self.track_weights[2] != other.track_weights[2]:
            self.packet_flags |= PACKET_FLAG_TRACK_WEIGHT_2
            self.track_weights[2] = other.track_weights[2]

        if self.track_weights[3] != other.track_weights[3]:
            self.packet_flags |= PACKET_FLAG_TRACK_WEIGHT_3
            self.track_weights[3] = other.track_weights[3]

    def pack(self) -> tuple[bytes, int]:
        out = BytesIO()

        packet_flags = self.packet_flags

        if packet_flags & PACKET_FLAG_POSITION_FLOAT:
            out.write(struct.pack(">3f", self.position_f.x, self.position_f.y, self.position_f.z))
        elif packet_flags & PACKET_FLAG_POSITION_INT:
            out.write(struct.pack(">3h", self.position.x, self.position.y, self.position.z))

        if packet_flags & PACKET_FLAG_VELOCITY:
            out.write(struct.pack("3b", self.velocity.x, self.velocity.y, self.velocity.z))

        if packet_flags & PACKET_FLAG_SCALE:
            out.write(struct.pack("3b", self.scale.x, self.scale.y, self.scale.z))

        if packet_flags & PACKET_FLAG_ROTATION_X:
            out.write(struct.pack("b", self.rotation.x))

        if packet_flags & PACKET_FLAG_ROTATION_Y:
            out.write(struct.pack("b", self.rotation.y))

        if packet_flags & PACKET_FLAG_ROTATION_Z:
            out.write(struct.pack("b", self.rotation.z))

        if packet_flags & PACKET_FLAG_ACTION_NAME:
            out.write((self.action_name + "\0").encode("ascii"))

        if packet_flags & PACKET_FLAG_ACTION_HASH:
            out.write(struct.pack(">I", self.action_hash))

        if packet_flags & PACKET_FLAG_BCK_FRAME:
            out.write(struct.pack("b", self.bck_frame))

        if packet_flags & PACKET_FLAG_BCK_RATE:
            out.write(struct.pack("b", self.bck_rate))

        if packet_flags & PACKET_FLAG_TRACK_WEIGHT_0:
            out.write(struct.pack("b", self.track_weights[0]))

        if packet_flags & PACKET_FLAG_TRACK_WEIGHT_1:
            out.write(struct.pack("b", self.track_weights[1]))

        if packet_flags & PACKET_FLAG_TRACK_WEIGHT_2:
            out.write(struct.pack("b", self.track_weights[2]))

        if packet_flags & PACKET_FLAG_TRACK_WEIGHT_3:
            out.write(struct.pack("b", self.track_weights[3]))

        return out.getbuffer().tobytes(), packet_flags


# ----------------------------------------------------------------------------------------------------------------------
# Main functionality

def record_gst_from_dolphin(output_folder_path: str, addr_gst_recorder_info_ptr: int = ADDR_GST_RECORDER_INFO_PTR):
    pass


def sleep_millis(millis: int):
    time.sleep(millis / 1000)

from __future__ import annotations
from io import BytesIO

import sys
import time
import os.path
import struct
import dolphin_memory_engine

__all__ = ["Vec3", "RawGhostData"]


def validate_ptr(name: str):
    def inner(func):
        def wrapper(*args, **kwargs):
            if args[0] == 0:
                raise IndexError(f"{name} is NULL!")
            return func(*args, **kwargs)
        return wrapper
    return inner


UNINITIALIZED_GAME_ID = "\0\0\0\0"
VALID_GAME_IDS = ["RMGP", "RMGE", "RMGJ", "RMGK", "RMGW",
                  "SB4P", "SB4E", "SB4J", "SB4K", "SB4W"]


# ----------------------------------------------------------------------------------------------------------------------
# GstRecorderInfo accessors for Dolphin
# The following values should be in sync with the respective information contained within "GstRecord.h"!

RECORDER_MODE_WAITING = 0
RECORDER_MODE_PREPARING = 1
RECORDER_MODE_RECORDING = 2
RECORDER_MODE_STOPPED = 3

GHOST_TYPE_INVALID = -1
GHOST_TYPE_GHOST_ATTACK_GHOST = 0
GHOST_TYPE_PICHAN_RACER = 1
GHOST_TYPE_GHOST_PLAYER_MARIO = 2
GHOST_TYPE_GHOST_PLAYER_LUIGI = 3

GHOST_FILE_FORMATS = [
    "GhostAttackGhostData{1:02d}.gst",
    "PichanRacerRaceData{1:03d}.gst",
    "{0}.gst",
    "{0}Luigi.gst",
]

GHOST_TYPE_NAMES = [
    "GhostAttackGhost",
    "PichanRacer",
    "GhostPlayer (Mario)",
    "GhostPlayer (Luigi)",
]

ADDR_GST_RECORDER_INFO_PTR = 0x80003FF8
OFFSET_UPDATE_FRAME = 0x00
OFFSET_RECORDER_MODE = 0x04
OFFSET_STAGE_NAME_PTR = 0x08
OFFSET_STAGE_SCENARIO = 0x0C
OFFSET_IS_SMG2 = 0x10
OFFSET_GST_DATA_TYPE = 0x14
OFFSET_GST_DATA_STRUCT = 0x18
GST_DATA_STRUCT_SIZE = 0x2E


def dolphin_get_game_id() -> str:
    """
    Reads and returns the game's ID name from Dolphin's emulated game memory.

    :return: the game's ID name.
    """
    return dolphin_memory_engine.read_bytes(0, 4).decode("ascii")


@validate_ptr("s32*")
def dolphin_read_s32(ptr: int) -> int:
    """
    Reads a signed 32-bit integer at the specified address in Dolphin's emulated game memory and returns it.

    :param ptr: the pointer to the signed 32-bit integer.
    :return: the value read.
    """
    return dolphin_memory_engine.read_word(ptr)


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


@validate_ptr("bool*")
def dolphin_read_bool(ptr: int) -> bool:
    """
    Reads a boolean value at the specified address in Dolphin's emulated game memory and returns it.

    :param ptr: the pointer to the boolean value.
    :return: the value read.
    """
    return dolphin_memory_engine.read_byte(ptr) != 0


@validate_ptr("char*")
def dolphin_read_cstring(ptr: int, encoding: str = "ascii") -> str:
    """
    Reads a C-string at the specified address in Dolphin's emulated game memory and returns it.

    :param ptr: the pointer to the C-string.
    :param encoding: the string's encoding.
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
    return chars.decode(encoding)


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
    return dolphin_read_s32(gst_recorder_info_ptr + OFFSET_RECORDER_MODE)


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
def dolphin_read_stage_scenario(gst_recorder_info_ptr: int) -> int:
    """
    Reads the currently selected scenario associated with the GstRecorderInfo in Dolphin's emulated game memory and
    returns it.

    :param gst_recorder_info_ptr: the pointer to GstRecorderInfo.
    :return: the value read.
    """
    return dolphin_read_s32(gst_recorder_info_ptr + OFFSET_STAGE_SCENARIO)


@validate_ptr("GstRecorderInfo*")
def dolphin_read_is_smg2(gst_recorder_info_ptr: int) -> bool:
    """
    Returns ``True`` if the GstRecordInfo in Dolphin's emulated game memory is for SMG2, otherwise ``False``.

    :param gst_recorder_info_ptr: the pointer to GstRecorderInfo.
    :return: True if the game is SMG2, otherwise False.
    """
    return dolphin_read_bool(gst_recorder_info_ptr + OFFSET_IS_SMG2)


@validate_ptr("GstRecorderInfo*")
def dolphin_read_ghost_data_type(gst_recorder_info_ptr: int) -> int:
    """
    Reads the ghost data type associated with the GstRecorderInfo in Dolphin's emulated game memory and returns it.

    :param gst_recorder_info_ptr: the pointer to GstRecorderInfo.
    :return: the value read.
    """
    return dolphin_read_s32(gst_recorder_info_ptr + OFFSET_GST_DATA_TYPE)


@validate_ptr("GstRecorderInfo*")
def dolphin_read_ghost_data_struct(gst_recorder_info_ptr: int, dest: RawGhostData):
    """
    Reads the raw ghost data associated with the GstRecorderInfo in Dolphin's emulated game memory.

    :param gst_recorder_info_ptr: the pointer to GstRecorderInfo.
    :param dest: the ghost data to be overwritten.
    """
    raw = dolphin_memory_engine.read_bytes(gst_recorder_info_ptr + OFFSET_GST_DATA_STRUCT, GST_DATA_STRUCT_SIZE)

    pos_f_x, pos_f_y, pos_f_z = struct.unpack_from(">3f", raw, 0x00)
    pos_i_x, pos_i_y, pos_i_z = struct.unpack_from(">3h", raw, 0x0C)
    rot_x, rot_y, rot_z = struct.unpack_from("3b", raw, 0x12)
    scale_x, scale_y, scale_z = struct.unpack_from("3b", raw, 0x15)
    vel_x, vel_y, vel_z = struct.unpack_from("3b", raw, 0x18)
    bck_name_ptr, bck_hash = struct.unpack_from(">2I", raw, 0x1C)
    use_bck_hash, use_pos_float = struct.unpack_from("2?", raw, 0x24)
    bck_frame, weight_0, weight_1, weight_2, weight_3, bck_rate = struct.unpack_from(">h5b", raw, 0x26)

    dest.position_f.x = pos_f_x
    dest.position_f.y = pos_f_y
    dest.position_f.z = pos_f_z
    dest.position_i.x = pos_i_x
    dest.position_i.y = pos_i_y
    dest.position_i.z = pos_i_z
    dest.rotation.x = rot_x
    dest.rotation.y = rot_y
    dest.rotation.z = rot_z
    dest.scale.x = scale_x
    dest.scale.y = scale_y
    dest.scale.z = scale_z
    dest.velocity.x = vel_x
    dest.velocity.y = vel_y
    dest.velocity.z = vel_z

    dest.action_name = dolphin_read_cstring(bck_name_ptr, encoding="shift_jisx0213")
    dest.action_hash = bck_hash

    dest.use_action_hash = use_bck_hash
    dest.use_position_float = use_pos_float

    dest.bck_frame = bck_frame
    dest.track_weights[0] = weight_0
    dest.track_weights[1] = weight_1
    dest.track_weights[2] = weight_2
    dest.track_weights[3] = weight_3
    dest.bck_rate = bck_rate


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


class Vec3:
    """Represents a simple 3D vector."""
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self.x = x
        self.y = y
        self.z = z

    def set(self, other: Vec3):
        self.x = other.x
        self.y = other.y
        self.z = other.z

    def __eq__(self, other):
        if type(other) != Vec3:
            return False
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __ne__(self, other):
        if type(other) != Vec3:
            return True
        return self.x != other.x or self.y != other.y or self.z != other.z


class RawGhostData:
    """Holds raw ghost data generated by the game. The data can be packed into smaller GhostPacket chunks."""
    def __init__(self, ghost_data_type: int, is_smg2: bool):
        self.ghost_data_type = ghost_data_type
        self.is_smg2 = is_smg2

        self.position_i = Vec3()
        self.position_f = Vec3()
        self.rotation = Vec3()
        self.scale = Vec3()
        self.velocity = Vec3()
        self.action_name = ""
        self.action_hash = 0
        self.use_action_hash = False
        self.use_position_float = False
        self.bck_frame = 0
        self.track_weights = [0, 0, 0, 0]
        self.bck_rate = 0

        self._packet_flags_ = 0

    def compare_and_update(self, other: RawGhostData):
        """
        Compares its ghost data with other ghost data. If some value doesn't match, the packet flags will be updated
        accordingly and the value will be replaced with the other's new value.

        :param other: the other ghost data.
        """
        # No object seems to use velocity, so it won't be updated here

        self._packet_flags_ = 0

        self.use_position_float = other.use_position_float
        self.use_action_hash = other.use_action_hash

        if self.is_smg2 and self.use_position_float:
            if self.position_f != other.position_f:
                self._packet_flags_ |= PACKET_FLAG_POSITION_FLOAT
                self.position_f.set(other.position_f)
        else:
            if self.position_i != other.position_i:
                self._packet_flags_ |= PACKET_FLAG_POSITION_INT
                self.position_i.set(other.position_i)

        if self.rotation.x != other.rotation.x:
            self._packet_flags_ |= PACKET_FLAG_ROTATION_X
            self.rotation.x = other.rotation.x

        if self.rotation.y != other.rotation.y:
            self._packet_flags_ |= PACKET_FLAG_ROTATION_Y
            self.rotation.y = other.rotation.y

        if self.rotation.z != other.rotation.z:
            self._packet_flags_ |= PACKET_FLAG_ROTATION_Z
            self.rotation.z = other.rotation.z

        if self.scale != other.scale:
            self._packet_flags_ |= PACKET_FLAG_SCALE
            self.scale.set(other.scale)

        if self.use_action_hash:
            if self.action_hash != other.action_hash:
                self._packet_flags_ |= PACKET_FLAG_ACTION_HASH
                self.action_hash = other.action_hash
        else:
            if self.action_name != other.action_name:
                self._packet_flags_ |= PACKET_FLAG_ACTION_NAME
                self.action_name = other.action_name

        if self.bck_frame != other.bck_frame:
            self._packet_flags_ |= PACKET_FLAG_BCK_FRAME
            self.bck_frame = other.bck_frame

        if self.track_weights[0] != other.track_weights[0]:
            self._packet_flags_ |= PACKET_FLAG_TRACK_WEIGHT_0
            self.track_weights[0] = other.track_weights[0]

        if self.track_weights[1] != other.track_weights[1]:
            self._packet_flags_ |= PACKET_FLAG_TRACK_WEIGHT_1
            self.track_weights[1] = other.track_weights[1]

        if self.track_weights[2] != other.track_weights[2]:
            self._packet_flags_ |= PACKET_FLAG_TRACK_WEIGHT_2
            self.track_weights[2] = other.track_weights[2]

        if self.track_weights[3] != other.track_weights[3]:
            self._packet_flags_ |= PACKET_FLAG_TRACK_WEIGHT_3
            self.track_weights[3] = other.track_weights[3]

        if self.bck_rate != other.bck_rate:
            self._packet_flags_ |= PACKET_FLAG_BCK_RATE
            self.bck_rate = other.bck_rate

    def pack(self) -> tuple[bytes, int]:
        """
        Packs the ghost data into a smaller GhostPacket chunk according to the packet flags. The resulting packed
        GhostPacket bytes and flags will be returned.

        :return: a tuple consisting of the packed GhostPacket and flags.
        """
        out = BytesIO()

        packet_flags = self._packet_flags_

        if packet_flags & PACKET_FLAG_POSITION_FLOAT:
            out.write(struct.pack(">3f", self.position_f.x, self.position_f.y, self.position_f.z))
        elif packet_flags & PACKET_FLAG_POSITION_INT:
            out.write(struct.pack(">3h", self.position_i.x, self.position_i.y, self.position_i.z))

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
            out.write(struct.pack(">h", self.bck_frame))

        if self.is_smg2 and packet_flags & PACKET_FLAG_BCK_RATE:
            out.write(struct.pack("b", self.bck_rate))

        if packet_flags & PACKET_FLAG_TRACK_WEIGHT_0:
            out.write(struct.pack("b", self.track_weights[0]))

        if packet_flags & PACKET_FLAG_TRACK_WEIGHT_1:
            out.write(struct.pack("b", self.track_weights[1]))

        if packet_flags & PACKET_FLAG_TRACK_WEIGHT_2:
            out.write(struct.pack("b", self.track_weights[2]))

        if packet_flags & PACKET_FLAG_TRACK_WEIGHT_3:
            out.write(struct.pack("b", self.track_weights[3]))

        if not self.is_smg2 and packet_flags & PACKET_FLAG_BCK_RATE:
            out.write(struct.pack("b", self.bck_rate))

        return out.getbuffer().tobytes(), packet_flags


# ----------------------------------------------------------------------------------------------------------------------
# Main functionality

def record_gst_from_dolphin(output_folder_path: str, addr_gst_recorder_info_ptr: int = ADDR_GST_RECORDER_INFO_PTR):
    gst_recorder_info_ptr = 0
    recorder_state = RECORDER_MODE_WAITING
    game_id = UNINITIALIZED_GAME_ID

    if os.path.exists(output_folder_path) and not os.path.isdir(output_folder_path):
        print(f"Error! Path '{output_folder_path}' is not a folder!", file=sys.stderr)

    # 2 - Hook to Dolphin and check if game ID is supported
    print("Waiting for Dolphin...")

    while not dolphin_memory_engine.is_hooked():
        sleep_millis(500)
        dolphin_memory_engine.hook()

    while game_id == UNINITIALIZED_GAME_ID:
        sleep_millis(500)
        game_id = dolphin_get_game_id()

    print(f"Hooked to Dolphin, game ID is {game_id}!")

    if game_id not in VALID_GAME_IDS:
        print("WARNING! Detected game's ID does not appear to be SMG1/SMG2, tool may fail!")

    # 3 - Find GstRecorderInfo and wait for recording
    print(f"Searching for GstRecorderInfo* at 0x{addr_gst_recorder_info_ptr:08X}...")

    while gst_recorder_info_ptr == 0:
        sleep_millis(250)
        gst_recorder_info_ptr = dolphin_read_u32(addr_gst_recorder_info_ptr)

    print("Waiting for GstRecordHelper...")

    while recorder_state == RECORDER_MODE_WAITING:
        sleep_millis(50)
        recorder_state = dolphin_read_recorder_mode(gst_recorder_info_ptr)

    if recorder_state == RECORDER_MODE_STOPPED:
        print("Aborted recording! Start again!")
        dolphin_memory_engine.un_hook()
        return

    while recorder_state == RECORDER_MODE_PREPARING:
        recorder_state = dolphin_read_recorder_mode(gst_recorder_info_ptr)

    # 5 - Get general information and prepare output
    stage_name = dolphin_read_stage_name(gst_recorder_info_ptr)
    stage_scenario = dolphin_read_stage_scenario(gst_recorder_info_ptr)
    is_smg2 = dolphin_read_is_smg2(gst_recorder_info_ptr)
    data_type = dolphin_read_ghost_data_type(gst_recorder_info_ptr)
    total_frames = 0

    if data_type == GHOST_TYPE_INVALID:
        print("Invalid ghost type!")
        dolphin_memory_engine.un_hook()
        return

    print(f"Started recording for {GHOST_TYPE_NAMES[data_type]} in {stage_name} Star {stage_scenario}!")

    gst_folder_path = os.path.join(output_folder_path, stage_name)
    gst_file_name = GHOST_FILE_FORMATS[data_type].format(stage_name, stage_scenario)
    gst_file_path = os.path.join(gst_folder_path, gst_file_name)
    os.makedirs(gst_folder_path, exist_ok=True)

    with open(gst_file_path, "wb") as f:
        writing_packet = RawGhostData(data_type, is_smg2)
        reading_packet = RawGhostData(data_type, is_smg2)

        current_frame = dolphin_read_update_frame(gst_recorder_info_ptr)
        next_frame = (current_frame + 1) & 0xFFFFFFFF

        while recorder_state == RECORDER_MODE_RECORDING:
            # Get current update frame
            current_frame = dolphin_read_update_frame(gst_recorder_info_ptr)

            if current_frame == ((next_frame - 1) & 0xFFFFFFFF):
                continue
            elif current_frame != next_frame:
                print("Aborted recording due to a synchronization error!")
                dolphin_memory_engine.un_hook()
                return

            next_frame = (current_frame + 1) & 0xFFFFFFFF

            # Still recording?
            recorder_state = dolphin_read_recorder_mode(gst_recorder_info_ptr)

            if recorder_state != RECORDER_MODE_RECORDING:
                break

            # Read packet info from memory
            dolphin_read_ghost_data_struct(gst_recorder_info_ptr, reading_packet)
            writing_packet.compare_and_update(reading_packet)

            packet_bytes, packet_flags = writing_packet.pack()
            packet_index = total_frames & 0xFF
            packet_size = len(packet_bytes) + 4

            f.write(struct.pack(">2BH", packet_index, packet_size, packet_flags))
            f.write(packet_bytes)

            total_frames += 1

        print("Stopped recording!")

    dolphin_memory_engine.un_hook()

    print(f"Dumped {total_frames} ghost frames (approx. {total_frames // 60} seconds) to '{gst_file_path}'.")


def sleep_millis(millis: int):
    time.sleep(millis / 1000)

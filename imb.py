import datetime
import typing
import imb_table


def get_first_serial() -> int:
    """
    Generate a 6-digit serial number for an intelligent mail barcode.
    The first 2 digits are the last 2 digits of the julian date, and the next 4
    are serial and the next number to use is stored in a temporary file.
    This will break if over 10000 serials are requested in a day
    """
    # Last 2 digits of the ordinal day
    date = datetime.datetime.utcnow().timetuple().tm_yday % 100
    try:
        serial_file = open("next_serial.txt")
        next_serial = int(serial_file.read().strip())
        if next_serial // 10000 == date:
            first_idx = next_serial % 10000
        else:
            first_idx = 0
    except (ValueError, IndexError, FileNotFoundError):
        first_idx = 0

    return date * 10000 + first_idx


def write_current_serial(current_serial: int):
    serial_file = open("next_serial.txt", "w")
    serial_file.write(format(current_serial, "06d"))


def _format_routing(routing: str) -> int:
    if len(routing) == 0:
        return 0
    elif len(routing) == 5:
        return int(routing) + 1
    elif len(routing) == 9:
        return int(routing) + 100000 + 1
    elif len(routing) == 11:
        return int(routing) + 1000000000 + 100000 + 1
    else:
        raise ValueError("Routing code must be 0, 5, 9, or 11 characters")


def _generate_crc(data_int: int) -> int:
    """
    Do the weird USPS CRC11 which requires precisely 102 bits in
    This is done by copying USPS code which is not very optimal
    """
    data = data_int.to_bytes(13, "big")
    poly = 0xF35
    fcs = 0x7FF

    current = data[0] << 5
    for _ in range(6):
        if (fcs ^ current) & 0x400:
            fcs = (fcs << 1) ^ poly
        else:
            fcs = fcs << 1
        fcs &= 0x7FF
        current <<= 1

    for current in data[1:]:
        current <<= 3
        for _ in range(8):
            if (fcs ^ current) & 0x400:
                fcs = (fcs << 1) ^ poly
            else:
                fcs = fcs << 1
            fcs &= 0x7FF
            current <<= 1

    return fcs


def _generate_codewords(data: int, crc: int) -> typing.List[int]:
    codewords = []
    codewords.append(data % 636)
    data //= 636
    for i in range(8):
        codewords.append(data % 1365)
        data //= 1365
    codewords.append(data)

    codewords.reverse()
    codewords[0] += ((crc >> 10) & 1) * 659
    codewords[9] *= 2
    return codewords


def _generate_characters(codewords: typing.List[int], crc: int) -> typing.List[int]:
    characters = []
    for idx, codeword in enumerate(codewords):
        xor = ((crc >> idx) & 1) * 0x1FFF
        characters.append(imb_table.CHARACTER_TABLE[codeword] ^ xor)

    return characters


def _get_bit(characters: typing.List[int], character: int, bit: int) -> int:
    return (characters[character] >> bit) & 1


def _generate_bars(characters: typing.List[int]) -> str:
    s = ""
    for bar in range(65):
        descender = _get_bit(characters, *imb_table.BAR_TABLE[bar * 2])
        ascender = _get_bit(characters, *imb_table.BAR_TABLE[bar * 2 + 1])
        s = s + "TADF"[descender * 2 + ascender]
    return s


def from_payload(data: int) -> str:
    crc = _generate_crc(data)
    codewords = _generate_codewords(data, crc)
    characters = _generate_characters(codewords, crc)
    return _generate_bars(characters)


def _generate_payload(bi: int, stid: int, mailer: int, serial: int, raw_routing: str):
    if mailer >= 1000000:
        decimal_tracking = int(f"{stid:03d}{mailer:09d}{serial:06d}")
    else:
        # Why are you using this program?
        decimal_tracking = int(f"{stid:03d}{mailer:06d}{serial:09d}")

    payload = _format_routing(raw_routing)

    # ... what the fuck usps
    payload = payload * 10 + (bi // 10)
    payload = payload * 5 + (bi % 10)
    payload = payload * 10**18 + decimal_tracking
    return payload


def generate(bi: int, stid: int, mailer: int, serial: int, raw_routing: str):
    return from_payload(_generate_payload(bi, stid, mailer, serial, raw_routing))

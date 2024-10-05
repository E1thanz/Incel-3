import os
import sys
from multiprocessing.managers import Value


class BIN:
    @staticmethod
    def int_to_unsigned(bits: int, number: int) -> str:
        if bits <= 0:
            raise ValueError(f"the number of bits must be a positive integer")
        MAX_NUM = 2 ** bits
        if number > MAX_NUM - 1 or number < 0:
            raise ValueError(f"the number {number} cannot be both unsigned and contained in {bits} bits")
        return format(number, f'0{bits}b')

    @staticmethod
    def int_to_signed(bits: int, number: int) -> str:
        if bits <= 0:
            raise ValueError(f"the number of bits must be a positive integer")
        MAX_NUM = 2 ** (bits - 1)
        if number > MAX_NUM - 1 or number < -MAX_NUM:
            raise ValueError(f"the number {number} cannot be both signed and contained in {bits} bits")
        if number >= 0:
            return format(number, f'0{bits}b')
        number_as_binary = format(number + (MAX_NUM * 2), f'0{bits}b')
        return number_as_binary

    @staticmethod
    def is_binary(string, bits: int = 0) -> (bool, str):
        if bits == 0 or len(string.lstrip("0")) > bits:
            raise ValueError(f"the number {string} does not fit in {bits} bits")
        return all([character in ["0", "1"] for character in string.lstrip("0").rjust(8, "0")]), string.lstrip("0").rjust(8, "0")


REGISTERS = {f"r{i}": BIN.int_to_unsigned(3, i) for i in range(8)}
CONDITIONS = {"novf": "000", "ovf": "001", "nc": "010", "c": "011", "nmsb": "100", "msb": "101", "nz": "110",
              "z": "111",
              "!overflow": "000", "overflow": "001", "!carry": "010", "carry": "011", "!msb": "100", "!zero": "110",
              "zero": "111",
              "!=": "110", "=": "111", "<": "010", ">=": "011", ">=0": "100", "<0": "101",
              "!ovf": "000", "!c": "010", "!z": "110", "eq": "111", "neq": "110"}
LABELS = {}
DEFINITIONS = {}


class PARAMETERS:

    @staticmethod
    def Register(value: str, line: int, instruction: str) -> str:
        try:
            return REGISTERS[value]
        except KeyError:
            exit(f"Invalid register on line {line} for instruction {instruction}, possible registers are: \n{REGISTERS.keys()}")

    @staticmethod
    def Condition(value: str, line: int, instruction: str) -> str:
        try:
            return CONDITIONS[value]
        except KeyError:
            exit(f"Invalid condition on line {line} for instruction {instruction}, possible conditions are: \n{CONDITIONS.keys()}")

    @staticmethod
    def Single(value: str, line: int, instruction: str) -> str:
        if not BIN.is_binary(value, 1)[0]:
            exit(f"Invalid single on line {line} for instruction {instruction}, a single is either a 0 or a 1")
        return value

    @staticmethod
    def Label(value: str, line: int, instruction: str) -> str:
        if value not in LABELS:
            exit(f"Invalid label on line {line} for instruction {instruction}")
        return LABELS[value][0]

    @staticmethod
    def Immediate(value: str, bits: int, line: int, instruction: str) -> str:

        if value in DEFINITIONS:
            value = DEFINITIONS[value]

        # if value is in binary form
        if value.startswith("0b"):
            try:
                if not (redid_value := BIN.is_binary(value[2:], bits))[0]:
                    exit(f"Non binary value given in a binary form immediate on line {line} for instruction {instruction}, a binary number can only have 0s and 1s")
                return redid_value[1]
            except ValueError as exception:
                exit(f"Invalid binary immediate on line {line} for instruction {instruction}, error: \n{repr(exception)}")

        # if value is in hex form
        if value.startswith("0x"):
            hex_digits = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f')

            # if any digit in the number is not a hex digit
            if any([digit.lower() not in hex_digits for digit in value[2:]]):
                exit(
                    f"Non hexadecimal digit in a hexadecimal form immediate on line {line} for instruction {instruction}, a hex number can only have: \n{hex_digits}")

            return BIN.int_to_unsigned(bits, int(value[2:], 16))

        # differentiate between positive and negative decimal numbers
        if value.startswith("-"):
            conversion_function = BIN.int_to_signed
            value = value[1:]
        else:
            conversion_function = BIN.int_to_unsigned

        if not value.isdigit():
            exit(f"Non decimal digit in a decimal form immediate on line {line} for instruction {instruction}")

        try:
            return conversion_function(bits, int(value))
        except ValueError as exception:
            exit(f"Invalid decimal immediate on line {line} for instruction {instruction}, error: \n{repr(exception)}")


INSTRUCTIONS = {"add": ((3, 4),
                        ("00000", PARAMETERS.Register, PARAMETERS.Register, "00", PARAMETERS.Register),
                        ("00000", PARAMETERS.Register, PARAMETERS.Register, PARAMETERS.Single, "0", PARAMETERS.Register)),
                "sub": ((3, 4),
                        ("00001", PARAMETERS.Register, PARAMETERS.Register, "00", PARAMETERS.Register),
                        ("00001", PARAMETERS.Register, PARAMETERS.Register, PARAMETERS.Single, "0", PARAMETERS.Register)),
                "and": ((3,),
                        ("00010", PARAMETERS.Register, PARAMETERS.Register, "00", PARAMETERS.Register)),
                "or": ((3,),
                       ("00011", PARAMETERS.Register, PARAMETERS.Register, "00", PARAMETERS.Register)),
                "xor": ((3,),
                        ("00100", PARAMETERS.Register, PARAMETERS.Register, "00", PARAMETERS.Register)),
                "bsh": ((4, 5),
                        (
                            "00101", PARAMETERS.Register, PARAMETERS.Register, PARAMETERS.Single, "0", PARAMETERS.Register),
                        ("00101", PARAMETERS.Register, PARAMETERS.Register, PARAMETERS.Single, PARAMETERS.Single,
                         PARAMETERS.Register)),
                "mld": ((2, 3),
                        ("00110", PARAMETERS.Register, "00000", PARAMETERS.Register),
                        ("00110", PARAMETERS.Register,
                         lambda value, line, instruction: PARAMETERS.Immediate(value, 5, line, instruction),
                         PARAMETERS.Register)),
                "mst": ((2, 3),
                        ("00111", PARAMETERS.Register, PARAMETERS.Register, "00000"),
                        ("00111", PARAMETERS.Register, PARAMETERS.Register,
                         lambda value, line, instruction: PARAMETERS.Immediate(value, 5, line, instruction))),
                "jmp": ((1,),
                        ("0100", PARAMETERS.Label)),
                "cal": ((1,),
                        ("0101", PARAMETERS.Label)),
                "ret": ((0,),
                        ("0110000000000000",)),
                "rdp": ((0, 1),
                        ("0110100000000000",),
                        ("011010000000000", PARAMETERS.Single)),
                "prd": ((1, 2),
                        ("01110", PARAMETERS.Condition, "00000000"),
                        ("01110", PARAMETERS.Condition, "0000000", PARAMETERS.Single)),
                "hlt": ((0,),
                        ("0111100000000000",)),
                "bsi": ((3, 4),
                        ("10000", PARAMETERS.Register, "000", PARAMETERS.Single, "0", lambda value, line, instruction: PARAMETERS.Immediate(value, 3, line, instruction)),
                        ("10000", PARAMETERS.Register, "000", PARAMETERS.Single, PARAMETERS.Single, lambda value, line, instruction: PARAMETERS.Immediate(value, 3, line, instruction))),
                "ani": ((2,),
                        ("10001", PARAMETERS.Register, lambda value, line, instruction: PARAMETERS.Immediate(value, 8, line, instruction))),
                "ori": ((2,),
                        ("10010", PARAMETERS.Register, lambda value, line, instruction: PARAMETERS.Immediate(value, 8, line, instruction))),
                "xri": ((2,),
                        ("10011", PARAMETERS.Register, lambda value, line, instruction: PARAMETERS.Immediate(value, 8, line, instruction))),
                "tst": ((2,),
                        ("10100", PARAMETERS.Register, lambda value, line, instruction: PARAMETERS.Immediate(value, 8, line, instruction))),
                "adi": ((2,),
                        ("10101", PARAMETERS.Register, lambda value, line, instruction: PARAMETERS.Immediate(value, 8, line, instruction))),
                "ldi": ((2,),
                        ("10110", PARAMETERS.Register, lambda value, line, instruction: PARAMETERS.Immediate(value, 8, line, instruction))),
                "pst": ((2,),
                        ("10111", PARAMETERS.Register, "000", lambda value, line, instruction: PARAMETERS.Immediate(value, 5, line, instruction))),
                "pld": ((2,),
                        ("11000", PARAMETERS.Register, "000", lambda value, line, instruction: PARAMETERS.Immediate(value, 5, line, instruction)))
                }


def main():
    # Check if the correct number of arguments is provided
    if len(sys.argv) != 3:
        exit("Usage: python LineAssembler.py <Line> <Index>")  # Exit the program with an error code

    input_line = sys.argv[1]  # The first argument after the script name
    line_index = sys.argv[2]

    assembled_instruction = ""

    if input_line.startswith("//") or input_line.startswith("#") or input_line.startswith(";"):
        exit("")

    if input_line.startswith("define"):
        # ADD CHECKS TO MAKE SURE THE DEFINE IS CORRECTLY WRITTEN
        exit("")

    if input_line.startswith(">"):
        try:
            int(input_line[1:])
        except ValueError:
            exit(f"Invalid decimal for page declaration on line {line_index}")
        print(input_line)

    split_line = input_line.strip().split(" ")

    if split_line[0] not in INSTRUCTIONS:
        exit(f"Instruction {split_line[0]} is not a valid instruction")

    index = 0
    for item in INSTRUCTIONS[split_line[0]]:
        if callable(item):
            assembled_instruction += item(split_line[index].lower(), index, split_line[0])
            index += 1
        else:
            assembled_instruction += split_line[index]


if __name__ == "__main__":
    main()

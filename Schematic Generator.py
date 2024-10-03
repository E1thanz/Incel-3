import mcschematic
import sys


def main():
    # Check if the correct number of arguments is provided
    if len(sys.argv) != 2:
        exit("Usage: python Assembler.py <assemblyFile>")  # Exit the program with an error code

    input_file = sys.argv[1]  # The first argument after the script name

    schem = mcschematic.MCSchematic()
    # Now you can open and process the file
    try:
        with open(input_file, 'r') as assembly_file:
            x, z = 0, 0
            page = ["0000000000000000" for _ in range(32)]
            in_page_index = 0
            for index, line in enumerate(assembly_file):
                if line.startswith("//") or line.startswith("#") or line.startswith(";"):
                    continue
                if line.startswith(">"):
                    for i in range(16):
                        compacted = [page[i+16][8:], page[i+16][:8], page[i][8:], page[i][:8]]
                        barrel_values = ["".join([compacted[j][i] for j in range(4)]) for i in range(8)]
                        for y in range(8):
                            schem.setBlock((x - 2*i, -y*2 - 1, z), "minecraft:magenta_concrete" if int(barrel_values[y], 2) == 0 else mcschematic.BlockDataDB.BARREL.fromSS(int(barrel_values[y], 2)))
                    page_number = int(line[1:])
                    x = 0 if page_number % 2 == 0 else -32
                    z = 2 * (page_number // 2)
                    in_page_index = 0
                    page = ["0000000000000000" for _ in range(32)]
                    continue
                if "//" in line:
                    line = line.split(" //")[0]
                elif "#" in line:
                    line = line.split(" #")[0]
                elif ";" in line:
                    line = line.split(" ;")[0]
                page[in_page_index] = line
                in_page_index += 1
    except FileNotFoundError:
        exit(f"Error: File '{input_file}' not found")

    schem.save("./", "program", mcschematic.Version.JE_1_20_PRE_RELEASE_4)


if __name__ == "__main__":
    main()

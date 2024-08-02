
# Explaination of core structures

Creating, accessing, modifying, or deleting a process involves manipulating these data structures.

`_EPROCESS` contains the `_PEB` and the `_KPROCESS`.

The general description of what they are doing:
- `_EPROCESS`: Contains bookkeeping data structures.
- `_KPROCESS`: A smaller structure compared to `_EPROCESS`, containing machine-dependent fields like `CR3`.
- `_PEB`: The user-mode data structure containing information like the heap, loaded DLLs, etc.




## Practical Demonstration

In the demonstration, we're connected to a `Windows 8.1` machine. Commands like `!process 0 0` will be used to display the processes running on the system.

We are going to make a small C++ program and debug on the function `printf` or `GetCommandLine();` (i don't know yet)


Windbg commands used:

```
dt nt!_eprocess 
```


In the video the highlighting was:
the ActiveProcesssLinks (the offset +0x0b8 in Windows 8.1, offset +0x448 in windows 11)
and the Peb (the offset +0x140 in Windows 8.1, offset +0x550 in windows 11) 
```
dc nt!psactiveprocesshead $$ will list the current process head 
```

The answer in the nt!psactiveprocesshead will containe the PE register


```bash
grep -i /tmp/debugging-dt\!_EPROCESS.TXT -e 'ActiveProcessLinks' -e 'peb' -e 'kd>'
0: kd> dt _eprocess
   +0x448 ActiveProcessLinks : _LIST_ENTRY
   +0x550 Peb              : Ptr64 _PEB
```


### ActiveProcesssLinks

So let's calculate the current ActiveProcesssLinks:

Windows 8.1:
```wds
?8546c0f8 - 0b8
$$ Evaluate expression: 2236006464 = 00000000`8546c040
$$ 8546c0f8 - 0b8
```
Windows 11:
```
? poi(nt!psactiveprocesshead) - 0x448
$$ output
$$ Evaluate expression: -140702228156352 = ffff8008`35abf040
```

### Using eprocess to enumerate the ImageFileName


```
dt nt!_EPROCESS -l ActiveProcessLinks.Flink ImageFileName (poi(nt!psactiveprocesshead) - 0x448)
ActiveProcessLinks.Flink at 0xffff8008`35abf040
---------------------------------------------
   +0x448 ActiveProcessLinks :  [ 0xffff8008`35bdf4c8 - 0xfffff803`06037e60 ]
   +0x5a8 ImageFileName : [15]  "System"

ActiveProcessLinks.Flink at 0xffff8008`35bdf080
...
```
[The full output in this link](./output-of-psactiveprocesshead.txt)


### attach to the peb

```
0: kd> !peb
PEB NULL...
0: kd> !process 0 0 explorer.exe
PROCESS ffff80083ef52080
    SessionId: 1  Cid: 199c    Peb: 00759000  ParentCid: 1928
    DirBase: 17b81c000  ObjectTable: 00000000  HandleCount:   0.
    Image: explorer.exe

PROCESS ffff8008415510c0
    SessionId: 1  Cid: 0260    Peb: 00c20000  ParentCid: 0de4
    DirBase: 109909000  ObjectTable: ffffac8abb9c7780  HandleCount: 4981.
    Image: explorer.exe

0: kd> .process /r /p ffff8008415510c0
Implicit process is now ffff8008`415510c0
.cache forcedecodeuser done
Loading User Symbols
................................................................
................................................................
................................................................
................................................................
................................................................
.....................

************* Symbol Loading Error Summary **************
Module name            Error
SharedUserData         No error - symbol load deferred
				Symbol loading has been deferred because this symbol is not needed
				at this time. Use reload /f to force load symbols.

0: kd> !peb
PEB at 0000000000c20000
    InheritedAddressSpace:    No
    ReadImageFileExecOptions: No
    BeingDebugged:            Yes
    ImageBaseAddress:         00007ff68e7a0000
    NtGlobalFlag:             0
    NtGlobalFlag2:            0
    Ldr                       00007ffd7f0b6440
    Ldr.Initialized:          Yes
    Ldr.InInitializationOrderModuleList: 0000000000ff23e0 . 00000000201dd960
    Ldr.InLoadOrderModuleList:           0000000000ff2560 . 00000000201dd940
    Ldr.InMemoryOrderModuleList:         0000000000ff2570 . 00000000201dd950
                    Base TimeStamp                     Module
            7ff68e7a0000 5b4afbdf Jul 15 09:46:39 2018 C:\Windows\explorer.exe
....
    SubSystemData:     00007ffd7464b6e0
    ProcessHeap:       0000000000ff0000
    ProcessParameters: 0000000000ff68e0
    CurrentDirectory:  'C:\WINDOWS\system32\'
    WindowTitle:  'Microsoft.Windows.Explorer'
    ImageFile:    'C:\Windows\explorer.exe'
    CommandLine:  'C:\Windows\explorer.exe'
    DllPath:      '< Name not readable >'
    Environment:  0000000003c859c0
        =::=::\
        ALLUSERSPROFILE=C:\ProgramData
....
```
[The full output in this link](./output-of-teb-in-process.txt)


# What is CR3 

## What is CR3 in the context of Windows?

In the context of Windows, CR3 is a control register in the CPU that holds the physical address of the Page Directory Base Register (PDBR). This address points to the base of the page directory used in translating virtual addresses to physical addresses. The CR3 register is essential for the memory management unit (MMU) to correctly map and access memory pages. It plays a key role in context switching, as each process has its own page directory, and switching the CR3 value changes the active page directory, thereby switching the memory context.

## What is CR3 in the CPU context?

In the CPU context, CR3 is one of the control registers used in the x86 architecture. It is specifically used to point to the page directory or the extended page table in systems using paging for memory management. The CR3 register contains the physical address of the Page Directory Base Register (PDBR) in systems using traditional paging, or the physical address of the Page Map Level 4 Table (PML4T) in systems using the x86-64 Long Mode. This register is critical for virtual memory translation and efficient memory management, as it allows the CPU to translate virtual addresses into physical addresses during memory accesses. CR3 remains in use in 64-bit systems, maintaining its role in pointing to the PML4T, an essential part of the hierarchical paging structure used in 64-bit mode.

| Bit            | Label | Description                 | [PAE](https://wiki.osdev.org/Physical_Address_Extension) | [Long Mode](https://wiki.osdev.org/X86-64) |
|----------------|-------|-----------------------------|----------------------------------------------------------|--------------------------------------------------------------------------|
| 3              | PWT   | Page-level Write-Through    | (Not used)                                               | (Not used if bit 17 of CR4 is 1)                                         |
| 4              | PCD   | Page-level Cache Disable    | (Not used)                                               | (Not used if bit 17 of CR4 is 1)                                         |
| 12-31 (63)     | PDBR  | Page Directory Base Register| Base of PDPT                                             | Base of PML4T/PML5T                                                      |


# Explaination of core structures

Creating, accessing, modifying, or deleting a process involves manipulating these data structures.

`_EPROCESS` contains the `_PEB` and the `_KPROCESS`.

The general description of what they are doing:
- `_EPROCESS`: Contains bookkeeping data structures.
- `_KPROCESS`: A smaller structure compared to `_EPROCESS`, containing machine-dependent fields like `CR3`.
- `_PEB`: The user-mode data structure containing information like the heap, loaded DLLs, etc.




## Practical Demonstration

In the demonstration, we're connected to a `Windows 8.1` machine. Commands like `!process 0 0` will be used to display the processes running on the system.

WE are going to make a small C++ program and debug on the function `printf` or `GetCommandLine();` (i don't know yet)


Windbg commands used:

```
dt nt!_eprocess 
$$ highlighting the ActiveProcesssLinks (the offset +0x0b8 in Windows 8.1)
$$ highlighting the Peb (the offset +0x140 in Windows 8.1) 

dc nt!psactiveprocesshead $$ will list the current process head 
$$ The answer in the nt!psactiveprocesshead will containe the PE register
```



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

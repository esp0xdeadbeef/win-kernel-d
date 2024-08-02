# What is CR3 in the context of Windows?

In the context of Windows, CR3 is a control register in the CPU that holds the physical address of the Page Directory Base Register (PDBR). This address points to the base of the page directory used in translating virtual addresses to physical addresses. The CR3 register is essential for the memory management unit (MMU) to correctly map and access memory pages. It plays a key role in context switching, as each process has its own page directory, and switching the CR3 value changes the active page directory, thereby switching the memory context.

# What is CR3 in the CPU context?

In the CPU context, CR3 is one of the control registers used in the x86 architecture. It is specifically used to point to the page directory or the extended page table in systems using paging for memory management. The CR3 register contains the physical address of the Page Directory Base Register (PDBR) in systems using traditional paging, or the physical address of the Page Map Level 4 Table (PML4T) in systems using the x86-64 Long Mode. This register is critical for virtual memory translation and efficient memory management, as it allows the CPU to translate virtual addresses into physical addresses during memory accesses. CR3 remains in use in 64-bit systems, maintaining its role in pointing to the PML4T, an essential part of the hierarchical paging structure used in 64-bit mode.

| Bit            | Label | Description                 | [PAE](https://wiki.osdev.org/Physical_Address_Extension) | [Long Mode](https://wiki.osdev.org/X86-64) |
|----------------|-------|-----------------------------|----------------------------------------------------------|--------------------------------------------------------------------------|
| 3              | PWT   | Page-level Write-Through    | (Not used)                                               | (Not used if bit 17 of CR4 is 1)                                         |
| 4              | PCD   | Page-level Cache Disable    | (Not used)                                               | (Not used if bit 17 of CR4 is 1)                                         |
| 12-31 (63)     | PDBR  | Page Directory Base Register| Base of PDPT                                             | Base of PML4T/PML5T                                                      |

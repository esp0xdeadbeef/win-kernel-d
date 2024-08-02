Here is the revised text with the additional column for the "Procedural" and "Equipment" models:

## ISA-88 Structure of the Windows Operating System 

Core research question
https://stackoverflow.com/questions/5790587/what-is-the-difference-between-eprocess-object-and-kprocess-object

Also a nice read:

https://www.ired.team/miscellaneous-reversing-forensics/windows-kernel-internals/interrupt-descriptor-table-idt


### KPROCESS 
**Description** : Represents procedural elements and equipment components in the Windows kernel. 
- **System Files (.sys)** : These are the hardware components.
 
- **Hardware Timers** : Represent the procedural model.
 
- **Memory Management** : Manages both physical and virtual memory.
 
- **Interrupt Handling** : Manages hardware interrupts.
 
- **Processor Control** : Handles CPU scheduling and context switching.

### EPROCESS 
**Description** : Represents the equipment model in the Windows operating system. 
- **Process Unit Level** : Operates within the kernel but is less system-dependent.
 
- **Thread Management** : Manages individual threads within processes.
 
- **Security Context** : Manages access tokens and security descriptors.
 
- **I/O Management** : Manages input and output operations.

### PEB 
**Description** : Represents the process cell, analogous to a control module. 
- **Thread Environment Block (TEB)** : Corresponds to the recipe phase.
 
- **User Program (Stack)** : Represents the control module at the user level.
 
- **Environment Variables** : Contains information about the process environment.
 
- **Loaded Modules** : Manages dynamic link libraries (DLLs) loaded by the process.
 
- **Heap Management** : Handles dynamic memory allocation for the process.

### Table Representation 
| ISA-88 Component | Windows Component                | Description                                                                 | Model Side |
| ---------------- | -------------------------------- | --------------------------------------------------------------------------- | ---------- |
| KPROCESS         | - System files (.sys)            | Contains both procedural and equipment components.                          | Procedural |
|                  | - Hardware timers                | Procedural model.                                                           | Procedural |
|                  | - Memory Management              | Manages physical and virtual memory.                                        | Procedural |
|                  | - Interrupt Handling             | Manages hardware interrupts.                                                | Procedural |
|                  | - Processor Control              | Manages CPU scheduling and context switching.                               | Procedural |
| EPROCESS         | - Process unit level             | Inside the procedural model, less system-dependent but still in the kernel. | Equipment  |
|                  | - Thread Management              | Manages individual threads within processes.                                | Equipment  |
|                  | - Security Context               | Manages access tokens and security descriptors.                             | Equipment  |
|                  | - I/O Management                 | Manages input/output operations.                                            | Equipment  |
| PEB              | - Thread Environment Block (TEB) | Process Cell, recipe phase.                                                 | Equipment  |
|                  | - User Program (Stack)           | Control module; user-level process.                                         | Equipment  |
|                  | - Environment Variables          | Contains information about the environment of the process.                  | Equipment  |
|                  | - Loaded Modules                 | Manages the dynamic link libraries (DLLs) loaded by the process.            | Equipment  |
|                  | - Heap Management                | Manages the dynamic memory allocation for the process.                      | Equipment  |

### Mapping to Windows Components 
 
- **Kernel (ntoskrnl.exe)** : The core of the operating system, managing CPU scheduling, memory management, and hardware interrupts, fitting into the procedural side of the model.
 
- **HAL (Hardware Abstraction Layer)** : Provides an abstraction layer between hardware and the kernel, part of the procedural model.
 
- **EPROCESS Structure** : Contains detailed information about the process, including its threads, security context, memory, and I/O operations, fitting into the equipment model.
 
- **PEB (Process Environment Block)** : Includes the TEB, user program stack, environment variables, loaded modules, and heap management, forming the equipment model for executing user-level processes.

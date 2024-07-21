# Understanding Binaries in Process Architecture

In this presentation, we will discuss binaries, which are vital assets of a process.

## What are Binaries?

Binaries determine the operations within a process's execution. Consider a new job where you're given a list of tasks on paper. Similarly, a binary in a process gives instructions and supports data manipulation.

### Key Points About Binaries:
- **Common Extensions**: Binaries typically have extensions like `.sys`, `.exe`, `.dll`, though any extension is technically possible.
- **Portable Executable (PE) Format**: Most binaries adhere to the PE format, although executing code in a process's space doesn't strictly require PE files.

### Creation of Binaries:
- Binaries are produced by a linker which compiles object files (.obj) generated from source code.
- For detailed processes on compilation and linking, refer to the "Compiling and Linking" presentation in the C programming series.

## Practical Demonstration with Process Explorer

### Process Explorer Tool:
- **Viewing Binaries**: Using Process Explorer, we can view binaries loaded in both user mode and kernel mode.
- **Selecting a Process**: For instance, by selecting `explorer.exe`, you can observe all the binaries loaded into the user mode of Explorer.

### Observations:
- **Common Libraries**: Some binaries like `kernel32.dll` are common across all processes.
- **Process-Specific Binaries**: Certain binaries, such as `explorer.exe`, are unique to their respective processes.

### Kernel Space Exploration:
- **Kernel Binaries**: In the system address space, kernel binaries (mostly `.sys` files) are loaded, which are shared across all processes.
- **Interaction with User Binaries**: Both user and kernel binaries contribute to a process's operations, illustrating the interdependent nature of system architecture.

## Summary

This presentation highlighted another critical asset of processes: binaries. We explored both kernel and user binaries and their roles in defining a process's capabilities and actions.

### Feedback and Further Learning

Please direct all feedback and suggestions to our designated platform. For more personalized assistance or detailed training, follow the provided links. Training options are available online and in direct classroom settings.

Thank you for joining, and we look forward to your participation in future presentations!

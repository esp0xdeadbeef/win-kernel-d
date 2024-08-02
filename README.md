# Reason

1. Why not?
2. Understanding OS structures
3. Getting better with WinDbg and debugging in general

# Research Questions:

1. What is the relationship between the Windows operating system and the ISA-88 standard, and how is it implemented in industrial settings?
2. What are the best practices for effectively using kernel debugging tools on Windows, and what are the critical areas to focus on during debugging?
3. What are the common vulnerabilities in the Windows kernel, and what interfaces are most often targeted by attackers?
4. How does the Windows operating system handle process synchronization and inter-process communication, and what are the security implications?
5. What are the primary differences between Windows kernel and user-mode debugging, and how can these differences impact the debugging process?
6. How can kernel-mode debugging tools be used to identify and mitigate potential security threats within the Windows operating system?
7. What are the most effective methods for exploiting vulnerabilities in the Windows kernel, and how can these exploits be detected and prevented?
8. How do Windows kernel updates and patches address known vulnerabilities, and what are the challenges associated with these updates?
9. What role do hardware abstraction layers play in the security and stability of the Windows operating system, and how can they be leveraged in kernel debugging?
10. How can developers and security professionals collaborate to improve the security of the Windows kernel, and what tools and techniques are most effective in this effort?


# Research Questions answered:

1. What is the relationship between the Windows operating system and the ISA-88 standard, and how is it implemented in industrial settings?

The ISA-88 standard, primarily designed for batch control, is not directly applicable to continuous processes such as those managed by the Windows operating system in industrial settings. I was aware of this limitation before starting this research. However, there are similarities, which I have explained in detail in [S88 structure](S88-structure-improvised-win-kernel.md).

To make a comprehensive comparison, it is essential to consider the ISA-88 (Batch Control) standard alongside other related standards:
 
- [ISA-106 (Procedure Automation for Continuous Process Operations)](https://www.isa.org/standards-and-publications/isa-standards/isa-standards-committees/isa106)
 
- [ISA-99 (Industrial Automation and Control Systems Security)](https://www.isa.org/standards-and-publications/isa-standards/isa-standards-committees/isa99)
 
- [ISA-18 (Instrument Signals and Alarms)](https://www.isa.org/standards-and-publications/isa-standards/isa-standards-committees/isa18)

Combining these standards provides a more complete framework for comparison and implementation in industrial environments.

1. What are the best practices for effectively using kernel debugging tools on Windows, and what are the critical areas to focus on during debugging?


3. What are the common vulnerabilities in the Windows kernel, and what interfaces are most often targeted by attackers?


4. How does the Windows operating system handle process synchronization and inter-process communication, and what are the security implications?


5. What are the primary differences between Windows kernel and user-mode debugging, and how can these differences impact the debugging process?


6. How can kernel-mode debugging tools be used to identify and mitigate potential security threats within the Windows operating system?


7. What are the most effective methods for exploiting vulnerabilities in the Windows kernel, and how can these exploits be detected and prevented?



8. How do Windows kernel updates and patches address known vulnerabilities, and what are the challenges associated with these updates?


9.  What role do hardware abstraction layers play in the security and stability of the Windows operating system, and how can they be leveraged in kernel debugging?


10. How can developers and security professionals collaborate to improve the security of the Windows kernel, and what tools and techniques are most effective in this effort?




# Getting my feet wet

By all means, this is a project I will be working on from time to time.

I'm not a developer, so my git pushes will be not as great as other projects.

To do:

* [ ] Following a long with Windows Internal Process 20 parts
  * [x] [Source](https://www.youtube.com/watch?v=4AkzIbmI3q4&list=PLhx7-txsG6t5i-kIZ_hwJSgZrnka4GXvn&index=1)

    <details><summary>Current status (20 parts with checkboxes)</summary>
    I'm using OCR / Transcripts (e.g. `tesseract ./<image-name>.png summary` or `https://kome.ai/tools/youtube-transcript-generator`) as notes, some parts are with debugging notes.

    * [x] [Part 01](https://youtu.be/4AkzIbmI3q4?si=AAggwGxv8TyE9Dw0)
      - This lesson emphasizes the complexity of seemingly simple tasks in modern operating systems like Windows, encouraging deeper understanding beyond abstractions. It includes a demo on executing a "Hello World" program, observing process creation, and delving into system internals like conhost and process explorer. The goal is to appreciate the underlying mechanisms, gaining programming language-independent knowledge, and enhancing skills in using, administrating, and troubleshooting operating systems.
    * [x] [Part 02](https://youtu.be/xh78GCMP9jY?si=eUkMF8EHDuyujb1K)
      - This lesson explains how Windows manages multitasking through process management, likening processes to independent households in a neighborhood to ensure privacy, space, and non-interference. It covers concepts such as memory allocation, threads, handles, security tokens, and the creation and termination of processes, using Task Manager and Process Explorer for practical demonstrations.
    * [x] [Part 03](https://youtu.be/P7KR2oEPBPw?si=O9bdTsYphRRQhHrm)
      - This presentation delves into process creation in Windows, focusing on the use of the CreateProcess API. It discusses key parameters, particularly the importance of specifying the .exe file name. A demo illustrates starting Notepad from Explorer, using WinDbg to break and inspect the CreateProcess function, and creating a process programmatically. The session emphasizes understanding process creation in user mode, inviting further feedback and interaction through specified channels.
      - source code for `CreateProcess` is in `Part-03/CreateProcess.cpp`
    * [x] [Part 04](https://youtu.be/P7KR2oEPBPw?si=Vulf4trfxb_zuVIa)
      - This presentation delves into the concept of processes within operating systems, highlighting how processes utilize isolated virtual address spaces to enable multiple programs to operate independently and securely on the same physical hardware. It explains the mechanism of memory management using page table entries to map virtual addresses to different physical locations for each process, ensuring that processes cannot access or interfere with each other’s data.
    * [x] [Part 05](https://youtu.be/3PI3xdIITiU?si=kBMtV_MpvMQyafPp)
      - This presentation focuses on the critical metadata structures of a process in Windows, examining kernel and user-mode data structures such as `_KPROCESS`, `_EPROCESS`, and `_PEB`. It explains how these structures interact and are crucial for the kernel's management of processes, detailing their roles in bookkeeping, memory management via page table entries, and the creation of processes through the CreateProcess function.
    * [ ] [Part 06](https://youtu.be/Hg0xcpBc6R4?si=YUcN0Tt5WRDkRDO_)
      - This presentation provides a detailed exploration of various debugger commands used for process analysis, particularly focusing on commands like !process, !thread, and !address. It highlights their applications, such as switching process context and dumping process structures, and introduces advanced usage like !process 0x17 for in-depth insights into process structures and user mode activities on a Windows 8.1 system.
    * [ ] [Part 07](https://youtu.be/GnZelk2B3yA?si=YDcURv7arDO8DTbS)
      - This presentation examines the implementation of the Windows API, specifically focusing on the GetCommandLine API, which retrieves the command line string of the current process. It details how this API accesses the command line information from the Process Environment Block (PEB) and demonstrates the use of debugging techniques to explore this functionality in a real-world scenario, highlighting practical applications like memory editing to alter the API's output.
    * [ ] [Part 08](https://youtu.be/Fj3sa1zKbyA?si=_zV5nuhzgil8zTMy)
      - This presentation focuses on understanding the key assets of a process, including address spaces, handles, threads, command-line arguments, and the current directory, highlighting their roles and limitations. It employs Process Explorer to demonstrate how to inspect these assets in real-time, such as viewing loaded DLLs and examining open handles, providing a practical approach to comprehending process management and its implications from both programming and user perspectives.
    * [ ] [Part 09](https://youtu.be/N6D6xnx1WAg?si=iQDhTJoKJnB-ebQ5)
      - This presentation delves into the concept of address space as a fundamental asset of any process, explaining its theoretical size and the importance of memory isolation to ensure independent program operation. It details how memory allocation and management occur, using functions like VirtualAlloc, and introduces tools like Sysinternals VMMap and Kernel Debugger for practical demonstration and analysis. The session provides insights into how processes manage their allocated and free memory regions, setting the stage for further detailed exploration in future sessions.
    * [ ] [Part 10](https://youtu.be/AtDH19fgAFM?si=JdT_ibXvHXkiYwAq)
      - This presentation explores the role of binaries as crucial components of process architecture, explaining how they dictate operations within a process's execution much like a task list in a new job. It covers different aspects of binaries, including common extensions like .sys, .exe, and .dll, and their creation through linking object files. The session uses Process Explorer to demonstrate how binaries are loaded into user and kernel modes, highlighting the distinctions between common and process-specific binaries, and discussing their interplay in system architecture. The presentation aims to enhance understanding of how binaries define a process's capabilities and actions.
    * [ ] [Part 11](https://youtu.be/0MQL2y4YYqs?si=K9cYbovQr2jbknhw)
      - This presentation focuses on the concept of process handles, explaining them as essential identifiers used by a process to access various system resources securely. Handles are described as akin to permissions granted by the kernel to access protected resources like files and devices, and are crucial for user-mode applications to interact indirectly with kernel data structures. The presentation further categorizes handles into types such as files, threads, processes, and synchronization objects, and uses Process Explorer to demonstrate how handles are viewed, utilized, and managed within the system. This session aims to enhance understanding of how handles function and their importance in system interactions.
    * [ ] [Part 12](https://youtu.be/T4Jc_Tl_Sl4?si=vUU4PiK_8_iSEFVu)
      - This presentation delves into threads as fundamental assets in process management, essential for executing actions within a computer system. It outlines how threads are the primary entities that execute instructions on the CPU, distinct from processes, which provide the necessary space and resources. The session covers thread lifecycle, creation, and management, including demonstrations using Process Explorer and Visual Studio to view and manage thread details. Additionally, it emphasizes the importance of threads in operating within the process's address space and their inability to interact outside of it, setting the stage for further exploration of multi-threading and thread synchronization in upcoming sessions.
    * [ ] [Part 13](https://youtu.be/9mo-rkOcZCQ?si=QEl_XHZng2JWp_Su)
      - This presentation focuses on GDI (Graphics Device Interface) and user object handles within Windows operating systems, detailing their specific roles in managing display-related artifacts crucial for user interface operations. It highlights the distinct management of these handles by the win32k.sys driver and their involvement in tasks like drawing, rendering, and interface element control. The session provides insights into the creation, management, and viewing of these handles using tools like Task Manager and Process Explorer, and discusses advanced topics such as session and desktop isolation and object sharing within the Windows environment. The presentation aims to enhance understanding of these handles' critical role in graphical and desktop management features.
    * [ ] [Part 14](https://youtu.be/RreHLbjU_mI?si=j97ddhIR4J7sncx6)
      - This presentation explores environmental variables and command-line arguments, emphasizing their roles in inter-process communication and program configuration within Windows. It details how these elements are stored in the Process Environment Block (PEB) and utilized to specify program operations and affect process behavior. The session includes a practical demonstration using Process Explorer to view these elements within specific processes, such as LogonUI.exe, and discusses their significance in defining the execution context of processes. The presentation aims to enhance understanding of how command-line arguments and environmental variables are set during process creation and managed within user mode, setting the stage for further exploration in future sessions.
    * [ ] [Part 15](https://youtu.be/NxI5DCM_BfQ?si=AdYbQ4_LkNnEumaq)
      - This presentation delves into the concept of Interprocess Communication (IPC) in Windows, a vital mechanism that enables processes to interact within an operating system beyond their isolated environments. It highlights various IPC methods including the use of handles, files, network sockets, Windows messages, and the Component Object Model (COM), demonstrating how these facilitate secure communications between processes and between processes and the kernel. Practical examples, such as the interaction between the on-screen keyboard and Notepad, and the use of COM between PowerPoint and Excel, illustrate the implementation and functionality of IPC. The session concludes with a comprehensive overview of IPC types and their roles in ensuring secure and efficient process communication under the supervision of the Windows kernel, setting the stage for deeper exploration in future sessions.
    * [ ] [Part 16](https://youtu.be/Mk42fHiG1no?si=lJkdi5TDzlcRwR9X)
      - This presentation explores the mechanisms and implications of process termination in the Windows operating system, outlining the essential steps involved in ending a process efficiently to free up system resources and maintain system stability. It covers both internal and external triggers for process termination, such as calls to ExitProcess and actions from the Task Manager, respectively. Additionally, it discusses the system's handling of resources during termination, including memory deallocation, file handle closure, and cleanup of user interfaces. Practical demonstrations illustrate how different resources are managed upon process termination, enhancing understanding of the coordination required between user-mode operations and kernel-level management. This session aims to deepen knowledge of process management and its impact on developing efficient applications and troubleshooting in Windows.
    * [ ] [Part 17](https://youtu.be/cWMvAZlruDE?si=nIYxjBGTQX4uJJvO)
      - This presentation addresses the design guidelines for process creation in Windows, emphasizing the scenarios that justify initiating new processes in application development. It discusses the importance of considering the overhead and complexity introduced by process creation, highlighting use cases such as application isolation, separation of service and UI components, distributed systems, third-party DLL integration, and compatibility issues. The session contrasts processes with threads, recommending the use of threads for multitasking within the same application due to their lower overhead and better performance, while processes provide isolation. Recommendations include minimizing interprocess communication (IPC) and using DLLs for modular design within a single process. This guidance aims to help developers make informed decisions about when and why to create a process, aligning with best practices in software architecture to optimize performance and resource utilization.
    * [ ] [Part 18](https://youtu.be/L77PZpFBpgY?si=a5vUxyYisxPiFavc)
      - This presentation provides an in-depth exploration of key system processes in the Windows operating system, explaining their critical roles and functionalities necessary for maintaining system stability and security. It covers essential processes like the System Idle Process, System Process, and various subsystems like smss.exe, csrss.exe, services.exe, lsass.exe, winlogon.exe, and explorer.exe, detailing their specific functions in session management, user interaction, and security protocols. Additionally, it highlights the complexities involved in modifying crucial system components like csrss.exe due to robust security measures. The session underscores how system processes manage services, user authentication, and interface operations, offering insights into the architectural efficiency and complexity of Windows. This discussion aims to enhance understanding of Windows’ core operations and the integral roles of its system processes.
    * [ ] [Part 19](https://youtu.be/YqfMpoOKEkA?si=Kl26rZ-g2tNiMgdS)
      - This presentation delves into the complexities of memory management in Windows, focusing on the critical interaction between kernel mode and user mode, underpinned by protected mode and paging on the 32-bit Intel x86 architecture. It emphasizes how security is preserved through hardware-assisted features like segmentation and paging, which prevent user-mode programs from accessing or modifying other programs’ data or operating system data. The session explores the roles of control registers, such as CR0 and CR3, in managing these protections and illustrates how CPU architecture facilitates robust access control and memory protection. Practical demonstrations using debuggers are included to show how memory addresses are translated and access controls enforced, providing a comprehensive understanding of the mechanisms that maintain security and  stability in a modern operating system. The presentation aims to enhance knowledge of Windows memory management strategies crucial for programming and system administration in secure environments.
  </details>


* [ ] Following a long with 0dr3f
  * [x] [Source](https://0dr3f.github.io/2023/07/14/HEVD_Win10_22H2_ArbitraryOverwrite/)


    <details><summary>Current status</summary>

    * [ ] Token impersonation
    * [ ] Understanding and making debuggable concepts:
      * [ ] SMEP & SMAP
    * [ ]  
    </details>

* [ ] Making my first driver:
  * [ ] [Source msdocs](https://learn.microsoft.com/en-us/windows-hardware/drivers/gettingstarted/writing-a-very-small-kmdf--driver)
  

* [ ] Understand how the kernel can have shared memory with the user space (these are the sources and sinks)
  * https://stackoverflow.com/questions/55054190/copying-data-from-user-app-to-kernel-driver-via-memcpy

* [ ] reading this and implementing a python script as google did https://cloud.google.com/blog/topics/threat-intelligence/monitoring-windows-console-activity-part-2
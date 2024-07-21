# Reason

1. Why not?
2. Understanding OS structures
3. Getting better with WinDbg and debugging in general


# Getting my feet wet

By all means, this is a project I will be working on from time to time.

I'm not a developer, so my git pushes will be not as great as other projects.

To do:

* [ ] Following a long with Windows Internal Process 20 parts
  * [x] [Source](https://www.youtube.com/watch?v=4AkzIbmI3q4&list=PLhx7-txsG6t5i-kIZ_hwJSgZrnka4GXvn&index=1)

    <details><summary>Current status (20 parts with checkboxes)</summary>
    I'm using OCR / Transcripts (e.g. `tesseract ./<image-name>.png summary` or `https://kome.ai/tools/youtube-transcript-generator`) as notes, some parts are with debugging notes.

    * [?] Part 01
      - This lesson emphasizes the complexity of seemingly simple tasks in modern operating systems like Windows, encouraging deeper understanding beyond abstractions. It includes a demo on executing a "Hello World" program, observing process creation, and delving into system internals like conhost and process explorer. The goal is to appreciate the underlying mechanisms, gaining programming language-independent knowledge, and enhancing skills in using, administrating, and troubleshooting operating systems.
      - Skipped because legacy code. 
        Check the notes in `Part-01/kernel-debugging-notes.md`
    * [x] Part 02 
      - This lesson explains how Windows manages multitasking through process management, likening processes to independent households in a neighborhood to ensure privacy, space, and non-interference. It covers concepts such as memory allocation, threads, handles, security tokens, and the creation and termination of processes, using Task Manager and Process Explorer for practical demonstrations.
    * [x] Part 03
      - This presentation delves into process creation in Windows, focusing on the use of the CreateProcess API. It discusses key parameters, particularly the importance of specifying the .exe file name. A demo illustrates starting Notepad from Explorer, using WinDbg to break and inspect the CreateProcess function, and creating a process programmatically. The session emphasizes understanding process creation in user mode, inviting further feedback and interaction through specified channels.
      - source code for `CreateProcess` is in `Part-03/CreateProcess.cpp`
    * [x] Part 04
      - This presentation delves into the concept of processes within operating systems, highlighting how processes utilize isolated virtual address spaces to enable multiple programs to operate independently and securely on the same physical hardware. It explains the mechanism of memory management using page table entries to map virtual addresses to different physical locations for each process, ensuring that processes cannot access or interfere with each other’s data.
    * [x] Part 05
      - This presentation focuses on the critical metadata structures of a process in Windows, examining kernel and user-mode data structures such as _KPROCESS, _EPROCESS, and _PEB. It explains how these structures interact and are crucial for the kernel's management of processes, detailing their roles in bookkeeping, memory management via page table entries, and the creation of processes through the CreateProcess function.
    * [ ] Part 06
      - This presentation provides a detailed exploration of various debugger commands used for process analysis, particularly focusing on commands like !process, !thread, and !address. It highlights their applications, such as switching process context and dumping process structures, and introduces advanced usage like !process 0x17 for in-depth insights into process structures and user mode activities on a Windows 8.1 system.
    * [ ] Part 07
    * [ ] Part 08
    * [ ] Part 09
    * [ ] Part 10
    * [ ] Part 11
    * [ ] Part 12
    * [ ] Part 13
    * [ ] Part 14
    * [ ] Part 15
    * [ ] Part 16
    * [ ] Part 17
    * [ ] Part 18
    * [ ] Part 19
    * [ ] Part 20
  </details>


* [ ] Following a long with 0dr3f
  * [x] [Source](https://0dr3f.github.io/2023/07/14/HEVD_Win10_22H2_ArbitraryOverwrite/)


    <details><summary>Current status</summary>

    * [ ] Token impersonation
    * [ ] Understanding and making debuggable concepts:
      * [ ] SMEP & SMAP
    * [ ]  
    </details>


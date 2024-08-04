


# Understanding the Heap and Heap Manager [source](https://techcommunity.microsoft.com/t5/ask-the-performance-team/what-a-heap-of-part-one/ba-p/372424)

Today's post is the result of a recent series of questions on the Heap and the Heap Manager that I fumbled quite hopelessly! Once I got back to my desk, I pulled out my trusty copy of *Windows Internals* and started reading. The more I read, the more I thought about a blog post. The catalyst for inspiration stems from all sorts of sources – in this case, I'm thankful to an engineer who simply wouldn't let me off the hook! So, let's get started...

## What Exactly is the Heap?

The heap is an area of memory reserved for data that is created when a program is executed. Each process has a process heap that is created when the process starts and remains as long as the process is running. By default, this heap is 1MB in size, which is just an initial reservation. As more memory is needed, the heap will expand. You can also specify a larger starting size in the image file by using the `/HEAP` linker flag. The default heap can be explicitly used by the program or implicitly used by some Windows internal functions.

Simply put, the default heap spans a range of addresses. Some of these ranges are reserved, while others are committed and have pages of memory associated with them. In this instance, the addresses are contiguous. If the default heap needs to allocate more memory than it has available in its current reserved address space, the heap can either fail the call requesting the memory or reserve an additional range elsewhere in the process. By default, the heap manager will attempt to perform the second operation. When the default heap needs more memory than is currently available, it reserves another 1MB address range within the process. Additionally, it performs an initial commit of the memory needed from this reserved range to satisfy the allocation request. The heap manager then becomes responsible for managing this new memory region as well as the original heap space.

## Private Heaps

Processes can also create a private heap – a block of one or more pages in the address space of the calling process. The process can then manage the memory in that heap. There is no difference between the memory allocated from a private heap and that allocated using other memory allocation functions. When creating this private heap object, you can specify both the initial size and maximum size for the heap. It is important to remember that the memory of a private heap object is only accessible to the process that created it. If a DLL creates a private heap, it does so in the address space of the process that called the DLL, making it accessible only to that process. When a process no longer needs a private heap, it can recover the virtual address space. Within each process, there is an array that maintains a list of all heaps.

## The Heap Manager

Before wrapping up, let's quickly look at the Heap Manager itself. Many applications allocate smaller blocks than the 64KB minimum allocation granularity possible. Allocating such a large area for relatively small allocations is hardly optimal from a memory usage or performance standpoint. To address this, Windows uses the heap manager to manage allocations inside larger memory areas. The allocation granularity in the heap manager is relatively small: 8 bytes on 32-bit systems and 16 bytes on 64-bit systems.

The heap manager is structured in two layers: a front-end layer (which is optional) and the core heap. The core heap is responsible for the basic functionality and is mostly common across user and kernel mode heap implementations. For user mode heaps only, an optional front-end heap layer can exist on top of the existing core functionality. There are two types of front-end layers: look-aside lists and the Low Fragmentation Heap (LFH), which is available in Windows XP and later operating systems. Only one front-end layer can be used for one heap at a time. We'll discuss both of these in our next post on the Heap.

## Conclusion

That will do it for Part One of our look at the Heap. In our next Heap post, we'll cover Look-Aside lists and Heap Fragmentation, among other things.

## Additional Resources

- **Book:** *Windows Internals, 4th Edition* – Chapter 7 covers Memory Management in depth!
- **MSDN:** [Managing Heap Memory in Win32](https://docs.microsoft.com/en-us/windows/win32/memory/managing-heap-memory)
- **MSDN:** [Automatic Memory Management](https://docs.microsoft.com/en-us/dotnet/standard/automatic-memory-management)

– CC Hameed


# Managing Heap Memory (2010) 


# Managing Heap Memory

**Randy Kath**  
Microsoft Developer Network Technology Group

Created: April 3, 1993

## Abstract

Determining which function or set of functions to use for managing memory in your application is difficult without a solid understanding of how each group of functions works and the overall impact they each have on the operating system. In an effort to simplify these decisions, this technical article focuses on the use of heaps in Windows: the functions that are available, the way they are used, and the impact their use has on operating system resources. The following topics are discussed:

- The purpose of heaps
- General heap behavior
- The two types of heaps
- Global and local memory functions
- Heap memory functions
- Overhead on heap memory allocations
- Summary and recommendations

In addition to this technical article, a sample application called ProcessWalker is included on the Microsoft Developer Network CD. This sample application explores the behavior of heap memory functions in a process, and it provides several useful implementation examples.

## Introduction

This is one of three related technical articles—"Managing Virtual Memory," "Managing Memory-Mapped Files," and "Managing Heap Memory"—that explain how to manage memory using the Windows API (application programming interface). This introduction identifies the basic memory components in the programming model and indicates which article to reference for specific areas of interest.

The first version of the Microsoft® Windows™ operating system introduced a method of managing dynamic memory based on a single _global heap_, which all applications and the system share, and multiple, private _local heaps_, one for each application. Local and global memory management functions were also provided, offering extended features for this new memory management system. More recently, the Microsoft C run-time (CRT) libraries were modified to include capabilities for managing these heaps in Windows using native CRT functions such as **malloc** and **free**. Consequently, developers are now left with a choice—learn the new API provided as part of Windows version 3.1 or stick to the portable, and typically familiar, CRT functions for managing memory in applications written for 16-bit Windows.

Windows offers three groups of functions for managing memory in applications: memory-mapped file functions, heap memory functions, and virtual memory functions.

![ms810603.heapmm_1(en-us,MSDN.10).gif](images/ms810603.heapmm_1(en-us,msdn.10).gif)
**Figure 1. The Windows API provides different levels of memory management for versatility in application programming.**

Six sets of memory management functions exist in Windows, as shown in Figure 1, all of which were designed to be used independently of one another. So which set of functions should you use? The answer to this question depends greatly on two things: the type of memory management you want, and how the functions relevant to it are implemented in the operating system. In other words, are you building a large database application where you plan to manipulate subsets of a large memory structure? Or maybe you're planning some simple dynamic memory structures, such as linked lists or binary trees? In both cases, you need to know which functions offer the features best suited to your intention and exactly how much of a resource hit occurs when using each function.

The following table categorizes the memory management function groups and indicates which of the three technical articles in this series describes each group's behavior. Each technical article emphasizes the impact these functions have on the system by describing the behavior of the system in response to using the functions.

### Table 1

| Memory set                   | System resource affected                                                                                         | Related technical article          |
|------------------------------|------------------------------------------------------------------------------------------------------------------|------------------------------------|
| Virtual memory functions     | A process's virtual address space<br>System pagefile<br>System memory<br>Hard disk space                         | "Managing Virtual Memory"          |
| Memory-mapped file functions | A process's virtual address space<br>System pagefile<br>Standard file I/O<br>System memory<br>Hard disk space    | "Managing Memory-Mapped Files"     |
| Heap memory functions        | A process's virtual address space<br>System memory<br>Process heap resource structure                            | "Managing Heap Memory"             |
| Global heap memory functions | A process's heap resource structure                                                                              | "Managing Heap Memory"             |
| Local heap memory functions  | A process's heap resource structure                                                                              | "Managing Heap Memory"             |
| C run-time reference library | A process's heap resource structure                                                                              | "Managing Heap Memory"             |

Each technical article discusses issues surrounding the use of Windows-specific functions.

## The Purpose of Heaps

The Windows subsystem on Windows NT provides high-level memory management functions that make it easy for applications to build dynamic data structures, provide compatibility with previous versions of Windows, and create buffers and temporary placeholders for system functions. These memory management functions return handles and pointers to blocks of memory that are allocated at run time and managed by an entity called the _heap_. The heap's primary function is to efficiently manage the memory and address space of a process for an application.

A tall order, considering the heap has absolutely no idea what the application intends to do with its memory and address space. Yet the heap manages to provide a robust set of functions that allow developers to overlook some of the finer details of system resources (such as the difference between reserved, free, and committed memory) so that they can turn their attention to the more important task at hand, that of implementing their applications.

In Windows NT, heaps provide a smaller granularity for the size of the smallest allocatable chunk of memory than the virtual memory management functions do. Applications typically need to allocate a specific number of bytes to fulfill a parameter request or to act as a temporary buffer. For example, when loading a string resource with the **LoadString** function, an application passes a pointer to a buffer that receives the string resource. The size of the buffer must be large enough to hold the string and a null terminator. Without the heap manager, applications would be forced to use the virtual memory management functions, which allocate a minimum of one page of memory at a time.

## General Heap Behavior

While the heap does provide support for managing smaller chunks of memory, it is itself nothing more than a chunk of memory implemented in the Windows NT virtual memory system. Consequently, the techniques that the heap uses to manage memory are based on the virtual memory management functions available to the heap. Evidence of this is found in the way heaps manifest themselves in a process, if only we could observe this behavior....

The ProcessWalker (PW) sample application explores each of the components within a process, including all of its heaps. PW identifies the heaps in a process and shows the amount of reserved and committed memory associated with a particular heap. As with all other regions of memory in a process, the smallest region of committed memory within a heap is one page (4096 bytes).

This does not mean that the smallest amount of memory that can be allocated in a heap is 4096 bytes; rather, the heap manager commits pages of memory as needed to satisfy specific allocation requests. If, for example, an application allocates 100 bytes via a call to **GlobalAlloc**, the heap manager allocates a 100-byte chunk of memory within its committed region for this request. If there is not enough committed memory available at the time of the request, the heap manager simply commits another page to make the memory available.

Ideally, then, if an application repetitively allocates 100-byte chunks of memory, the heap will commit an additional page of memory every forty-first request (40 * 100 bytes = 4000 bytes). Upon the forty-first request for a chunk of 100 bytes, the heap manager realizes there is not enough committed memory to satisfy the request, so it commits another page of memory and then completes the requested allocation. In this way, the heap manager is responsible for managing the virtual memory environment completely transparent of the application.

In reality, though, the heap manager requires additional memory for managing the memory in the heap. So instead of allocating only 100 bytes as requested, it also allocates some space for managing each particular chunk of memory. The type of memory and the size of the allocation determine the size of this additional memory. I'll discuss these issues later in this article.

## The Two Types of Heaps

Every process in Windows has one heap called the _default heap_. Processes can also have as many other _dynamic heaps_ as they wish, simply by creating and destroying them on the fly. The system uses the default heap for all global and local memory management functions, and the C run-time library uses the default heap for supporting **malloc** functions. The heap memory functions, which indicate a specific heap by its handle, use dynamic heaps. The behavior of dynamic heaps is discussed in the "Heap Memory API" section later in this article.

The default and dynamic heaps are basically the same thing, but the default heap has the special characteristic of being identifiable as the default. This is how the C run-time library and the system identify which heap to allocate from. The **GetProcessHeap** function returns a handle to the default heap for a process. Since functions such as **GlobalAlloc** or **malloc** are executed within the context of the thread that called them, they can simply call **GetProcessHeap** to retrieve a handle to the default heap, and then manage memory accordingly.

### Managing the Default Heap

Both default and dynamic heaps have a specific amount of reserved and committed memory regions associated with them, but they behave differently with respect to these limits. The default heap's reserved and committed memory region sizes are designated when the application is linked. Each application carries this information about itself within its executable image information. You can view this information by dumping header information for the executable image. For example, type the following command at a Windows NT command prompt (PWALK.EXE is used here to complete the example; you will need to substitute your own path and executable file):

```plaintext
link32 -dump -headers d:\samples\walker\pwalk.exe

...
OPTIONAL HEADER VALUES             
     10B magic #                   
    2.29 linker version            
    B000 size of code              
   1E800 size of initialized data  
     600 size of uninitialized data
   18470 address of entry point    
   10000 base of code              
   20000 base of data              
         ----- new -----           
  400000 image base                
   10000 section alignment         
     200 file alignment            
       2 subsystem (Windows GUI)   
     0.B operating system version  
     1.0 image version             
     3.A subsystem version         
   C0000 size of image             
     400 size of headers           
       0 checksum                  
   10000 size of stack reserve     
    1000 size of stack commit      
   10000 size of heap reserve      
    1000 size of heap commit       
   ...
```

The last two entries are hexadecimal values specifying the amount of reserved and committed space initially needed by the application.

There are two ways to tell the linker what to use for these values. You can link your application with a module definition file and include a statement in the file like the following:


```plaintext
HEAPSIZE   0x10000 0x1000
```
Or you can directly inform the linker by using the **/HEAP**  linker switch, as in:

```plaintext
/HEAP: 0x10000, 0x1000
```

In both examples, the heap is specified to initially have 0x10000 (64K) bytes reserved address space and 0x1000 (4K) bytes committed memory. If you fail to indicate the heap size in either method, the linker uses the default values of 0x100000 (1 MB) reserved address space and 0x1000 (4K) committed memory.

The linker accepts almost any value for heap reserve space, because the application loader ensures that the application will meet certain minimum requirements during the load process. In other words, you can link an application with an initial heap value of 1 page reserved address space. The linker doesn't perform any data validation; it simply marks the executable with the given value. Yet, since the minimum range of address space that can be reserved is 16 pages (64K), the loader compensates by reserving 16 pages for the application heap at load time.

As indicated above, options exist that indicate how much memory should initially be committed for an application's default heap. The problem is they don't seem to work yet. The linker for the second beta release of Windows NT marks all executable applications with 0x1000 (4K) initial committed memory for the default heap size, regardless of the value indicated as an option. Yet this is not that big a deal because it actually may be better for an application to commit as it needs to, rather than to commit memory that is not being used.

### A Default Heap That Grows and Spreads 

In its simplest form, the default heap spans a range of addresses. Some ranges are reserved, while others are committed and have pages of memory associated with them. In this case the addresses are contiguous, and they all originated from the same base allocation address. In some cases the default heap needs to allocate more memory than is available in its current reserved address space. For these cases the heap can either fail the call that requests the memory, or reserve an additional address range elsewhere in the process. The default heap manager opts for the second choice.

When the default heap needs more memory than is currently available, it reserves another 1-MB address range in the process. It also initially commits as much memory as it needs from this reserved address range to satisfy the allocation request. The default heap manager is then responsible for managing this new memory region as well as the original heap space. If necessary, it will repeat this throughout the application until the process runs out of memory and address space. You could end up with a default heap that manifests itself in your process in a manner similar to the heap represented in Figure 2.
![ms810603.heapmm_2(en-us,MSDN.10).gif](https://chatgpt.com/c/images/ms810603.heapmm_2(en-us,msdn.10).gif) 

**Figure 2. The default heap for each process can expand into free address regions within the process.** 
So the default heap is not really a static heap at all. In fact, it may seem like a waste of energy to bother with managing the size of the initial heap since the heap always behaves in the same way after initialization. Managing the size of the default heap offers one advantage, though. It takes time to locate and reserve a new range of addresses in a process; you can save time by simply reserving a large enough address range initially. If you expect your application to require more heap space than the 1-MB default, reserve more address space initially to avoid allocating another region of addresses in your process later. Remember, each application has 2 gigabytes (GB) of address space to work with, and requires very little physical memory to support it.

## Global and Local Memory Functions 

At first glance it appears that the local and global memory management functions exist in Windows purely for backward compatibility with Windows version 3.1. This may be true, but the functions are managed as efficiently as the new heap functions discussed below. In fact, porting an application from 16-bit Windows does not necessarily include migrating from global and local memory functions to heap memory functions. The global and local functions offer the same basic capabilities (and then some) and are just as fast to work with. If anything, they are probably more convenient to work with because you do not have to keep track of a heap handle.
Nonetheless, the implementation of these functions is not the same as it was for 16-bit Windows. 16-bit Windows had a global heap, and each application had a local heap. Those two heap managers implemented the global and local functions. Allocating memory via **GlobalAlloc**  meant retrieving a chunk of memory from the global heap, while **LocalAlloc**  allocated memory from the local heap. Windows now has a single heap for both types of functions—the default heap described above.Now you're probably wondering if there is any difference between the local and global functions themselves. Well, the answer is no, they are now the same. In fact, they are interchangeable. Memory allocated via a call to **LocalAlloc**  can be reallocated with **GlobalReAlloc**  and then locked by **LocalLock** . The following table lists the global and local functions now available.
### Table 2 
| Global memory functions | Local memory functions | 
| --- | --- | 
| GlobalAlloc | LocalAlloc | 
| GlobalDiscard | LocalDiscard | 
| GlobalFlags | LocalFlags | 
| GlobalFree | LocalFree | 
| GlobalHandle | LocalHandle | 
| GlobalLock | LocalLock | 
| GlobalReAlloc | LocalReAlloc | 
| GlobalSize | LocalSize | 
| GlobalUnlock | LocalUnlock | 

It seems redundant to have two sets of functions that perform exactly the same, but that's where the backward compatibility comes in. Whether you used the global or local functions in a 16-bit Windows application before doesn't matter now—they are equally efficient.

### Types of Global and Local Memory 
In the Windows API, the global and local memory management functions provide two types of memory, MOVEABLE and FIXED. MOVEABLE memory can be further qualified as DISCARDABLE memory. When you allocate memory with either **GlobalAlloc**  or **LocalAlloc** , you designate the type of memory you want by supplying the appropriate memory flag. The following table lists and describes each memory flag for global and local memory.
### Table 3 
| Global memory flag | Local memory flag | Allocation meaning | 
| --- | --- | --- | 
| GMEM_FIXED | LMEM_FIXED | Allocate fixed memory. | 
| GMEM_MOVEABLE | LMEM_MOVEABLE | Allocate movable memory. | 
| GMEM_DISCARDABLE | LMEM_DISCARDABLE | Allocate discardable, movable memory. | 
| GMEM_ZEROINIT | LMEM_ZEROINIT | Initialize memory to zeros during allocation. | 
| GMEM_NODISCARD | LMEM_NODISCARD | Do not discard other memory to meet the needs of this allocation; instead, fail this request. | 
| GMEM_NOCOMPACT | LMEM_NOCOMPACT | Do not discard or move other memory to meet the needs of this allocation; instead, fail this request. | 
| GMEM_SHARE, GMEM_DDESHARE | N/A | Allocate global memory that is more efficient to use with DDE. | 

It is surprising that the distinction between FIXED and MOVEABLE memory still exists in these functions. In 16-bit Windows, MOVEABLE memory compacted the local and global heaps to reduce fragmentation and make more memory available to all applications. Yet the Windows NT virtual memory system does not rely on these techniques for efficient memory management and has little to gain by applications using them. In any case, they still exist and could actually be used in some circumstances.
When allocating FIXED memory in Windows, the **GlobalAlloc**  and **LocalAlloc**  functions return a 32-bit pointer to the memory block rather than a handle as they do for MOVEABLE memory. The pointer can directly access the memory without having to lock it first. This pointer can also be passed to the **GlobalFree**  and **LocalFree**  functions to release the memory without having to first retrieve the handle by calling the **GlobalHandle**  function. With FIXED memory, allocating and freeing memory is similar to using the C run-time functions **_malloc**  and **_free** .MOVEABLE memory, on the other hand, cannot provide this luxury. Because MOVEABLE memory can be moved (and DISCARDABLE memory can be discarded), the heap manager needs a handle to identify the chunk of memory to move or discard. To access the memory, the handle must first be locked by calling either **GlobalLock**  or **LocalLock** . As in 16-bit Windows, the memory cannot be moved or discarded while the handle is locked.
### The MOVEABLE Memory Handle Table 

As it turns out, each handle to MOVEABLE memory is actually a pointer into the MOVEABLE memory handle table. The handle table exists outside the heap, elsewhere in the process's address space. To learn more about this behavior, we created a test application that allocates several MOVEABLE memory blocks from the default heap. The handle table was created only upon allocation of the first MOVEABLE chunk of memory. This is nice, because if you never allocate any MOVEABLE memory, the table is never created and does not waste memory. ProcessWalker reveals that when this handle table is created, 1 page of memory is committed for the initial table and 512K of address space is reserved (see Figure 3).
![ms810603.heapmm_3(en-us,MSDN.10).gif](https://chatgpt.com/c/images/ms810603.heapmm_3(en-us,msdn.10).gif) 

**Figure 3. ProcessWalker highlights changes in the address space of a process. The heap memory handle table is shown as it looks immediately after it is created.** 
If you work out the math you can see that the number of memory handles available for MOVEABLE memory is limited. 512K bytes / 8 bytes per handle = 65,535 handles. In fact, the system imposes this limitation on each process. Fortunately, this only applies to MOVEABLE memory. You can allocate as many chunks of FIXED memory as you like, provided the memory and address space are available in your process.

Each handle requires 8 bytes of committed memory in the handle table to represent information, including the virtual address of the memory, the lock count on the handle, and the type of memory. Figure 4 shows how the handle table looks when viewed in ProcessWalker.
![ms810603.heapmm_4(en-us,MSDN.10).gif](https://chatgpt.com/c/images/ms810603.heapmm_4(en-us,msdn.10).gif) 

**Figure 4. Each MOVEABLE memory handle is 8 bytes and represents the location of the chunk of memory.** 
> **Note**  In the ProcessWalker view window, each line is 16 bytes (two memory handles). The far-left column represents the address of each line within the process. The addresses in white indicate the lines in which data changed since the last refresh. Red text shows exactly which bytes changed. This feature allows you to easily track changes in memory in response to certain events within the child process. A very useful debugging tool, to say the least.
The first 8 bytes in the view window—at address 0x000f0000—show the first handle allocated in the table. The handle value for this example would actually be 0x000f0004, which is a 4-byte offset into the 8-byte handle table entry. At the 4-byte offset in the table entry is the current 32-bit address representing the location of the chunk of memory. In this example, the 32-bit address is 0x00042A70, reading 4 bytes from right to left starting at 0x000f0008 and ending at 0x000f0004. If the memory is moved to a new location, this address changes to reflect the new location.
If you back up 4 bytes from the handle to the first byte in this handle table entry, you'll find the lock count for the handle. Remember, a block of memory can be moved or discarded only if its handle's lock count is zero. Since there is only 1 byte to record the lock count, it stands to reason that a handle can be locked only 256 (0xFF) times. Unfortunately, the system currently does not warn you when you reach that limit. If you lock a handle a 257th time, you receive a valid pointer to the memory, but the lock count remains at 256. It is possible, then, that you could unlock the handle 256 times and expect the memory to be locked. Yet the lock count is decremented to 0, and the memory could be moved or discarded. So what happens if you try to access the pointer you believe to be valid? Well, it depends on what is now at the address where you believe the memory to be. The memory could still be there, or some other memory could have been moved there. This is not the desired behavior, and we hope the system will be fixed to prevent this from happening. Incidentally, how should the system be fixed? The easiest thing to do would be to fail the call to **GlobalLock**  or **LocalLock**  on any attempt beyond 256, so check the return value to make sure the function succeeds.
The third and fourth bytes of the handle represent the memory type, that is, MOVEABLE, DDESHARE, or DISCARDABLE. Presumably because of compatibility with 16-bit Windows, local and global memory flags that have the same name and meaning do not have the same value. (The WINBASE.H header file defines each flag.) Yet once the memory is allocated, the handle table entry records no difference. Whether you use LMEM_DISCARDABLE or GMEM_DISCARDABLE does not matter—the handle table identifies all DISCARDABLE memory the same way. A little exploring in ProcessWalker shows the following type value identifiers.

### Table 4 
| Memory type | Byte 3 | Byte 4 | 
| --- | --- | --- | 
| MOVEABLE | 02 | – | 
| DISCARDABLE | 06 | – | 
| DDESHARE | – | 08 | 

Keep in mind that these values as represented in the handle table are not documented, so they could change with a new release of Windows NT. But it would be easy to use ProcessWalker to view the handle table to see the changes.

Returning to the test application example.... After allocating the first MOVEABLE memory block and thereby creating the handle table, we used the test application to allocate 15 more handles from the table. A quick view of the memory window showed the first eight lines had data associated with them, while the rest of the committed page was filled with zeros. Then we allocated one more handle, making a total of 17 handles. The view window was refreshed to indicate what changes occurred in the table as a result of allocating the seventeenth handle only. Figure 4 (above) shows the results.

As you can see, more than 8 bytes changed during the last allocation. In fact, 8 lines were updated for a total of 128 bytes. The first 8 bytes represent the seventeenth handle entry information as expected. The following 120 bytes indicate that the heap manager initializes the handle table every sixteenth handle. Examining this initialization data shows that the next 15 available handle table entries are identified in the table. When allocating the eighteenth handle, the location of the nineteenth handle is identified by the address location portion of the eighteenth handle table entry. As expected, then, if a handle is removed from the table (the memory is freed), the address location in that entry is replaced with the location of the next available handle after it. This behavior indicates that the heap manager keeps the location of the next available handle table entry in a static variable and uses that entry itself to store the location of the subsequent entry. Notice also that the last initialized entry has a null location for the next address. The heap manager uses this as an indicator to initialize another 16 handle table entries during the next handle allocation.

Another efficiency in the heap manager is its ability to commit pages of memory for the handle table as it needs them, not all 128 pages (512K) at once. Since the heap manager initializes its handle table in 16-handle (128-byte) increments, it is easy to determine when to commit a new page of memory. Every thirty-second (4096 / 128 = 32) initialization requires a new page of committed memory. Also, the entries do not straddle page boundaries, so their management is easier and potentially more efficient.

### CRT Library 

Managing memory in 16-bit Windows involved a great deal of uncertainty about using the C run-time (CRT) library. Now, there should be little hesitation. The current CRT library is implemented in a manner similar to FIXED memory allocated via the local and global memory management functions. The CRT library is also implemented using the same default heap manager as the global and local memory management functions.
Subsequent memory allocations via **malloc** , **GlobalAlloc** , and **LocalAlloc**  return pointers to memory allocated from the same heap. The heap manager does not divide its space among the CRT and global/local memory functions, and it does not maintain separate heaps for these functions. Instead, it treats them the same, promoting consistent behavior across the types of functions. As a result, you can now write code using the functions you're most comfortable with. And, if you're interested in portability, you can safely use the CRT functions exclusively for managing heap memory.
## Heap Memory API 
As mentioned earlier, you can create as many dynamic heaps as you like by simply calling **HeapCreate** . You must specify the maximum size of the heap so that the function knows how much address space to reserve. You can also indicate how much memory to commit initially. In the following example, a heap is created in your process that reserves 1 MB of address space and initially commits two pages of memory:

```plaintext
hHeap = HeapCreate (0, 0x2000, 0x100000);
```
Since you can have many dynamic heaps in your process, you need a handle to identify each heap when you access it. The **HeapCreate**  function returns this handle. Each heap you create returns a unique handle so that several dynamic heaps may coexist in your process. Having to identify your heap by handle also makes managing dynamic heaps more difficult than managing the default heap, since you have to keep each heap handle around for the life of the heap.If you're bothered by having to keep this handle around, there is an alternative. You can use the heap memory functions on the default heap instead of creating a dynamic heap explicitly for them. To do this, simply use the **GetProcessHeap**  function to get the handle of the default heap. For simple allocations of short-term memory, the following example taken from the ProcessWalker sample application illustrates how easy this is to do:

```plaintext
char    *szCaption;
int     nCaption = GetWindowTextLength (hWnd);

/* retrieve view memory range */
szCaption = HeapAlloc (GetProcessHeap (), 
                       HEAP_ZERO_MEMORY, 
                       nCaption+1);
GetWindowText (hViewWnd, szCaption, nCaption);
```

In this example the default heap is chosen because the allocation is independent of other memory management needs, and there is no reason to create a dynamic heap just for this one allocation. Note that you could achieve the same result by using the global, local, or CRT functions since they allocate only from the default heap.
As shown earlier, the first parameter to **HeapCreate**  allows you to specify an optional HEAP_NO_SERIALIZE flag. A serialized heap does not allow two threads to access it simultaneously. The default behavior is to serialize access to the heap. If you plan to use a heap strictly within one thread, specifying the HEAP_NO_SERIALIZE flag improves overall heap performance slightly.Like all of the heap memory functions, **HeapAlloc**  requires a heap handle as its first argument. The example uses the **GetProcessHeap**  function instead of a dynamic heap handle. The second parameter to **HeapAlloc**  is an optional flag that indicates whether the memory should be zeroed first and whether to generate exceptions on error. To get zeroed memory, specify the HEAP_ZERO_MEMORY flag as shown above. The generate exceptions flag (HEAP_GENERATE_EXCEPTIONS) is a useful feature if you have exception handling built into your application. When using this flag, the function raises an exception on failure rather than just returning NULL. Depending on your use, exception handling can be an effective way of triggering special events—such as low memory situations—in your application.**HeapAlloc**  has a cousin called **HeapReAlloc**  that works in much the same way as the standard global and local memory management functions described earlier. Use **HeapReAlloc**  primarily to resize a previous allocation. This function has four parameters, three of which are the same as for **HeapAlloc** . The new parameter, *lpMem*, is a pointer to the chunk of memory being resized.It is important to note that although heap memory is not movable as in global and local memory, it may be moved during the **HeapReAlloc**  function. This function returns a pointer to the resized chunk of memory, which may or may not be at the same location as initially indicated by the pointer passed to the function. This is the only time memory can be moved in dynamic heaps, and the only chunk of memory affected is the one identified by *lpMem* in the function. You can also override this behavior by specifying the HEAP_REALLOC_IN_PLACE_ONLY flag. With this flag, if there is not enough room to reallocate the memory in place, the function returns with failure status rather than move the memory.Memory allocated with **HeapAlloc**  or reallocated with **HeapReAlloc**  can be freed by calling **HeapFree** . This function is easy to use: simply indicate the heap handle and a pointer to the chunk of memory to free. Completing the example above, here is how you can use **HeapFree**  with the default heap:

```plaintext
/* free default heap memory */
HeapFree (GetProcessHeap (), szCaption);
```

This example shows how easy it can be to work with heaps in Windows. However, you may still want to create a dynamic heap specifically to manage complex dynamic data structures in your application. In fact, one nice benefit of heap memory is how well it caters to the needs of traditional data structures such as binary trees, linked lists, and dynamic arrays. Having the heap handle provides a way of uniquely identifying these structures independently. One example that comes to mind is when you're building a multiwindow application—perhaps a multiple document interface (MDI) application. Simply create and store a heap handle in the window extra bytes or window property list for each window during the WM_CREATE message. Then it is easy to write a window procedure that manages data structures from its own heap by retrieving the heap handle when necessary. When the window goes away, simply have it destroy the heap in the WM_DESTROY message.
You can easily destroy dynamic heaps by calling **HeapDestroy**  on a specific heap handle. This powerful function will remove a heap regardless of its state. The **HeapDestroy**  function doesn't care whether you have outstanding allocations in the heap or not.
To make heap memory management most efficient, you would only create a heap of the size you need. In some cases it is easy to determine the heap size you need—if you're allocating a buffer to read a file into, simply check the size of the file. In other cases, heap size is more difficult to figure—if you're creating a dynamic data structure that grows according to user interaction, it is difficult to predict what the user will do. Dynamic heaps have a provision for this latter circumstance. By specifying a maximum heap size of zero, you make the heap assume a behavior like the default heap. That is, it will grow and spread in your process as much as necessary, limited only by available memory. In this case, available memory means available address space in your process and available pagefile space on your hard disk.

## Overhead on Heap Memory Allocations 

With all types of heap memory, an overhead is associated with each memory allocation. This overhead is due to:

- Granularity on memory allocations within the heap.

- The overhead necessary to manage each memory segment within the heap.

The granularity of heap allocations in 32-bit Windows is 16 bytes. So if you request a global memory allocation of 1 byte, the heap returns a pointer to a chunk of memory, guaranteeing that the 1 byte is available. Chances are, 16 bytes will actually be available because the heap cannot allocate less than 16 bytes at a time.

### Global and Local Memory Functions 
For global and local memory functions, the documentation suggests that you use the **GlobalSize**  and **LocalSize**  functions to determine the exact size of the allocation, but in my tests this function consistently returned the size I requested and not the size actually allocated.To confirm this finding, turn to ProcessWalker again and view the committed memory in your default heap. For the sake of observation, perform consecutive allocations of 1, 2, 3, 14, 15, and 16 bytes using either **GlobalAlloc**  or **LocalAlloc** . In this particular example, we used **GlobalAlloc**  with the GMEM_MOVEABLE flag, but the result is the same for memory allocated as GMEM_FIXED. Then, refresh your view of the committed memory in the heap. Finally, scroll the view window so that the addresses of the allocated blocks of memory are all in view. You should see something similar to the window in Figure 5.![ms810603.heapmm_5(en-us,MSDN.10).gif](https://chatgpt.com/c/images/ms810603.heapmm_5(en-us,msdn.10).gif) 

**
Here's the entire content converted to markdown, including the table:


```markdown
# Managing Heap Memory

**Randy Kath**  
Microsoft Developer Network Technology Group

Created: April 3, 1993

## Abstract

Determining which function or set of functions to use for managing memory in your application is difficult without a solid understanding of how each group of functions works and the overall impact they each have on the operating system. In an effort to simplify these decisions, this technical article focuses on the use of heaps in Windows: the functions that are available, the way they are used, and the impact their use has on operating system resources. The following topics are discussed:

- The purpose of heaps
- General heap behavior
- The two types of heaps
- Global and local memory functions
- Heap memory functions
- Overhead on heap memory allocations
- Summary and recommendations

In addition to this technical article, a sample application called ProcessWalker is included on the Microsoft Developer Network CD. This sample application explores the behavior of heap memory functions in a process, and it provides several useful implementation examples.

## Introduction

This is one of three related technical articles—"Managing Virtual Memory," "Managing Memory-Mapped Files," and "Managing Heap Memory"—that explain how to manage memory using the Windows API (application programming interface). This introduction identifies the basic memory components in the programming model and indicates which article to reference for specific areas of interest.

The first version of the Microsoft® Windows™ operating system introduced a method of managing dynamic memory based on a single _global heap_, which all applications and the system share, and multiple, private _local heaps_, one for each application. Local and global memory management functions were also provided, offering extended features for this new memory management system. More recently, the Microsoft C run-time (CRT) libraries were modified to include capabilities for managing these heaps in Windows using native CRT functions such as **malloc** and **free**. Consequently, developers are now left with a choice—learn the new API provided as part of Windows version 3.1 or stick to the portable, and typically familiar, CRT functions for managing memory in applications written for 16-bit Windows.

Windows offers three groups of functions for managing memory in applications: memory-mapped file functions, heap memory functions, and virtual memory functions.

![ms810603.heapmm_1(en-us,MSDN.10).gif](images/ms810603.heapmm_1(en-us,msdn.10).gif)
**Figure 1. The Windows API provides different levels of memory management for versatility in application programming.**

Six sets of memory management functions exist in Windows, as shown in Figure 1, all of which were designed to be used independently of one another. So which set of functions should you use? The answer to this question depends greatly on two things: the type of memory management you want, and how the functions relevant to it are implemented in the operating system. In other words, are you building a large database application where you plan to manipulate subsets of a large memory structure? Or maybe you're planning some simple dynamic memory structures, such as linked lists or binary trees? In both cases, you need to know which functions offer the features best suited to your intention and exactly how much of a resource hit occurs when using each function.

The following table categorizes the memory management function groups and indicates which of the three technical articles in this series describes each group's behavior. Each technical article emphasizes the impact these functions have on the system by describing the behavior of the system in response to using the functions.

### Table 1

| Memory set                   | System resource affected                                                                                         | Related technical article          |
|------------------------------|------------------------------------------------------------------------------------------------------------------|------------------------------------|
| Virtual memory functions     | A process's virtual address space<br>System pagefile<br>System memory<br>Hard disk space                         | "Managing Virtual Memory"          |
| Memory-mapped file functions | A process's virtual address space<br>System pagefile<br>Standard file I/O<br>System memory<br>Hard disk space    | "Managing Memory-Mapped Files"     |
| Heap memory functions        | A process's virtual address space<br>System memory<br>Process heap resource structure                            | "Managing Heap Memory"             |
| Global heap memory functions | A process's heap resource structure                                                                              | "Managing Heap Memory"             |
| Local heap memory functions  | A process's heap resource structure                                                                              | "Managing Heap Memory"             |
| C run-time reference library | A process's heap resource structure                                                                              | "Managing Heap Memory"             |

Each technical article discusses issues surrounding the use of Windows-specific functions.

## The Purpose of Heaps

The Windows subsystem on Windows NT provides high-level memory management functions that make it easy for applications to build dynamic data structures, provide compatibility with previous versions of Windows, and create buffers and temporary placeholders for system functions. These memory management functions return handles and pointers to blocks of memory that are allocated at run time and managed by an entity called the _heap_. The heap's primary function is to efficiently manage the memory and address space of a process for an application.

A tall order, considering the heap has absolutely no idea what the application intends to do with its memory and address space. Yet the heap manages to provide a robust set of functions that allow developers to overlook some of the finer details of system resources (such as the difference between reserved, free, and committed memory) so that they can turn their attention to the more important task at hand, that of implementing their applications.

In Windows NT, heaps provide a smaller granularity for the size of the smallest allocatable chunk of memory than the virtual memory management functions do. Applications typically need to allocate a specific number of bytes to fulfill a parameter request or to act as a temporary buffer. For example, when loading a string resource with the **LoadString** function, an application passes a pointer to a buffer that receives the string resource. The size of the buffer must be large enough to hold the string and a null terminator. Without the heap manager, applications would be forced to use the virtual memory management functions, which allocate a minimum of one page of memory at a time.

## General Heap Behavior

While the heap does provide support for managing smaller chunks of memory, it is itself nothing more than a chunk of memory implemented in the Windows NT virtual memory system. Consequently, the techniques that the heap uses to manage memory are based on the virtual memory management functions available to the heap. Evidence of this is found in the way heaps manifest themselves in a process, if only we could observe this behavior....

The ProcessWalker (PW) sample application explores each of the components within a process, including all of its heaps. PW identifies the heaps in a process and shows the amount of reserved and committed memory associated with a particular heap. As with all other regions of memory in a process, the smallest region of committed memory within a heap is one page (4096 bytes).

This does not mean that the smallest amount of memory that can be allocated in a heap is 4096 bytes; rather, the heap manager commits pages of memory as needed to satisfy specific allocation requests. If, for example, an application allocates 100 bytes via a call to **GlobalAlloc**, the heap manager allocates a 100-byte chunk of memory within its committed region for this request. If there is not enough committed memory available at the time of the request, the heap manager simply commits another page to make the memory available.

Ideally, then, if an application repetitively allocates 100-byte chunks of memory, the heap will commit an additional page of memory every forty-first request (40 * 100 bytes = 4000 bytes). Upon the forty-first request for a chunk of 100 bytes, the heap manager realizes there is not enough committed memory to satisfy the request, so it commits another page of memory and then completes the requested allocation. In this way, the heap manager is responsible for managing the virtual memory environment completely transparent of the application.

In reality, though, the heap manager requires additional memory for managing the memory in the heap. So instead of allocating only 100 bytes as requested, it also allocates some space for managing each particular chunk of memory. The type of memory and the size of the allocation determine the size of this additional memory. I'll discuss these issues later in this article.

## The Two Types of Heaps

Every process in Windows has one heap called the _default heap_. Processes can also have as many other _dynamic heaps_ as they wish, simply by creating and destroying them on the fly. The system uses the default heap for all global and local memory management functions, and the C run-time library uses the default heap for supporting **malloc** functions. The heap memory functions, which indicate a specific heap by its handle, use dynamic heaps. The behavior of dynamic heaps is discussed in the "Heap Memory API" section later in this article.

The default and dynamic heaps are basically the same thing, but the default heap has the special characteristic of being identifiable as the default. This is how the C run-time library and the system identify which heap to allocate from. The **GetProcessHeap** function returns a handle to the default heap for a process. Since functions such as **GlobalAlloc** or **malloc** are executed within the context of the thread that called them, they can simply call **GetProcessHeap** to retrieve a handle to the default heap, and then manage memory accordingly.

### Managing the Default Heap

Both default and dynamic heaps have a specific amount of reserved and committed memory regions associated with them, but they behave differently with respect to these limits. The default heap's reserved and committed memory region sizes are designated when the application is linked. Each application carries this information about itself within its executable image information. You can view this information by dumping header information for the executable image. For example, type the following command at a Windows NT command prompt (PWALK.EXE is used here to complete the example; you will need to substitute your own path and executable file):

```plaintext
link32 -dump -headers d:\samples\walker\pwalk.exe

...
OPTIONAL HEADER VALUES             
     10B magic #                   
    2.29 linker version            
    B000 size of code              
   1E800 size of initialized data  
     600 size of uninitialized data
   18470 address of entry point    
   10000 base of code              
   20000 base of data              
         ----- new -----           
  400000 image base                
   10000 section alignment         
     200 file alignment            
       2 subsystem (Windows GUI)   
     0.B operating system version  
     1.0 image version             
     3.A subsystem version         
   C0000 size of image             
     400 size of headers           
       0 checksum                  
   10000 size of stack reserve     
    1000 size of stack commit      
   10000 size of heap reserve      
    1000 size of heap commit       
   ...
```

The last two entries are hexadecimal values specifying the amount of reserved and committed space initially needed by the application.

There are two ways to tell the linker what to use for these values. You can link your application with a module definition file and include a statement in the file like the following:


```plaintext
HEAPSIZE   0x10000 0x1000
```
Or you can directly inform the linker by using the **/HEAP**  linker switch, as in:

```plaintext
/HEAP: 0x10000, 0x1000
```

In both examples, the heap is specified to initially have 0x10000 (64K) bytes reserved address space and 0x1000 (4K) bytes committed memory. If you fail to indicate the heap size in either method, the linker uses the default values of 0x100000 (1 MB) reserved address space and 0x1000 (4K) committed memory.

The linker accepts almost any value for heap reserve space, because the application loader ensures that the application will meet certain minimum requirements during the load process. In other words, you can link an application with an initial heap value of 1 page reserved address space. The linker doesn't perform any data validation; it simply marks the executable with the given value. Yet, since the minimum range of address space that can be reserved is 16 pages (64K), the loader compensates by reserving 16 pages for the application heap at load time.

As indicated above, options exist that indicate how much memory should initially be committed for an application's default heap. The problem is they don't seem to work yet. The linker for the second beta release of Windows NT marks all executable applications with 0x1000 (4K) initial committed memory for the default heap size, regardless of the value indicated as an option. Yet this is not that big a deal because it actually may be better for an application to commit as it needs to, rather than to commit memory that is not being used.

### A Default Heap That Grows and Spreads 

In its simplest form, the default heap spans a range of addresses. Some ranges are reserved, while others are committed and have pages of memory associated with them. In this case the addresses are contiguous, and they all originated from the same base allocation address. In some cases the default heap needs to allocate more memory than is available in its current reserved address space. For these cases the heap can either fail the call that requests the memory, or reserve an additional address range elsewhere in the process. The default heap manager opts for the second choice.

When the default heap needs more memory than is currently available, it reserves another 1-MB address range in the process. It also initially commits as much memory as it needs from this reserved address range to satisfy the allocation request. The default heap manager is then responsible for managing this new memory region as well as the original heap space. If necessary, it will repeat this throughout the application until the process runs out of memory and address space. You could end up with a default heap that manifests itself in your process in a manner similar to the heap represented in Figure 2.
![ms810603.heapmm_2(en-us,MSDN.10).gif](https://chatgpt.com/c/images/ms810603.heapmm_2(en-us,msdn.10).gif) 

**Figure 2. The default heap for each process can expand into free address regions within the process.** 
So the default heap is not really a static heap at all. In fact, it may seem like a waste of energy to bother with managing the size of the initial heap since the heap always behaves in the same way after initialization. Managing the size of the default heap offers one advantage, though. It takes time to locate and reserve a new range of addresses in a process; you can save time by simply reserving a large enough address range initially. If you expect your application to require more heap space than the 1-MB default, reserve more address space initially to avoid allocating another region of addresses in your process later. Remember, each application has 2 gigabytes (GB) of address space to work with, and requires very little physical memory to support it.

## Global and Local Memory Functions 

At first glance it appears that the local and global memory management functions exist in Windows purely for backward compatibility with Windows version 3.1. This may be true, but the functions are managed as efficiently as the new heap functions discussed below. In fact, porting an application from 16-bit Windows does not necessarily include migrating from global and local memory functions to heap memory functions. The global and local functions offer the same basic capabilities (and then some) and are just as fast to work with. If anything, they are probably more convenient to work with because you do not have to keep track of a heap handle.
Nonetheless, the implementation of these functions is not the same as it was for 16-bit Windows. 16-bit Windows had a global heap, and each application had a local heap. Those two heap managers implemented the global and local functions. Allocating memory via **GlobalAlloc**  meant retrieving a chunk of memory from the global heap, while **LocalAlloc**  allocated memory from the local heap. Windows now has a single heap for both types of functions—the default heap described above.Now you're probably wondering if there is any difference between the local and global functions themselves. Well, the answer is no, they are now the same. In fact, they are interchangeable. Memory allocated via a call to **LocalAlloc**  can be reallocated with **GlobalReAlloc**  and then locked by **LocalLock** . The following table lists the global and local functions now available.
### Table 2 
| Global memory functions | Local memory functions | 
| --- | --- | 
| GlobalAlloc | LocalAlloc | 
| GlobalDiscard | LocalDiscard | 
| GlobalFlags | LocalFlags | 
| GlobalFree | LocalFree | 
| GlobalHandle | LocalHandle | 
| GlobalLock | LocalLock | 
| GlobalReAlloc | LocalReAlloc | 
| GlobalSize | LocalSize | 
| GlobalUnlock | LocalUnlock | 

It seems redundant to have two sets of functions that perform exactly the same, but that's where the backward compatibility comes in. Whether you used the global or local functions in a 16-bit Windows application before doesn't matter now—they are equally efficient.

### Types of Global and Local Memory 
In the Windows API, the global and local memory management functions provide two types of memory, MOVEABLE and FIXED. MOVEABLE memory can be further qualified as DISCARDABLE memory. When you allocate memory with either **GlobalAlloc**  or **LocalAlloc** , you designate the type of memory you want by supplying the appropriate memory flag. The following table lists and describes each memory flag for global and local memory.
### Table 3 
| Global memory flag | Local memory flag | Allocation meaning | 
| --- | --- | --- | 
| GMEM_FIXED | LMEM_FIXED | Allocate fixed memory. | 
| GMEM_MOVEABLE | LMEM_MOVEABLE | Allocate movable memory. | 
| GMEM_DISCARDABLE | LMEM_DISCARDABLE | Allocate discardable, movable memory. | 
| GMEM_ZEROINIT | LMEM_ZEROINIT | Initialize memory to zeros during allocation. | 
| GMEM_NODISCARD | LMEM_NODISCARD | Do not discard other memory to meet the needs of this allocation; instead, fail this request. | 
| GMEM_NOCOMPACT | LMEM_NOCOMPACT | Do not discard or move other memory to meet the needs of this allocation; instead, fail this request. | 
| GMEM_SHARE, GMEM_DDESHARE | N/A | Allocate global memory that is more efficient to use with DDE. | 

It is surprising that the distinction between FIXED and MOVEABLE memory still exists in these functions. In 16-bit Windows, MOVEABLE memory compacted the local and global heaps to reduce fragmentation and make more memory available to all applications. Yet the Windows NT virtual memory system does not rely on these techniques for efficient memory management and has little to gain by applications using them. In any case, they still exist and could actually be used in some circumstances.
When allocating FIXED memory in Windows, the **GlobalAlloc**  and **LocalAlloc**  functions return a 32-bit pointer to the memory block rather than a handle as they do for MOVEABLE memory. The pointer can directly access the memory without having to lock it first. This pointer can also be passed to the **GlobalFree**  and **LocalFree**  functions to release the memory without having to first retrieve the handle by calling the **GlobalHandle**  function. With FIXED memory, allocating and freeing memory is similar to using the C run-time functions **_malloc**  and **_free** .MOVEABLE memory, on the other hand, cannot provide this luxury. Because MOVEABLE memory can be moved (and DISCARDABLE memory can be discarded), the heap manager needs a handle to identify the chunk of memory to move or discard. To access the memory, the handle must first be locked by calling either **GlobalLock**  or **LocalLock** . As in 16-bit Windows, the memory cannot be moved or discarded while the handle is locked.
### The MOVEABLE Memory Handle Table 

As it turns out, each handle to MOVEABLE memory is actually a pointer into the MOVEABLE memory handle table. The handle table exists outside the heap, elsewhere in the process's address space. To learn more about this behavior, we created a test application that allocates several MOVEABLE memory blocks from the default heap. The handle table was created only upon allocation of the first MOVEABLE chunk of memory. This is nice, because if you never allocate any MOVEABLE memory, the table is never created and does not waste memory. ProcessWalker reveals that when this handle table is created, 1 page of memory is committed for the initial table and 512K of address space is reserved (see Figure 3).
![ms810603.heapmm_3(en-us,MSDN.10).gif](https://chatgpt.com/c/images/ms810603.heapmm_3(en-us,msdn.10).gif) 

**Figure 3. ProcessWalker highlights changes in the address space of a process. The heap memory handle table is shown as it looks immediately after it is created.** 
If you work out the math you can see that the number of memory handles available for MOVEABLE memory is limited. 512K bytes / 8 bytes per handle = 65,535 handles. In fact, the system imposes this limitation on each process. Fortunately, this only applies to MOVEABLE memory. You can allocate as many chunks of FIXED memory as you like, provided the memory and address space are available in your process.

Each handle requires 8 bytes of committed memory in the handle table to represent information, including the virtual address of the memory, the lock count on the handle, and the type of memory. Figure 4 shows how the handle table looks when viewed in ProcessWalker.
![ms810603.heapmm_4(en-us,MSDN.10).gif](https://chatgpt.com/c/images/ms810603.heapmm_4(en-us,msdn.10).gif) 

**Figure 4. Each MOVEABLE memory handle is 8 bytes and represents the location of the chunk of memory.** 
> **Note**  In the ProcessWalker view window, each line is 16 bytes (two memory handles). The far-left column represents the address of each line within the process. The addresses in white indicate the lines in which data changed since the last refresh. Red text shows exactly which bytes changed. This feature allows you to easily track changes in memory in response to certain events within the child process. A very useful debugging tool, to say the least.
The first 8 bytes in the view window—at address 0x000f0000—show the first handle allocated in the table. The handle value for this example would actually be 0x000f0004, which is a 4-byte offset into the 8-byte handle table entry. At the 4-byte offset in the table entry is the current 32-bit address representing the location of the chunk of memory. In this example, the 32-bit address is 0x00042A70, reading 4 bytes from right to left starting at 0x000f0008 and ending at 0x000f0004. If the memory is moved to a new location, this address changes to reflect the new location.
If you back up 4 bytes from the handle to the first byte in this handle table entry, you'll find the lock count for the handle. Remember, a block of memory can be moved or discarded only if its handle's lock count is zero. Since there is only 1 byte to record the lock count, it stands to reason that a handle can be locked only 256 (0xFF) times. Unfortunately, the system currently does not warn you when you reach that limit. If you lock a handle a 257th time, you receive a valid pointer to the memory, but the lock count remains at 256. It is possible, then, that you could unlock the handle 256 times and expect the memory to be locked. Yet the lock count is decremented to 0, and the memory could be moved or discarded. So what happens if you try to access the pointer you believe to be valid? Well, it depends on what is now at the address where you believe the memory to be. The memory could still be there, or some other memory could have been moved there. This is not the desired behavior, and we hope the system will be fixed to prevent this from happening. Incidentally, how should the system be fixed? The easiest thing to do would be to fail the call to **GlobalLock**  or **LocalLock**  on any attempt beyond 256, so check the return value to make sure the function succeeds.
The third and fourth bytes of the handle represent the memory type, that is, MOVEABLE, DDESHARE, or DISCARDABLE. Presumably because of compatibility with 16-bit Windows, local and global memory flags that have the same name and meaning do not have the same value. (The WINBASE.H header file defines each flag.) Yet once the memory is allocated, the handle table entry records no difference. Whether you use LMEM_DISCARDABLE or GMEM_DISCARDABLE does not matter—the handle table identifies all DISCARDABLE memory the same way. A little exploring in ProcessWalker shows the following type value identifiers.

### Table 4 
| Memory type | Byte 3 | Byte 4 | 
| --- | --- | --- | 
| MOVEABLE | 02 | – | 
| DISCARDABLE | 06 | – | 
| DDESHARE | – | 08 | 

Keep in mind that these values as represented in the handle table are not documented, so they could change with a new release of Windows NT. But it would be easy to use ProcessWalker to view the handle table to see the changes.

Returning to the test application example.... After allocating the first MOVEABLE memory block and thereby creating the handle table, we used the test application to allocate 15 more handles from the table. A quick view of the memory window showed the first eight lines had data associated with them, while the rest of the committed page was filled with zeros. Then we allocated one more handle, making a total of 17 handles. The view window was refreshed to indicate what changes occurred in the table as a result of allocating the seventeenth handle only. Figure 4 (above) shows the results.

As you can see, more than 8 bytes changed during the last allocation. In fact, 8 lines were updated for a total of 128 bytes. The first 8 bytes represent the seventeenth handle entry information as expected. The following 120 bytes indicate that the heap manager initializes the handle table every sixteenth handle. Examining this initialization data shows that the next 15 available handle table entries are identified in the table. When allocating the eighteenth handle, the location of the nineteenth handle is identified by the address location portion of the eighteenth handle table entry. As expected, then, if a handle is removed from the table (the memory is freed), the address location in that entry is replaced with the location of the next available handle after it. This behavior indicates that the heap manager keeps the location of the next available handle table entry in a static variable and uses that entry itself to store the location of the subsequent entry. Notice also that the last initialized entry has a null location for the next address. The heap manager uses this as an indicator to initialize another 16 handle table entries during the next handle allocation.

Another efficiency in the heap manager is its ability to commit pages of memory for the handle table as it needs them, not all 128 pages (512K) at once. Since the heap manager initializes its handle table in 16-handle (128-byte) increments, it is easy to determine when to commit a new page of memory. Every thirty-second (4096 / 128 = 32) initialization requires a new page of committed memory. Also, the entries do not straddle page boundaries, so their management is easier and potentially more efficient.

### CRT Library 

Managing memory in 16-bit Windows involved a great deal of uncertainty about using the C run-time (CRT) library. Now, there should be little hesitation. The current CRT library is implemented in a manner similar to FIXED memory allocated via the local and global memory management functions. The CRT library is also implemented using the same default heap manager as the global and local memory management functions.
Subsequent memory allocations via **malloc** , **GlobalAlloc** , and **LocalAlloc**  return pointers to memory allocated from the same heap. The heap manager does not divide its space among the CRT and global/local memory functions, and it does not maintain separate heaps for these functions. Instead, it treats them the same, promoting consistent behavior across the types of functions. As a result, you can now write code using the functions you're most comfortable with. And, if you're interested in portability, you can safely use the CRT functions exclusively for managing heap memory.
## Heap Memory API 
As mentioned earlier, you can create as many dynamic heaps as you like by simply calling **HeapCreate** . You must specify the maximum size of the heap so that the function knows how much address space to reserve. You can also indicate how much memory to commit initially. In the following example, a heap is created in your process that reserves 1 MB of address space and initially commits two pages of memory:

```plaintext
hHeap = HeapCreate (0, 0x2000, 0x100000);
```
Since you can have many dynamic heaps in your process, you need a handle to identify each heap when you access it. The **HeapCreate**  function returns this handle. Each heap you create returns a unique handle so that several dynamic heaps may coexist in your process. Having to identify your heap by handle also makes managing dynamic heaps more difficult than managing the default heap, since you have to keep each heap handle around for the life of the heap.If you're bothered by having to keep this handle around, there is an alternative. You can use the heap memory functions on the default heap instead of creating a dynamic heap explicitly for them. To do this, simply use the **GetProcessHeap**  function to get the handle of the default heap. For simple allocations of short-term memory, the following example taken from the ProcessWalker sample application illustrates how easy this is to do:

```plaintext
char    *szCaption;
int     nCaption = GetWindowTextLength (hWnd);

/* retrieve view memory range */
szCaption = HeapAlloc (GetProcessHeap (), 
                       HEAP_ZERO_MEMORY, 
                       nCaption+1);
GetWindowText (hViewWnd, szCaption, nCaption);
```

In this example the default heap is chosen because the allocation is independent of other memory management needs, and there is no reason to create a dynamic heap just for this one allocation. Note that you could achieve the same result by using the global, local, or CRT functions since they allocate only from the default heap.
As shown earlier, the first parameter to **HeapCreate**  allows you to specify an optional HEAP_NO_SERIALIZE flag. A serialized heap does not allow two threads to access it simultaneously. The default behavior is to serialize access to the heap. If you plan to use a heap strictly within one thread, specifying the HEAP_NO_SERIALIZE flag improves overall heap performance slightly.Like all of the heap memory functions, **HeapAlloc**  requires a heap handle as its first argument. The example uses the **GetProcessHeap**  function instead of a dynamic heap handle. The second parameter to **HeapAlloc**  is an optional flag that indicates whether the memory should be zeroed first and whether to generate exceptions on error. To get zeroed memory, specify the HEAP_ZERO_MEMORY flag as shown above. The generate exceptions flag (HEAP_GENERATE_EXCEPTIONS) is a useful feature if you have exception handling built into your application. When using this flag, the function raises an exception on failure rather than just returning NULL. Depending on your use, exception handling can be an effective way of triggering special events—such as low memory situations—in your application.**HeapAlloc**  has a cousin called **HeapReAlloc**  that works in much the same way as the standard global and local memory management functions described earlier. Use **HeapReAlloc**  primarily to resize a previous allocation. This function has four parameters, three of which are the same as for **HeapAlloc** . The new parameter, *lpMem*, is a pointer to the chunk of memory being resized.It is important to note that although heap memory is not movable as in global and local memory, it may be moved during the **HeapReAlloc**  function. This function returns a pointer to the resized chunk of memory, which may or may not be at the same location as initially indicated by the pointer passed to the function. This is the only time memory can be moved in dynamic heaps, and the only chunk of memory affected is the one identified by *lpMem* in the function. You can also override this behavior by specifying the HEAP_REALLOC_IN_PLACE_ONLY flag. With this flag, if there is not enough room to reallocate the memory in place, the function returns with failure status rather than move the memory.Memory allocated with **HeapAlloc**  or reallocated with **HeapReAlloc**  can be freed by calling **HeapFree** . This function is easy to use: simply indicate the heap handle and a pointer to the chunk of memory to free. Completing the example above, here is how you can use **HeapFree**  with the default heap:

```plaintext
/* free default heap memory */
HeapFree (GetProcessHeap (), szCaption);
```

This example shows how easy it can be to work with heaps in Windows. However, you may still want to create a dynamic heap specifically to manage complex dynamic data structures in your application. In fact, one nice benefit of heap memory is how well it caters to the needs of traditional data structures such as binary trees, linked lists, and dynamic arrays. Having the heap handle provides a way of uniquely identifying these structures independently. One example that comes to mind is when you're building a multiwindow application—perhaps a multiple document interface (MDI) application. Simply create and store a heap handle in the window extra bytes or window property list for each window during the WM_CREATE message. Then it is easy to write a window procedure that manages data structures from its own heap by retrieving the heap handle when necessary. When the window goes away, simply have it destroy the heap in the WM_DESTROY message.
You can easily destroy dynamic heaps by calling **HeapDestroy**  on a specific heap handle. This powerful function will remove a heap regardless of its state. The **HeapDestroy**  function doesn't care whether you have outstanding allocations in the heap or not.
To make heap memory management most efficient, you would only create a heap of the size you need. In some cases it is easy to determine the heap size you need—if you're allocating a buffer to read a file into, simply check the size of the file. In other cases, heap size is more difficult to figure—if you're creating a dynamic data structure that grows according to user interaction, it is difficult to predict what the user will do. Dynamic heaps have a provision for this latter circumstance. By specifying a maximum heap size of zero, you make the heap assume a behavior like the default heap. That is, it will grow and spread in your process as much as necessary, limited only by available memory. In this case, available memory means available address space in your process and available pagefile space on your hard disk.

## Overhead on Heap Memory Allocations 

With all types of heap memory, an overhead is associated with each memory allocation. This overhead is due to:

- Granularity on memory allocations within the heap.

- The overhead necessary to manage each memory segment within the heap.

The granularity of heap allocations in 32-bit Windows is 16 bytes. So if you request a global memory allocation of 1 byte, the heap returns a pointer to a chunk of memory, guaranteeing that the 1 byte is available. Chances are, 16 bytes will actually be available because the heap cannot allocate less than 16 bytes at a time.

### Global and Local Memory Functions 
For global and local memory functions, the documentation suggests that you use the **GlobalSize**  and **LocalSize**  functions to determine the exact size of the allocation, but in my tests this function consistently returned the size I requested and not the size actually allocated.To confirm this finding, turn to ProcessWalker again and view the committed memory in your default heap. For the sake of observation, perform consecutive allocations of 1, 2, 3, 14, 15, and 16 bytes using either **GlobalAlloc**  or **LocalAlloc** . In this particular example, we used **GlobalAlloc**  with the GMEM_MOVEABLE flag, but the result is the same for memory allocated as GMEM_FIXED. Then, refresh your view of the committed memory in the heap. Finally, scroll the view window so that the addresses of the allocated blocks of memory are all in view. You should see something similar to the window in Figure 5.![ms810603.heapmm_5(en-us,MSDN.10).gif](https://chatgpt.com/c/images/ms810603.heapmm_5(en-us,msdn.10).gif) 

Figure 5. A ProcessWalker view of the default heap after making consecutive allocations of 1, 2, 3, 14, 15, and 16 bytes using the *GlobalAlloc* function.** In Figure 5, the first line represents the header for the 1-byte allocation, followed immediately by the minimum 16 bytes allocated for the 1-byte request. Just to add visual clarity, the letter *m* appears in each allocated byte beginning at the address of the allocation. The *m*'s are visible in the ASCII representation of memory to the right of each line. At the end of all heap allocations is a heap tail, as indicated by the last line of new information in Figure 5.So, although you request only 1 byte and **GlobalSize**  returns a size of 1 byte, there are actually 16 bytes allocated and available. Similarly, for the 3-byte allocation, 13 additional bytes are available. Even more interesting is the apparent waste of memory for allocations of 14, 15, and 16 bytes. In these allocations an additional 16 bytes were allocated for no reason. These are the lines immediately following the lines with 14, 15, and 16 *m* characters. Presumably you could also use these extra 16 bytes, but again **GlobalSize**  does not indicate their existence.
So what is the cost of allocating from a heap? Well, it depends on the size of the allocation. Every 1-byte allocation uses a total of 32 bytes, and a 16-byte allocation uses a total of 48 bytes. This is a considerable amount of overhead on smaller allocations. Therefore, it would not be a good idea to accumulate a number of small heap allocations because they would cost a great deal in actual memory used. On the other hand, there is nothing wrong with allocating a large chunk of memory from the heap and dividing it into smaller pieces.

### Heap Memory Functions 
Similar to the global and local memory functions, the heap memory functions have a minimum 16-byte granularity and the same overhead on memory allocations. Figure 6 presents a ProcessWalker view of a dynamic heap using the same allocations of 1, 2, 3, 14, 15, and 16 bytes, but this time using the **HeapAlloc**  function.![ms810603.heapmm_6(en-us,MSDN.10).gif](https://chatgpt.com/c/images/ms810603.heapmm_6(en-us,msdn.10).gif) 

**
Here's the entire content converted to markdown, including the table:


```markdown
# Managing Heap Memory

**Randy Kath**  
Microsoft Developer Network Technology Group

Created: April 3, 1993

## Abstract

Determining which function or set of functions to use for managing memory in your application is difficult without a solid understanding of how each group of functions works and the overall impact they each have on the operating system. In an effort to simplify these decisions, this technical article focuses on the use of heaps in Windows: the functions that are available, the way they are used, and the impact their use has on operating system resources. The following topics are discussed:

- The purpose of heaps
- General heap behavior
- The two types of heaps
- Global and local memory functions
- Heap memory functions
- Overhead on heap memory allocations
- Summary and recommendations

In addition to this technical article, a sample application called ProcessWalker is included on the Microsoft Developer Network CD. This sample application explores the behavior of heap memory functions in a process, and it provides several useful implementation examples.

## Introduction

This is one of three related technical articles—"Managing Virtual Memory," "Managing Memory-Mapped Files," and "Managing Heap Memory"—that explain how to manage memory using the Windows API (application programming interface). This introduction identifies the basic memory components in the programming model and indicates which article to reference for specific areas of interest.

The first version of the Microsoft® Windows™ operating system introduced a method of managing dynamic memory based on a single _global heap_, which all applications and the system share, and multiple, private _local heaps_, one for each application. Local and global memory management functions were also provided, offering extended features for this new memory management system. More recently, the Microsoft C run-time (CRT) libraries were modified to include capabilities for managing these heaps in Windows using native CRT functions such as **malloc** and **free**. Consequently, developers are now left with a choice—learn the new API provided as part of Windows version 3.1 or stick to the portable, and typically familiar, CRT functions for managing memory in applications written for 16-bit Windows.

Windows offers three groups of functions for managing memory in applications: memory-mapped file functions, heap memory functions, and virtual memory functions.

![ms810603.heapmm_1(en-us,MSDN.10).gif](images/ms810603.heapmm_1(en-us,msdn.10).gif)
**Figure 1. The Windows API provides different levels of memory management for versatility in application programming.**

Six sets of memory management functions exist in Windows, as shown in Figure 1, all of which were designed to be used independently of one another. So which set of functions should you use? The answer to this question depends greatly on two things: the type of memory management you want, and how the functions relevant to it are implemented in the operating system. In other words, are you building a large database application where you plan to manipulate subsets of a large memory structure? Or maybe you're planning some simple dynamic memory structures, such as linked lists or binary trees? In both cases, you need to know which functions offer the features best suited to your intention and exactly how much of a resource hit occurs when using each function.

The following table categorizes the memory management function groups and indicates which of the three technical articles in this series describes each group's behavior. Each technical article emphasizes the impact these functions have on the system by describing the behavior of the system in response to using the functions.

### Table 1

| Memory set                   | System resource affected                                                                                         | Related technical article          |
|------------------------------|------------------------------------------------------------------------------------------------------------------|------------------------------------|
| Virtual memory functions     | A process's virtual address space<br>System pagefile<br>System memory<br>Hard disk space                         | "Managing Virtual Memory"          |
| Memory-mapped file functions | A process's virtual address space<br>System pagefile<br>Standard file I/O<br>System memory<br>Hard disk space    | "Managing Memory-Mapped Files"     |
| Heap memory functions        | A process's virtual address space<br>System memory<br>Process heap resource structure                            | "Managing Heap Memory"             |
| Global heap memory functions | A process's heap resource structure                                                                              | "Managing Heap Memory"             |
| Local heap memory functions  | A process's heap resource structure                                                                              | "Managing Heap Memory"             |
| C run-time reference library | A process's heap resource structure                                                                              | "Managing Heap Memory"             |

Each technical article discusses issues surrounding the use of Windows-specific functions.

## The Purpose of Heaps

The Windows subsystem on Windows NT provides high-level memory management functions that make it easy for applications to build dynamic data structures, provide compatibility with previous versions of Windows, and create buffers and temporary placeholders for system functions. These memory management functions return handles and pointers to blocks of memory that are allocated at run time and managed by an entity called the _heap_. The heap's primary function is to efficiently manage the memory and address space of a process for an application.

A tall order, considering the heap has absolutely no idea what the application intends to do with its memory and address space. Yet the heap manages to provide a robust set of functions that allow developers to overlook some of the finer details of system resources (such as the difference between reserved, free, and committed memory) so that they can turn their attention to the more important task at hand, that of implementing their applications.

In Windows NT, heaps provide a smaller granularity for the size of the smallest allocatable chunk of memory than the virtual memory management functions do. Applications typically need to allocate a specific number of bytes to fulfill a parameter request or to act as a temporary buffer. For example, when loading a string resource with the **LoadString** function, an application passes a pointer to a buffer that receives the string resource. The size of the buffer must be large enough to hold the string and a null terminator. Without the heap manager, applications would be forced to use the virtual memory management functions, which allocate a minimum of one page of memory at a time.

## General Heap Behavior

While the heap does provide support for managing smaller chunks of memory, it is itself nothing more than a chunk of memory implemented in the Windows NT virtual memory system. Consequently, the techniques that the heap uses to manage memory are based on the virtual memory management functions available to the heap. Evidence of this is found in the way heaps manifest themselves in a process, if only we could observe this behavior....

The ProcessWalker (PW) sample application explores each of the components within a process, including all of its heaps. PW identifies the heaps in a process and shows the amount of reserved and committed memory associated with a particular heap. As with all other regions of memory in a process, the smallest region of committed memory within a heap is one page (4096 bytes).

This does not mean that the smallest amount of memory that can be allocated in a heap is 4096 bytes; rather, the heap manager commits pages of memory as needed to satisfy specific allocation requests. If, for example, an application allocates 100 bytes via a call to **GlobalAlloc**, the heap manager allocates a 100-byte chunk of memory within its committed region for this request. If there is not enough committed memory available at the time of the request, the heap manager simply commits another page to make the memory available.

Ideally, then, if an application repetitively allocates 100-byte chunks of memory, the heap will commit an additional page of memory every forty-first request (40 * 100 bytes = 4000 bytes). Upon the forty-first request for a chunk of 100 bytes, the heap manager realizes there is not enough committed memory to satisfy the request, so it commits another page of memory and then completes the requested allocation. In this way, the heap manager is responsible for managing the virtual memory environment completely transparent of the application.

In reality, though, the heap manager requires additional memory for managing the memory in the heap. So instead of allocating only 100 bytes as requested, it also allocates some space for managing each particular chunk of memory. The type of memory and the size of the allocation determine the size of this additional memory. I'll discuss these issues later in this article.

## The Two Types of Heaps

Every process in Windows has one heap called the _default heap_. Processes can also have as many other _dynamic heaps_ as they wish, simply by creating and destroying them on the fly. The system uses the default heap for all global and local memory management functions, and the C run-time library uses the default heap for supporting **malloc** functions. The heap memory functions, which indicate a specific heap by its handle, use dynamic heaps. The behavior of dynamic heaps is discussed in the "Heap Memory API" section later in this article.

The default and dynamic heaps are basically the same thing, but the default heap has the special characteristic of being identifiable as the default. This is how the C run-time library and the system identify which heap to allocate from. The **GetProcessHeap** function returns a handle to the default heap for a process. Since functions such as **GlobalAlloc** or **malloc** are executed within the context of the thread that called them, they can simply call **GetProcessHeap** to retrieve a handle to the default heap, and then manage memory accordingly.

### Managing the Default Heap

Both default and dynamic heaps have a specific amount of reserved and committed memory regions associated with them, but they behave differently with respect to these limits. The default heap's reserved and committed memory region sizes are designated when the application is linked. Each application carries this information about itself within its executable image information. You can view this information by dumping header information for the executable image. For example, type the following command at a Windows NT command prompt (PWALK.EXE is used here to complete the example; you will need to substitute your own path and executable file):

```plaintext
link32 -dump -headers d:\samples\walker\pwalk.exe

...
OPTIONAL HEADER VALUES             
     10B magic #                   
    2.29 linker version            
    B000 size of code              
   1E800 size of initialized data  
     600 size of uninitialized data
   18470 address of entry point    
   10000 base of code              
   20000 base of data              
         ----- new -----           
  400000 image base                
   10000 section alignment         
     200 file alignment            
       2 subsystem (Windows GUI)   
     0.B operating system version  
     1.0 image version             
     3.A subsystem version         
   C0000 size of image             
     400 size of headers           
       0 checksum                  
   10000 size of stack reserve     
    1000 size of stack commit      
   10000 size of heap reserve      
    1000 size of heap commit       
   ...
```

The last two entries are hexadecimal values specifying the amount of reserved and committed space initially needed by the application.

There are two ways to tell the linker what to use for these values. You can link your application with a module definition file and include a statement in the file like the following:


```plaintext
HEAPSIZE   0x10000 0x1000
```
Or you can directly inform the linker by using the **/HEAP**  linker switch, as in:

```plaintext
/HEAP: 0x10000, 0x1000
```

In both examples, the heap is specified to initially have 0x10000 (64K) bytes reserved address space and 0x1000 (4K) bytes committed memory. If you fail to indicate the heap size in either method, the linker uses the default values of 0x100000 (1 MB) reserved address space and 0x1000 (4K) committed memory.

The linker accepts almost any value for heap reserve space, because the application loader ensures that the application will meet certain minimum requirements during the load process. In other words, you can link an application with an initial heap value of 1 page reserved address space. The linker doesn't perform any data validation; it simply marks the executable with the given value. Yet, since the minimum range of address space that can be reserved is 16 pages (64K), the loader compensates by reserving 16 pages for the application heap at load time.

As indicated above, options exist that indicate how much memory should initially be committed for an application's default heap. The problem is they don't seem to work yet. The linker for the second beta release of Windows NT marks all executable applications with 0x1000 (4K) initial committed memory for the default heap size, regardless of the value indicated as an option. Yet this is not that big a deal because it actually may be better for an application to commit as it needs to, rather than to commit memory that is not being used.

### A Default Heap That Grows and Spreads 

In its simplest form, the default heap spans a range of addresses. Some ranges are reserved, while others are committed and have pages of memory associated with them. In this case the addresses are contiguous, and they all originated from the same base allocation address. In some cases the default heap needs to allocate more memory than is available in its current reserved address space. For these cases the heap can either fail the call that requests the memory, or reserve an additional address range elsewhere in the process. The default heap manager opts for the second choice.

When the default heap needs more memory than is currently available, it reserves another 1-MB address range in the process. It also initially commits as much memory as it needs from this reserved address range to satisfy the allocation request. The default heap manager is then responsible for managing this new memory region as well as the original heap space. If necessary, it will repeat this throughout the application until the process runs out of memory and address space. You could end up with a default heap that manifests itself in your process in a manner similar to the heap represented in Figure 2.
![ms810603.heapmm_2(en-us,MSDN.10).gif](https://chatgpt.com/c/images/ms810603.heapmm_2(en-us,msdn.10).gif) 

**Figure 2. The default heap for each process can expand into free address regions within the process.** 
So the default heap is not really a static heap at all. In fact, it may seem like a waste of energy to bother with managing the size of the initial heap since the heap always behaves in the same way after initialization. Managing the size of the default heap offers one advantage, though. It takes time to locate and reserve a new range of addresses in a process; you can save time by simply reserving a large enough address range initially. If you expect your application to require more heap space than the 1-MB default, reserve more address space initially to avoid allocating another region of addresses in your process later. Remember, each application has 2 gigabytes (GB) of address space to work with, and requires very little physical memory to support it.

## Global and Local Memory Functions 

At first glance it appears that the local and global memory management functions exist in Windows purely for backward compatibility with Windows version 3.1. This may be true, but the functions are managed as efficiently as the new heap functions discussed below. In fact, porting an application from 16-bit Windows does not necessarily include migrating from global and local memory functions to heap memory functions. The global and local functions offer the same basic capabilities (and then some) and are just as fast to work with. If anything, they are probably more convenient to work with because you do not have to keep track of a heap handle.
Nonetheless, the implementation of these functions is not the same as it was for 16-bit Windows. 16-bit Windows had a global heap, and each application had a local heap. Those two heap managers implemented the global and local functions. Allocating memory via **GlobalAlloc**  meant retrieving a chunk of memory from the global heap, while **LocalAlloc**  allocated memory from the local heap. Windows now has a single heap for both types of functions—the default heap described above.Now you're probably wondering if there is any difference between the local and global functions themselves. Well, the answer is no, they are now the same. In fact, they are interchangeable. Memory allocated via a call to **LocalAlloc**  can be reallocated with **GlobalReAlloc**  and then locked by **LocalLock** . The following table lists the global and local functions now available.
### Table 2 
| Global memory functions | Local memory functions | 
| --- | --- | 
| GlobalAlloc | LocalAlloc | 
| GlobalDiscard | LocalDiscard | 
| GlobalFlags | LocalFlags | 
| GlobalFree | LocalFree | 
| GlobalHandle | LocalHandle | 
| GlobalLock | LocalLock | 
| GlobalReAlloc | LocalReAlloc | 
| GlobalSize | LocalSize | 
| GlobalUnlock | LocalUnlock | 

It seems redundant to have two sets of functions that perform exactly the same, but that's where the backward compatibility comes in. Whether you used the global or local functions in a 16-bit Windows application before doesn't matter now—they are equally efficient.

### Types of Global and Local Memory 
In the Windows API, the global and local memory management functions provide two types of memory, MOVEABLE and FIXED. MOVEABLE memory can be further qualified as DISCARDABLE memory. When you allocate memory with either **GlobalAlloc**  or **LocalAlloc** , you designate the type of memory you want by supplying the appropriate memory flag. The following table lists and describes each memory flag for global and local memory.
### Table 3 
| Global memory flag | Local memory flag | Allocation meaning | 
| --- | --- | --- | 
| GMEM_FIXED | LMEM_FIXED | Allocate fixed memory. | 
| GMEM_MOVEABLE | LMEM_MOVEABLE | Allocate movable memory. | 
| GMEM_DISCARDABLE | LMEM_DISCARDABLE | Allocate discardable, movable memory. | 
| GMEM_ZEROINIT | LMEM_ZEROINIT | Initialize memory to zeros during allocation. | 
| GMEM_NODISCARD | LMEM_NODISCARD | Do not discard other memory to meet the needs of this allocation; instead, fail this request. | 
| GMEM_NOCOMPACT | LMEM_NOCOMPACT | Do not discard or move other memory to meet the needs of this allocation; instead, fail this request. | 
| GMEM_SHARE, GMEM_DDESHARE | N/A | Allocate global memory that is more efficient to use with DDE. | 

It is surprising that the distinction between FIXED and MOVEABLE memory still exists in these functions. In 16-bit Windows, MOVEABLE memory compacted the local and global heaps to reduce fragmentation and make more memory available to all applications. Yet the Windows NT virtual memory system does not rely on these techniques for efficient memory management and has little to gain by applications using them. In any case, they still exist and could actually be used in some circumstances.
When allocating FIXED memory in Windows, the **GlobalAlloc**  and **LocalAlloc**  functions return a 32-bit pointer to the memory block rather than a handle as they do for MOVEABLE memory. The pointer can directly access the memory without having to lock it first. This pointer can also be passed to the **GlobalFree**  and **LocalFree**  functions to release the memory without having to first retrieve the handle by calling the **GlobalHandle**  function. With FIXED memory, allocating and freeing memory is similar to using the C run-time functions **_malloc**  and **_free** .MOVEABLE memory, on the other hand, cannot provide this luxury. Because MOVEABLE memory can be moved (and DISCARDABLE memory can be discarded), the heap manager needs a handle to identify the chunk of memory to move or discard. To access the memory, the handle must first be locked by calling either **GlobalLock**  or **LocalLock** . As in 16-bit Windows, the memory cannot be moved or discarded while the handle is locked.
### The MOVEABLE Memory Handle Table 

As it turns out, each handle to MOVEABLE memory is actually a pointer into the MOVEABLE memory handle table. The handle table exists outside the heap, elsewhere in the process's address space. To learn more about this behavior, we created a test application that allocates several MOVEABLE memory blocks from the default heap. The handle table was created only upon allocation of the first MOVEABLE chunk of memory. This is nice, because if you never allocate any MOVEABLE memory, the table is never created and does not waste memory. ProcessWalker reveals that when this handle table is created, 1 page of memory is committed for the initial table and 512K of address space is reserved (see Figure 3).
![ms810603.heapmm_3(en-us,MSDN.10).gif](https://chatgpt.com/c/images/ms810603.heapmm_3(en-us,msdn.10).gif) 

**Figure 3. ProcessWalker highlights changes in the address space of a process. The heap memory handle table is shown as it looks immediately after it is created.** 
If you work out the math you can see that the number of memory handles available for MOVEABLE memory is limited. 512K bytes / 8 bytes per handle = 65,535 handles. In fact, the system imposes this limitation on each process. Fortunately, this only applies to MOVEABLE memory. You can allocate as many chunks of FIXED memory as you like, provided the memory and address space are available in your process.

Each handle requires 8 bytes of committed memory in the handle table to represent information, including the virtual address of the memory, the lock count on the handle, and the type of memory. Figure 4 shows how the handle table looks when viewed in ProcessWalker.
![ms810603.heapmm_4(en-us,MSDN.10).gif](https://chatgpt.com/c/images/ms810603.heapmm_4(en-us,msdn.10).gif) 

**Figure 4. Each MOVEABLE memory handle is 8 bytes and represents the location of the chunk of memory.** 
> **Note**  In the ProcessWalker view window, each line is 16 bytes (two memory handles). The far-left column represents the address of each line within the process. The addresses in white indicate the lines in which data changed since the last refresh. Red text shows exactly which bytes changed. This feature allows you to easily track changes in memory in response to certain events within the child process. A very useful debugging tool, to say the least.
The first 8 bytes in the view window—at address 0x000f0000—show the first handle allocated in the table. The handle value for this example would actually be 0x000f0004, which is a 4-byte offset into the 8-byte handle table entry. At the 4-byte offset in the table entry is the current 32-bit address representing the location of the chunk of memory. In this example, the 32-bit address is 0x00042A70, reading 4 bytes from right to left starting at 0x000f0008 and ending at 0x000f0004. If the memory is moved to a new location, this address changes to reflect the new location.
If you back up 4 bytes from the handle to the first byte in this handle table entry, you'll find the lock count for the handle. Remember, a block of memory can be moved or discarded only if its handle's lock count is zero. Since there is only 1 byte to record the lock count, it stands to reason that a handle can be locked only 256 (0xFF) times. Unfortunately, the system currently does not warn you when you reach that limit. If you lock a handle a 257th time, you receive a valid pointer to the memory, but the lock count remains at 256. It is possible, then, that you could unlock the handle 256 times and expect the memory to be locked. Yet the lock count is decremented to 0, and the memory could be moved or discarded. So what happens if you try to access the pointer you believe to be valid? Well, it depends on what is now at the address where you believe the memory to be. The memory could still be there, or some other memory could have been moved there. This is not the desired behavior, and we hope the system will be fixed to prevent this from happening. Incidentally, how should the system be fixed? The easiest thing to do would be to fail the call to **GlobalLock**  or **LocalLock**  on any attempt beyond 256, so check the return value to make sure the function succeeds.
The third and fourth bytes of the handle represent the memory type, that is, MOVEABLE, DDESHARE, or DISCARDABLE. Presumably because of compatibility with 16-bit Windows, local and global memory flags that have the same name and meaning do not have the same value. (The WINBASE.H header file defines each flag.) Yet once the memory is allocated, the handle table entry records no difference. Whether you use LMEM_DISCARDABLE or GMEM_DISCARDABLE does not matter—the handle table identifies all DISCARDABLE memory the same way. A little exploring in ProcessWalker shows the following type value identifiers.

### Table 4 
| Memory type | Byte 3 | Byte 4 | 
| --- | --- | --- | 
| MOVEABLE | 02 | – | 
| DISCARDABLE | 06 | – | 
| DDESHARE | – | 08 | 

Keep in mind that these values as represented in the handle table are not documented, so they could change with a new release of Windows NT. But it would be easy to use ProcessWalker to view the handle table to see the changes.

Returning to the test application example.... After allocating the first MOVEABLE memory block and thereby creating the handle table, we used the test application to allocate 15 more handles from the table. A quick view of the memory window showed the first eight lines had data associated with them, while the rest of the committed page was filled with zeros. Then we allocated one more handle, making a total of 17 handles. The view window was refreshed to indicate what changes occurred in the table as a result of allocating the seventeenth handle only. Figure 4 (above) shows the results.

As you can see, more than 8 bytes changed during the last allocation. In fact, 8 lines were updated for a total of 128 bytes. The first 8 bytes represent the seventeenth handle entry information as expected. The following 120 bytes indicate that the heap manager initializes the handle table every sixteenth handle. Examining this initialization data shows that the next 15 available handle table entries are identified in the table. When allocating the eighteenth handle, the location of the nineteenth handle is identified by the address location portion of the eighteenth handle table entry. As expected, then, if a handle is removed from the table (the memory is freed), the address location in that entry is replaced with the location of the next available handle after it. This behavior indicates that the heap manager keeps the location of the next available handle table entry in a static variable and uses that entry itself to store the location of the subsequent entry. Notice also that the last initialized entry has a null location for the next address. The heap manager uses this as an indicator to initialize another 16 handle table entries during the next handle allocation.

Another efficiency in the heap manager is its ability to commit pages of memory for the handle table as it needs them, not all 128 pages (512K) at once. Since the heap manager initializes its handle table in 16-handle (128-byte) increments, it is easy to determine when to commit a new page of memory. Every thirty-second (4096 / 128 = 32) initialization requires a new page of committed memory. Also, the entries do not straddle page boundaries, so their management is easier and potentially more efficient.

### CRT Library 

Managing memory in 16-bit Windows involved a great deal of uncertainty about using the C run-time (CRT) library. Now, there should be little hesitation. The current CRT library is implemented in a manner similar to FIXED memory allocated via the local and global memory management functions. The CRT library is also implemented using the same default heap manager as the global and local memory management functions.
Subsequent memory allocations via **malloc** , **GlobalAlloc** , and **LocalAlloc**  return pointers to memory allocated from the same heap. The heap manager does not divide its space among the CRT and global/local memory functions, and it does not maintain separate heaps for these functions. Instead, it treats them the same, promoting consistent behavior across the types of functions. As a result, you can now write code using the functions you're most comfortable with. And, if you're interested in portability, you can safely use the CRT functions exclusively for managing heap memory.
## Heap Memory API 
As mentioned earlier, you can create as many dynamic heaps as you like by simply calling **HeapCreate** . You must specify the maximum size of the heap so that the function knows how much address space to reserve. You can also indicate how much memory to commit initially. In the following example, a heap is created in your process that reserves 1 MB of address space and initially commits two pages of memory:

```plaintext
hHeap = HeapCreate (0, 0x2000, 0x100000);
```
Since you can have many dynamic heaps in your process, you need a handle to identify each heap when you access it. The **HeapCreate**  function returns this handle. Each heap you create returns a unique handle so that several dynamic heaps may coexist in your process. Having to identify your heap by handle also makes managing dynamic heaps more difficult than managing the default heap, since you have to keep each heap handle around for the life of the heap.If you're bothered by having to keep this handle around, there is an alternative. You can use the heap memory functions on the default heap instead of creating a dynamic heap explicitly for them. To do this, simply use the **GetProcessHeap**  function to get the handle of the default heap. For simple allocations of short-term memory, the following example taken from the ProcessWalker sample application illustrates how easy this is to do:

```plaintext
char    *szCaption;
int     nCaption = GetWindowTextLength (hWnd);

/* retrieve view memory range */
szCaption = HeapAlloc (GetProcessHeap (), 
                       HEAP_ZERO_MEMORY, 
                       nCaption+1);
GetWindowText (hViewWnd, szCaption, nCaption);
```

In this example the default heap is chosen because the allocation is independent of other memory management needs, and there is no reason to create a dynamic heap just for this one allocation. Note that you could achieve the same result by using the global, local, or CRT functions since they allocate only from the default heap.
As shown earlier, the first parameter to **HeapCreate**  allows you to specify an optional HEAP_NO_SERIALIZE flag. A serialized heap does not allow two threads to access it simultaneously. The default behavior is to serialize access to the heap. If you plan to use a heap strictly within one thread, specifying the HEAP_NO_SERIALIZE flag improves overall heap performance slightly.Like all of the heap memory functions, **HeapAlloc**  requires a heap handle as its first argument. The example uses the **GetProcessHeap**  function instead of a dynamic heap handle. The second parameter to **HeapAlloc**  is an optional flag that indicates whether the memory should be zeroed first and whether to generate exceptions on error. To get zeroed memory, specify the HEAP_ZERO_MEMORY flag as shown above. The generate exceptions flag (HEAP_GENERATE_EXCEPTIONS) is a useful feature if you have exception handling built into your application. When using this flag, the function raises an exception on failure rather than just returning NULL. Depending on your use, exception handling can be an effective way of triggering special events—such as low memory situations—in your application.**HeapAlloc**  has a cousin called **HeapReAlloc**  that works in much the same way as the standard global and local memory management functions described earlier. Use **HeapReAlloc**  primarily to resize a previous allocation. This function has four parameters, three of which are the same as for **HeapAlloc** . The new parameter, *lpMem*, is a pointer to the chunk of memory being resized.It is important to note that although heap memory is not movable as in global and local memory, it may be moved during the **HeapReAlloc**  function. This function returns a pointer to the resized chunk of memory, which may or may not be at the same location as initially indicated by the pointer passed to the function. This is the only time memory can be moved in dynamic heaps, and the only chunk of memory affected is the one identified by *lpMem* in the function. You can also override this behavior by specifying the HEAP_REALLOC_IN_PLACE_ONLY flag. With this flag, if there is not enough room to reallocate the memory in place, the function returns with failure status rather than move the memory.Memory allocated with **HeapAlloc**  or reallocated with **HeapReAlloc**  can be freed by calling **HeapFree** . This function is easy to use: simply indicate the heap handle and a pointer to the chunk of memory to free. Completing the example above, here is how you can use **HeapFree**  with the default heap:

```plaintext
/* free default heap memory */
HeapFree (GetProcessHeap (), szCaption);
```

This example shows how easy it can be to work with heaps in Windows. However, you may still want to create a dynamic heap specifically to manage complex dynamic data structures in your application. In fact, one nice benefit of heap memory is how well it caters to the needs of traditional data structures such as binary trees, linked lists, and dynamic arrays. Having the heap handle provides a way of uniquely identifying these structures independently. One example that comes to mind is when you're building a multiwindow application—perhaps a multiple document interface (MDI) application. Simply create and store a heap handle in the window extra bytes or window property list for each window during the WM_CREATE message. Then it is easy to write a window procedure that manages data structures from its own heap by retrieving the heap handle when necessary. When the window goes away, simply have it destroy the heap in the WM_DESTROY message.
You can easily destroy dynamic heaps by calling **HeapDestroy**  on a specific heap handle. This powerful function will remove a heap regardless of its state. The **HeapDestroy**  function doesn't care whether you have outstanding allocations in the heap or not.
To make heap memory management most efficient, you would only create a heap of the size you need. In some cases it is easy to determine the heap size you need—if you're allocating a buffer to read a file into, simply check the size of the file. In other cases, heap size is more difficult to figure—if you're creating a dynamic data structure that grows according to user interaction, it is difficult to predict what the user will do. Dynamic heaps have a provision for this latter circumstance. By specifying a maximum heap size of zero, you make the heap assume a behavior like the default heap. That is, it will grow and spread in your process as much as necessary, limited only by available memory. In this case, available memory means available address space in your process and available pagefile space on your hard disk.

## Overhead on Heap Memory Allocations 

With all types of heap memory, an overhead is associated with each memory allocation. This overhead is due to:

- Granularity on memory allocations within the heap.

- The overhead necessary to manage each memory segment within the heap.

The granularity of heap allocations in 32-bit Windows is 16 bytes. So if you request a global memory allocation of 1 byte, the heap returns a pointer to a chunk of memory, guaranteeing that the 1 byte is available. Chances are, 16 bytes will actually be available because the heap cannot allocate less than 16 bytes at a time.

### Global and Local Memory Functions 
For global and local memory functions, the documentation suggests that you use the **GlobalSize**  and **LocalSize**  functions to determine the exact size of the allocation, but in my tests this function consistently returned the size I requested and not the size actually allocated.To confirm this finding, turn to ProcessWalker again and view the committed memory in your default heap. For the sake of observation, perform consecutive allocations of 1, 2, 3, 14, 15, and 16 bytes using either **GlobalAlloc**  or **LocalAlloc** . In this particular example, we used **GlobalAlloc**  with the GMEM_MOVEABLE flag, but the result is the same for memory allocated as GMEM_FIXED. Then, refresh your view of the committed memory in the heap. Finally, scroll the view window so that the addresses of the allocated blocks of memory are all in view. You should see something similar to the window in Figure 5.![ms810603.heapmm_5(en-us,MSDN.10).gif](https://chatgpt.com/c/images/ms810603.heapmm_5(en-us,msdn.10).gif) 

**
Here's the entire content converted to markdown, including the table:


```markdown
# Managing Heap Memory

**Randy Kath**  
Microsoft Developer Network Technology Group

Created: April 3, 1993

## Abstract

Determining which function or set of functions to use for managing memory in your application is difficult without a solid understanding of how each group of functions works and the overall impact they each have on the operating system. In an effort to simplify these decisions, this technical article focuses on the use of heaps in Windows: the functions that are available, the way they are used, and the impact their use has on operating system resources. The following topics are discussed:

- The purpose of heaps
- General heap behavior
- The two types of heaps
- Global and local memory functions
- Heap memory functions
- Overhead on heap memory allocations
- Summary and recommendations

In addition to this technical article, a sample application called ProcessWalker is included on the Microsoft Developer Network CD. This sample application explores the behavior of heap memory functions in a process, and it provides several useful implementation examples.

## Introduction

This is one of three related technical articles—"Managing Virtual Memory," "Managing Memory-Mapped Files," and "Managing Heap Memory"—that explain how to manage memory using the Windows API (application programming interface). This introduction identifies the basic memory components in the programming model and indicates which article to reference for specific areas of interest.

The first version of the Microsoft® Windows™ operating system introduced a method of managing dynamic memory based on a single _global heap_, which all applications and the system share, and multiple, private _local heaps_, one for each application. Local and global memory management functions were also provided, offering extended features for this new memory management system. More recently, the Microsoft C run-time (CRT) libraries were modified to include capabilities for managing these heaps in Windows using native CRT functions such as **malloc** and **free**. Consequently, developers are now left with a choice—learn the new API provided as part of Windows version 3.1 or stick to the portable, and typically familiar, CRT functions for managing memory in applications written for 16-bit Windows.

Windows offers three groups of functions for managing memory in applications: memory-mapped file functions, heap memory functions, and virtual memory functions.

![ms810603.heapmm_1(en-us,MSDN.10).gif](images/ms810603.heapmm_1(en-us,msdn.10).gif)
**Figure 1. The Windows API provides different levels of memory management for versatility in application programming.**

Six sets of memory management functions exist in Windows, as shown in Figure 1, all of which were designed to be used independently of one another. So which set of functions should you use? The answer to this question depends greatly on two things: the type of memory management you want, and how the functions relevant to it are implemented in the operating system. In other words, are you building a large database application where you plan to manipulate subsets of a large memory structure? Or maybe you're planning some simple dynamic memory structures, such as linked lists or binary trees? In both cases, you need to know which functions offer the features best suited to your intention and exactly how much of a resource hit occurs when using each function.

The following table categorizes the memory management function groups and indicates which of the three technical articles in this series describes each group's behavior. Each technical article emphasizes the impact these functions have on the system by describing the behavior of the system in response to using the functions.

### Table 1

| Memory set                   | System resource affected                                                                                         | Related technical article          |
|------------------------------|------------------------------------------------------------------------------------------------------------------|------------------------------------|
| Virtual memory functions     | A process's virtual address space<br>System pagefile<br>System memory<br>Hard disk space                         | "Managing Virtual Memory"          |
| Memory-mapped file functions | A process's virtual address space<br>System pagefile<br>Standard file I/O<br>System memory<br>Hard disk space    | "Managing Memory-Mapped Files"     |
| Heap memory functions        | A process's virtual address space<br>System memory<br>Process heap resource structure                            | "Managing Heap Memory"             |
| Global heap memory functions | A process's heap resource structure                                                                              | "Managing Heap Memory"             |
| Local heap memory functions  | A process's heap resource structure                                                                              | "Managing Heap Memory"             |
| C run-time reference library | A process's heap resource structure                                                                              | "Managing Heap Memory"             |

Each technical article discusses issues surrounding the use of Windows-specific functions.

## The Purpose of Heaps

The Windows subsystem on Windows NT provides high-level memory management functions that make it easy for applications to build dynamic data structures, provide compatibility with previous versions of Windows, and create buffers and temporary placeholders for system functions. These memory management functions return handles and pointers to blocks of memory that are allocated at run time and managed by an entity called the _heap_. The heap's primary function is to efficiently manage the memory and address space of a process for an application.

A tall order, considering the heap has absolutely no idea what the application intends to do with its memory and address space. Yet the heap manages to provide a robust set of functions that allow developers to overlook some of the finer details of system resources (such as the difference between reserved, free, and committed memory) so that they can turn their attention to the more important task at hand, that of implementing their applications.

In Windows NT, heaps provide a smaller granularity for the size of the smallest allocatable chunk of memory than the virtual memory management functions do. Applications typically need to allocate a specific number of bytes to fulfill a parameter request or to act as a temporary buffer. For example, when loading a string resource with the **LoadString** function, an application passes a pointer to a buffer that receives the string resource. The size of the buffer must be large enough to hold the string and a null terminator. Without the heap manager, applications would be forced to use the virtual memory management functions, which allocate a minimum of one page of memory at a time.

## General Heap Behavior

While the heap does provide support for managing smaller chunks of memory, it is itself nothing more than a chunk of memory implemented in the Windows NT virtual memory system. Consequently, the techniques that the heap uses to manage memory are based on the virtual memory management functions available to the heap. Evidence of this is found in the way heaps manifest themselves in a process, if only we could observe this behavior....

The ProcessWalker (PW) sample application explores each of the components within a process, including all of its heaps. PW identifies the heaps in a process and shows the amount of reserved and committed memory associated with a particular heap. As with all other regions of memory in a process, the smallest region of committed memory within a heap is one page (4096 bytes).

This does not mean that the smallest amount of memory that can be allocated in a heap is 4096 bytes; rather, the heap manager commits pages of memory as needed to satisfy specific allocation requests. If, for example, an application allocates 100 bytes via a call to **GlobalAlloc**, the heap manager allocates a 100-byte chunk of memory within its committed region for this request. If there is not enough committed memory available at the time of the request, the heap manager simply commits another page to make the memory available.

Ideally, then, if an application repetitively allocates 100-byte chunks of memory, the heap will commit an additional page of memory every forty-first request (40 * 100 bytes = 4000 bytes). Upon the forty-first request for a chunk of 100 bytes, the heap manager realizes there is not enough committed memory to satisfy the request, so it commits another page of memory and then completes the requested allocation. In this way, the heap manager is responsible for managing the virtual memory environment completely transparent of the application.

In reality, though, the heap manager requires additional memory for managing the memory in the heap. So instead of allocating only 100 bytes as requested, it also allocates some space for managing each particular chunk of memory. The type of memory and the size of the allocation determine the size of this additional memory. I'll discuss these issues later in this article.

## The Two Types of Heaps

Every process in Windows has one heap called the _default heap_. Processes can also have as many other _dynamic heaps_ as they wish, simply by creating and destroying them on the fly. The system uses the default heap for all global and local memory management functions, and the C run-time library uses the default heap for supporting **malloc** functions. The heap memory functions, which indicate a specific heap by its handle, use dynamic heaps. The behavior of dynamic heaps is discussed in the "Heap Memory API" section later in this article.

The default and dynamic heaps are basically the same thing, but the default heap has the special characteristic of being identifiable as the default. This is how the C run-time library and the system identify which heap to allocate from. The **GetProcessHeap** function returns a handle to the default heap for a process. Since functions such as **GlobalAlloc** or **malloc** are executed within the context of the thread that called them, they can simply call **GetProcessHeap** to retrieve a handle to the default heap, and then manage memory accordingly.

### Managing the Default Heap

Both default and dynamic heaps have a specific amount of reserved and committed memory regions associated with them, but they behave differently with respect to these limits. The default heap's reserved and committed memory region sizes are designated when the application is linked. Each application carries this information about itself within its executable image information. You can view this information by dumping header information for the executable image. For example, type the following command at a Windows NT command prompt (PWALK.EXE is used here to complete the example; you will need to substitute your own path and executable file):

```plaintext
link32 -dump -headers d:\samples\walker\pwalk.exe

...
OPTIONAL HEADER VALUES             
     10B magic #                   
    2.29 linker version            
    B000 size of code              
   1E800 size of initialized data  
     600 size of uninitialized data
   18470 address of entry point    
   10000 base of code              
   20000 base of data              
         ----- new -----           
  400000 image base                
   10000 section alignment         
     200 file alignment            
       2 subsystem (Windows GUI)   
     0.B operating system version  
     1.0 image version             
     3.A subsystem version         
   C0000 size of image             
     400 size of headers           
       0 checksum                  
   10000 size of stack reserve     
    1000 size of stack commit      
   10000 size of heap reserve      
    1000 size of heap commit       
   ...
```

The last two entries are hexadecimal values specifying the amount of reserved and committed space initially needed by the application.

There are two ways to tell the linker what to use for these values. You can link your application with a module definition file and include a statement in the file like the following:


```plaintext
HEAPSIZE   0x10000 0x1000
```
Or you can directly inform the linker by using the **/HEAP**  linker switch, as in:

```plaintext
/HEAP: 0x10000, 0x1000
```

In both examples, the heap is specified to initially have 0x10000 (64K) bytes reserved address space and 0x1000 (4K) bytes committed memory. If you fail to indicate the heap size in either method, the linker uses the default values of 0x100000 (1 MB) reserved address space and 0x1000 (4K) committed memory.

The linker accepts almost any value for heap reserve space, because the application loader ensures that the application will meet certain minimum requirements during the load process. In other words, you can link an application with an initial heap value of 1 page reserved address space. The linker doesn't perform any data validation; it simply marks the executable with the given value. Yet, since the minimum range of address space that can be reserved is 16 pages (64K), the loader compensates by reserving 16 pages for the application heap at load time.

As indicated above, options exist that indicate how much memory should initially be committed for an application's default heap. The problem is they don't seem to work yet. The linker for the second beta release of Windows NT marks all executable applications with 0x1000 (4K) initial committed memory for the default heap size, regardless of the value indicated as an option. Yet this is not that big a deal because it actually may be better for an application to commit as it needs to, rather than to commit memory that is not being used.

### A Default Heap That Grows and Spreads 

In its simplest form, the default heap spans a range of addresses. Some ranges are reserved, while others are committed and have pages of memory associated with them. In this case the addresses are contiguous, and they all originated from the same base allocation address. In some cases the default heap needs to allocate more memory than is available in its current reserved address space. For these cases the heap can either fail the call that requests the memory, or reserve an additional address range elsewhere in the process. The default heap manager opts for the second choice.

When the default heap needs more memory than is currently available, it reserves another 1-MB address range in the process. It also initially commits as much memory as it needs from this reserved address range to satisfy the allocation request. The default heap manager is then responsible for managing this new memory region as well as the original heap space. If necessary, it will repeat this throughout the application until the process runs out of memory and address space. You could end up with a default heap that manifests itself in your process in a manner similar to the heap represented in Figure 2.
![ms810603.heapmm_2(en-us,MSDN.10).gif](https://chatgpt.com/c/images/ms810603.heapmm_2(en-us,msdn.10).gif) 

**Figure 2. The default heap for each process can expand into free address regions within the process.** 
So the default heap is not really a static heap at all. In fact, it may seem like a waste of energy to bother with managing the size of the initial heap since the heap always behaves in the same way after initialization. Managing the size of the default heap offers one advantage, though. It takes time to locate and reserve a new range of addresses in a process; you can save time by simply reserving a large enough address range initially. If you expect your application to require more heap space than the 1-MB default, reserve more address space initially to avoid allocating another region of addresses in your process later. Remember, each application has 2 gigabytes (GB) of address space to work with, and requires very little physical memory to support it.

## Global and Local Memory Functions 

At first glance it appears that the local and global memory management functions exist in Windows purely for backward compatibility with Windows version 3.1. This may be true, but the functions are managed as efficiently as the new heap functions discussed below. In fact, porting an application from 16-bit Windows does not necessarily include migrating from global and local memory functions to heap memory functions. The global and local functions offer the same basic capabilities (and then some) and are just as fast to work with. If anything, they are probably more convenient to work with because you do not have to keep track of a heap handle.
Nonetheless, the implementation of these functions is not the same as it was for 16-bit Windows. 16-bit Windows had a global heap, and each application had a local heap. Those two heap managers implemented the global and local functions. Allocating memory via **GlobalAlloc**  meant retrieving a chunk of memory from the global heap, while **LocalAlloc**  allocated memory from the local heap. Windows now has a single heap for both types of functions—the default heap described above.Now you're probably wondering if there is any difference between the local and global functions themselves. Well, the answer is no, they are now the same. In fact, they are interchangeable. Memory allocated via a call to **LocalAlloc**  can be reallocated with **GlobalReAlloc**  and then locked by **LocalLock** . The following table lists the global and local functions now available.
### Table 2 
| Global memory functions | Local memory functions | 
| --- | --- | 
| GlobalAlloc | LocalAlloc | 
| GlobalDiscard | LocalDiscard | 
| GlobalFlags | LocalFlags | 
| GlobalFree | LocalFree | 
| GlobalHandle | LocalHandle | 
| GlobalLock | LocalLock | 
| GlobalReAlloc | LocalReAlloc | 
| GlobalSize | LocalSize | 
| GlobalUnlock | LocalUnlock | 

It seems redundant to have two sets of functions that perform exactly the same, but that's where the backward compatibility comes in. Whether you used the global or local functions in a 16-bit Windows application before doesn't matter now—they are equally efficient.

### Types of Global and Local Memory 
In the Windows API, the global and local memory management functions provide two types of memory, MOVEABLE and FIXED. MOVEABLE memory can be further qualified as DISCARDABLE memory. When you allocate memory with either **GlobalAlloc**  or **LocalAlloc** , you designate the type of memory you want by supplying the appropriate memory flag. The following table lists and describes each memory flag for global and local memory.
### Table 3 
| Global memory flag | Local memory flag | Allocation meaning | 
| --- | --- | --- | 
| GMEM_FIXED | LMEM_FIXED | Allocate fixed memory. | 
| GMEM_MOVEABLE | LMEM_MOVEABLE | Allocate movable memory. | 
| GMEM_DISCARDABLE | LMEM_DISCARDABLE | Allocate discardable, movable memory. | 
| GMEM_ZEROINIT | LMEM_ZEROINIT | Initialize memory to zeros during allocation. | 
| GMEM_NODISCARD | LMEM_NODISCARD | Do not discard other memory to meet the needs of this allocation; instead, fail this request. | 
| GMEM_NOCOMPACT | LMEM_NOCOMPACT | Do not discard or move other memory to meet the needs of this allocation; instead, fail this request. | 
| GMEM_SHARE, GMEM_DDESHARE | N/A | Allocate global memory that is more efficient to use with DDE. | 

It is surprising that the distinction between FIXED and MOVEABLE memory still exists in these functions. In 16-bit Windows, MOVEABLE memory compacted the local and global heaps to reduce fragmentation and make more memory available to all applications. Yet the Windows NT virtual memory system does not rely on these techniques for efficient memory management and has little to gain by applications using them. In any case, they still exist and could actually be used in some circumstances.
When allocating FIXED memory in Windows, the **GlobalAlloc**  and **LocalAlloc**  functions return a 32-bit pointer to the memory block rather than a handle as they do for MOVEABLE memory. The pointer can directly access the memory without having to lock it first. This pointer can also be passed to the **GlobalFree**  and **LocalFree**  functions to release the memory without having to first retrieve the handle by calling the **GlobalHandle**  function. With FIXED memory, allocating and freeing memory is similar to using the C run-time functions **_malloc**  and **_free** .MOVEABLE memory, on the other hand, cannot provide this luxury. Because MOVEABLE memory can be moved (and DISCARDABLE memory can be discarded), the heap manager needs a handle to identify the chunk of memory to move or discard. To access the memory, the handle must first be locked by calling either **GlobalLock**  or **LocalLock** . As in 16-bit Windows, the memory cannot be moved or discarded while the handle is locked.
### The MOVEABLE Memory Handle Table 

As it turns out, each handle to MOVEABLE memory is actually a pointer into the MOVEABLE memory handle table. The handle table exists outside the heap, elsewhere in the process's address space. To learn more about this behavior, we created a test application that allocates several MOVEABLE memory blocks from the default heap. The handle table was created only upon allocation of the first MOVEABLE chunk of memory. This is nice, because if you never allocate any MOVEABLE memory, the table is never created and does not waste memory. ProcessWalker reveals that when this handle table is created, 1 page of memory is committed for the initial table and 512K of address space is reserved (see Figure 3).
![ms810603.heapmm_3(en-us,MSDN.10).gif](https://chatgpt.com/c/images/ms810603.heapmm_3(en-us,msdn.10).gif) 

**Figure 3. ProcessWalker highlights changes in the address space of a process. The heap memory handle table is shown as it looks immediately after it is created.** 
If you work out the math you can see that the number of memory handles available for MOVEABLE memory is limited. 512K bytes / 8 bytes per handle = 65,535 handles. In fact, the system imposes this limitation on each process. Fortunately, this only applies to MOVEABLE memory. You can allocate as many chunks of FIXED memory as you like, provided the memory and address space are available in your process.

Each handle requires 8 bytes of committed memory in the handle table to represent information, including the virtual address of the memory, the lock count on the handle, and the type of memory. Figure 4 shows how the handle table looks when viewed in ProcessWalker.
![ms810603.heapmm_4(en-us,MSDN.10).gif](https://chatgpt.com/c/images/ms810603.heapmm_4(en-us,msdn.10).gif) 

**Figure 4. Each MOVEABLE memory handle is 8 bytes and represents the location of the chunk of memory.** 
> **Note**  In the ProcessWalker view window, each line is 16 bytes (two memory handles). The far-left column represents the address of each line within the process. The addresses in white indicate the lines in which data changed since the last refresh. Red text shows exactly which bytes changed. This feature allows you to easily track changes in memory in response to certain events within the child process. A very useful debugging tool, to say the least.
The first 8 bytes in the view window—at address 0x000f0000—show the first handle allocated in the table. The handle value for this example would actually be 0x000f0004, which is a 4-byte offset into the 8-byte handle table entry. At the 4-byte offset in the table entry is the current 32-bit address representing the location of the chunk of memory. In this example, the 32-bit address is 0x00042A70, reading 4 bytes from right to left starting at 0x000f0008 and ending at 0x000f0004. If the memory is moved to a new location, this address changes to reflect the new location.
If you back up 4 bytes from the handle to the first byte in this handle table entry, you'll find the lock count for the handle. Remember, a block of memory can be moved or discarded only if its handle's lock count is zero. Since there is only 1 byte to record the lock count, it stands to reason that a handle can be locked only 256 (0xFF) times. Unfortunately, the system currently does not warn you when you reach that limit. If you lock a handle a 257th time, you receive a valid pointer to the memory, but the lock count remains at 256. It is possible, then, that you could unlock the handle 256 times and expect the memory to be locked. Yet the lock count is decremented to 0, and the memory could be moved or discarded. So what happens if you try to access the pointer you believe to be valid? Well, it depends on what is now at the address where you believe the memory to be. The memory could still be there, or some other memory could have been moved there. This is not the desired behavior, and we hope the system will be fixed to prevent this from happening. Incidentally, how should the system be fixed? The easiest thing to do would be to fail the call to **GlobalLock**  or **LocalLock**  on any attempt beyond 256, so check the return value to make sure the function succeeds.
The third and fourth bytes of the handle represent the memory type, that is, MOVEABLE, DDESHARE, or DISCARDABLE. Presumably because of compatibility with 16-bit Windows, local and global memory flags that have the same name and meaning do not have the same value. (The WINBASE.H header file defines each flag.) Yet once the memory is allocated, the handle table entry records no difference. Whether you use LMEM_DISCARDABLE or GMEM_DISCARDABLE does not matter—the handle table identifies all DISCARDABLE memory the same way. A little exploring in ProcessWalker shows the following type value identifiers.

### Table 4 
| Memory type | Byte 3 | Byte 4 | 
| --- | --- | --- | 
| MOVEABLE | 02 | – | 
| DISCARDABLE | 06 | – | 
| DDESHARE | – | 08 | 

Keep in mind that these values as represented in the handle table are not documented, so they could change with a new release of Windows NT. But it would be easy to use ProcessWalker to view the handle table to see the changes.

Returning to the test application example.... After allocating the first MOVEABLE memory block and thereby creating the handle table, we used the test application to allocate 15 more handles from the table. A quick view of the memory window showed the first eight lines had data associated with them, while the rest of the committed page was filled with zeros. Then we allocated one more handle, making a total of 17 handles. The view window was refreshed to indicate what changes occurred in the table as a result of allocating the seventeenth handle only. Figure 4 (above) shows the results.

As you can see, more than 8 bytes changed during the last allocation. In fact, 8 lines were updated for a total of 128 bytes. The first 8 bytes represent the seventeenth handle entry information as expected. The following 120 bytes indicate that the heap manager initializes the handle table every sixteenth handle. Examining this initialization data shows that the next 15 available handle table entries are identified in the table. When allocating the eighteenth handle, the location of the nineteenth handle is identified by the address location portion of the eighteenth handle table entry. As expected, then, if a handle is removed from the table (the memory is freed), the address location in that entry is replaced with the location of the next available handle after it. This behavior indicates that the heap manager keeps the location of the next available handle table entry in a static variable and uses that entry itself to store the location of the subsequent entry. Notice also that the last initialized entry has a null location for the next address. The heap manager uses this as an indicator to initialize another 16 handle table entries during the next handle allocation.

Another efficiency in the heap manager is its ability to commit pages of memory for the handle table as it needs them, not all 128 pages (512K) at once. Since the heap manager initializes its handle table in 16-handle (128-byte) increments, it is easy to determine when to commit a new page of memory. Every thirty-second (4096 / 128 = 32) initialization requires a new page of committed memory. Also, the entries do not straddle page boundaries, so their management is easier and potentially more efficient.

### CRT Library 

Managing memory in 16-bit Windows involved a great deal of uncertainty about using the C run-time (CRT) library. Now, there should be little hesitation. The current CRT library is implemented in a manner similar to FIXED memory allocated via the local and global memory management functions. The CRT library is also implemented using the same default heap manager as the global and local memory management functions.
Subsequent memory allocations via **malloc** , **GlobalAlloc** , and **LocalAlloc**  return pointers to memory allocated from the same heap. The heap manager does not divide its space among the CRT and global/local memory functions, and it does not maintain separate heaps for these functions. Instead, it treats them the same, promoting consistent behavior across the types of functions. As a result, you can now write code using the functions you're most comfortable with. And, if you're interested in portability, you can safely use the CRT functions exclusively for managing heap memory.
## Heap Memory API 
As mentioned earlier, you can create as many dynamic heaps as you like by simply calling **HeapCreate** . You must specify the maximum size of the heap so that the function knows how much address space to reserve. You can also indicate how much memory to commit initially. In the following example, a heap is created in your process that reserves 1 MB of address space and initially commits two pages of memory:

```plaintext
hHeap = HeapCreate (0, 0x2000, 0x100000);
```
Since you can have many dynamic heaps in your process, you need a handle to identify each heap when you access it. The **HeapCreate**  function returns this handle. Each heap you create returns a unique handle so that several dynamic heaps may coexist in your process. Having to identify your heap by handle also makes managing dynamic heaps more difficult than managing the default heap, since you have to keep each heap handle around for the life of the heap.If you're bothered by having to keep this handle around, there is an alternative. You can use the heap memory functions on the default heap instead of creating a dynamic heap explicitly for them. To do this, simply use the **GetProcessHeap**  function to get the handle of the default heap. For simple allocations of short-term memory, the following example taken from the ProcessWalker sample application illustrates how easy this is to do:

```plaintext
char    *szCaption;
int     nCaption = GetWindowTextLength (hWnd);

/* retrieve view memory range */
szCaption = HeapAlloc (GetProcessHeap (), 
                       HEAP_ZERO_MEMORY, 
                       nCaption+1);
GetWindowText (hViewWnd, szCaption, nCaption);
```

In this example the default heap is chosen because the allocation is independent of other memory management needs, and there is no reason to create a dynamic heap just for this one allocation. Note that you could achieve the same result by using the global, local, or CRT functions since they allocate only from the default heap.
As shown earlier, the first parameter to **HeapCreate**  allows you to specify an optional HEAP_NO_SERIALIZE flag. A serialized heap does not allow two threads to access it simultaneously. The default behavior is to serialize access to the heap. If you plan to use a heap strictly within one thread, specifying the HEAP_NO_SERIALIZE flag improves overall heap performance slightly.Like all of the heap memory functions, **HeapAlloc**  requires a heap handle as its first argument. The example uses the **GetProcessHeap**  function instead of a dynamic heap handle. The second parameter to **HeapAlloc**  is an optional flag that indicates whether the memory should be zeroed first and whether to generate exceptions on error. To get zeroed memory, specify the HEAP_ZERO_MEMORY flag as shown above. The generate exceptions flag (HEAP_GENERATE_EXCEPTIONS) is a useful feature if you have exception handling built into your application. When using this flag, the function raises an exception on failure rather than just returning NULL. Depending on your use, exception handling can be an effective way of triggering special events—such as low memory situations—in your application.**HeapAlloc**  has a cousin called **HeapReAlloc**  that works in much the same way as the standard global and local memory management functions described earlier. Use **HeapReAlloc**  primarily to resize a previous allocation. This function has four parameters, three of which are the same as for **HeapAlloc** . The new parameter, *lpMem*, is a pointer to the chunk of memory being resized.It is important to note that although heap memory is not movable as in global and local memory, it may be moved during the **HeapReAlloc**  function. This function returns a pointer to the resized chunk of memory, which may or may not be at the same location as initially indicated by the pointer passed to the function. This is the only time memory can be moved in dynamic heaps, and the only chunk of memory affected is the one identified by *lpMem* in the function. You can also override this behavior by specifying the HEAP_REALLOC_IN_PLACE_ONLY flag. With this flag, if there is not enough room to reallocate the memory in place, the function returns with failure status rather than move the memory.Memory allocated with **HeapAlloc**  or reallocated with **HeapReAlloc**  can be freed by calling **HeapFree** . This function is easy to use: simply indicate the heap handle and a pointer to the chunk of memory to free. Completing the example above, here is how you can use **HeapFree**  with the default heap:

```plaintext
/* free default heap memory */
HeapFree (GetProcessHeap (), szCaption);
```

This example shows how easy it can be to work with heaps in Windows. However, you may still want to create a dynamic heap specifically to manage complex dynamic data structures in your application. In fact, one nice benefit of heap memory is how well it caters to the needs of traditional data structures such as binary trees, linked lists, and dynamic arrays. Having the heap handle provides a way of uniquely identifying these structures independently. One example that comes to mind is when you're building a multiwindow application—perhaps a multiple document interface (MDI) application. Simply create and store a heap handle in the window extra bytes or window property list for each window during the WM_CREATE message. Then it is easy to write a window procedure that manages data structures from its own heap by retrieving the heap handle when necessary. When the window goes away, simply have it destroy the heap in the WM_DESTROY message.
You can easily destroy dynamic heaps by calling **HeapDestroy**  on a specific heap handle. This powerful function will remove a heap regardless of its state. The **HeapDestroy**  function doesn't care whether you have outstanding allocations in the heap or not.
To make heap memory management most efficient, you would only create a heap of the size you need. In some cases it is easy to determine the heap size you need—if you're allocating a buffer to read a file into, simply check the size of the file. In other cases, heap size is more difficult to figure—if you're creating a dynamic data structure that grows according to user interaction, it is difficult to predict what the user will do. Dynamic heaps have a provision for this latter circumstance. By specifying a maximum heap size of zero, you make the heap assume a behavior like the default heap. That is, it will grow and spread in your process as much as necessary, limited only by available memory. In this case, available memory means available address space in your process and available pagefile space on your hard disk.

## Overhead on Heap Memory Allocations 

With all types of heap memory, an overhead is associated with each memory allocation. This overhead is due to:

- Granularity on memory allocations within the heap.

- The overhead necessary to manage each memory segment within the heap.

The granularity of heap allocations in 32-bit Windows is 16 bytes. So if you request a global memory allocation of 1 byte, the heap returns a pointer to a chunk of memory, guaranteeing that the 1 byte is available. Chances are, 16 bytes will actually be available because the heap cannot allocate less than 16 bytes at a time.

### Global and Local Memory Functions 
For global and local memory functions, the documentation suggests that you use the **GlobalSize**  and **LocalSize**  functions to determine the exact size of the allocation, but in my tests this function consistently returned the size I requested and not the size actually allocated.To confirm this finding, turn to ProcessWalker again and view the committed memory in your default heap. For the sake of observation, perform consecutive allocations of 1, 2, 3, 14, 15, and 16 bytes using either **GlobalAlloc**  or **LocalAlloc** . In this particular example, we used **GlobalAlloc**  with the GMEM_MOVEABLE flag, but the result is the same for memory allocated as GMEM_FIXED. Then, refresh your view of the committed memory in the heap. Finally, scroll the view window so that the addresses of the allocated blocks of memory are all in view. You should see something similar to the window in Figure 5.![ms810603.heapmm_5(en-us,MSDN.10).gif](https://chatgpt.com/c/images/ms810603.heapmm_5(en-us,msdn.10).gif) 

Figure 5. A ProcessWalker view of the default heap after making consecutive allocations of 1, 2, 3, 14, 15, and 16 bytes using the *GlobalAlloc* function.** In Figure 5, the first line represents the header for the 1-byte allocation, followed immediately by the minimum 16 bytes allocated for the 1-byte request. Just to add visual clarity, the letter *m* appears in each allocated byte beginning at the address of the allocation. The *m*'s are visible in the ASCII representation of memory to the right of each line. At the end of all heap allocations is a heap tail, as indicated by the last line of new information in Figure 5.So, although you request only 1 byte and **GlobalSize**  returns a size of 1 byte, there are actually 16 bytes allocated and available. Similarly, for the 3-byte allocation, 13 additional bytes are available. Even more interesting is the apparent waste of memory for allocations of 14, 15, and 16 bytes. In these allocations an additional 16 bytes were allocated for no reason. These are the lines immediately following the lines with 14, 15, and 16 *m* characters. Presumably you could also use these extra 16 bytes, but again **GlobalSize**  does not indicate their existence.
So what is the cost of allocating from a heap? Well, it depends on the size of the allocation. Every 1-byte allocation uses a total of 32 bytes, and a 16-byte allocation uses a total of 48 bytes. This is a considerable amount of overhead on smaller allocations. Therefore, it would not be a good idea to accumulate a number of small heap allocations because they would cost a great deal in actual memory used. On the other hand, there is nothing wrong with allocating a large chunk of memory from the heap and dividing it into smaller pieces.

### Heap Memory Functions 
Similar to the global and local memory functions, the heap memory functions have a minimum 16-byte granularity and the same overhead on memory allocations. Figure 6 presents a ProcessWalker view of a dynamic heap using the same allocations of 1, 2, 3, 14, 15, and 16 bytes, but this time using the **HeapAlloc**  function.![ms810603.heapmm_6(en-us,MSDN.10).gif](https://chatgpt.com/c/images/ms810603.heapmm_6(en-us,msdn.10).gif) 

Figure 6. A ProcessWalker view of a dynamic heap after making consecutive allocations of 1, 2, 3, 14, 15, and 16 bytes using the *HeapAlloc* function.** For this example, the letter *h* appears in the allocated memory for comparison with the global memory allocations shown in Figure 5. A comparison of Figures 5 and 6 shows that the two heaps behave in an identical manner for the test allocations. Also, as in the global and local memory functions, a **HeapSize**  function determines the exact amount of memory allocated for a given request. Unfortunately, this function seems to be implemented exactly like the **GlobalSize**  and **LocalSize**  functions. In my tests, **HeapSize**  always returned the amount of the allocation request, while actually allocating with the same 16-byte granularity.
### C Run-Time Memory Functions 
Can you guess how the C run-time library memory functions will behave on this same test? Yes, the C run-time functions exhibit the same heap memory behavior. Figure 7 represents the same allocations using the **malloc**  function.![ms810603.heapmm_7(en-us,MSDN.10).gif](https://chatgpt.com/c/images/ms810603.heapmm_7(en-us,msdn.10).gif) 

**
Here's the entire content converted to markdown, including the table:


```markdown
# Managing Heap Memory

**Randy Kath**  
Microsoft Developer Network Technology Group

Created: April 3, 1993

## Abstract

Determining which function or set of functions to use for managing memory in your application is difficult without a solid understanding of how each group of functions works and the overall impact they each have on the operating system. In an effort to simplify these decisions, this technical article focuses on the use of heaps in Windows: the functions that are available, the way they are used, and the impact their use has on operating system resources. The following topics are discussed:

- The purpose of heaps
- General heap behavior
- The two types of heaps
- Global and local memory functions
- Heap memory functions
- Overhead on heap memory allocations
- Summary and recommendations

In addition to this technical article, a sample application called ProcessWalker is included on the Microsoft Developer Network CD. This sample application explores the behavior of heap memory functions in a process, and it provides several useful implementation examples.

## Introduction

This is one of three related technical articles—"Managing Virtual Memory," "Managing Memory-Mapped Files," and "Managing Heap Memory"—that explain how to manage memory using the Windows API (application programming interface). This introduction identifies the basic memory components in the programming model and indicates which article to reference for specific areas of interest.

The first version of the Microsoft® Windows™ operating system introduced a method of managing dynamic memory based on a single _global heap_, which all applications and the system share, and multiple, private _local heaps_, one for each application. Local and global memory management functions were also provided, offering extended features for this new memory management system. More recently, the Microsoft C run-time (CRT) libraries were modified to include capabilities for managing these heaps in Windows using native CRT functions such as **malloc** and **free**. Consequently, developers are now left with a choice—learn the new API provided as part of Windows version 3.1 or stick to the portable, and typically familiar, CRT functions for managing memory in applications written for 16-bit Windows.

Windows offers three groups of functions for managing memory in applications: memory-mapped file functions, heap memory functions, and virtual memory functions.

![ms810603.heapmm_1(en-us,MSDN.10).gif](images/ms810603.heapmm_1(en-us,msdn.10).gif)
**Figure 1. The Windows API provides different levels of memory management for versatility in application programming.**

Six sets of memory management functions exist in Windows, as shown in Figure 1, all of which were designed to be used independently of one another. So which set of functions should you use? The answer to this question depends greatly on two things: the type of memory management you want, and how the functions relevant to it are implemented in the operating system. In other words, are you building a large database application where you plan to manipulate subsets of a large memory structure? Or maybe you're planning some simple dynamic memory structures, such as linked lists or binary trees? In both cases, you need to know which functions offer the features best suited to your intention and exactly how much of a resource hit occurs when using each function.

The following table categorizes the memory management function groups and indicates which of the three technical articles in this series describes each group's behavior. Each technical article emphasizes the impact these functions have on the system by describing the behavior of the system in response to using the functions.

### Table 1

| Memory set                   | System resource affected                                                                                         | Related technical article          |
|------------------------------|------------------------------------------------------------------------------------------------------------------|------------------------------------|
| Virtual memory functions     | A process's virtual address space<br>System pagefile<br>System memory<br>Hard disk space                         | "Managing Virtual Memory"          |
| Memory-mapped file functions | A process's virtual address space<br>System pagefile<br>Standard file I/O<br>System memory<br>Hard disk space    | "Managing Memory-Mapped Files"     |
| Heap memory functions        | A process's virtual address space<br>System memory<br>Process heap resource structure                            | "Managing Heap Memory"             |
| Global heap memory functions | A process's heap resource structure                                                                              | "Managing Heap Memory"             |
| Local heap memory functions  | A process's heap resource structure                                                                              | "Managing Heap Memory"             |
| C run-time reference library | A process's heap resource structure                                                                              | "Managing Heap Memory"             |

Each technical article discusses issues surrounding the use of Windows-specific functions.

## The Purpose of Heaps

The Windows subsystem on Windows NT provides high-level memory management functions that make it easy for applications to build dynamic data structures, provide compatibility with previous versions of Windows, and create buffers and temporary placeholders for system functions. These memory management functions return handles and pointers to blocks of memory that are allocated at run time and managed by an entity called the _heap_. The heap's primary function is to efficiently manage the memory and address space of a process for an application.

A tall order, considering the heap has absolutely no idea what the application intends to do with its memory and address space. Yet the heap manages to provide a robust set of functions that allow developers to overlook some of the finer details of system resources (such as the difference between reserved, free, and committed memory) so that they can turn their attention to the more important task at hand, that of implementing their applications.

In Windows NT, heaps provide a smaller granularity for the size of the smallest allocatable chunk of memory than the virtual memory management functions do. Applications typically need to allocate a specific number of bytes to fulfill a parameter request or to act as a temporary buffer. For example, when loading a string resource with the **LoadString** function, an application passes a pointer to a buffer that receives the string resource. The size of the buffer must be large enough to hold the string and a null terminator. Without the heap manager, applications would be forced to use the virtual memory management functions, which allocate a minimum of one page of memory at a time.

## General Heap Behavior

While the heap does provide support for managing smaller chunks of memory, it is itself nothing more than a chunk of memory implemented in the Windows NT virtual memory system. Consequently, the techniques that the heap uses to manage memory are based on the virtual memory management functions available to the heap. Evidence of this is found in the way heaps manifest themselves in a process, if only we could observe this behavior....

The ProcessWalker (PW) sample application explores each of the components within a process, including all of its heaps. PW identifies the heaps in a process and shows the amount of reserved and committed memory associated with a particular heap. As with all other regions of memory in a process, the smallest region of committed memory within a heap is one page (4096 bytes).

This does not mean that the smallest amount of memory that can be allocated in a heap is 4096 bytes; rather, the heap manager commits pages of memory as needed to satisfy specific allocation requests. If, for example, an application allocates 100 bytes via a call to **GlobalAlloc**, the heap manager allocates a 100-byte chunk of memory within its committed region for this request. If there is not enough committed memory available at the time of the request, the heap manager simply commits another page to make the memory available.

Ideally, then, if an application repetitively allocates 100-byte chunks of memory, the heap will commit an additional page of memory every forty-first request (40 * 100 bytes = 4000 bytes). Upon the forty-first request for a chunk of 100 bytes, the heap manager realizes there is not enough committed memory to satisfy the request, so it commits another page of memory and then completes the requested allocation. In this way, the heap manager is responsible for managing the virtual memory environment completely transparent of the application.

In reality, though, the heap manager requires additional memory for managing the memory in the heap. So instead of allocating only 100 bytes as requested, it also allocates some space for managing each particular chunk of memory. The type of memory and the size of the allocation determine the size of this additional memory. I'll discuss these issues later in this article.

## The Two Types of Heaps

Every process in Windows has one heap called the _default heap_. Processes can also have as many other _dynamic heaps_ as they wish, simply by creating and destroying them on the fly. The system uses the default heap for all global and local memory management functions, and the C run-time library uses the default heap for supporting **malloc** functions. The heap memory functions, which indicate a specific heap by its handle, use dynamic heaps. The behavior of dynamic heaps is discussed in the "Heap Memory API" section later in this article.

The default and dynamic heaps are basically the same thing, but the default heap has the special characteristic of being identifiable as the default. This is how the C run-time library and the system identify which heap to allocate from. The **GetProcessHeap** function returns a handle to the default heap for a process. Since functions such as **GlobalAlloc** or **malloc** are executed within the context of the thread that called them, they can simply call **GetProcessHeap** to retrieve a handle to the default heap, and then manage memory accordingly.

### Managing the Default Heap

Both default and dynamic heaps have a specific amount of reserved and committed memory regions associated with them, but they behave differently with respect to these limits. The default heap's reserved and committed memory region sizes are designated when the application is linked. Each application carries this information about itself within its executable image information. You can view this information by dumping header information for the executable image. For example, type the following command at a Windows NT command prompt (PWALK.EXE is used here to complete the example; you will need to substitute your own path and executable file):

```plaintext
link32 -dump -headers d:\samples\walker\pwalk.exe

...
OPTIONAL HEADER VALUES             
     10B magic #                   
    2.29 linker version            
    B000 size of code              
   1E800 size of initialized data  
     600 size of uninitialized data
   18470 address of entry point    
   10000 base of code              
   20000 base of data              
         ----- new -----           
  400000 image base                
   10000 section alignment         
     200 file alignment            
       2 subsystem (Windows GUI)   
     0.B operating system version  
     1.0 image version             
     3.A subsystem version         
   C0000 size of image             
     400 size of headers           
       0 checksum                  
   10000 size of stack reserve     
    1000 size of stack commit      
   10000 size of heap reserve      
    1000 size of heap commit       
   ...
```

The last two entries are hexadecimal values specifying the amount of reserved and committed space initially needed by the application.

There are two ways to tell the linker what to use for these values. You can link your application with a module definition file and include a statement in the file like the following:


```plaintext
HEAPSIZE   0x10000 0x1000
```
Or you can directly inform the linker by using the **/HEAP**  linker switch, as in:

```plaintext
/HEAP: 0x10000, 0x1000
```

In both examples, the heap is specified to initially have 0x10000 (64K) bytes reserved address space and 0x1000 (4K) bytes committed memory. If you fail to indicate the heap size in either method, the linker uses the default values of 0x100000 (1 MB) reserved address space and 0x1000 (4K) committed memory.

The linker accepts almost any value for heap reserve space, because the application loader ensures that the application will meet certain minimum requirements during the load process. In other words, you can link an application with an initial heap value of 1 page reserved address space. The linker doesn't perform any data validation; it simply marks the executable with the given value. Yet, since the minimum range of address space that can be reserved is 16 pages (64K), the loader compensates by reserving 16 pages for the application heap at load time.

As indicated above, options exist that indicate how much memory should initially be committed for an application's default heap. The problem is they don't seem to work yet. The linker for the second beta release of Windows NT marks all executable applications with 0x1000 (4K) initial committed memory for the default heap size, regardless of the value indicated as an option. Yet this is not that big a deal because it actually may be better for an application to commit as it needs to, rather than to commit memory that is not being used.

### A Default Heap That Grows and Spreads 

In its simplest form, the default heap spans a range of addresses. Some ranges are reserved, while others are committed and have pages of memory associated with them. In this case the addresses are contiguous, and they all originated from the same base allocation address. In some cases the default heap needs to allocate more memory than is available in its current reserved address space. For these cases the heap can either fail the call that requests the memory, or reserve an additional address range elsewhere in the process. The default heap manager opts for the second choice.

When the default heap needs more memory than is currently available, it reserves another 1-MB address range in the process. It also initially commits as much memory as it needs from this reserved address range to satisfy the allocation request. The default heap manager is then responsible for managing this new memory region as well as the original heap space. If necessary, it will repeat this throughout the application until the process runs out of memory and address space. You could end up with a default heap that manifests itself in your process in a manner similar to the heap represented in Figure 2.
![ms810603.heapmm_2(en-us,MSDN.10).gif](https://chatgpt.com/c/images/ms810603.heapmm_2(en-us,msdn.10).gif) 

**Figure 2. The default heap for each process can expand into free address regions within the process.** 
So the default heap is not really a static heap at all. In fact, it may seem like a waste of energy to bother with managing the size of the initial heap since the heap always behaves in the same way after initialization. Managing the size of the default heap offers one advantage, though. It takes time to locate and reserve a new range of addresses in a process; you can save time by simply reserving a large enough address range initially. If you expect your application to require more heap space than the 1-MB default, reserve more address space initially to avoid allocating another region of addresses in your process later. Remember, each application has 2 gigabytes (GB) of address space to work with, and requires very little physical memory to support it.

## Global and Local Memory Functions 

At first glance it appears that the local and global memory management functions exist in Windows purely for backward compatibility with Windows version 3.1. This may be true, but the functions are managed as efficiently as the new heap functions discussed below. In fact, porting an application from 16-bit Windows does not necessarily include migrating from global and local memory functions to heap memory functions. The global and local functions offer the same basic capabilities (and then some) and are just as fast to work with. If anything, they are probably more convenient to work with because you do not have to keep track of a heap handle.
Nonetheless, the implementation of these functions is not the same as it was for 16-bit Windows. 16-bit Windows had a global heap, and each application had a local heap. Those two heap managers implemented the global and local functions. Allocating memory via **GlobalAlloc**  meant retrieving a chunk of memory from the global heap, while **LocalAlloc**  allocated memory from the local heap. Windows now has a single heap for both types of functions—the default heap described above.Now you're probably wondering if there is any difference between the local and global functions themselves. Well, the answer is no, they are now the same. In fact, they are interchangeable. Memory allocated via a call to **LocalAlloc**  can be reallocated with **GlobalReAlloc**  and then locked by **LocalLock** . The following table lists the global and local functions now available.
### Table 2 
| Global memory functions | Local memory functions | 
| --- | --- | 
| GlobalAlloc | LocalAlloc | 
| GlobalDiscard | LocalDiscard | 
| GlobalFlags | LocalFlags | 
| GlobalFree | LocalFree | 
| GlobalHandle | LocalHandle | 
| GlobalLock | LocalLock | 
| GlobalReAlloc | LocalReAlloc | 
| GlobalSize | LocalSize | 
| GlobalUnlock | LocalUnlock | 

It seems redundant to have two sets of functions that perform exactly the same, but that's where the backward compatibility comes in. Whether you used the global or local functions in a 16-bit Windows application before doesn't matter now—they are equally efficient.

### Types of Global and Local Memory 
In the Windows API, the global and local memory management functions provide two types of memory, MOVEABLE and FIXED. MOVEABLE memory can be further qualified as DISCARDABLE memory. When you allocate memory with either **GlobalAlloc**  or **LocalAlloc** , you designate the type of memory you want by supplying the appropriate memory flag. The following table lists and describes each memory flag for global and local memory.
### Table 3 
| Global memory flag | Local memory flag | Allocation meaning | 
| --- | --- | --- | 
| GMEM_FIXED | LMEM_FIXED | Allocate fixed memory. | 
| GMEM_MOVEABLE | LMEM_MOVEABLE | Allocate movable memory. | 
| GMEM_DISCARDABLE | LMEM_DISCARDABLE | Allocate discardable, movable memory. | 
| GMEM_ZEROINIT | LMEM_ZEROINIT | Initialize memory to zeros during allocation. | 
| GMEM_NODISCARD | LMEM_NODISCARD | Do not discard other memory to meet the needs of this allocation; instead, fail this request. | 
| GMEM_NOCOMPACT | LMEM_NOCOMPACT | Do not discard or move other memory to meet the needs of this allocation; instead, fail this request. | 
| GMEM_SHARE, GMEM_DDESHARE | N/A | Allocate global memory that is more efficient to use with DDE. | 

It is surprising that the distinction between FIXED and MOVEABLE memory still exists in these functions. In 16-bit Windows, MOVEABLE memory compacted the local and global heaps to reduce fragmentation and make more memory available to all applications. Yet the Windows NT virtual memory system does not rely on these techniques for efficient memory management and has little to gain by applications using them. In any case, they still exist and could actually be used in some circumstances.
When allocating FIXED memory in Windows, the **GlobalAlloc**  and **LocalAlloc**  functions return a 32-bit pointer to the memory block rather than a handle as they do for MOVEABLE memory. The pointer can directly access the memory without having to lock it first. This pointer can also be passed to the **GlobalFree**  and **LocalFree**  functions to release the memory without having to first retrieve the handle by calling the **GlobalHandle**  function. With FIXED memory, allocating and freeing memory is similar to using the C run-time functions **_malloc**  and **_free** .MOVEABLE memory, on the other hand, cannot provide this luxury. Because MOVEABLE memory can be moved (and DISCARDABLE memory can be discarded), the heap manager needs a handle to identify the chunk of memory to move or discard. To access the memory, the handle must first be locked by calling either **GlobalLock**  or **LocalLock** . As in 16-bit Windows, the memory cannot be moved or discarded while the handle is locked.
### The MOVEABLE Memory Handle Table 

As it turns out, each handle to MOVEABLE memory is actually a pointer into the MOVEABLE memory handle table. The handle table exists outside the heap, elsewhere in the process's address space. To learn more about this behavior, we created a test application that allocates several MOVEABLE memory blocks from the default heap. The handle table was created only upon allocation of the first MOVEABLE chunk of memory. This is nice, because if you never allocate any MOVEABLE memory, the table is never created and does not waste memory. ProcessWalker reveals that when this handle table is created, 1 page of memory is committed for the initial table and 512K of address space is reserved (see Figure 3).
![ms810603.heapmm_3(en-us,MSDN.10).gif](https://chatgpt.com/c/images/ms810603.heapmm_3(en-us,msdn.10).gif) 

**Figure 3. ProcessWalker highlights changes in the address space of a process. The heap memory handle table is shown as it looks immediately after it is created.** 
If you work out the math you can see that the number of memory handles available for MOVEABLE memory is limited. 512K bytes / 8 bytes per handle = 65,535 handles. In fact, the system imposes this limitation on each process. Fortunately, this only applies to MOVEABLE memory. You can allocate as many chunks of FIXED memory as you like, provided the memory and address space are available in your process.

Each handle requires 8 bytes of committed memory in the handle table to represent information, including the virtual address of the memory, the lock count on the handle, and the type of memory. Figure 4 shows how the handle table looks when viewed in ProcessWalker.
![ms810603.heapmm_4(en-us,MSDN.10).gif](https://chatgpt.com/c/images/ms810603.heapmm_4(en-us,msdn.10).gif) 

**Figure 4. Each MOVEABLE memory handle is 8 bytes and represents the location of the chunk of memory.** 
> **Note**  In the ProcessWalker view window, each line is 16 bytes (two memory handles). The far-left column represents the address of each line within the process. The addresses in white indicate the lines in which data changed since the last refresh. Red text shows exactly which bytes changed. This feature allows you to easily track changes in memory in response to certain events within the child process. A very useful debugging tool, to say the least.
The first 8 bytes in the view window—at address 0x000f0000—show the first handle allocated in the table. The handle value for this example would actually be 0x000f0004, which is a 4-byte offset into the 8-byte handle table entry. At the 4-byte offset in the table entry is the current 32-bit address representing the location of the chunk of memory. In this example, the 32-bit address is 0x00042A70, reading 4 bytes from right to left starting at 0x000f0008 and ending at 0x000f0004. If the memory is moved to a new location, this address changes to reflect the new location.
If you back up 4 bytes from the handle to the first byte in this handle table entry, you'll find the lock count for the handle. Remember, a block of memory can be moved or discarded only if its handle's lock count is zero. Since there is only 1 byte to record the lock count, it stands to reason that a handle can be locked only 256 (0xFF) times. Unfortunately, the system currently does not warn you when you reach that limit. If you lock a handle a 257th time, you receive a valid pointer to the memory, but the lock count remains at 256. It is possible, then, that you could unlock the handle 256 times and expect the memory to be locked. Yet the lock count is decremented to 0, and the memory could be moved or discarded. So what happens if you try to access the pointer you believe to be valid? Well, it depends on what is now at the address where you believe the memory to be. The memory could still be there, or some other memory could have been moved there. This is not the desired behavior, and we hope the system will be fixed to prevent this from happening. Incidentally, how should the system be fixed? The easiest thing to do would be to fail the call to **GlobalLock**  or **LocalLock**  on any attempt beyond 256, so check the return value to make sure the function succeeds.
The third and fourth bytes of the handle represent the memory type, that is, MOVEABLE, DDESHARE, or DISCARDABLE. Presumably because of compatibility with 16-bit Windows, local and global memory flags that have the same name and meaning do not have the same value. (The WINBASE.H header file defines each flag.) Yet once the memory is allocated, the handle table entry records no difference. Whether you use LMEM_DISCARDABLE or GMEM_DISCARDABLE does not matter—the handle table identifies all DISCARDABLE memory the same way. A little exploring in ProcessWalker shows the following type value identifiers.

### Table 4 
| Memory type | Byte 3 | Byte 4 | 
| --- | --- | --- | 
| MOVEABLE | 02 | – | 
| DISCARDABLE | 06 | – | 
| DDESHARE | – | 08 | 

Keep in mind that these values as represented in the handle table are not documented, so they could change with a new release of Windows NT. But it would be easy to use ProcessWalker to view the handle table to see the changes.

Returning to the test application example.... After allocating the first MOVEABLE memory block and thereby creating the handle table, we used the test application to allocate 15 more handles from the table. A quick view of the memory window showed the first eight lines had data associated with them, while the rest of the committed page was filled with zeros. Then we allocated one more handle, making a total of 17 handles. The view window was refreshed to indicate what changes occurred in the table as a result of allocating the seventeenth handle only. Figure 4 (above) shows the results.

As you can see, more than 8 bytes changed during the last allocation. In fact, 8 lines were updated for a total of 128 bytes. The first 8 bytes represent the seventeenth handle entry information as expected. The following 120 bytes indicate that the heap manager initializes the handle table every sixteenth handle. Examining this initialization data shows that the next 15 available handle table entries are identified in the table. When allocating the eighteenth handle, the location of the nineteenth handle is identified by the address location portion of the eighteenth handle table entry. As expected, then, if a handle is removed from the table (the memory is freed), the address location in that entry is replaced with the location of the next available handle after it. This behavior indicates that the heap manager keeps the location of the next available handle table entry in a static variable and uses that entry itself to store the location of the subsequent entry. Notice also that the last initialized entry has a null location for the next address. The heap manager uses this as an indicator to initialize another 16 handle table entries during the next handle allocation.

Another efficiency in the heap manager is its ability to commit pages of memory for the handle table as it needs them, not all 128 pages (512K) at once. Since the heap manager initializes its handle table in 16-handle (128-byte) increments, it is easy to determine when to commit a new page of memory. Every thirty-second (4096 / 128 = 32) initialization requires a new page of committed memory. Also, the entries do not straddle page boundaries, so their management is easier and potentially more efficient.

### CRT Library 

Managing memory in 16-bit Windows involved a great deal of uncertainty about using the C run-time (CRT) library. Now, there should be little hesitation. The current CRT library is implemented in a manner similar to FIXED memory allocated via the local and global memory management functions. The CRT library is also implemented using the same default heap manager as the global and local memory management functions.
Subsequent memory allocations via **malloc** , **GlobalAlloc** , and **LocalAlloc**  return pointers to memory allocated from the same heap. The heap manager does not divide its space among the CRT and global/local memory functions, and it does not maintain separate heaps for these functions. Instead, it treats them the same, promoting consistent behavior across the types of functions. As a result, you can now write code using the functions you're most comfortable with. And, if you're interested in portability, you can safely use the CRT functions exclusively for managing heap memory.
## Heap Memory API 
As mentioned earlier, you can create as many dynamic heaps as you like by simply calling **HeapCreate** . You must specify the maximum size of the heap so that the function knows how much address space to reserve. You can also indicate how much memory to commit initially. In the following example, a heap is created in your process that reserves 1 MB of address space and initially commits two pages of memory:

```plaintext
hHeap = HeapCreate (0, 0x2000, 0x100000);
```
Since you can have many dynamic heaps in your process, you need a handle to identify each heap when you access it. The **HeapCreate**  function returns this handle. Each heap you create returns a unique handle so that several dynamic heaps may coexist in your process. Having to identify your heap by handle also makes managing dynamic heaps more difficult than managing the default heap, since you have to keep each heap handle around for the life of the heap.If you're bothered by having to keep this handle around, there is an alternative. You can use the heap memory functions on the default heap instead of creating a dynamic heap explicitly for them. To do this, simply use the **GetProcessHeap**  function to get the handle of the default heap. For simple allocations of short-term memory, the following example taken from the ProcessWalker sample application illustrates how easy this is to do:

```plaintext
char    *szCaption;
int     nCaption = GetWindowTextLength (hWnd);

/* retrieve view memory range */
szCaption = HeapAlloc (GetProcessHeap (), 
                       HEAP_ZERO_MEMORY, 
                       nCaption+1);
GetWindowText (hViewWnd, szCaption, nCaption);
```

In this example the default heap is chosen because the allocation is independent of other memory management needs, and there is no reason to create a dynamic heap just for this one allocation. Note that you could achieve the same result by using the global, local, or CRT functions since they allocate only from the default heap.
As shown earlier, the first parameter to **HeapCreate**  allows you to specify an optional HEAP_NO_SERIALIZE flag. A serialized heap does not allow two threads to access it simultaneously. The default behavior is to serialize access to the heap. If you plan to use a heap strictly within one thread, specifying the HEAP_NO_SERIALIZE flag improves overall heap performance slightly.Like all of the heap memory functions, **HeapAlloc**  requires a heap handle as its first argument. The example uses the **GetProcessHeap**  function instead of a dynamic heap handle. The second parameter to **HeapAlloc**  is an optional flag that indicates whether the memory should be zeroed first and whether to generate exceptions on error. To get zeroed memory, specify the HEAP_ZERO_MEMORY flag as shown above. The generate exceptions flag (HEAP_GENERATE_EXCEPTIONS) is a useful feature if you have exception handling built into your application. When using this flag, the function raises an exception on failure rather than just returning NULL. Depending on your use, exception handling can be an effective way of triggering special events—such as low memory situations—in your application.**HeapAlloc**  has a cousin called **HeapReAlloc**  that works in much the same way as the standard global and local memory management functions described earlier. Use **HeapReAlloc**  primarily to resize a previous allocation. This function has four parameters, three of which are the same as for **HeapAlloc** . The new parameter, *lpMem*, is a pointer to the chunk of memory being resized.It is important to note that although heap memory is not movable as in global and local memory, it may be moved during the **HeapReAlloc**  function. This function returns a pointer to the resized chunk of memory, which may or may not be at the same location as initially indicated by the pointer passed to the function. This is the only time memory can be moved in dynamic heaps, and the only chunk of memory affected is the one identified by *lpMem* in the function. You can also override this behavior by specifying the HEAP_REALLOC_IN_PLACE_ONLY flag. With this flag, if there is not enough room to reallocate the memory in place, the function returns with failure status rather than move the memory.Memory allocated with **HeapAlloc**  or reallocated with **HeapReAlloc**  can be freed by calling **HeapFree** . This function is easy to use: simply indicate the heap handle and a pointer to the chunk of memory to free. Completing the example above, here is how you can use **HeapFree**  with the default heap:

```plaintext
/* free default heap memory */
HeapFree (GetProcessHeap (), szCaption);
```

This example shows how easy it can be to work with heaps in Windows. However, you may still want to create a dynamic heap specifically to manage complex dynamic data structures in your application. In fact, one nice benefit of heap memory is how well it caters to the needs of traditional data structures such as binary trees, linked lists, and dynamic arrays. Having the heap handle provides a way of uniquely identifying these structures independently. One example that comes to mind is when you're building a multiwindow application—perhaps a multiple document interface (MDI) application. Simply create and store a heap handle in the window extra bytes or window property list for each window during the WM_CREATE message. Then it is easy to write a window procedure that manages data structures from its own heap by retrieving the heap handle when necessary. When the window goes away, simply have it destroy the heap in the WM_DESTROY message.
You can easily destroy dynamic heaps by calling **HeapDestroy**  on a specific heap handle. This powerful function will remove a heap regardless of its state. The **HeapDestroy**  function doesn't care whether you have outstanding allocations in the heap or not.
To make heap memory management most efficient, you would only create a heap of the size you need. In some cases it is easy to determine the heap size you need—if you're allocating a buffer to read a file into, simply check the size of the file. In other cases, heap size is more difficult to figure—if you're creating a dynamic data structure that grows according to user interaction, it is difficult to predict what the user will do. Dynamic heaps have a provision for this latter circumstance. By specifying a maximum heap size of zero, you make the heap assume a behavior like the default heap. That is, it will grow and spread in your process as much as necessary, limited only by available memory. In this case, available memory means available address space in your process and available pagefile space on your hard disk.

## Overhead on Heap Memory Allocations 

With all types of heap memory, an overhead is associated with each memory allocation. This overhead is due to:

- Granularity on memory allocations within the heap.

- The overhead necessary to manage each memory segment within the heap.

The granularity of heap allocations in 32-bit Windows is 16 bytes. So if you request a global memory allocation of 1 byte, the heap returns a pointer to a chunk of memory, guaranteeing that the 1 byte is available. Chances are, 16 bytes will actually be available because the heap cannot allocate less than 16 bytes at a time.

### Global and Local Memory Functions 
For global and local memory functions, the documentation suggests that you use the **GlobalSize**  and **LocalSize**  functions to determine the exact size of the allocation, but in my tests this function consistently returned the size I requested and not the size actually allocated.To confirm this finding, turn to ProcessWalker again and view the committed memory in your default heap. For the sake of observation, perform consecutive allocations of 1, 2, 3, 14, 15, and 16 bytes using either **GlobalAlloc**  or **LocalAlloc** . In this particular example, we used **GlobalAlloc**  with the GMEM_MOVEABLE flag, but the result is the same for memory allocated as GMEM_FIXED. Then, refresh your view of the committed memory in the heap. Finally, scroll the view window so that the addresses of the allocated blocks of memory are all in view. You should see something similar to the window in Figure 5.![ms810603.heapmm_5(en-us,MSDN.10).gif](https://chatgpt.com/c/images/ms810603.heapmm_5(en-us,msdn.10).gif) 

**
Here's the entire content converted to markdown, including the table:


# Managing Heap Memory

**Randy Kath**  
Microsoft Developer Network Technology Group

Created: April 3, 1993

## Abstract

Determining which function or set of functions to use for managing memory in your application is difficult without a solid understanding of how each group of functions works and the overall impact they each have on the operating system. In an effort to simplify these decisions, this technical article focuses on the use of heaps in Windows: the functions that are available, the way they are used, and the impact their use has on operating system resources. The following topics are discussed:

- The purpose of heaps
- General heap behavior
- The two types of heaps
- Global and local memory functions
- Heap memory functions
- Overhead on heap memory allocations
- Summary and recommendations

In addition to this technical article, a sample application called ProcessWalker is included on the Microsoft Developer Network CD. This sample application explores the behavior of heap memory functions in a process, and it provides several useful implementation examples.

## Introduction

This is one of three related technical articles—"Managing Virtual Memory," "Managing Memory-Mapped Files," and "Managing Heap Memory"—that explain how to manage memory using the Windows API (application programming interface). This introduction identifies the basic memory components in the programming model and indicates which article to reference for specific areas of interest.

The first version of the Microsoft® Windows™ operating system introduced a method of managing dynamic memory based on a single _global heap_, which all applications and the system share, and multiple, private _local heaps_, one for each application. Local and global memory management functions were also provided, offering extended features for this new memory management system. More recently, the Microsoft C run-time (CRT) libraries were modified to include capabilities for managing these heaps in Windows using native CRT functions such as **malloc** and **free**. Consequently, developers are now left with a choice—learn the new API provided as part of Windows version 3.1 or stick to the portable, and typically familiar, CRT functions for managing memory in applications written for 16-bit Windows.

Windows offers three groups of functions for managing memory in applications: memory-mapped file functions, heap memory functions, and virtual memory functions.

![ms810603.heapmm_1(en-us,MSDN.10).gif](images/ms810603.heapmm_1(en-us,msdn.10).gif)
**Figure 1. The Windows API provides different levels of memory management for versatility in application programming.**

Six sets of memory management functions exist in Windows, as shown in Figure 1, all of which were designed to be used independently of one another. So which set of functions should you use? The answer to this question depends greatly on two things: the type of memory management you want, and how the functions relevant to it are implemented in the operating system. In other words, are you building a large database application where you plan to manipulate subsets of a large memory structure? Or maybe you're planning some simple dynamic memory structures, such as linked lists or binary trees? In both cases, you need to know which functions offer the features best suited to your intention and exactly how much of a resource hit occurs when using each function.

The following table categorizes the memory management function groups and indicates which of the three technical articles in this series describes each group's behavior. Each technical article emphasizes the impact these functions have on the system by describing the behavior of the system in response to using the functions.

### Table 1

| Memory set                   | System resource affected                                                                                         | Related technical article          |
|------------------------------|------------------------------------------------------------------------------------------------------------------|------------------------------------|
| Virtual memory functions     | A process's virtual address space<br>System pagefile<br>System memory<br>Hard disk space                         | "Managing Virtual Memory"          |
| Memory-mapped file functions | A process's virtual address space<br>System pagefile<br>Standard file I/O<br>System memory<br>Hard disk space    | "Managing Memory-Mapped Files"     |
| Heap memory functions        | A process's virtual address space<br>System memory<br>Process heap resource structure                            | "Managing Heap Memory"             |
| Global heap memory functions | A process's heap resource structure                                                                              | "Managing Heap Memory"             |
| Local heap memory functions  | A process's heap resource structure                                                                              | "Managing Heap Memory"             |
| C run-time reference library | A process's heap resource structure                                                                              | "Managing Heap Memory"             |

Each technical article discusses issues surrounding the use of Windows-specific functions.

## The Purpose of Heaps

The Windows subsystem on Windows NT provides high-level memory management functions that make it easy for applications to build dynamic data structures, provide compatibility with previous versions of Windows, and create buffers and temporary placeholders for system functions. These memory management functions return handles and pointers to blocks of memory that are allocated at run time and managed by an entity called the _heap_. The heap's primary function is to efficiently manage the memory and address space of a process for an application.

A tall order, considering the heap has absolutely no idea what the application intends to do with its memory and address space. Yet the heap manages to provide a robust set of functions that allow developers to overlook some of the finer details of system resources (such as the difference between reserved, free, and committed memory) so that they can turn their attention to the more important task at hand, that of implementing their applications.

In Windows NT, heaps provide a smaller granularity for the size of the smallest allocatable chunk of memory than the virtual memory management functions do. Applications typically need to allocate a specific number of bytes to fulfill a parameter request or to act as a temporary buffer. For example, when loading a string resource with the **LoadString** function, an application passes a pointer to a buffer that receives the string resource. The size of the buffer must be large enough to hold the string and a null terminator. Without the heap manager, applications would be forced to use the virtual memory management functions, which allocate a minimum of one page of memory at a time.

## General Heap Behavior

While the heap does provide support for managing smaller chunks of memory, it is itself nothing more than a chunk of memory implemented in the Windows NT virtual memory system. Consequently, the techniques that the heap uses to manage memory are based on the virtual memory management functions available to the heap. Evidence of this is found in the way heaps manifest themselves in a process, if only we could observe this behavior....

The ProcessWalker (PW) sample application explores each of the components within a process, including all of its heaps. PW identifies the heaps in a process and shows the amount of reserved and committed memory associated with a particular heap. As with all other regions of memory in a process, the smallest region of committed memory within a heap is one page (4096 bytes).

This does not mean that the smallest amount of memory that can be allocated in a heap is 4096 bytes; rather, the heap manager commits pages of memory as needed to satisfy specific allocation requests. If, for example, an application allocates 100 bytes via a call to **GlobalAlloc**, the heap manager allocates a 100-byte chunk of memory within its committed region for this request. If there is not enough committed memory available at the time of the request, the heap manager simply commits another page to make the memory available.

Ideally, then, if an application repetitively allocates 100-byte chunks of memory, the heap will commit an additional page of memory every forty-first request (40 * 100 bytes = 4000 bytes). Upon the forty-first request for a chunk of 100 bytes, the heap manager realizes there is not enough committed memory to satisfy the request, so it commits another page of memory and then completes the requested allocation. In this way, the heap manager is responsible for managing the virtual memory environment completely transparent of the application.

In reality, though, the heap manager requires additional memory for managing the memory in the heap. So instead of allocating only 100 bytes as requested, it also allocates some space for managing each particular chunk of memory. The type of memory and the size of the allocation determine the size of this additional memory. I'll discuss these issues later in this article.

## The Two Types of Heaps

Every process in Windows has one heap called the _default heap_. Processes can also have as many other _dynamic heaps_ as they wish, simply by creating and destroying them on the fly. The system uses the default heap for all global and local memory management functions, and the C run-time library uses the default heap for supporting **malloc** functions. The heap memory functions, which indicate a specific heap by its handle, use dynamic heaps. The behavior of dynamic heaps is discussed in the "Heap Memory API" section later in this article.

The default and dynamic heaps are basically the same thing, but the default heap has the special characteristic of being identifiable as the default. This is how the C run-time library and the system identify which heap to allocate from. The **GetProcessHeap** function returns a handle to the default heap for a process. Since functions such as **GlobalAlloc** or **malloc** are executed within the context of the thread that called them, they can simply call **GetProcessHeap** to retrieve a handle to the default heap, and then manage memory accordingly.

### Managing the Default Heap

Both default and dynamic heaps have a specific amount of reserved and committed memory regions associated with them, but they behave differently with respect to these limits. The default heap's reserved and committed memory region sizes are designated when the application is linked. Each application carries this information about itself within its executable image information. You can view this information by dumping header information for the executable image. For example, type the following command at a Windows NT command prompt (PWALK.EXE is used here to complete the example; you will need to substitute your own path and executable file):

```plaintext
link32 -dump -headers d:\samples\walker\pwalk.exe

...
OPTIONAL HEADER VALUES             
     10B magic #                   
    2.29 linker version            
    B000 size of code              
   1E800 size of initialized data  
     600 size of uninitialized data
   18470 address of entry point    
   10000 base of code              
   20000 base of data              
         ----- new -----           
  400000 image base                
   10000 section alignment         
     200 file alignment            
       2 subsystem (Windows GUI)   
     0.B operating system version  
     1.0 image version             
     3.A subsystem version         
   C0000 size of image             
     400 size of headers           
       0 checksum                  
   10000 size of stack reserve     
    1000 size of stack commit      
   10000 size of heap reserve      
    1000 size of heap commit       
   ...
```

The last two entries are hexadecimal values specifying the amount of reserved and committed space initially needed by the application.

There are two ways to tell the linker what to use for these values. You can link your application with a module definition file and include a statement in the file like the following:


```plaintext
HEAPSIZE   0x10000 0x1000
```
Or you can directly inform the linker by using the **/HEAP**  linker switch, as in:

```plaintext
/HEAP: 0x10000, 0x1000
```

In both examples, the heap is specified to initially have 0x10000 (64K) bytes reserved address space and 0x1000 (4K) bytes committed memory. If you fail to indicate the heap size in either method, the linker uses the default values of 0x100000 (1 MB) reserved address space and 0x1000 (4K) committed memory.

The linker accepts almost any value for heap reserve space, because the application loader ensures that the application will meet certain minimum requirements during the load process. In other words, you can link an application with an initial heap value of 1 page reserved address space. The linker doesn't perform any data validation; it simply marks the executable with the given value. Yet, since the minimum range of address space that can be reserved is 16 pages (64K), the loader compensates by reserving 16 pages for the application heap at load time.

As indicated above, options exist that indicate how much memory should initially be committed for an application's default heap. The problem is they don't seem to work yet. The linker for the second beta release of Windows NT marks all executable applications with 0x1000 (4K) initial committed memory for the default heap size, regardless of the value indicated as an option. Yet this is not that big a deal because it actually may be better for an application to commit as it needs to, rather than to commit memory that is not being used.

### A Default Heap That Grows and Spreads 

In its simplest form, the default heap spans a range of addresses. Some ranges are reserved, while others are committed and have pages of memory associated with them. In this case the addresses are contiguous, and they all originated from the same base allocation address. In some cases the default heap needs to allocate more memory than is available in its current reserved address space. For these cases the heap can either fail the call that requests the memory, or reserve an additional address range elsewhere in the process. The default heap manager opts for the second choice.

When the default heap needs more memory than is currently available, it reserves another 1-MB address range in the process. It also initially commits as much memory as it needs from this reserved address range to satisfy the allocation request. The default heap manager is then responsible for managing this new memory region as well as the original heap space. If necessary, it will repeat this throughout the application until the process runs out of memory and address space. You could end up with a default heap that manifests itself in your process in a manner similar to the heap represented in Figure 2.
![ms810603.heapmm_2(en-us,MSDN.10).gif](https://chatgpt.com/c/images/ms810603.heapmm_2(en-us,msdn.10).gif) 

**Figure 2. The default heap for each process can expand into free address regions within the process.** 
So the default heap is not really a static heap at all. In fact, it may seem like a waste of energy to bother with managing the size of the initial heap since the heap always behaves in the same way after initialization. Managing the size of the default heap offers one advantage, though. It takes time to locate and reserve a new range of addresses in a process; you can save time by simply reserving a large enough address range initially. If you expect your application to require more heap space than the 1-MB default, reserve more address space initially to avoid allocating another region of addresses in your process later. Remember, each application has 2 gigabytes (GB) of address space to work with, and requires very little physical memory to support it.

## Global and Local Memory Functions 

At first glance it appears that the local and global memory management functions exist in Windows purely for backward compatibility with Windows version 3.1. This may be true, but the functions are managed as efficiently as the new heap functions discussed below. In fact, porting an application from 16-bit Windows does not necessarily include migrating from global and local memory functions to heap memory functions. The global and local functions offer the same basic capabilities (and then some) and are just as fast to work with. If anything, they are probably more convenient to work with because you do not have to keep track of a heap handle.
Nonetheless, the implementation of these functions is not the same as it was for 16-bit Windows. 16-bit Windows had a global heap, and each application had a local heap. Those two heap managers implemented the global and local functions. Allocating memory via **GlobalAlloc**  meant retrieving a chunk of memory from the global heap, while **LocalAlloc**  allocated memory from the local heap. Windows now has a single heap for both types of functions—the default heap described above.Now you're probably wondering if there is any difference between the local and global functions themselves. Well, the answer is no, they are now the same. In fact, they are interchangeable. Memory allocated via a call to **LocalAlloc**  can be reallocated with **GlobalReAlloc**  and then locked by **LocalLock** . The following table lists the global and local functions now available.
### Table 2 
| Global memory functions | Local memory functions | 
| --- | --- | 
| GlobalAlloc | LocalAlloc | 
| GlobalDiscard | LocalDiscard | 
| GlobalFlags | LocalFlags | 
| GlobalFree | LocalFree | 
| GlobalHandle | LocalHandle | 
| GlobalLock | LocalLock | 
| GlobalReAlloc | LocalReAlloc | 
| GlobalSize | LocalSize | 
| GlobalUnlock | LocalUnlock | 

It seems redundant to have two sets of functions that perform exactly the same, but that's where the backward compatibility comes in. Whether you used the global or local functions in a 16-bit Windows application before doesn't matter now—they are equally efficient.

### Types of Global and Local Memory 
In the Windows API, the global and local memory management functions provide two types of memory, MOVEABLE and FIXED. MOVEABLE memory can be further qualified as DISCARDABLE memory. When you allocate memory with either **GlobalAlloc**  or **LocalAlloc** , you designate the type of memory you want by supplying the appropriate memory flag. The following table lists and describes each memory flag for global and local memory.
### Table 3 
| Global memory flag | Local memory flag | Allocation meaning | 
| --- | --- | --- | 
| GMEM_FIXED | LMEM_FIXED | Allocate fixed memory. | 
| GMEM_MOVEABLE | LMEM_MOVEABLE | Allocate movable memory. | 
| GMEM_DISCARDABLE | LMEM_DISCARDABLE | Allocate discardable, movable memory. | 
| GMEM_ZEROINIT | LMEM_ZEROINIT | Initialize memory to zeros during allocation. | 
| GMEM_NODISCARD | LMEM_NODISCARD | Do not discard other memory to meet the needs of this allocation; instead, fail this request. | 
| GMEM_NOCOMPACT | LMEM_NOCOMPACT | Do not discard or move other memory to meet the needs of this allocation; instead, fail this request. | 
| GMEM_SHARE, GMEM_DDESHARE | N/A | Allocate global memory that is more efficient to use with DDE. | 

It is surprising that the distinction between FIXED and MOVEABLE memory still exists in these functions. In 16-bit Windows, MOVEABLE memory compacted the local and global heaps to reduce fragmentation and make more memory available to all applications. Yet the Windows NT virtual memory system does not rely on these techniques for efficient memory management and has little to gain by applications using them. In any case, they still exist and could actually be used in some circumstances.
When allocating FIXED memory in Windows, the **GlobalAlloc**  and **LocalAlloc**  functions return a 32-bit pointer to the memory block rather than a handle as they do for MOVEABLE memory. The pointer can directly access the memory without having to lock it first. This pointer can also be passed to the **GlobalFree**  and **LocalFree**  functions to release the memory without having to first retrieve the handle by calling the **GlobalHandle**  function. With FIXED memory, allocating and freeing memory is similar to using the C run-time functions **_malloc**  and **_free** .MOVEABLE memory, on the other hand, cannot provide this luxury. Because MOVEABLE memory can be moved (and DISCARDABLE memory can be discarded), the heap manager needs a handle to identify the chunk of memory to move or discard. To access the memory, the handle must first be locked by calling either **GlobalLock**  or **LocalLock** . As in 16-bit Windows, the memory cannot be moved or discarded while the handle is locked.
### The MOVEABLE Memory Handle Table 

As it turns out, each handle to MOVEABLE memory is actually a pointer into the MOVEABLE memory handle table. The handle table exists outside the heap, elsewhere in the process's address space. To learn more about this behavior, we created a test application that allocates several MOVEABLE memory blocks from the default heap. The handle table was created only upon allocation of the first MOVEABLE chunk of memory. This is nice, because if you never allocate any MOVEABLE memory, the table is never created and does not waste memory. ProcessWalker reveals that when this handle table is created, 1 page of memory is committed for the initial table and 512K of address space is reserved (see Figure 3).
![ms810603.heapmm_3(en-us,MSDN.10).gif](https://chatgpt.com/c/images/ms810603.heapmm_3(en-us,msdn.10).gif) 

**Figure 3. ProcessWalker highlights changes in the address space of a process. The heap memory handle table is shown as it looks immediately after it is created.** 
If you work out the math you can see that the number of memory handles available for MOVEABLE memory is limited. 512K bytes / 8 bytes per handle = 65,535 handles. In fact, the system imposes this limitation on each process. Fortunately, this only applies to MOVEABLE memory. You can allocate as many chunks of FIXED memory as you like, provided the memory and address space are available in your process.

Each handle requires 8 bytes of committed memory in the handle table to represent information, including the virtual address of the memory, the lock count on the handle, and the type of memory. Figure 4 shows how the handle table looks when viewed in ProcessWalker.
![ms810603.heapmm_4(en-us,MSDN.10).gif](https://chatgpt.com/c/images/ms810603.heapmm_4(en-us,msdn.10).gif) 

**Figure 4. Each MOVEABLE memory handle is 8 bytes and represents the location of the chunk of memory.** 
> **Note**  In the ProcessWalker view window, each line is 16 bytes (two memory handles). The far-left column represents the address of each line within the process. The addresses in white indicate the lines in which data changed since the last refresh. Red text shows exactly which bytes changed. This feature allows you to easily track changes in memory in response to certain events within the child process. A very useful debugging tool, to say the least.
The first 8 bytes in the view window—at address 0x000f0000—show the first handle allocated in the table. The handle value for this example would actually be 0x000f0004, which is a 4-byte offset into the 8-byte handle table entry. At the 4-byte offset in the table entry is the current 32-bit address representing the location of the chunk of memory. In this example, the 32-bit address is 0x00042A70, reading 4 bytes from right to left starting at 0x000f0008 and ending at 0x000f0004. If the memory is moved to a new location, this address changes to reflect the new location.
If you back up 4 bytes from the handle to the first byte in this handle table entry, you'll find the lock count for the handle. Remember, a block of memory can be moved or discarded only if its handle's lock count is zero. Since there is only 1 byte to record the lock count, it stands to reason that a handle can be locked only 256 (0xFF) times. Unfortunately, the system currently does not warn you when you reach that limit. If you lock a handle a 257th time, you receive a valid pointer to the memory, but the lock count remains at 256. It is possible, then, that you could unlock the handle 256 times and expect the memory to be locked. Yet the lock count is decremented to 0, and the memory could be moved or discarded. So what happens if you try to access the pointer you believe to be valid? Well, it depends on what is now at the address where you believe the memory to be. The memory could still be there, or some other memory could have been moved there. This is not the desired behavior, and we hope the system will be fixed to prevent this from happening. Incidentally, how should the system be fixed? The easiest thing to do would be to fail the call to **GlobalLock**  or **LocalLock**  on any attempt beyond 256, so check the return value to make sure the function succeeds.
The third and fourth bytes of the handle represent the memory type, that is, MOVEABLE, DDESHARE, or DISCARDABLE. Presumably because of compatibility with 16-bit Windows, local and global memory flags that have the same name and meaning do not have the same value. (The WINBASE.H header file defines each flag.) Yet once the memory is allocated, the handle table entry records no difference. Whether you use LMEM_DISCARDABLE or GMEM_DISCARDABLE does not matter—the handle table identifies all DISCARDABLE memory the same way. A little exploring in ProcessWalker shows the following type value identifiers.

### Table 4 
| Memory type | Byte 3 | Byte 4 | 
| --- | --- | --- | 
| MOVEABLE | 02 | – | 
| DISCARDABLE | 06 | – | 
| DDESHARE | – | 08 | 

Keep in mind that these values as represented in the handle table are not documented, so they could change with a new release of Windows NT. But it would be easy to use ProcessWalker to view the handle table to see the changes.

Returning to the test application example.... After allocating the first MOVEABLE memory block and thereby creating the handle table, we used the test application to allocate 15 more handles from the table. A quick view of the memory window showed the first eight lines had data associated with them, while the rest of the committed page was filled with zeros. Then we allocated one more handle, making a total of 17 handles. The view window was refreshed to indicate what changes occurred in the table as a result of allocating the seventeenth handle only. Figure 4 (above) shows the results.

As you can see, more than 8 bytes changed during the last allocation. In fact, 8 lines were updated for a total of 128 bytes. The first 8 bytes represent the seventeenth handle entry information as expected. The following 120 bytes indicate that the heap manager initializes the handle table every sixteenth handle. Examining this initialization data shows that the next 15 available handle table entries are identified in the table. When allocating the eighteenth handle, the location of the nineteenth handle is identified by the address location portion of the eighteenth handle table entry. As expected, then, if a handle is removed from the table (the memory is freed), the address location in that entry is replaced with the location of the next available handle after it. This behavior indicates that the heap manager keeps the location of the next available handle table entry in a static variable and uses that entry itself to store the location of the subsequent entry. Notice also that the last initialized entry has a null location for the next address. The heap manager uses this as an indicator to initialize another 16 handle table entries during the next handle allocation.

Another efficiency in the heap manager is its ability to commit pages of memory for the handle table as it needs them, not all 128 pages (512K) at once. Since the heap manager initializes its handle table in 16-handle (128-byte) increments, it is easy to determine when to commit a new page of memory. Every thirty-second (4096 / 128 = 32) initialization requires a new page of committed memory. Also, the entries do not straddle page boundaries, so their management is easier and potentially more efficient.

### CRT Library 

Managing memory in 16-bit Windows involved a great deal of uncertainty about using the C run-time (CRT) library. Now, there should be little hesitation. The current CRT library is implemented in a manner similar to FIXED memory allocated via the local and global memory management functions. The CRT library is also implemented using the same default heap manager as the global and local memory management functions.
Subsequent memory allocations via **malloc** , **GlobalAlloc** , and **LocalAlloc**  return pointers to memory allocated from the same heap. The heap manager does not divide its space among the CRT and global/local memory functions, and it does not maintain separate heaps for these functions. Instead, it treats them the same, promoting consistent behavior across the types of functions. As a result, you can now write code using the functions you're most comfortable with. And, if you're interested in portability, you can safely use the CRT functions exclusively for managing heap memory.
## Heap Memory API 
As mentioned earlier, you can create as many dynamic heaps as you like by simply calling **HeapCreate** . You must specify the maximum size of the heap so that the function knows how much address space to reserve. You can also indicate how much memory to commit initially. In the following example, a heap is created in your process that reserves 1 MB of address space and initially commits two pages of memory:

```plaintext
hHeap = HeapCreate (0, 0x2000, 0x100000);
```
Since you can have many dynamic heaps in your process, you need a handle to identify each heap when you access it. The **HeapCreate**  function returns this handle. Each heap you create returns a unique handle so that several dynamic heaps may coexist in your process. Having to identify your heap by handle also makes managing dynamic heaps more difficult than managing the default heap, since you have to keep each heap handle around for the life of the heap.If you're bothered by having to keep this handle around, there is an alternative. You can use the heap memory functions on the default heap instead of creating a dynamic heap explicitly for them. To do this, simply use the **GetProcessHeap**  function to get the handle of the default heap. For simple allocations of short-term memory, the following example taken from the ProcessWalker sample application illustrates how easy this is to do:

```plaintext
char    *szCaption;
int     nCaption = GetWindowTextLength (hWnd);

/* retrieve view memory range */
szCaption = HeapAlloc (GetProcessHeap (), 
                       HEAP_ZERO_MEMORY, 
                       nCaption+1);
GetWindowText (hViewWnd, szCaption, nCaption);
```

In this example the default heap is chosen because the allocation is independent of other memory management needs, and there is no reason to create a dynamic heap just for this one allocation. Note that you could achieve the same result by using the global, local, or CRT functions since they allocate only from the default heap.
As shown earlier, the first parameter to **HeapCreate**  allows you to specify an optional HEAP_NO_SERIALIZE flag. A serialized heap does not allow two threads to access it simultaneously. The default behavior is to serialize access to the heap. If you plan to use a heap strictly within one thread, specifying the HEAP_NO_SERIALIZE flag improves overall heap performance slightly.Like all of the heap memory functions, **HeapAlloc**  requires a heap handle as its first argument. The example uses the **GetProcessHeap**  function instead of a dynamic heap handle. The second parameter to **HeapAlloc**  is an optional flag that indicates whether the memory should be zeroed first and whether to generate exceptions on error. To get zeroed memory, specify the HEAP_ZERO_MEMORY flag as shown above. The generate exceptions flag (HEAP_GENERATE_EXCEPTIONS) is a useful feature if you have exception handling built into your application. When using this flag, the function raises an exception on failure rather than just returning NULL. Depending on your use, exception handling can be an effective way of triggering special events—such as low memory situations—in your application.**HeapAlloc**  has a cousin called **HeapReAlloc**  that works in much the same way as the standard global and local memory management functions described earlier. Use **HeapReAlloc**  primarily to resize a previous allocation. This function has four parameters, three of which are the same as for **HeapAlloc** . The new parameter, *lpMem*, is a pointer to the chunk of memory being resized.It is important to note that although heap memory is not movable as in global and local memory, it may be moved during the **HeapReAlloc**  function. This function returns a pointer to the resized chunk of memory, which may or may not be at the same location as initially indicated by the pointer passed to the function. This is the only time memory can be moved in dynamic heaps, and the only chunk of memory affected is the one identified by *lpMem* in the function. You can also override this behavior by specifying the HEAP_REALLOC_IN_PLACE_ONLY flag. With this flag, if there is not enough room to reallocate the memory in place, the function returns with failure status rather than move the memory.Memory allocated with **HeapAlloc**  or reallocated with **HeapReAlloc**  can be freed by calling **HeapFree** . This function is easy to use: simply indicate the heap handle and a pointer to the chunk of memory to free. Completing the example above, here is how you can use **HeapFree**  with the default heap:

```plaintext
/* free default heap memory */
HeapFree (GetProcessHeap (), szCaption);
```

This example shows how easy it can be to work with heaps in Windows. However, you may still want to create a dynamic heap specifically to manage complex dynamic data structures in your application. In fact, one nice benefit of heap memory is how well it caters to the needs of traditional data structures such as binary trees, linked lists, and dynamic arrays. Having the heap handle provides a way of uniquely identifying these structures independently. One example that comes to mind is when you're building a multiwindow application—perhaps a multiple document interface (MDI) application. Simply create and store a heap handle in the window extra bytes or window property list for each window during the WM_CREATE message. Then it is easy to write a window procedure that manages data structures from its own heap by retrieving the heap handle when necessary. When the window goes away, simply have it destroy the heap in the WM_DESTROY message.
You can easily destroy dynamic heaps by calling **HeapDestroy**  on a specific heap handle. This powerful function will remove a heap regardless of its state. The **HeapDestroy**  function doesn't care whether you have outstanding allocations in the heap or not.
To make heap memory management most efficient, you would only create a heap of the size you need. In some cases it is easy to determine the heap size you need—if you're allocating a buffer to read a file into, simply check the size of the file. In other cases, heap size is more difficult to figure—if you're creating a dynamic data structure that grows according to user interaction, it is difficult to predict what the user will do. Dynamic heaps have a provision for this latter circumstance. By specifying a maximum heap size of zero, you make the heap assume a behavior like the default heap. That is, it will grow and spread in your process as much as necessary, limited only by available memory. In this case, available memory means available address space in your process and available pagefile space on your hard disk.

## Overhead on Heap Memory Allocations 

With all types of heap memory, an overhead is associated with each memory allocation. This overhead is due to:

- Granularity on memory allocations within the heap.

- The overhead necessary to manage each memory segment within the heap.

The granularity of heap allocations in 32-bit Windows is 16 bytes. So if you request a global memory allocation of 1 byte, the heap returns a pointer to a chunk of memory, guaranteeing that the 1 byte is available. Chances are, 16 bytes will actually be available because the heap cannot allocate less than 16 bytes at a time.

### Global and Local Memory Functions 
For global and local memory functions, the documentation suggests that you use the **GlobalSize**  and **LocalSize**  functions to determine the exact size of the allocation, but in my tests this function consistently returned the size I requested and not the size actually allocated.To confirm this finding, turn to ProcessWalker again and view the committed memory in your default heap. For the sake of observation, perform consecutive allocations of 1, 2, 3, 14, 15, and 16 bytes using either **GlobalAlloc**  or **LocalAlloc** . In this particular example, we used **GlobalAlloc**  with the GMEM_MOVEABLE flag, but the result is the same for memory allocated as GMEM_FIXED. Then, refresh your view of the committed memory in the heap. Finally, scroll the view window so that the addresses of the allocated blocks of memory are all in view. You should see something similar to the window in Figure 5.![ms810603.heapmm_5(en-us,MSDN.10).gif](https://chatgpt.com/c/images/ms810603.heapmm_5(en-us,msdn.10).gif) 

Figure 5. A ProcessWalker view of the default heap after making consecutive allocations of 1, 2, 3, 14, 15, and 16 bytes using the *GlobalAlloc* function.** In Figure 5, the first line represents the header for the 1-byte allocation, followed immediately by the minimum 16 bytes allocated for the 1-byte request. Just to add visual clarity, the letter *m* appears in each allocated byte beginning at the address of the allocation. The *m*'s are visible in the ASCII representation of memory to the right of each line. At the end of all heap allocations is a heap tail, as indicated by the last line of new information in Figure 5.So, although you request only 1 byte and **GlobalSize**  returns a size of 1 byte, there are actually 16 bytes allocated and available. Similarly, for the 3-byte allocation, 13 additional bytes are available. Even more interesting is the apparent waste of memory for allocations of 14, 15, and 16 bytes. In these allocations an additional 16 bytes were allocated for no reason. These are the lines immediately following the lines with 14, 15, and 16 *m* characters. Presumably you could also use these extra 16 bytes, but again **GlobalSize**  does not indicate their existence.
So what is the cost of allocating from a heap? Well, it depends on the size of the allocation. Every 1-byte allocation uses a total of 32 bytes, and a 16-byte allocation uses a total of 48 bytes. This is a considerable amount of overhead on smaller allocations. Therefore, it would not be a good idea to accumulate a number of small heap allocations because they would cost a great deal in actual memory used. On the other hand, there is nothing wrong with allocating a large chunk of memory from the heap and dividing it into smaller pieces.

### Heap Memory Functions 
Similar to the global and local memory functions, the heap memory functions have a minimum 16-byte granularity and the same overhead on memory allocations. Figure 6 presents a ProcessWalker view of a dynamic heap using the same allocations of 1, 2, 3, 14, 15, and 16 bytes, but this time using the **HeapAlloc**  function.![ms810603.heapmm_6(en-us,MSDN.10).gif](https://chatgpt.com/c/images/ms810603.heapmm_6(en-us,msdn.10).gif) 

**
Here's the entire content converted to markdown, including the table:


```markdown
# Managing Heap Memory

**Randy Kath**  
Microsoft Developer Network Technology Group

Created: April 3, 1993

## Abstract

Determining which function or set of functions to use for managing memory in your application is difficult without a solid understanding of how each group of functions works and the overall impact they each have on the operating system. In an effort to simplify these decisions, this technical article focuses on the use of heaps in Windows: the functions that are available, the way they are used, and the impact their use has on operating system resources. The following topics are discussed:

- The purpose of heaps
- General heap behavior
- The two types of heaps
- Global and local memory functions
- Heap memory functions
- Overhead on heap memory allocations
- Summary and recommendations

In addition to this technical article, a sample application called ProcessWalker is included on the Microsoft Developer Network CD. This sample application explores the behavior of heap memory functions in a process, and it provides several useful implementation examples.

## Introduction

This is one of three related technical articles—"Managing Virtual Memory," "Managing Memory-Mapped Files," and "Managing Heap Memory"—that explain how to manage memory using the Windows API (application programming interface). This introduction identifies the basic memory components in the programming model and indicates which article to reference for specific areas of interest.

The first version of the Microsoft® Windows™ operating system introduced a method of managing dynamic memory based on a single _global heap_, which all applications and the system share, and multiple, private _local heaps_, one for each application. Local and global memory management functions were also provided, offering extended features for this new memory management system. More recently, the Microsoft C run-time (CRT) libraries were modified to include capabilities for managing these heaps in Windows using native CRT functions such as **malloc** and **free**. Consequently, developers are now left with a choice—learn the new API provided as part of Windows version 3.1 or stick to the portable, and typically familiar, CRT functions for managing memory in applications written for 16-bit Windows.

Windows offers three groups of functions for managing memory in applications: memory-mapped file functions, heap memory functions, and virtual memory functions.

![ms810603.heapmm_1(en-us,MSDN.10).gif](images/ms810603.heapmm_1(en-us,msdn.10).gif)
**Figure 1. The Windows API provides different levels of memory management for versatility in application programming.**

Six sets of memory management functions exist in Windows, as shown in Figure 1, all of which were designed to be used independently of one another. So which set of functions should you use? The answer to this question depends greatly on two things: the type of memory management you want, and how the functions relevant to it are implemented in the operating system. In other words, are you building a large database application where you plan to manipulate subsets of a large memory structure? Or maybe you're planning some simple dynamic memory structures, such as linked lists or binary trees? In both cases, you need to know which functions offer the features best suited to your intention and exactly how much of a resource hit occurs when using each function.

The following table categorizes the memory management function groups and indicates which of the three technical articles in this series describes each group's behavior. Each technical article emphasizes the impact these functions have on the system by describing the behavior of the system in response to using the functions.

### Table 1

| Memory set                   | System resource affected                                                                                         | Related technical article          |
|------------------------------|------------------------------------------------------------------------------------------------------------------|------------------------------------|
| Virtual memory functions     | A process's virtual address space<br>System pagefile<br>System memory<br>Hard disk space                         | "Managing Virtual Memory"          |
| Memory-mapped file functions | A process's virtual address space<br>System pagefile<br>Standard file I/O<br>System memory<br>Hard disk space    | "Managing Memory-Mapped Files"     |
| Heap memory functions        | A process's virtual address space<br>System memory<br>Process heap resource structure                            | "Managing Heap Memory"             |
| Global heap memory functions | A process's heap resource structure                                                                              | "Managing Heap Memory"             |
| Local heap memory functions  | A process's heap resource structure                                                                              | "Managing Heap Memory"             |
| C run-time reference library | A process's heap resource structure                                                                              | "Managing Heap Memory"             |

Each technical article discusses issues surrounding the use of Windows-specific functions.

## The Purpose of Heaps

The Windows subsystem on Windows NT provides high-level memory management functions that make it easy for applications to build dynamic data structures, provide compatibility with previous versions of Windows, and create buffers and temporary placeholders for system functions. These memory management functions return handles and pointers to blocks of memory that are allocated at run time and managed by an entity called the _heap_. The heap's primary function is to efficiently manage the memory and address space of a process for an application.

A tall order, considering the heap has absolutely no idea what the application intends to do with its memory and address space. Yet the heap manages to provide a robust set of functions that allow developers to overlook some of the finer details of system resources (such as the difference between reserved, free, and committed memory) so that they can turn their attention to the more important task at hand, that of implementing their applications.

In Windows NT, heaps provide a smaller granularity for the size of the smallest allocatable chunk of memory than the virtual memory management functions do. Applications typically need to allocate a specific number of bytes to fulfill a parameter request or to act as a temporary buffer. For example, when loading a string resource with the **LoadString** function, an application passes a pointer to a buffer that receives the string resource. The size of the buffer must be large enough to hold the string and a null terminator. Without the heap manager, applications would be forced to use the virtual memory management functions, which allocate a minimum of one page of memory at a time.

## General Heap Behavior

While the heap does provide support for managing smaller chunks of memory, it is itself nothing more than a chunk of memory implemented in the Windows NT virtual memory system. Consequently, the techniques that the heap uses to manage memory are based on the virtual memory management functions available to the heap. Evidence of this is found in the way heaps manifest themselves in a process, if only we could observe this behavior....

The ProcessWalker (PW) sample application explores each of the components within a process, including all of its heaps. PW identifies the heaps in a process and shows the amount of reserved and committed memory associated with a particular heap. As with all other regions of memory in a process, the smallest region of committed memory within a heap is one page (4096 bytes).

This does not mean that the smallest amount of memory that can be allocated in a heap is 4096 bytes; rather, the heap manager commits pages of memory as needed to satisfy specific allocation requests. If, for example, an application allocates 100 bytes via a call to **GlobalAlloc**, the heap manager allocates a 100-byte chunk of memory within its committed region for this request. If there is not enough committed memory available at the time of the request, the heap manager simply commits another page to make the memory available.

Ideally, then, if an application repetitively allocates 100-byte chunks of memory, the heap will commit an additional page of memory every forty-first request (40 * 100 bytes = 4000 bytes). Upon the forty-first request for a chunk of 100 bytes, the heap manager realizes there is not enough committed memory to satisfy the request, so it commits another page of memory and then completes the requested allocation. In this way, the heap manager is responsible for managing the virtual memory environment completely transparent of the application.

In reality, though, the heap manager requires additional memory for managing the memory in the heap. So instead of allocating only 100 bytes as requested, it also allocates some space for managing each particular chunk of memory. The type of memory and the size of the allocation determine the size of this additional memory. I'll discuss these issues later in this article.

## The Two Types of Heaps

Every process in Windows has one heap called the _default heap_. Processes can also have as many other _dynamic heaps_ as they wish, simply by creating and destroying them on the fly. The system uses the default heap for all global and local memory management functions, and the C run-time library uses the default heap for supporting **malloc** functions. The heap memory functions, which indicate a specific heap by its handle, use dynamic heaps. The behavior of dynamic heaps is discussed in the "Heap Memory API" section later in this article.

The default and dynamic heaps are basically the same thing, but the default heap has the special characteristic of being identifiable as the default. This is how the C run-time library and the system identify which heap to allocate from. The **GetProcessHeap** function returns a handle to the default heap for a process. Since functions such as **GlobalAlloc** or **malloc** are executed within the context of the thread that called them, they can simply call **GetProcessHeap** to retrieve a handle to the default heap, and then manage memory accordingly.

### Managing the Default Heap

Both default and dynamic heaps have a specific amount of reserved and committed memory regions associated with them, but they behave differently with respect to these limits. The default heap's reserved and committed memory region sizes are designated when the application is linked. Each application carries this information about itself within its executable image information. You can view this information by dumping header information for the executable image. For example, type the following command at a Windows NT command prompt (PWALK.EXE is used here to complete the example; you will need to substitute your own path and executable file):

```plaintext
link32 -dump -headers d:\samples\walker\pwalk.exe

...
OPTIONAL HEADER VALUES             
     10B magic #                   
    2.29 linker version            
    B000 size of code              
   1E800 size of initialized data  
     600 size of uninitialized data
   18470 address of entry point    
   10000 base of code              
   20000 base of data              
         ----- new -----           
  400000 image base                
   10000 section alignment         
     200 file alignment            
       2 subsystem (Windows GUI)   
     0.B operating system version  
     1.0 image version             
     3.A subsystem version         
   C0000 size of image             
     400 size of headers           
       0 checksum                  
   10000 size of stack reserve     
    1000 size of stack commit      
   10000 size of heap reserve      
    1000 size of heap commit       
   ...
```

The last two entries are hexadecimal values specifying the amount of reserved and committed space initially needed by the application.

There are two ways to tell the linker what to use for these values. You can link your application with a module definition file and include a statement in the file like the following:


```plaintext
HEAPSIZE   0x10000 0x1000
```
Or you can directly inform the linker by using the **/HEAP**  linker switch, as in:

```plaintext
/HEAP: 0x10000, 0x1000
```

In both examples, the heap is specified to initially have 0x10000 (64K) bytes reserved address space and 0x1000 (4K) bytes committed memory. If you fail to indicate the heap size in either method, the linker uses the default values of 0x100000 (1 MB) reserved address space and 0x1000 (4K) committed memory.

The linker accepts almost any value for heap reserve space, because the application loader ensures that the application will meet certain minimum requirements during the load process. In other words, you can link an application with an initial heap value of 1 page reserved address space. The linker doesn't perform any data validation; it simply marks the executable with the given value. Yet, since the minimum range of address space that can be reserved is 16 pages (64K), the loader compensates by reserving 16 pages for the application heap at load time.

As indicated above, options exist that indicate how much memory should initially be committed for an application's default heap. The problem is they don't seem to work yet. The linker for the second beta release of Windows NT marks all executable applications with 0x1000 (4K) initial committed memory for the default heap size, regardless of the value indicated as an option. Yet this is not that big a deal because it actually may be better for an application to commit as it needs to, rather than to commit memory that is not being used.

### A Default Heap That Grows and Spreads 

In its simplest form, the default heap spans a range of addresses. Some ranges are reserved, while others are committed and have pages of memory associated with them. In this case the addresses are contiguous, and they all originated from the same base allocation address. In some cases the default heap needs to allocate more memory than is available in its current reserved address space. For these cases the heap can either fail the call that requests the memory, or reserve an additional address range elsewhere in the process. The default heap manager opts for the second choice.

When the default heap needs more memory than is currently available, it reserves another 1-MB address range in the process. It also initially commits as much memory as it needs from this reserved address range to satisfy the allocation request. The default heap manager is then responsible for managing this new memory region as well as the original heap space. If necessary, it will repeat this throughout the application until the process runs out of memory and address space. You could end up with a default heap that manifests itself in your process in a manner similar to the heap represented in Figure 2.
![ms810603.heapmm_2(en-us,MSDN.10).gif](https://chatgpt.com/c/images/ms810603.heapmm_2(en-us,msdn.10).gif) 

**Figure 2. The default heap for each process can expand into free address regions within the process.** 
So the default heap is not really a static heap at all. In fact, it may seem like a waste of energy to bother with managing the size of the initial heap since the heap always behaves in the same way after initialization. Managing the size of the default heap offers one advantage, though. It takes time to locate and reserve a new range of addresses in a process; you can save time by simply reserving a large enough address range initially. If you expect your application to require more heap space than the 1-MB default, reserve more address space initially to avoid allocating another region of addresses in your process later. Remember, each application has 2 gigabytes (GB) of address space to work with, and requires very little physical memory to support it.

## Global and Local Memory Functions 

At first glance it appears that the local and global memory management functions exist in Windows purely for backward compatibility with Windows version 3.1. This may be true, but the functions are managed as efficiently as the new heap functions discussed below. In fact, porting an application from 16-bit Windows does not necessarily include migrating from global and local memory functions to heap memory functions. The global and local functions offer the same basic capabilities (and then some) and are just as fast to work with. If anything, they are probably more convenient to work with because you do not have to keep track of a heap handle.
Nonetheless, the implementation of these functions is not the same as it was for 16-bit Windows. 16-bit Windows had a global heap, and each application had a local heap. Those two heap managers implemented the global and local functions. Allocating memory via **GlobalAlloc**  meant retrieving a chunk of memory from the global heap, while **LocalAlloc**  allocated memory from the local heap. Windows now has a single heap for both types of functions—the default heap described above.Now you're probably wondering if there is any difference between the local and global functions themselves. Well, the answer is no, they are now the same. In fact, they are interchangeable. Memory allocated via a call to **LocalAlloc**  can be reallocated with **GlobalReAlloc**  and then locked by **LocalLock** . The following table lists the global and local functions now available.
### Table 2 
| Global memory functions | Local memory functions | 
| --- | --- | 
| GlobalAlloc | LocalAlloc | 
| GlobalDiscard | LocalDiscard | 
| GlobalFlags | LocalFlags | 
| GlobalFree | LocalFree | 
| GlobalHandle | LocalHandle | 
| GlobalLock | LocalLock | 
| GlobalReAlloc | LocalReAlloc | 
| GlobalSize | LocalSize | 
| GlobalUnlock | LocalUnlock | 

It seems redundant to have two sets of functions that perform exactly the same, but that's where the backward compatibility comes in. Whether you used the global or local functions in a 16-bit Windows application before doesn't matter now—they are equally efficient.

### Types of Global and Local Memory 
In the Windows API, the global and local memory management functions provide two types of memory, MOVEABLE and FIXED. MOVEABLE memory can be further qualified as DISCARDABLE memory. When you allocate memory with either **GlobalAlloc**  or **LocalAlloc** , you designate the type of memory you want by supplying the appropriate memory flag. The following table lists and describes each memory flag for global and local memory.
### Table 3 
| Global memory flag | Local memory flag | Allocation meaning | 
| --- | --- | --- | 
| GMEM_FIXED | LMEM_FIXED | Allocate fixed memory. | 
| GMEM_MOVEABLE | LMEM_MOVEABLE | Allocate movable memory. | 
| GMEM_DISCARDABLE | LMEM_DISCARDABLE | Allocate discardable, movable memory. | 
| GMEM_ZEROINIT | LMEM_ZEROINIT | Initialize memory to zeros during allocation. | 
| GMEM_NODISCARD | LMEM_NODISCARD | Do not discard other memory to meet the needs of this allocation; instead, fail this request. | 
| GMEM_NOCOMPACT | LMEM_NOCOMPACT | Do not discard or move other memory to meet the needs of this allocation; instead, fail this request. | 
| GMEM_SHARE, GMEM_DDESHARE | N/A | Allocate global memory that is more efficient to use with DDE. | 

It is surprising that the distinction between FIXED and MOVEABLE memory still exists in these functions. In 16-bit Windows, MOVEABLE memory compacted the local and global heaps to reduce fragmentation and make more memory available to all applications. Yet the Windows NT virtual memory system does not rely on these techniques for efficient memory management and has little to gain by applications using them. In any case, they still exist and could actually be used in some circumstances.
When allocating FIXED memory in Windows, the **GlobalAlloc**  and **LocalAlloc**  functions return a 32-bit pointer to the memory block rather than a handle as they do for MOVEABLE memory. The pointer can directly access the memory without having to lock it first. This pointer can also be passed to the **GlobalFree**  and **LocalFree**  functions to release the memory without having to first retrieve the handle by calling the **GlobalHandle**  function. With FIXED memory, allocating and freeing memory is similar to using the C run-time functions **_malloc**  and **_free** .MOVEABLE memory, on the other hand, cannot provide this luxury. Because MOVEABLE memory can be moved (and DISCARDABLE memory can be discarded), the heap manager needs a handle to identify the chunk of memory to move or discard. To access the memory, the handle must first be locked by calling either **GlobalLock**  or **LocalLock** . As in 16-bit Windows, the memory cannot be moved or discarded while the handle is locked.
### The MOVEABLE Memory Handle Table 

As it turns out, each handle to MOVEABLE memory is actually a pointer into the MOVEABLE memory handle table. The handle table exists outside the heap, elsewhere in the process's address space. To learn more about this behavior, we created a test application that allocates several MOVEABLE memory blocks from the default heap. The handle table was created only upon allocation of the first MOVEABLE chunk of memory. This is nice, because if you never allocate any MOVEABLE memory, the table is never created and does not waste memory. ProcessWalker reveals that when this handle table is created, 1 page of memory is committed for the initial table and 512K of address space is reserved (see Figure 3).
![ms810603.heapmm_3(en-us,MSDN.10).gif](https://chatgpt.com/c/images/ms810603.heapmm_3(en-us,msdn.10).gif) 

**Figure 3. ProcessWalker highlights changes in the address space of a process. The heap memory handle table is shown as it looks immediately after it is created.** 
If you work out the math you can see that the number of memory handles available for MOVEABLE memory is limited. 512K bytes / 8 bytes per handle = 65,535 handles. In fact, the system imposes this limitation on each process. Fortunately, this only applies to MOVEABLE memory. You can allocate as many chunks of FIXED memory as you like, provided the memory and address space are available in your process.

Each handle requires 8 bytes of committed memory in the handle table to represent information, including the virtual address of the memory, the lock count on the handle, and the type of memory. Figure 4 shows how the handle table looks when viewed in ProcessWalker.
![ms810603.heapmm_4(en-us,MSDN.10).gif](https://chatgpt.com/c/images/ms810603.heapmm_4(en-us,msdn.10).gif) 

**Figure 4. Each MOVEABLE memory handle is 8 bytes and represents the location of the chunk of memory.** 
> **Note**  In the ProcessWalker view window, each line is 16 bytes (two memory handles). The far-left column represents the address of each line within the process. The addresses in white indicate the lines in which data changed since the last refresh. Red text shows exactly which bytes changed. This feature allows you to easily track changes in memory in response to certain events within the child process. A very useful debugging tool, to say the least.
The first 8 bytes in the view window—at address 0x000f0000—show the first handle allocated in the table. The handle value for this example would actually be 0x000f0004, which is a 4-byte offset into the 8-byte handle table entry. At the 4-byte offset in the table entry is the current 32-bit address representing the location of the chunk of memory. In this example, the 32-bit address is 0x00042A70, reading 4 bytes from right to left starting at 0x000f0008 and ending at 0x000f0004. If the memory is moved to a new location, this address changes to reflect the new location.
If you back up 4 bytes from the handle to the first byte in this handle table entry, you'll find the lock count for the handle. Remember, a block of memory can be moved or discarded only if its handle's lock count is zero. Since there is only 1 byte to record the lock count, it stands to reason that a handle can be locked only 256 (0xFF) times. Unfortunately, the system currently does not warn you when you reach that limit. If you lock a handle a 257th time, you receive a valid pointer to the memory, but the lock count remains at 256. It is possible, then, that you could unlock the handle 256 times and expect the memory to be locked. Yet the lock count is decremented to 0, and the memory could be moved or discarded. So what happens if you try to access the pointer you believe to be valid? Well, it depends on what is now at the address where you believe the memory to be. The memory could still be there, or some other memory could have been moved there. This is not the desired behavior, and we hope the system will be fixed to prevent this from happening. Incidentally, how should the system be fixed? The easiest thing to do would be to fail the call to **GlobalLock**  or **LocalLock**  on any attempt beyond 256, so check the return value to make sure the function succeeds.
The third and fourth bytes of the handle represent the memory type, that is, MOVEABLE, DDESHARE, or DISCARDABLE. Presumably because of compatibility with 16-bit Windows, local and global memory flags that have the same name and meaning do not have the same value. (The WINBASE.H header file defines each flag.) Yet once the memory is allocated, the handle table entry records no difference. Whether you use LMEM_DISCARDABLE or GMEM_DISCARDABLE does not matter—the handle table identifies all DISCARDABLE memory the same way. A little exploring in ProcessWalker shows the following type value identifiers.

### Table 4 
| Memory type | Byte 3 | Byte 4 | 
| --- | --- | --- | 
| MOVEABLE | 02 | – | 
| DISCARDABLE | 06 | – | 
| DDESHARE | – | 08 | 

Keep in mind that these values as represented in the handle table are not documented, so they could change with a new release of Windows NT. But it would be easy to use ProcessWalker to view the handle table to see the changes.

Returning to the test application example.... After allocating the first MOVEABLE memory block and thereby creating the handle table, we used the test application to allocate 15 more handles from the table. A quick view of the memory window showed the first eight lines had data associated with them, while the rest of the committed page was filled with zeros. Then we allocated one more handle, making a total of 17 handles. The view window was refreshed to indicate what changes occurred in the table as a result of allocating the seventeenth handle only. Figure 4 (above) shows the results.

As you can see, more than 8 bytes changed during the last allocation. In fact, 8 lines were updated for a total of 128 bytes. The first 8 bytes represent the seventeenth handle entry information as expected. The following 120 bytes indicate that the heap manager initializes the handle table every sixteenth handle. Examining this initialization data shows that the next 15 available handle table entries are identified in the table. When allocating the eighteenth handle, the location of the nineteenth handle is identified by the address location portion of the eighteenth handle table entry. As expected, then, if a handle is removed from the table (the memory is freed), the address location in that entry is replaced with the location of the next available handle after it. This behavior indicates that the heap manager keeps the location of the next available handle table entry in a static variable and uses that entry itself to store the location of the subsequent entry. Notice also that the last initialized entry has a null location for the next address. The heap manager uses this as an indicator to initialize another 16 handle table entries during the next handle allocation.

Another efficiency in the heap manager is its ability to commit pages of memory for the handle table as it needs them, not all 128 pages (512K) at once. Since the heap manager initializes its handle table in 16-handle (128-byte) increments, it is easy to determine when to commit a new page of memory. Every thirty-second (4096 / 128 = 32) initialization requires a new page of committed memory. Also, the entries do not straddle page boundaries, so their management is easier and potentially more efficient.

### CRT Library 

Managing memory in 16-bit Windows involved a great deal of uncertainty about using the C run-time (CRT) library. Now, there should be little hesitation. The current CRT library is implemented in a manner similar to FIXED memory allocated via the local and global memory management functions. The CRT library is also implemented using the same default heap manager as the global and local memory management functions.
Subsequent memory allocations via **malloc** , **GlobalAlloc** , and **LocalAlloc**  return pointers to memory allocated from the same heap. The heap manager does not divide its space among the CRT and global/local memory functions, and it does not maintain separate heaps for these functions. Instead, it treats them the same, promoting consistent behavior across the types of functions. As a result, you can now write code using the functions you're most comfortable with. And, if you're interested in portability, you can safely use the CRT functions exclusively for managing heap memory.
## Heap Memory API 
As mentioned earlier, you can create as many dynamic heaps as you like by simply calling **HeapCreate** . You must specify the maximum size of the heap so that the function knows how much address space to reserve. You can also indicate how much memory to commit initially. In the following example, a heap is created in your process that reserves 1 MB of address space and initially commits two pages of memory:

```plaintext
hHeap = HeapCreate (0, 0x2000, 0x100000);
```
Since you can have many dynamic heaps in your process, you need a handle to identify each heap when you access it. The **HeapCreate**  function returns this handle. Each heap you create returns a unique handle so that several dynamic heaps may coexist in your process. Having to identify your heap by handle also makes managing dynamic heaps more difficult than managing the default heap, since you have to keep each heap handle around for the life of the heap.If you're bothered by having to keep this handle around, there is an alternative. You can use the heap memory functions on the default heap instead of creating a dynamic heap explicitly for them. To do this, simply use the **GetProcessHeap**  function to get the handle of the default heap. For simple allocations of short-term memory, the following example taken from the ProcessWalker sample application illustrates how easy this is to do:

```plaintext
char    *szCaption;
int     nCaption = GetWindowTextLength (hWnd);

/* retrieve view memory range */
szCaption = HeapAlloc (GetProcessHeap (), 
                       HEAP_ZERO_MEMORY, 
                       nCaption+1);
GetWindowText (hViewWnd, szCaption, nCaption);
```

In this example the default heap is chosen because the allocation is independent of other memory management needs, and there is no reason to create a dynamic heap just for this one allocation. Note that you could achieve the same result by using the global, local, or CRT functions since they allocate only from the default heap.
As shown earlier, the first parameter to **HeapCreate**  allows you to specify an optional HEAP_NO_SERIALIZE flag. A serialized heap does not allow two threads to access it simultaneously. The default behavior is to serialize access to the heap. If you plan to use a heap strictly within one thread, specifying the HEAP_NO_SERIALIZE flag improves overall heap performance slightly.Like all of the heap memory functions, **HeapAlloc**  requires a heap handle as its first argument. The example uses the **GetProcessHeap**  function instead of a dynamic heap handle. The second parameter to **HeapAlloc**  is an optional flag that indicates whether the memory should be zeroed first and whether to generate exceptions on error. To get zeroed memory, specify the HEAP_ZERO_MEMORY flag as shown above. The generate exceptions flag (HEAP_GENERATE_EXCEPTIONS) is a useful feature if you have exception handling built into your application. When using this flag, the function raises an exception on failure rather than just returning NULL. Depending on your use, exception handling can be an effective way of triggering special events—such as low memory situations—in your application.**HeapAlloc**  has a cousin called **HeapReAlloc**  that works in much the same way as the standard global and local memory management functions described earlier. Use **HeapReAlloc**  primarily to resize a previous allocation. This function has four parameters, three of which are the same as for **HeapAlloc** . The new parameter, *lpMem*, is a pointer to the chunk of memory being resized.It is important to note that although heap memory is not movable as in global and local memory, it may be moved during the **HeapReAlloc**  function. This function returns a pointer to the resized chunk of memory, which may or may not be at the same location as initially indicated by the pointer passed to the function. This is the only time memory can be moved in dynamic heaps, and the only chunk of memory affected is the one identified by *lpMem* in the function. You can also override this behavior by specifying the HEAP_REALLOC_IN_PLACE_ONLY flag. With this flag, if there is not enough room to reallocate the memory in place, the function returns with failure status rather than move the memory.Memory allocated with **HeapAlloc**  or reallocated with **HeapReAlloc**  can be freed by calling **HeapFree** . This function is easy to use: simply indicate the heap handle and a pointer to the chunk of memory to free. Completing the example above, here is how you can use **HeapFree**  with the default heap:

```plaintext
/* free default heap memory */
HeapFree (GetProcessHeap (), szCaption);
```

This example shows how easy it can be to work with heaps in Windows. However, you may still want to create a dynamic heap specifically to manage complex dynamic data structures in your application. In fact, one nice benefit of heap memory is how well it caters to the needs of traditional data structures such as binary trees, linked lists, and dynamic arrays. Having the heap handle provides a way of uniquely identifying these structures independently. One example that comes to mind is when you're building a multiwindow application—perhaps a multiple document interface (MDI) application. Simply create and store a heap handle in the window extra bytes or window property list for each window during the WM_CREATE message. Then it is easy to write a window procedure that manages data structures from its own heap by retrieving the heap handle when necessary. When the window goes away, simply have it destroy the heap in the WM_DESTROY message.
You can easily destroy dynamic heaps by calling **HeapDestroy**  on a specific heap handle. This powerful function will remove a heap regardless of its state. The **HeapDestroy**  function doesn't care whether you have outstanding allocations in the heap or not.
To make heap memory management most efficient, you would only create a heap of the size you need. In some cases it is easy to determine the heap size you need—if you're allocating a buffer to read a file into, simply check the size of the file. In other cases, heap size is more difficult to figure—if you're creating a dynamic data structure that grows according to user interaction, it is difficult to predict what the user will do. Dynamic heaps have a provision for this latter circumstance. By specifying a maximum heap size of zero, you make the heap assume a behavior like the default heap. That is, it will grow and spread in your process as much as necessary, limited only by available memory. In this case, available memory means available address space in your process and available pagefile space on your hard disk.

## Overhead on Heap Memory Allocations 

With all types of heap memory, an overhead is associated with each memory allocation. This overhead is due to:

- Granularity on memory allocations within the heap.

- The overhead necessary to manage each memory segment within the heap.

The granularity of heap allocations in 32-bit Windows is 16 bytes. So if you request a global memory allocation of 1 byte, the heap returns a pointer to a chunk of memory, guaranteeing that the 1 byte is available. Chances are, 16 bytes will actually be available because the heap cannot allocate less than 16 bytes at a time.

### Global and Local Memory Functions 
For global and local memory functions, the documentation suggests that you use the **GlobalSize**  and **LocalSize**  functions to determine the exact size of the allocation, but in my tests this function consistently returned the size I requested and not the size actually allocated.To confirm this finding, turn to ProcessWalker again and view the committed memory in your default heap. For the sake of observation, perform consecutive allocations of 1, 2, 3, 14, 15, and 16 bytes using either **GlobalAlloc**  or **LocalAlloc** . In this particular example, we used **GlobalAlloc**  with the GMEM_MOVEABLE flag, but the result is the same for memory allocated as GMEM_FIXED. Then, refresh your view of the committed memory in the heap. Finally, scroll the view window so that the addresses of the allocated blocks of memory are all in view. You should see something similar to the window in Figure 5.![ms810603.heapmm_5(en-us,MSDN.10).gif](https://chatgpt.com/c/images/ms810603.heapmm_5(en-us,msdn.10).gif) 

**
Here's the entire content converted to markdown, including the table:


# Managing Heap Memory

**Randy Kath**  
Microsoft Developer Network Technology Group

Created: April 3, 1993

## Abstract

Determining which function or set of functions to use for managing memory in your application is difficult without a solid understanding of how each group of functions works and the overall impact they each have on the operating system. In an effort to simplify these decisions, this technical article focuses on the use of heaps in Windows: the functions that are available, the way they are used, and the impact their use has on operating system resources. The following topics are discussed:

- The purpose of heaps
- General heap behavior
- The two types of heaps
- Global and local memory functions
- Heap memory functions
- Overhead on heap memory allocations
- Summary and recommendations

In addition to this technical article, a sample application called ProcessWalker is included on the Microsoft Developer Network CD. This sample application explores the behavior of heap memory functions in a process, and it provides several useful implementation examples.

## Introduction

This is one of three related technical articles—"Managing Virtual Memory," "Managing Memory-Mapped Files," and "Managing Heap Memory"—that explain how to manage memory using the Windows API (application programming interface). This introduction identifies the basic memory components in the programming model and indicates which article to reference for specific areas of interest.

The first version of the Microsoft® Windows™ operating system introduced a method of managing dynamic memory based on a single _global heap_, which all applications and the system share, and multiple, private _local heaps_, one for each application. Local and global memory management functions were also provided, offering extended features for this new memory management system. More recently, the Microsoft C run-time (CRT) libraries were modified to include capabilities for managing these heaps in Windows using native CRT functions such as **malloc** and **free**. Consequently, developers are now left with a choice—learn the new API provided as part of Windows version 3.1 or stick to the portable, and typically familiar, CRT functions for managing memory in applications written for 16-bit Windows.

Windows offers three groups of functions for managing memory in applications: memory-mapped file functions, heap memory functions, and virtual memory functions.

![ms810603.heapmm_1(en-us,MSDN.10).gif](images/ms810603.heapmm_1(en-us,msdn.10).gif)
**Figure 1. The Windows API provides different levels of memory management for versatility in application programming.**

Six sets of memory management functions exist in Windows, as shown in Figure 1, all of which were designed to be used independently of one another. So which set of functions should you use? The answer to this question depends greatly on two things: the type of memory management you want, and how the functions relevant to it are implemented in the operating system. In other words, are you building a large database application where you plan to manipulate subsets of a large memory structure? Or maybe you're planning some simple dynamic memory structures, such as linked lists or binary trees? In both cases, you need to know which functions offer the features best suited to your intention and exactly how much of a resource hit occurs when using each function.

The following table categorizes the memory management function groups and indicates which of the three technical articles in this series describes each group's behavior. Each technical article emphasizes the impact these functions have on the system by describing the behavior of the system in response to using the functions.

### Table 1

| Memory set                   | System resource affected                                                                                         | Related technical article          |
|------------------------------|------------------------------------------------------------------------------------------------------------------|------------------------------------|
| Virtual memory functions     | A process's virtual address space<br>System pagefile<br>System memory<br>Hard disk space                         | "Managing Virtual Memory"          |
| Memory-mapped file functions | A process's virtual address space<br>System pagefile<br>Standard file I/O<br>System memory<br>Hard disk space    | "Managing Memory-Mapped Files"     |
| Heap memory functions        | A process's virtual address space<br>System memory<br>Process heap resource structure                            | "Managing Heap Memory"             |
| Global heap memory functions | A process's heap resource structure                                                                              | "Managing Heap Memory"             |
| Local heap memory functions  | A process's heap resource structure                                                                              | "Managing Heap Memory"             |
| C run-time reference library | A process's heap resource structure                                                                              | "Managing Heap Memory"             |

Each technical article discusses issues surrounding the use of Windows-specific functions.

## The Purpose of Heaps

The Windows subsystem on Windows NT provides high-level memory management functions that make it easy for applications to build dynamic data structures, provide compatibility with previous versions of Windows, and create buffers and temporary placeholders for system functions. These memory management functions return handles and pointers to blocks of memory that are allocated at run time and managed by an entity called the _heap_. The heap's primary function is to efficiently manage the memory and address space of a process for an application.

A tall order, considering the heap has absolutely no idea what the application intends to do with its memory and address space. Yet the heap manages to provide a robust set of functions that allow developers to overlook some of the finer details of system resources (such as the difference between reserved, free, and committed memory) so that they can turn their attention to the more important task at hand, that of implementing their applications.

In Windows NT, heaps provide a smaller granularity for the size of the smallest allocatable chunk of memory than the virtual memory management functions do. Applications typically need to allocate a specific number of bytes to fulfill a parameter request or to act as a temporary buffer. For example, when loading a string resource with the **LoadString** function, an application passes a pointer to a buffer that receives the string resource. The size of the buffer must be large enough to hold the string and a null terminator. Without the heap manager, applications would be forced to use the virtual memory management functions, which allocate a minimum of one page of memory at a time.

## General Heap Behavior

While the heap does provide support for managing smaller chunks of memory, it is itself nothing more than a chunk of memory implemented in the Windows NT virtual memory system. Consequently, the techniques that the heap uses to manage memory are based on the virtual memory management functions available to the heap. Evidence of this is found in the way heaps manifest themselves in a process, if only we could observe this behavior....

The ProcessWalker (PW) sample application explores each of the components within a process, including all of its heaps. PW identifies the heaps in a process and shows the amount of reserved and committed memory associated with a particular heap. As with all other regions of memory in a process, the smallest region of committed memory within a heap is one page (4096 bytes).

This does not mean that the smallest amount of memory that can be allocated in a heap is 4096 bytes; rather, the heap manager commits pages of memory as needed to satisfy specific allocation requests. If, for example, an application allocates 100 bytes via a call to **GlobalAlloc**, the heap manager allocates a 100-byte chunk of memory within its committed region for this request. If there is not enough committed memory available at the time of the request, the heap manager simply commits another page to make the memory available.

Ideally, then, if an application repetitively allocates 100-byte chunks of memory, the heap will commit an additional page of memory every forty-first request (40 * 100 bytes = 4000 bytes). Upon the forty-first request for a chunk of 100 bytes, the heap manager realizes there is not enough committed memory to satisfy the request, so it commits another page of memory and then completes the requested allocation. In this way, the heap manager is responsible for managing the virtual memory environment completely transparent of the application.

In reality, though, the heap manager requires additional memory for managing the memory in the heap. So instead of allocating only 100 bytes as requested, it also allocates some space for managing each particular chunk of memory. The type of memory and the size of the allocation determine the size of this additional memory. I'll discuss these issues later in this article.

## The Two Types of Heaps

Every process in Windows has one heap called the _default heap_. Processes can also have as many other _dynamic heaps_ as they wish, simply by creating and destroying them on the fly. The system uses the default heap for all global and local memory management functions, and the C run-time library uses the default heap for supporting **malloc** functions. The heap memory functions, which indicate a specific heap by its handle, use dynamic heaps. The behavior of dynamic heaps is discussed in the "Heap Memory API" section later in this article.

The default and dynamic heaps are basically the same thing, but the default heap has the special characteristic of being identifiable as the default. This is how the C run-time library and the system identify which heap to allocate from. The **GetProcessHeap** function returns a handle to the default heap for a process. Since functions such as **GlobalAlloc** or **malloc** are executed within the context of the thread that called them, they can simply call **GetProcessHeap** to retrieve a handle to the default heap, and then manage memory accordingly.

### Managing the Default Heap

Both default and dynamic heaps have a specific amount of reserved and committed memory regions associated with them, but they behave differently with respect to these limits. The default heap's reserved and committed memory region sizes are designated when the application is linked. Each application carries this information about itself within its executable image information. You can view this information by dumping header information for the executable image. For example, type the following command at a Windows NT command prompt (PWALK.EXE is used here to complete the example; you will need to substitute your own path and executable file):

```powershell
link32 -dump -headers d:\samples\walker\pwalk.exe

...
OPTIONAL HEADER VALUES             
     10B magic #                   
    2.29 linker version            
    B000 size of code              
   1E800 size of initialized data  
     600 size of uninitialized data
   18470 address of entry point    
   10000 base of code              
   20000 base of data              
         ----- new -----           
  400000 image base                
   10000 section alignment         
     200 file alignment            
       2 subsystem (Windows GUI)   
     0.B operating system version  
     1.0 image version             
     3.A subsystem version         
   C0000 size of image             
     400 size of headers           
       0 checksum                  
   10000 size of stack reserve     
    1000 size of stack commit      
   10000 size of heap reserve      
    1000 size of heap commit       
   ...
```

The last two entries are hexadecimal values specifying the amount of reserved and committed space initially needed by the application.

There are two ways to tell the linker what to use for these values. You can link your application with a module definition file and include a statement in the file like the following:


```plaintext
HEAPSIZE   0x10000 0x1000
```
Or you can directly inform the linker by using the **/HEAP**  linker switch, as in:

```plaintext
/HEAP: 0x10000, 0x1000
```

In both examples, the heap is specified to initially have 0x10000 (64K) bytes reserved address space and 0x1000 (4K) bytes committed memory. If you fail to indicate the heap size in either method, the linker uses the default values of 0x100000 (1 MB) reserved address space and 0x1000 (4K) committed memory.

The linker accepts almost any value for heap reserve space, because the application loader ensures that the application will meet certain minimum requirements during the load process. In other words, you can link an application with an initial heap value of 1 page reserved address space. The linker doesn't perform any data validation; it simply marks the executable with the given value. Yet, since the minimum range of address space that can be reserved is 16 pages (64K), the loader compensates by reserving 16 pages for the application heap at load time.

As indicated above, options exist that indicate how much memory should initially be committed for an application's default heap. The problem is they don't seem to work yet. The linker for the second beta release of Windows NT marks all executable applications with 0x1000 (4K) initial committed memory for the default heap size, regardless of the value indicated as an option. Yet this is not that big a deal because it actually may be better for an application to commit as it needs to, rather than to commit memory that is not being used.

### A Default Heap That Grows and Spreads 

In its simplest form, the default heap spans a range of addresses. Some ranges are reserved, while others are committed and have pages of memory associated with them. In this case the addresses are contiguous, and they all originated from the same base allocation address. In some cases the default heap needs to allocate more memory than is available in its current reserved address space. For these cases the heap can either fail the call that requests the memory, or reserve an additional address range elsewhere in the process. The default heap manager opts for the second choice.

When the default heap needs more memory than is currently available, it reserves another 1-MB address range in the process. It also initially commits as much memory as it needs from this reserved address range to satisfy the allocation request. The default heap manager is then responsible for managing this new memory region as well as the original heap space. If necessary, it will repeat this throughout the application until the process runs out of memory and address space. You could end up with a default heap that manifests itself in your process in a manner similar to the heap represented in Figure 2.
![ms810603.heapmm_2(en-us,MSDN.10).gif](https://chatgpt.com/c/images/ms810603.heapmm_2(en-us,msdn.10).gif) 

**Figure 2. The default heap for each process can expand into free address regions within the process.** 
So the default heap is not really a static heap at all. In fact, it may seem like a waste of energy to bother with managing the size of the initial heap since the heap always behaves in the same way after initialization. Managing the size of the default heap offers one advantage, though. It takes time to locate and reserve a new range of addresses in a process; you can save time by simply reserving a large enough address range initially. If you expect your application to require more heap space than the 1-MB default, reserve more address space initially to avoid allocating another region of addresses in your process later. Remember, each application has 2 gigabytes (GB) of address space to work with, and requires very little physical memory to support it.

## Global and Local Memory Functions 

At first glance it appears that the local and global memory management functions exist in Windows purely for backward compatibility with Windows version 3.1. This may be true, but the functions are managed as efficiently as the new heap functions discussed below. In fact, porting an application from 16-bit Windows does not necessarily include migrating from global and local memory functions to heap memory functions. The global and local functions offer the same basic capabilities (and then some) and are just as fast to work with. If anything, they are probably more convenient to work with because you do not have to keep track of a heap handle.
Nonetheless, the implementation of these functions is not the same as it was for 16-bit Windows. 16-bit Windows had a global heap, and each application had a local heap. Those two heap managers implemented the global and local functions. Allocating memory via **GlobalAlloc**  meant retrieving a chunk of memory from the global heap, while **LocalAlloc**  allocated memory from the local heap. Windows now has a single heap for both types of functions—the default heap described above.Now you're probably wondering if there is any difference between the local and global functions themselves. Well, the answer is no, they are now the same. In fact, they are interchangeable. Memory allocated via a call to **LocalAlloc**  can be reallocated with **GlobalReAlloc**  and then locked by **LocalLock** . The following table lists the global and local functions now available.
### Table 2 
| Global memory functions | Local memory functions | 
| --- | --- | 
| GlobalAlloc | LocalAlloc | 
| GlobalDiscard | LocalDiscard | 
| GlobalFlags | LocalFlags | 
| GlobalFree | LocalFree | 
| GlobalHandle | LocalHandle | 
| GlobalLock | LocalLock | 
| GlobalReAlloc | LocalReAlloc | 
| GlobalSize | LocalSize | 
| GlobalUnlock | LocalUnlock | 

It seems redundant to have two sets of functions that perform exactly the same, but that's where the backward compatibility comes in. Whether you used the global or local functions in a 16-bit Windows application before doesn't matter now—they are equally efficient.

### Types of Global and Local Memory 
In the Windows API, the global and local memory management functions provide two types of memory, MOVEABLE and FIXED. MOVEABLE memory can be further qualified as DISCARDABLE memory. When you allocate memory with either **GlobalAlloc**  or **LocalAlloc** , you designate the type of memory you want by supplying the appropriate memory flag. The following table lists and describes each memory flag for global and local memory.
### Table 3 
| Global memory flag | Local memory flag | Allocation meaning | 
| --- | --- | --- | 
| GMEM_FIXED | LMEM_FIXED | Allocate fixed memory. | 
| GMEM_MOVEABLE | LMEM_MOVEABLE | Allocate movable memory. | 
| GMEM_DISCARDABLE | LMEM_DISCARDABLE | Allocate discardable, movable memory. | 
| GMEM_ZEROINIT | LMEM_ZEROINIT | Initialize memory to zeros during allocation. | 
| GMEM_NODISCARD | LMEM_NODISCARD | Do not discard other memory to meet the needs of this allocation; instead, fail this request. | 
| GMEM_NOCOMPACT | LMEM_NOCOMPACT | Do not discard or move other memory to meet the needs of this allocation; instead, fail this request. | 
| GMEM_SHARE, GMEM_DDESHARE | N/A | Allocate global memory that is more efficient to use with DDE. | 

It is surprising that the distinction between FIXED and MOVEABLE memory still exists in these functions. In 16-bit Windows, MOVEABLE memory compacted the local and global heaps to reduce fragmentation and make more memory available to all applications. Yet the Windows NT virtual memory system does not rely on these techniques for efficient memory management and has little to gain by applications using them. In any case, they still exist and could actually be used in some circumstances.
When allocating FIXED memory in Windows, the **GlobalAlloc**  and **LocalAlloc**  functions return a 32-bit pointer to the memory block rather than a handle as they do for MOVEABLE memory. The pointer can directly access the memory without having to lock it first. This pointer can also be passed to the **GlobalFree**  and **LocalFree**  functions to release the memory without having to first retrieve the handle by calling the **GlobalHandle**  function. With FIXED memory, allocating and freeing memory is similar to using the C run-time functions **_malloc**  and **_free** .MOVEABLE memory, on the other hand, cannot provide this luxury. Because MOVEABLE memory can be moved (and DISCARDABLE memory can be discarded), the heap manager needs a handle to identify the chunk of memory to move or discard. To access the memory, the handle must first be locked by calling either **GlobalLock**  or **LocalLock** . As in 16-bit Windows, the memory cannot be moved or discarded while the handle is locked.
### The MOVEABLE Memory Handle Table 

As it turns out, each handle to MOVEABLE memory is actually a pointer into the MOVEABLE memory handle table. The handle table exists outside the heap, elsewhere in the process's address space. To learn more about this behavior, we created a test application that allocates several MOVEABLE memory blocks from the default heap. The handle table was created only upon allocation of the first MOVEABLE chunk of memory. This is nice, because if you never allocate any MOVEABLE memory, the table is never created and does not waste memory. ProcessWalker reveals that when this handle table is created, 1 page of memory is committed for the initial table and 512K of address space is reserved (see Figure 3).
![ms810603.heapmm_3(en-us,MSDN.10).gif](https://chatgpt.com/c/images/ms810603.heapmm_3(en-us,msdn.10).gif) 

**Figure 3. ProcessWalker highlights changes in the address space of a process. The heap memory handle table is shown as it looks immediately after it is created.** 
If you work out the math you can see that the number of memory handles available for MOVEABLE memory is limited. 512K bytes / 8 bytes per handle = 65,535 handles. In fact, the system imposes this limitation on each process. Fortunately, this only applies to MOVEABLE memory. You can allocate as many chunks of FIXED memory as you like, provided the memory and address space are available in your process.

Each handle requires 8 bytes of committed memory in the handle table to represent information, including the virtual address of the memory, the lock count on the handle, and the type of memory. Figure 4 shows how the handle table looks when viewed in ProcessWalker.
![ms810603.heapmm_4(en-us,MSDN.10).gif](https://chatgpt.com/c/images/ms810603.heapmm_4(en-us,msdn.10).gif) 

**Figure 4. Each MOVEABLE memory handle is 8 bytes and represents the location of the chunk of memory.** 
> **Note**  In the ProcessWalker view window, each line is 16 bytes (two memory handles). The far-left column represents the address of each line within the process. The addresses in white indicate the lines in which data changed since the last refresh. Red text shows exactly which bytes changed. This feature allows you to easily track changes in memory in response to certain events within the child process. A very useful debugging tool, to say the least.
The first 8 bytes in the view window—at address 0x000f0000—show the first handle allocated in the table. The handle value for this example would actually be 0x000f0004, which is a 4-byte offset into the 8-byte handle table entry. At the 4-byte offset in the table entry is the current 32-bit address representing the location of the chunk of memory. In this example, the 32-bit address is 0x00042A70, reading 4 bytes from right to left starting at 0x000f0008 and ending at 0x000f0004. If the memory is moved to a new location, this address changes to reflect the new location.
If you back up 4 bytes from the handle to the first byte in this handle table entry, you'll find the lock count for the handle. Remember, a block of memory can be moved or discarded only if its handle's lock count is zero. Since there is only 1 byte to record the lock count, it stands to reason that a handle can be locked only 256 (0xFF) times. Unfortunately, the system currently does not warn you when you reach that limit. If you lock a handle a 257th time, you receive a valid pointer to the memory, but the lock count remains at 256. It is possible, then, that you could unlock the handle 256 times and expect the memory to be locked. Yet the lock count is decremented to 0, and the memory could be moved or discarded. So what happens if you try to access the pointer you believe to be valid? Well, it depends on what is now at the address where you believe the memory to be. The memory could still be there, or some other memory could have been moved there. This is not the desired behavior, and we hope the system will be fixed to prevent this from happening. Incidentally, how should the system be fixed? The easiest thing to do would be to fail the call to **GlobalLock**  or **LocalLock**  on any attempt beyond 256, so check the return value to make sure the function succeeds.
The third and fourth bytes of the handle represent the memory type, that is, MOVEABLE, DDESHARE, or DISCARDABLE. Presumably because of compatibility with 16-bit Windows, local and global memory flags that have the same name and meaning do not have the same value. (The WINBASE.H header file defines each flag.) Yet once the memory is allocated, the handle table entry records no difference. Whether you use LMEM_DISCARDABLE or GMEM_DISCARDABLE does not matter—the handle table identifies all DISCARDABLE memory the same way. A little exploring in ProcessWalker shows the following type value identifiers.

### Table 4 
| Memory type | Byte 3 | Byte 4 | 
| --- | --- | --- | 
| MOVEABLE | 02 | – | 
| DISCARDABLE | 06 | – | 
| DDESHARE | – | 08 | 

Keep in mind that these values as represented in the handle table are not documented, so they could change with a new release of Windows NT. But it would be easy to use ProcessWalker to view the handle table to see the changes.

Returning to the test application example.... After allocating the first MOVEABLE memory block and thereby creating the handle table, we used the test application to allocate 15 more handles from the table. A quick view of the memory window showed the first eight lines had data associated with them, while the rest of the committed page was filled with zeros. Then we allocated one more handle, making a total of 17 handles. The view window was refreshed to indicate what changes occurred in the table as a result of allocating the seventeenth handle only. Figure 4 (above) shows the results.

As you can see, more than 8 bytes changed during the last allocation. In fact, 8 lines were updated for a total of 128 bytes. The first 8 bytes represent the seventeenth handle entry information as expected. The following 120 bytes indicate that the heap manager initializes the handle table every sixteenth handle. Examining this initialization data shows that the next 15 available handle table entries are identified in the table. When allocating the eighteenth handle, the location of the nineteenth handle is identified by the address location portion of the eighteenth handle table entry. As expected, then, if a handle is removed from the table (the memory is freed), the address location in that entry is replaced with the location of the next available handle after it. This behavior indicates that the heap manager keeps the location of the next available handle table entry in a static variable and uses that entry itself to store the location of the subsequent entry. Notice also that the last initialized entry has a null location for the next address. The heap manager uses this as an indicator to initialize another 16 handle table entries during the next handle allocation.

Another efficiency in the heap manager is its ability to commit pages of memory for the handle table as it needs them, not all 128 pages (512K) at once. Since the heap manager initializes its handle table in 16-handle (128-byte) increments, it is easy to determine when to commit a new page of memory. Every thirty-second (4096 / 128 = 32) initialization requires a new page of committed memory. Also, the entries do not straddle page boundaries, so their management is easier and potentially more efficient.

### CRT Library 

Managing memory in 16-bit Windows involved a great deal of uncertainty about using the C run-time (CRT) library. Now, there should be little hesitation. The current CRT library is implemented in a manner similar to FIXED memory allocated via the local and global memory management functions. The CRT library is also implemented using the same default heap manager as the global and local memory management functions.
Subsequent memory allocations via **malloc** , **GlobalAlloc** , and **LocalAlloc**  return pointers to memory allocated from the same heap. The heap manager does not divide its space among the CRT and global/local memory functions, and it does not maintain separate heaps for these functions. Instead, it treats them the same, promoting consistent behavior across the types of functions. As a result, you can now write code using the functions you're most comfortable with. And, if you're interested in portability, you can safely use the CRT functions exclusively for managing heap memory.
## Heap Memory API 
As mentioned earlier, you can create as many dynamic heaps as you like by simply calling **HeapCreate** . You must specify the maximum size of the heap so that the function knows how much address space to reserve. You can also indicate how much memory to commit initially. In the following example, a heap is created in your process that reserves 1 MB of address space and initially commits two pages of memory:

```plaintext
hHeap = HeapCreate (0, 0x2000, 0x100000);
```
Since you can have many dynamic heaps in your process, you need a handle to identify each heap when you access it. The **HeapCreate**  function returns this handle. Each heap you create returns a unique handle so that several dynamic heaps may coexist in your process. Having to identify your heap by handle also makes managing dynamic heaps more difficult than managing the default heap, since you have to keep each heap handle around for the life of the heap.If you're bothered by having to keep this handle around, there is an alternative. You can use the heap memory functions on the default heap instead of creating a dynamic heap explicitly for them. To do this, simply use the **GetProcessHeap**  function to get the handle of the default heap. For simple allocations of short-term memory, the following example taken from the ProcessWalker sample application illustrates how easy this is to do:

```plaintext
char    *szCaption;
int     nCaption = GetWindowTextLength (hWnd);

/* retrieve view memory range */
szCaption = HeapAlloc (GetProcessHeap (), 
                       HEAP_ZERO_MEMORY, 
                       nCaption+1);
GetWindowText (hViewWnd, szCaption, nCaption);
```

In this example the default heap is chosen because the allocation is independent of other memory management needs, and there is no reason to create a dynamic heap just for this one allocation. Note that you could achieve the same result by using the global, local, or CRT functions since they allocate only from the default heap.
As shown earlier, the first parameter to **HeapCreate**  allows you to specify an optional HEAP_NO_SERIALIZE flag. A serialized heap does not allow two threads to access it simultaneously. The default behavior is to serialize access to the heap. If you plan to use a heap strictly within one thread, specifying the HEAP_NO_SERIALIZE flag improves overall heap performance slightly.Like all of the heap memory functions, **HeapAlloc**  requires a heap handle as its first argument. The example uses the **GetProcessHeap**  function instead of a dynamic heap handle. The second parameter to **HeapAlloc**  is an optional flag that indicates whether the memory should be zeroed first and whether to generate exceptions on error. To get zeroed memory, specify the HEAP_ZERO_MEMORY flag as shown above. The generate exceptions flag (HEAP_GENERATE_EXCEPTIONS) is a useful feature if you have exception handling built into your application. When using this flag, the function raises an exception on failure rather than just returning NULL. Depending on your use, exception handling can be an effective way of triggering special events—such as low memory situations—in your application.**HeapAlloc**  has a cousin called **HeapReAlloc**  that works in much the same way as the standard global and local memory management functions described earlier. Use **HeapReAlloc**  primarily to resize a previous allocation. This function has four parameters, three of which are the same as for **HeapAlloc** . The new parameter, *lpMem*, is a pointer to the chunk of memory being resized.It is important to note that although heap memory is not movable as in global and local memory, it may be moved during the **HeapReAlloc**  function. This function returns a pointer to the resized chunk of memory, which may or may not be at the same location as initially indicated by the pointer passed to the function. This is the only time memory can be moved in dynamic heaps, and the only chunk of memory affected is the one identified by *lpMem* in the function. You can also override this behavior by specifying the HEAP_REALLOC_IN_PLACE_ONLY flag. With this flag, if there is not enough room to reallocate the memory in place, the function returns with failure status rather than move the memory.Memory allocated with **HeapAlloc**  or reallocated with **HeapReAlloc**  can be freed by calling **HeapFree** . This function is easy to use: simply indicate the heap handle and a pointer to the chunk of memory to free. Completing the example above, here is how you can use **HeapFree**  with the default heap:

```plaintext
/* free default heap memory */
HeapFree (GetProcessHeap (), szCaption);
```

This example shows how easy it can be to work with heaps in Windows. However, you may still want to create a dynamic heap specifically to manage complex dynamic data structures in your application. In fact, one nice benefit of heap memory is how well it caters to the needs of traditional data structures such as binary trees, linked lists, and dynamic arrays. Having the heap handle provides a way of uniquely identifying these structures independently. One example that comes to mind is when you're building a multiwindow application—perhaps a multiple document interface (MDI) application. Simply create and store a heap handle in the window extra bytes or window property list for each window during the WM_CREATE message. Then it is easy to write a window procedure that manages data structures from its own heap by retrieving the heap handle when necessary. When the window goes away, simply have it destroy the heap in the WM_DESTROY message.
You can easily destroy dynamic heaps by calling **HeapDestroy**  on a specific heap handle. This powerful function will remove a heap regardless of its state. The **HeapDestroy**  function doesn't care whether you have outstanding allocations in the heap or not.
To make heap memory management most efficient, you would only create a heap of the size you need. In some cases it is easy to determine the heap size you need—if you're allocating a buffer to read a file into, simply check the size of the file. In other cases, heap size is more difficult to figure—if you're creating a dynamic data structure that grows according to user interaction, it is difficult to predict what the user will do. Dynamic heaps have a provision for this latter circumstance. By specifying a maximum heap size of zero, you make the heap assume a behavior like the default heap. That is, it will grow and spread in your process as much as necessary, limited only by available memory. In this case, available memory means available address space in your process and available pagefile space on your hard disk.

## Overhead on Heap Memory Allocations 

With all types of heap memory, an overhead is associated with each memory allocation. This overhead is due to:

- Granularity on memory allocations within the heap.

- The overhead necessary to manage each memory segment within the heap.

The granularity of heap allocations in 32-bit Windows is 16 bytes. So if you request a global memory allocation of 1 byte, the heap returns a pointer to a chunk of memory, guaranteeing that the 1 byte is available. Chances are, 16 bytes will actually be available because the heap cannot allocate less than 16 bytes at a time.

### Global and Local Memory Functions 
For global and local memory functions, the documentation suggests that you use the **GlobalSize**  and **LocalSize**  functions to determine the exact size of the allocation, but in my tests this function consistently returned the size I requested and not the size actually allocated.To confirm this finding, turn to ProcessWalker again and view the committed memory in your default heap. For the sake of observation, perform consecutive allocations of 1, 2, 3, 14, 15, and 16 bytes using either **GlobalAlloc**  or **LocalAlloc** . In this particular example, we used **GlobalAlloc**  with the GMEM_MOVEABLE flag, but the result is the same for memory allocated as GMEM_FIXED. Then, refresh your view of the committed memory in the heap. Finally, scroll the view window so that the addresses of the allocated blocks of memory are all in view. You should see something similar to the window in Figure 5.![ms810603.heapmm_5(en-us,MSDN.10).gif](https://chatgpt.com/c/images/ms810603.heapmm_5(en-us,msdn.10).gif) 

Figure 5. A ProcessWalker view of the default heap after making consecutive allocations of 1, 2, 3, 14, 15, and 16 bytes using the *GlobalAlloc* function.** In Figure 5, the first line represents the header for the 1-byte allocation, followed immediately by the minimum 16 bytes allocated for the 1-byte request. Just to add visual clarity, the letter *m* appears in each allocated byte beginning at the address of the allocation. The *m*'s are visible in the ASCII representation of memory to the right of each line. At the end of all heap allocations is a heap tail, as indicated by the last line of new information in Figure 5.So, although you request only 1 byte and **GlobalSize**  returns a size of 1 byte, there are actually 16 bytes allocated and available. Similarly, for the 3-byte allocation, 13 additional bytes are available. Even more interesting is the apparent waste of memory for allocations of 14, 15, and 16 bytes. In these allocations an additional 16 bytes were allocated for no reason. These are the lines immediately following the lines with 14, 15, and 16 *m* characters. Presumably you could also use these extra 16 bytes, but again **GlobalSize**  does not indicate their existence.
So what is the cost of allocating from a heap? Well, it depends on the size of the allocation. Every 1-byte allocation uses a total of 32 bytes, and a 16-byte allocation uses a total of 48 bytes. This is a considerable amount of overhead on smaller allocations. Therefore, it would not be a good idea to accumulate a number of small heap allocations because they would cost a great deal in actual memory used. On the other hand, there is nothing wrong with allocating a large chunk of memory from the heap and dividing it into smaller pieces.

### Heap Memory Functions 
Similar to the global and local memory functions, the heap memory functions have a minimum 16-byte granularity and the same overhead on memory allocations. Figure 6 presents a ProcessWalker view of a dynamic heap using the same allocations of 1, 2, 3, 14, 15, and 16 bytes, but this time using the **HeapAlloc**  function.![ms810603.heapmm_6(en-us,MSDN.10).gif](https://chatgpt.com/c/images/ms810603.heapmm_6(en-us,msdn.10).gif) 

Figure 6. A ProcessWalker view of a dynamic heap after making consecutive allocations of 1, 2, 3, 14, 15, and 16 bytes using the *HeapAlloc* function.** For this example, the letter *h* appears in the allocated memory for comparison with the global memory allocations shown in Figure 5. A comparison of Figures 5 and 6 shows that the two heaps behave in an identical manner for the test allocations. Also, as in the global and local memory functions, a **HeapSize**  function determines the exact amount of memory allocated for a given request. Unfortunately, this function seems to be implemented exactly like the **GlobalSize**  and **LocalSize**  functions. In my tests, **HeapSize**  always returned the amount of the allocation request, while actually allocating with the same 16-byte granularity.
### C Run-Time Memory Functions 
Can you guess how the C run-time library memory functions will behave on this same test? Yes, the C run-time functions exhibit the same heap memory behavior. Figure 7 represents the same allocations using the **malloc**  function.![ms810603.heapmm_7(en-us,MSDN.10).gif](https://chatgpt.com/c/images/ms810603.heapmm_7(en-us,msdn.10).gif) 

Figure 7. A ProcessWalker view of the default heap after making consecutive allocations of 1, 2, 3, 14, 15, and 16 bytes using the C run-time *malloc* function.** Unlike the global/local and heap memory functions, the C run-time library does not provide a means for retrieving the exact number of bytes allocated. Then again, how useful is that information anyway, since the **GlobalSize** , **LocalSize** , and **HeapSize**  functions fail to perform accurately?
## Summary and Recommendations 

Heap memory management in Windows is greatly improved over 16-bit Windows. Instead of a systemwide global heap and application-specific local heaps, each application has a default heap and as many dynamic heaps as the application wants to create. Both types of heaps can grow dynamically and use as much of the address space as they need to satisfy an allocation request.
The default heap provides all dynamic memory allocations for the C run-time library **malloc**  functions as well as the global and local memory functions. The heap memory functions can also allocate from the default heap by using its handle, which they retrieve by calling the **GetProcessHeap**  function.The dynamic heap provides serialization to avoid conflict among multiple threads accessing the same heap. To support the management of multiple dynamic heaps, each heap is identified by a unique handle returned by the **HeapCreate**  function.Heaps do at least one thing well—they allocate smaller chunks of memory rather quickly. So whenever you are reluctant to create an automatic variable in a window procedure simply for an occasional **LoadString**  buffer, why not use **GlobalAlloc**  or **LocalAlloc** , **malloc**  or **HeapAlloc** ? Heaps are also very good at allocating storage for dynamic data structures. Dynamic heaps lend themselves particularly well to managing several distinct dynamic data structures in an application.
Finally, what is the cost of using a heap? Well, if you never use any MOVEABLE (including DISCARDABLE) memory, the cost is considerably lower, and MOVEABLE memory probably doesn't buy you much in a 32-bit linear address space. Not to mention that at 8 bytes per MOVEABLE memory handle, the system limits processes to 65,535 handles. Each chunk of heap memory allocated in either the default heap or a dynamic heap is subject to a 16-byte granularity and is charged a 16-byte header. In total, then, allocating 1 byte of MOVEABLE memory costs 40 bytes (8 bytes for the handle table entry, 16 bytes for granularity, and 16 bytes for the header). Happy heaping.

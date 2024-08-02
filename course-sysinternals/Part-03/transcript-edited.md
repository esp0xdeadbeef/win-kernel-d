# Introduction

In this presentation, we're going to look at process creation in a little bit more depth.

We're going to discuss the functions of the Application Program Interface (API) which we can use to create a process. Here are some of the functions used to create a process in the Windows operating system:

- `CreateProcess` (Kernel32.dll) — This is the most frequently used API.
- `CreateProcessAsUser` (Advapi32.dll) — We probably won't be discussing this in this presentation.
- `ZwCreateUserProcess` (ntdll.dll)  — An undocumented function, but that is how you create a user mode process from the console. There are a couple of other undocumented APIs to create a process.
- ... and more

## Prototype definitions

### Kernel32.dll:CreateProcess

[Source ms](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessa)

```c
BOOL CreateProcessA(
  [in, optional]      LPCSTR                lpApplicationName,
  [in, out, optional] LPSTR                 lpCommandLine,
  [in, optional]      LPSECURITY_ATTRIBUTES lpProcessAttributes,
  [in, optional]      LPSECURITY_ATTRIBUTES lpThreadAttributes,
  [in]                BOOL                  bInheritHandles,
  [in]                DWORD                 dwCreationFlags,
  [in, optional]      LPVOID                lpEnvironment,
  [in, optional]      LPCSTR                lpCurrentDirectory,
  [in]                LPSTARTUPINFOA        lpStartupInfo,
  [out]               LPPROCESS_INFORMATION lpProcessInformation
);
```

### Advapi32.dll:CreateProcessAsUser


[Source ms](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessasusera)

```c
BOOL CreateProcessAsUserA(
  [in, optional]      HANDLE                hToken,
  [in, optional]      LPCSTR                lpApplicationName,
  [in, out, optional] LPSTR                 lpCommandLine,
  [in, optional]      LPSECURITY_ATTRIBUTES lpProcessAttributes,
  [in, optional]      LPSECURITY_ATTRIBUTES lpThreadAttributes,
  [in]                BOOL                  bInheritHandles,
  [in]                DWORD                 dwCreationFlags,
  [in, optional]      LPVOID                lpEnvironment,
  [in, optional]      LPCSTR                lpCurrentDirectory,
  [in]                LPSTARTUPINFOA        lpStartupInfo,
  [out]               LPPROCESS_INFORMATION lpProcessInformation
);
```

### ntdll.dll:ZwCreateUserProcess

[source reactos](https://processhacker.sourceforge.io/doc/ntzwapi_8h.html)

```c
NTSYSCALLAPI NTSTATUS NTAPI ZwCreateUserProcess	(	_Out_ PHANDLE 	ProcessHandle,
_Out_ PHANDLE 	ThreadHandle,
_In_ ACCESS_MASK 	ProcessDesiredAccess,
_In_ ACCESS_MASK 	ThreadDesiredAccess,
_In_opt_ POBJECT_ATTRIBUTES 	ProcessObjectAttributes,
_In_opt_ POBJECT_ATTRIBUTES 	ThreadObjectAttributes,
_In_ ULONG 	ProcessFlags,
_In_ ULONG 	ThreadFlags,
_In_opt_ PVOID 	ProcessParameters,
_Inout_ PPS_CREATE_INFO 	CreateInfo,
_In_opt_ PPS_ATTRIBUTE_LIST 	AttributeList 
)	
```



## Parameters

One of the most important parameters we have to pass into functions which we have discussed is the name of the `.exe` file. A process needs to have an `.exe` to start. The name of the `.exe` is the most important parameter which we should pass into the CreateProcess APIs. There are a lot of other parameters, but we will only focus on this particular parameter in this presentation.

## Demo

Let's go straight into a demo and see a couple of things:

### Starting a Process

These are the processes which are running in the system at the moment, as we have seen before in the previous presentation. In this particular presentation, I'm going to start a process from Explorer. Before that, let's look at the Explorer process, which is the shell itself. For example, the Start menu is owned by Explorer, as is the taskbar. For example, if I drag and drop it here, it will point to Explorer.

I'm going to start Notepad from Explorer. This is the default location for Notepad: `C:\Windows\notepad.exe`. I'm going to double-click on this particular icon, and a Notepad process starts. Now, if I want, I can kill this Notepad process from the Task Manager.

To dig a little deeper into what is happening when we double-click on that Notepad icon, I'm going to attach a WinDbg debugger to the process (`explorer.exe`). Only one Explorer instance is running.

I have a 64-bit operating system, so my Explorer is 64-bit, and I have used a 64-bit debugger for this.

We have discussed all the steps which I am doing in the presentation series. If you're not familiar with how to use WinDbg, please refer to that series.

What I have done is I have attached every WinDbg instance to my Explorer. For example, now I cannot click my Start menu; nothing will work because my shell is broken into the debugger.

I'm going to put a breakpoint as soon as possible. The breakpoint I am going to put is `BP kernel32!CreateProcessW`. This is the export library (DLL) that exports this particular function. Now, I'm going to let Explorer go by pressing `G`, so now Explorer is not hanging. I can click the Start menu, for example.

Now, I'm going to do the exact same step which I have done before—double-clicking on the Notepad icon.

Everything is hung. I go back to my WinDbg to see what is happening. I have to use Task Manager for that. I press `Ctrl+Shift+Escape`, and I'm going to bring the WinDbg window to the front because I cannot click on the taskbar because its icons are not active at the moment.

I have broken into the CreateProcess function, so the process which I am debugging is Explorer itself. Let's have a quick look at the call stack.

This is the call stack. This is our look. This is one of the most important DLLs as far as the shell is concerned. I'm not going to go into the details of that. It is trying to create a process, so how do we confirm that this is the Notepad which is being created?

The first parameter to a CreateProcess API is the name of the `.exe`, which we have mentioned before. I'm going to execute the command `R` to see the registers. In a 64-bit [calling convention](https://learn.microsoft.com/en-us/cpp/build/x64-calling-convention?view=msvc-170), the first parameter is always passed in the `RCX` register.

So, I'm going to execute `DU` on that pointer. I got `C:\Windows\notepad.exe`, so this was the `.exe` I was trying to start. All these commands which I am trying to execute here are discussed in the WinDbg presentation series. So, if you're not familiar, once again, please refer to that.

I'm going to press `G`.

Now, we have just seen how to start a process from Explorer. Now, I have a small program up here which calls `CreateProcess` API from the program itself. So, I'm going to start Notepad again from my own program. This is a small, more or less "Hello World" application which just creates a process and calls the `CreateProcess` API.

Just a small walkthrough first, it's a main of the application, and I have included this particular header file called `Windows.h`. So, that is the header file in which I have the declaration for `CreateProcess`.

I have initialized a couple of structures here which `CreateProcess` needs right here. As I don't want to do any customization (because this API is very powerful and can do a lot of customization), I am just initializing all those parameters to empty. If you want more details on these parameters, they take a lot of parameters, you can check MSDN for the documentation of the `CreateProcess` API.

In this case, I'm going for the simplest scenario in which I am just passing the `.exe` name, as I mentioned, and the rest of the parameters are more or less null. And this is, as you can see, it's zero memory structures right here.

So, my breakpoint hit. The Notepad is yet to start because I am yet to execute the `CreateProcess` API. Before that, I would like to go to the Process Explorer. As you can see, in the Process Explorer, DevWeek (which is Visual Studio itself) has started my application, which is "Create a Process GCC". You can see the name of the application here.

Inspecting in Notepad as the child of this, after executing the `CreateProcess`. So let's do that.

I'm going to press `F10`. A Notepad got started, as you can see here, and I'm going to close this Explorer, and you can see in Notepad it started.

## Summary

Coming back to the summary and to the presentation, we have seen process creation, and we have seen a process creation API from user mode. That's about the presentation.

Now, reviews, comments, and suggestions: I would like to take them from one single location, so if you don't mind, I would like to follow this particular pattern for the reviews and comments.

So, that's it. Thank you for watching, see you next time!

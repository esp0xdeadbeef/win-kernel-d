## How to Debug `explorer.exe` on Windows 11?

This guide will help you debug `explorer.exe` on Windows 11, particularly focusing on setting breakpoints for `kernel!CreateProcessW`. Note that the approach for setting breakpoints on `CreateProcessW` has changed in Windows 11 since Windows 8.1.

## Steps to Kill and Relaunch `explorer.exe` 
1. First, open WinDbg.
 
2. Open an administrator Command Prompt and type the following command to kill `explorer.exe`:

```powershell
taskkill -f -im explorer.exe
```
 
3. After killing `explorer.exe`, you need to launch it from within the debugger. Attaching the debugger to an already running instance of `explorer.exe` will not work, as `explorer.exe` checks for an existing instance and terminates itself if found.
 
4. After the debugging session, detach the debugger. If you've killed `explorer.exe`, restore the Windows environment by doing the following: 
 * Press `Ctrl + Shift + Esc` to open Task Manager.
 * Click on "Run new task".
 * Type `explorer.exe` and hit Enter or click OK.


By following these steps, you can effectively kill, debug, and relaunch `explorer.exe` on Windows 11.


## Debugging `CreateProcessW`

To debug the `CreateProcessW` function: 

1. After killing `explorer.exe` (untill step 3 of last heading) using Task Manager or Command Prompt as described above, run a new instance of `explorer.exe` from within the debugger.
 
2. In the debugger, use the following command to list the stub functions for `CreateProcessW`:

```powershell
x kernel32!CreateProcess*
```
 
3. You will see stub functions like `KERNEL32!CreateProcessWStub`. Set breakpoints on these stub functions. For example:

```powershell
bp KERNEL32!CreateProcessWStub
```
By following these steps, you should be able to effectively debug the `CreateProcessW` function in `explorer.exe` on Windows 11.
Feel free to adapt this guide as needed for your specific debugging environment and requirements.
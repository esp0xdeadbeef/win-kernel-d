#include <iostream>
#include <Windows.h>
#include <stdio.h>
#include <tchar.h>

int _tmain(int argc, TCHAR* argv[]) {
    STARTUPINFO si;
    PROCESS_INFORMATION pi;
    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si);
    ZeroMemory(&pi, sizeof(pi));
    // Define command_line as a mutable array if modification is expected, otherwise as a const pointer
    TCHAR command_line[] = _T("C:\\Windows\\notepad.exe");  // Use array if modification is needed

    if (!CreateProcess(
        NULL,                    // Application name
        command_line,            // Command line (mutable if command_line is an array)
        NULL,                    // Process security attributes
        NULL,                    // Thread security attributes
        FALSE,                   // Handle inheritance option
        0,                       // Creation flags
        NULL,                    // Environment
        NULL,                    // Current directory
        &si,                     // Pointer to STARTUPINFO
        &pi                      // Pointer to PROCESS_INFORMATION
    )) {
        _tprintf(_T("CreateProcess failed (%d).\n"), GetLastError());
        return 1;
    }

    STARTUPINFOA si2;
    PROCESS_INFORMATION pi2;
    ZeroMemory(&si2, sizeof(si2));
    si2.cb = sizeof(si2);
    ZeroMemory(&pi2, sizeof(pi2));
    char* szCmdline = _strdup("C:\\Windows\\notepad.exe");
    printf("Duplicated string: %s\n", szCmdline);


    // From https://doxygen.reactos.org/d9/dd7/dll_2win32_2kernel32_2client_2proc_8c_source.html#L594   
    //  /*
    //  * FUNCTION: The CreateProcess function creates a new process and its
    //  * primary thread. The new process executes the specified executable file
    //  * ARGUMENTS:
    //  *
    //  *     lpApplicationName = Pointer to name of executable module
    //  *     lpCommandLine = Pointer to command line string
    //  *     lpProcessAttributes = Process security attributes
    //  *     lpThreadAttributes = Thread security attributes
    //  *     bInheritHandles = Handle inheritance flag
    //  *     dwCreationFlags = Creation flags
    //  *     lpEnvironment = Pointer to new environment block
    //  *     lpCurrentDirectory = Pointer to current directory name
    //  *     lpStartupInfo = Pointer to startup info
    //  *     lpProcessInformation = Pointer to process information
    //  *
    //  * @implemented
    //  */
    // BOOL
    // WINAPI
    // DECLSPEC_HOTPATCH
    // CreateProcessA(LPCSTR lpApplicationName,
    //                LPSTR lpCommandLine,
    //                LPSECURITY_ATTRIBUTES lpProcessAttributes,
    //                LPSECURITY_ATTRIBUTES lpThreadAttributes,
    //                BOOL bInheritHandles,
    //                DWORD dwCreationFlags,
    //                LPVOID lpEnvironment,
    //                LPCSTR lpCurrentDirectory,
    //                LPSTARTUPINFOA lpStartupInfo,
    //                LPPROCESS_INFORMATION lpProcessInformation)
    // {
    //     /* Call the internal (but exported) version */
    //     return CreateProcessInternalA(NULL,
    //                                   lpApplicationName,
    //                                   lpCommandLine,
    //                                   lpProcessAttributes,
    //                                   lpThreadAttributes,
    //                                   bInheritHandles,
    //                                   dwCreationFlags,
    //                                   lpEnvironment,
    //                                   lpCurrentDirectory,
    //                                   lpStartupInfo,
    //                                   lpProcessInformation,
    //                                   NULL);
    // }
    

    if (!CreateProcessA(
        NULL,                    // Application name
        szCmdline,               // Command line
        NULL,                    // Process security attributes
        NULL,                    // Thread security attributes
        FALSE,                   // Handle inheritance option
        0,                       // Creation flags
        NULL,                    // Environment
        NULL,                    // Current directory
        &si2,                    // Pointer to STARTUPINFOA
        &pi2                     // Pointer to PROCESS_INFORMATION
    )) {
        printf("CreateProcessAsUserA failed (%d).\n", GetLastError());
        free(szCmdline); // Free strdup allocated memory
        return 1;
    }
    free(szCmdline); // Free strdup allocated memory
    std::cout << "Hello World!\n";

    WaitForSingleObject(pi.hProcess, INFINITE);

    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);

    WaitForSingleObject(pi2.hProcess, INFINITE);

    CloseHandle(pi2.hProcess);
    CloseHandle(pi2.hThread);

    return 0;
}

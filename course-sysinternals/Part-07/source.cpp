// Because fuck microsoft:
// we need to use __debugbreak() instead of `__asm int 3`
// tl.tr., i fucking hate ms.

#include <iostream>
#include <Windows.h>
#include <conio.h>

int main()
{
    __debugbreak();
    while (1)
    {
        LPTSTR test = GetCommandLine();
        printf("%s", test);
        _getch();
    }
    return 0;
}
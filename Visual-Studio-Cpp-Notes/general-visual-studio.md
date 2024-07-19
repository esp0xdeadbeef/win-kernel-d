
# Comments
## Comment out the selected code.

Ctrl + K + C :  

## Uncomment the selected code
Ctrl + K + U : 

## Toggle line comments (doesn't work for me??!)
Ctrl + / 



# _T() macro

https://stackoverflow.com/questions/63364995/c-tchar-units-szteststring-how-to-assign-a-string-value


## fails

You can't use the `_T()` macro to convert data at runtime. It only works on char/string literals at compile-time.

```cpp
string par = "1234.32.23";   
HKEY ProxyServerKey;
RegCreateKeyExW(HKEY_CURRENT_USER, L"Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings", 0, NULL, REG_OPTION_NON_VOLATILE, KEY_WRITE, NULL, &ProxyServerKey, NULL);
_TCHAR szTestString[] = _T(par);
RegSetValueExW(ProxyServerKey, L"ProxyServer", 0, REG_SZ, (BYTE*)szTestString, sizeof(szTestString));
RegCloseKey(ProxyServerKey);
SendNotifyMessageW(HWND_BROADCAST, WM_SETTINGCHANGE, 0, 0);
```

## Solution:

Instead of using the macro `_T()` use:
```cpp
(const BYTE*)objectname.c_str()
```

```cpp
wstring par = L"1234.32.23";   

HKEY ProxyServerKey;
if (RegCreateKeyExW(HKEY_CURRENT_USER, L"Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings", 0, NULL, REG_OPTION_NON_VOLATILE, KEY_WRITE, NULL, &ProxyServerKey, NULL) == ERROR_SUCCESS)
{
    RegSetValueExW(ProxyServerKey, L"ProxyServer", 0, REG_SZ, (const BYTE*)par.c_str(), (par.size()+1) * sizeof(wchar_t));
    RegCloseKey(ProxyServerKey);
    SendNotifyMessageW(HWND_BROADCAST, WM_SETTINGCHANGE, 0, 0);
}

```


# When should I use std::wstring over std::string?

If the programming platform or API function is a single-byte one, and we want to process or parse some Unicode data, e.g read from Windows'.REG file or network 2-byte stream, we should declare std::wstring variable to easily process them. e.g.: wstring ws=L"中国a"(6 octets memory: 0x4E2D 0x56FD 0x0061), we can use ws[0] to get character '中' and ws[1] to get character '国' and ws[2] to get character 'a', etc.


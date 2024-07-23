import pykd


functions = [
    {"alloca": ".printf \"void *_alloca(\n    size_t size = %x\n);\", poi(esp)"},  # Use malloc() or new(), which allocate memory on the heap.
    
    {"scanf": ".printf \"int scanf(\n    const char *format (%x)\n    [,\n    argument1 %x,\n    argument2 %x,\n    ...]\n);\\\n\", poi(esp + (0 * 4)), poi(esp + (1 * 4)), poi(esp + (2 * 4))"},  # Use fgets() or fscanf() instead of scanf() functions.
    {"wscanf": ".printf \"int wscanf(\n    const wchar_t *format (%x)\n    [,\n    argument1 %x,\n    argument2 %x,\n    ...]\n);\\\n\", poi(esp + (0 * 4)), poi(esp + (1 * 4)), poi(esp + (2 * 4))"},  # Use fgets() or fscanf() instead of scanf() functions.
    {"sscanf": ".printf \"int sscanf(\n    const char *str (%x),\n    const char *format (%x)\n    [,\n    argument1 %x,\n    argument2 %x,\n    ...]\n);\\\n\", poi(esp + (0 * 4)), poi(esp + (1 * 4)), poi(esp + (2 * 4)), poi(esp + (3 * 4))"},  # Use fgets() or fscanf() instead of scanf() functions.
    {"swscanf": ".printf \"int swscanf(\n    const wchar_t *str (%x),\n    const wchar_t *format (%x)\n    [,\n    argument1 %x,\n    argument2 %x,\n    ...]\n);\\\n\", poi(esp + (0 * 4)), poi(esp + (1 * 4)), poi(esp + (2 * 4)), poi(esp + (3 * 4))"},  # Use fgets() or fscanf() instead of scanf() functions.
    {"vscanf": ".printf \"int vscanf(\n    const char *format (%x),\n    va_list args (%x)\n);\\\n\", poi(esp + (0 * 4)), poi(esp + (1 * 4))"},  # Use fgets() or fscanf() instead of scanf() functions.
    {"vsscanf": ".printf \"int vsscanf(\n    const char *str (%x),\n    const char *format (%x),\n    va_list args (%x)\n);\\\n\", poi(esp + (0 * 4)), poi(esp + (1 * 4)), poi(esp + (2 * 4))"},  # Use fgets() or fscanf() instead of scanf() functions.

    {"strlen": ".printf \"size_t strlen(\n    const char *str (%x)\n);\\\n\", poi(esp + (0 * 4))"},  # Use strnlen_s() and wcsnlen_s() for safer string length calculations.
    {"wcslen": ".printf \"size_t wcslen(\n    const wchar_t *str (%x)\n);\\\n\", poi(esp + (0 * 4))"},  # Use strnlen_s() and wcsnlen_s() for safer string length calculations.

    {"strtok": ".printf \"char *strtok(\n    char *str (%x),\n    const char *delim (%x)\n);\\\n\", poi(esp + (0 * 4)), poi(esp + (1 * 4))"},  # Use strtok_s() for safer tokenizing.
    {"strtok_r": ".printf \"char *strtok_r(\n    char *str (%x),\n    const char *delim (%x),\n    char **saveptr (%x)\n);\\\n\", poi(esp + (0 * 4)), poi(esp + (1 * 4)), poi(esp + (2 * 4))"},  # Use strtok_s() for safer tokenizing.
    {"wcstok": ".printf \"wchar_t *wcstok(\n    wchar_t *str (%x),\n    const wchar_t *delim (%x),\n    wchar_t **saveptr (%x)\n);\\\n\", poi(esp + (0 * 4)), poi(esp + (1 * 4)), poi(esp + (2 * 4))"},  # Use strtok_s() for safer tokenizing.

    {"strcat": ".printf \"char *strcat(\n    char *dest (%x),\n    const char *src (%x)\n);\\\n\", poi(esp + (0 * 4)), poi(esp + (1 * 4))"},  # Use strcat_s(), strncat_s(), wcscat_s(), wcsncat_s().
    {"strncat": ".printf \"char *strncat(\n    char *dest (%x),\n    const char *src (%x),\n    size_t n = %x\n);\\\n\", poi(esp + (0 * 4)), poi(esp + (1 * 4)), poi(esp + (2 * 4))"},  # Use strcat_s(), strncat_s(), wcscat_s(), wcsncat_s().
    {"wcscat": ".printf \"wchar_t *wcscat(\n    wchar_t *dest (%x),\n    const wchar_t *src (%x)\n);\\\n\", poi(esp + (0 * 4)), poi(esp + (1 * 4))"},  # Use strcat_s(), strncat_s(), wcscat_s(), wcsncat_s().
    {"wcsncat": ".printf \"wchar_t *wcsncat(\n    wchar_t *dest (%x),\n    const wchar_t *src (%x),\n    size_t n = %x\n);\\\n\", poi(esp + (0 * 4)), poi(esp + (1 * 4)), poi(esp + (2 * 4))"},  # Use strcat_s(), strncat_s(), wcscat_s(), wcsncat_s().

    {"strcpy": ".printf \"char *strcpy(\n    char *dest (%x),\n    const char *src (%x)\n);\\\n\", poi(esp + (0 * 4)), poi(esp + (1 * 4))"},  # Use strcpy_s(), strncpy_s(), wcscpy_s(), wcsncpy_s().
    {"strncpy": ".printf \"char *strncpy(\n    char *dest (%x),\n    const char *src (%x),\n    size_t n = %x\n);\\\n\", poi(esp + (0 * 4)), poi(esp + (1 * 4)), poi(esp + (2 * 4))"},  # Use strcpy_s(), strncpy_s(), wcscpy_s(), wcsncpy_s().
    {"wcscpy": ".printf \"wchar_t *wcscpy(\n    wchar_t *dest (%x),\n    const wchar_t *src (%x)\n);\\\n\", poi(esp + (0 * 4)), poi(esp + (1 * 4))"},  # Use strcpy_s(), strncpy_s(), wcscpy_s(), wcsncpy_s().
    {"wcsncpy": ".printf \"wchar_t *wcsncpy(\n    wchar_t *dest (%x),\n    const wchar_t *src (%x),\n    size_t n = %x\n);\\\n\", poi(esp + (0 * 4)), poi(esp + (1 * 4)), poi(esp + (2 * 4))"},  # Use strcpy_s(), strncpy_s(), wcscpy_s(), wcsncpy_s().

    {"memcpy": ".printf \"void *memcpy(\n    void *dest (%x),\n    const void *src (%x),\n    size_t n = %x\n);\\\n\", poi(esp + (0 * 4)), poi(esp + (1 * 4)), poi(esp + (2 * 4))"},  # Use memcpy_s(), wmemcpy_s() for safer memory copying.
    {"wmemcpy": ".printf \"wchar_t *wmemcpy(\n    wchar_t *dest (%x),\n    const wchar_t *src (%x),\n    size_t n = %x\n);\\\n\", poi(esp + (0 * 4)), poi(esp + (1 * 4)), poi(esp + (2 * 4))"},  # Use memcpy_s(), wmemcpy_s() for safer memory copying.

    {"stpcpy": ".printf \"char *stpcpy(\n    char *dest (%x),\n    const char *src (%x)\n);\\\n\", poi(esp + (0 * 4)), poi(esp + (1 * 4))"},  # Use stpcpy_s(), stpncpy_s(), wcpcpy_s(), wcpncpy_s().
    {"stpncpy": ".printf \"char *stpncpy(\n    char *dest (%x),\n    const char *src (%x),\n    size_t n = %x\n);\\\n\", poi(esp + (0 * 4)), poi(esp + (1 * 4)), poi(esp + (2 * 4))"},  # Use stpcpy_s(), stpncpy_s(), wcpcpy_s(), wcpncpy_s().
    {"wcpcpy": ".printf \"wchar_t *wcpcpy(\n    wchar_t *dest (%x),\n    const wchar_t *src (%x)\n);\\\n\", poi(esp + (0 * 4)), poi(esp + (1 * 4))"},  # Use stpcpy_s(), stpncpy_s(), wcpcpy_s(), wcpncpy_s().
    {"wcpncpy": ".printf \"wchar_t *wcpncpy(\n    wchar_t *dest (%x),\n    const wchar_t *src (%x),\n    size_t n = %x\n);\\\n\", poi(esp + (0 * 4)), poi(esp + (1 * 4)), poi(esp + (2 * 4))"},  # Use stpcpy_s(), stpncpy_s(), wcpcpy_s(), wcpncpy_s().

    {"memmove": ".printf \"void *memmove(\n    void *dest (%x),\n    const void *src (%x),\n    size_t n = %x\n);\\\n\", poi(esp + (0 * 4)), poi(esp + (1 * 4)), poi(esp + (2 * 4))"},  # Use memmove_s(), wmemmove_s() for safer memory moving.
    {"wmemmove": ".printf \"wchar_t *wmemmove(\n    wchar_t *dest (%x),\n    const wchar_t *src (%x),\n    size_t n = %x\n);\\\n\", poi(esp + (0 * 4)), poi(esp + (1 * 4)), poi(esp + (2 * 4))"},  # Use memmove_s(), wmemmove_s() for safer memory moving.

    {"memcmp": ".printf \"int memcmp(\n    const void *ptr1 (%x),\n    const void *ptr2 (%x),\n    size_t n = %x\n);\\\n\", poi(esp + (0 * 4)), poi(esp + (1 * 4)), poi(esp + (2 * 4))"},  # Use memcmp_s(), wmemcmp_s() for safer memory comparison.
    {"wmemcmp": ".printf \"int wmemcmp(\n    const wchar_t *ptr1 (%x),\n    const wchar_t *ptr2 (%x),\n    size_t n = %x\n);\\\n\", poi(esp + (0 * 4)), poi(esp + (1 * 4)), poi(esp + (2 * 4))"},  # Use memcmp_s(), wmemcmp_s() for safer memory comparison.

    {"memset": ".printf \"void *memset(\n    void *ptr (%x),\n    int value = %x,\n    size_t n = %x\n);\\\n\", poi(esp + (0 * 4)), poi(esp + (1 * 4)), poi(esp + (2 * 4))"},  # Use memset_s(), wmemset_s() for safer memory setting.
    {"wmemset": ".printf \"wchar_t *wmemset(\n    wchar_t *ptr (%x),\n    wchar_t value = %x,\n    size_t n = %x\n);\\\n\", poi(esp + (0 * 4)), poi(esp + (1 * 4)), poi(esp + (2 * 4))"},  # Use memset_s(), wmemset_s() for safer memory setting.

    {"gets": ".printf \"char *gets(\n    char *str (%x)\n);\\\n\", poi(esp + (0 * 4))"},  # Use fgets() instead, as gets() does not check buffer size.

    {"sprintf": ".printf \"int sprintf(\n    char *str (%x),\n    const char *format (%x)\n    [,\n    argument1 %x,\n    argument2 %x,\n    ...]\n);\\\n\", poi(esp + (0 * 4)), poi(esp + (1 * 4)), poi(esp + (2 * 4)), poi(esp + (3 * 4))"},  # Use snprintf() or safer non-varg versions.
    {"vsprintf": ".printf \"int vsprintf(\n    char *str (%x),\n    const char *format (%x),\n    va_list args (%x)\n);\\\n\", poi(esp + (0 * 4)), poi(esp + (1 * 4)), poi(esp + (2 * 4))"},  # Use snprintf() or safer non-varg versions.
    {"swprintf": ".printf \"int swprintf(\n    wchar_t *str (%x),\n    const wchar_t *format (%x)\n    [,\n    argument1 %x,\n    argument2 %x,\n    ...]\n);\\\n\", poi(esp + (0 * 4)), poi(esp + (1 * 4)), poi(esp + (2 * 4)), poi(esp + (3 * 4))"},  # Use snprintf() or safer non-varg versions.
    {"vswprintf": ".printf \"int vswprintf(\n    wchar_t *str (%x),\n    const wchar_t *format (%x),\n    va_list args (%x)\n);\\\n\", poi(esp + (0 * 4)), poi(esp + (1 * 4)), poi(esp + (2 * 4))"},  # Use snprintf() or safer non-varg versions.

    {"snprintf": ".printf \"int snprintf(\n    char *str (%x),\n    size_t size = %x,\n    const char *format (%x)\n    [,\n    argument1 %x,\n    argument2 %x,\n    ...]\n);\\\n\", poi(esp + (0 * 4)), poi(esp + (1 * 4)), poi(esp + (2 * 4)), poi(esp + (3 * 4)), poi(esp + (4 * 4))"},  # Consider using a wrapper function that avoids vargs and checks parameters.
    {"vsnprintf": ".printf \"int vsnprintf(\n    char *str (%x),\n    size_t size = %x,\n    const char *format (%x),\n    va_list args (%x)\n);\\\n\", poi(esp + (0 * 4)), poi(esp + (1 * 4)), poi(esp + (2 * 4)), poi(esp + (3 * 4))"},  # Consider using a wrapper function that avoids vargs and checks parameters.

    {"realpath": ".printf \"char *realpath(\n    const char *path (%x),\n    char *resolved_path (%x)\n);\\\n\", poi(esp + (0 * 4)), poi(esp + (1 * 4))"},  # Use realpath() with NULL for the second parameter.
    {"getwd": ".printf \"char *getwd(\n    char *buf (%x)\n);\\\n\", poi(esp + (0 * 4))"},  # Use getcwd() instead because it checks the buffer size.

    {"wctomb": ".printf \"int wctomb(\n    char *s (%x),\n    wchar_t wchar (%x)\n);\\\n\", poi(esp + (0 * 4)), poi(esp + (1 * 4))"},  # Use safer alternatives where available or ensure proper use with caution.
    {"wcrtomb": ".printf \"size_t wcrtomb(\n    char *s (%x),\n    wchar_t wc (%x),\n    mbstate_t *ps (%x)\n);\\\n\", poi(esp + (0 * 4)), poi(esp + (1 * 4)), poi(esp + (2 * 4))"},  # Use safer alternatives where available or ensure proper use with caution.
    {"wcstombs": ".printf \"size_t wcstombs(\n    char *dest (%x),\n    const wchar_t *src (%x),\n    size_t n = %x\n);\\\n\", poi(esp + (0 * 4)), poi(esp + (1 * 4)), poi(esp + (2 * 4))"},  # Use safer alternatives where available or ensure proper use with caution.
    {"wcsrtombs": ".printf \"size_t wcsrtombs(\n    char *dest (%x),\n    const wchar_t **src (%x),\n    size_t n = %x,\n    mbstate_t *ps (%x)\n);\\\n\", poi(esp + (0 * 4)), poi(esp + (1 * 4)), poi(esp + (2 * 4)), poi(esp + (3 * 4))"},  # Use safer alternatives where available or ensure proper use with caution.
    {"wcsnrtombs": ".printf \"size_t wcsnrtombs(\n    char *dest (%x),\n    const wchar_t **src (%x),\n    size_t nwc = %x,\n    size_t n = %x,\n    mbstate_t *ps (%x)\n);\\\n\", poi(esp + (0 * 4)), poi(esp + (1 * 4)), poi(esp + (2 * 4)), poi(esp + (3 * 4)), poi(esp + (4 * 4))"},  # Use safer alternatives where available or ensure proper use with caution.

    {"HeapAlloc": ".printf \"void *HeapAlloc(\n    HANDLE hHeap (%x),\n    DWORD dwFlags = %x,\n    SIZE_T dwBytes = %x\n);\\\n\", poi(esp + (0 * 4)), poi(esp + (1 * 4)), poi(esp + (2 * 4))"},  # Validate and sanitize user inputs and check for overflows.

    {"gmtime": ".printf \"struct tm *gmtime(\n    const time_t *timep (%x)\n);\\\n\", poi(esp + (0 * 4))"},  # Use safer alternatives that return thread-local storage or reentrant versions.
    {"localtime": ".printf \"struct tm *localtime(\n    const time_t *timep (%x)\n);\\\n\", poi(esp + (0 * 4))"},  # Use safer alternatives that return thread-local storage or reentrant versions.
    {"ctime": ".printf \"char *ctime(\n    const time_t *timep (%x)\n);\\\n\", poi(esp + (0 * 4))"},  # Use safer alternatives that return thread-local storage or reentrant versions.
    {"ctime_r": ".printf \"char *ctime_r(\n    const time_t *timep (%x),\n    char *buf (%x)\n);\\\n\", poi(esp + (0 * 4)), poi(esp + (1 * 4))"},  # Use safer alternatives that return thread-local storage or reentrant versions.
    {"asctime": ".printf \"char *asctime(\n    const struct tm *tm (%x)\n);\\\n\", poi(esp + (0 * 4))"},  # Use safer alternatives that return thread-local storage or reentrant versions.
    {"asctime_r": ".printf \"char *asctime_r(\n    const struct tm *tm (%x),\n    char *buf (%x)\n);\\\n\", poi(esp + (0 * 4)), poi(esp + (1 * 4))"},  # Use safer alternatives that return thread-local storage or reentrant versions.

    {"getpwent": ".printf \"struct passwd *getpwent(\n);\\\n\""},  # Use getpwent_r(), getpwuid_r(), getpwnam_r() for reentrant and safer alternatives.
    {"getpwuid": ".printf \"struct passwd *getpwuid(\n    uid_t uid = %x\n);\\\n\", poi(esp + (0 * 4))"},  # Use getpwent_r(), getpwuid_r(), getpwnam_r() for reentrant and safer alternatives.
    {"getpwnam": ".printf \"struct passwd *getpwnam(\n    const char *name (%x)\n);\\\n\", poi(esp + (0 * 4))"},  # Use getpwent_r(), getpwuid_r(), getpwnam_r() for reentrant and safer alternatives.
    {"gethostbyname": ".printf \"struct hostent *gethostbyname(\n    const char *name (%x)\n);\\\n\", poi(esp + (0 * 4))"},  # Use getaddrinfo() and getnameinfo() instead for safer and thread-safe alternatives.
    {"gethostbyaddr": ".printf \"struct hostent *gethostbyaddr(\n    const void *addr (%x),\n    int len = %x,\n    int type = %x\n);\\\n\", poi(esp + (0 * 4)), poi(esp + (1 * 4)), poi(esp + (2 * 4))"},  # Use getaddrinfo() and getnameinfo() instead for safer and thread-safe alternatives.

    {"tmpnam": ".printf \"char *tmpnam(\n    char *str (%x)\n);\\\n\", poi(esp + (0 * 4))"},  # Use mkstemp() or tmpfile() instead for secure temporary file creation.
    {"tempnam": ".printf \"char *tempnam(\n    const char *dir (%x),\n    const char *prefix (%x)\n);\\\n\", poi(esp + (0 * 4)), poi(esp + (1 * 4))"}  # Use mkstemp() or tmpfile() instead for secure temporary file creation.
]




disabled_names = [
    # "memset", 
    # "memcmp", 
    # "memmove", 
    # "KERNELBASE!WriteFile"
]


for i in functions:
    import re
    # Search for all symbols that match the function across all modules
    
    for func, debugger_statement in i.items():
        result = pykd.dbgCommand(f"x *!{func}")
        if not(result):
            continue
        lines = result.splitlines()
        for line in lines:
            if 'Unable to resolve unqualified' in line:
                continue
            if '!' + func + ' ' in line:
                splitted_on_spaces = line.split()
                address = splitted_on_spaces[0]
                exact_function_name = splitted_on_spaces[1]
                new_db_s = debugger_statement
                # new_db_s = new_db_s.replace('\\n', '\n')
                new_db_s = new_db_s.replace('"', '\\"')
                # print(new_db_s)
                add_debug_point = f"bp {exact_function_name} \"{new_db_s};k; g\""
                # print(add_debug_point)
                try:
                    pykd.dbgCommand(add_debug_point)
                except Exception as e:
                    print(e)
            # exit()


result = pykd.dbgCommand(f"bl")
for i in result.splitlines():
    for disable_address in disabled_names:
       if disable_address + " " in i:
            splitted_on_spaces = i.split()
            cmd = "bd " + splitted_on_spaces[0]
            print(cmd)
            print("disabled function: ", cmd )
            pykd.dbgCommand(cmd)
             



pykd.dprintln("All breakpoints have been set.")

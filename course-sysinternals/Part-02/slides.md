**A house has rooms, bed room, kitchen etc .. what a process has?**  
- **A virtual Address space**  which defines the boundary of the process like the boundary of the house. More of like a universe for a program. Size is always equal to size of the pointer in bits as power of 2. Ex 32 bit 2^32 = 4 GB. This has nothing to do with memory but just space or theoretical max memory a process can access at a time.
 
- **Threads**  – like human beings who is living inside the house.
 
- **Loaded dll and exe**  think of it like stuffs in the house which people living in the house uses for living. (programs or instructions)
 
- **Handles**  for different computing resources like files, network sockets etc. (like a key to a car – not the car itself)
 
- **Security Token**  to decide what privilege the inhabitants of the process has mainly outside the process. Inhabitants (threads) of the "white house" (system process) will have a very high permissions and privilege over outsiders in the country US.
 
- **Different types of memory allocations**  inside the virtual address space like rooms in the house, stack heap raw virtual memory, reserved memory. In turn defined by VAD and PTEs.
 
- More stuffs... pid, handle for the process itself etc.

"""
generate_dataset.py
Generates 500+ (525 total) beginner-level IT interview questions across 21 categories:
1. Computer Fundamentals
2. Programming
3. Python
4. C/C++
5. Java
6. OOP
7. Data Structures
8. Database & SQL
9. Operating Systems
10. Computer Networks
11. Web Development
12. HTML/CSS/JavaScript
13. APIs
14. Software Engineering
15. Git/GitHub
16. AI & Machine Learning
17. Cybersecurity
18. Cloud Computing
19. Flutter
20. Firebase
21. IoT

Each question contains:
- id: integer
- question: question text
- category: IT category
- difficulty: Easy
- answer_1: Very short and simple
- answer_2: Simple explanation
- answer_3: Slightly detailed explanation
"""

import os
import json
import csv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(BASE_DIR)
DATASETS_DIR = os.path.join(BASE_DIR, "datasets")
os.makedirs(DATASETS_DIR, exist_ok=True)

# 21 Categories, 25 questions each = 525 Questions
RAW_DATA = {
    "Computer Fundamentals": [
        (
            "What is a computer?",
            "A computer is an electronic device that processes data.",
            "A computer is an electronic machine that accepts raw data, processes it according to instructions, and outputs useful information.",
            "A computer is a programmable digital electronic device composed of hardware and software components that takes input data, performs arithmetic and logic operations, and produces information for storage or display."
        ),
        (
            "What is CPU in a computer?",
            "CPU is the central processor or brain of a computer.",
            "The Central Processing Unit (CPU) executes software instructions and processes data for the system.",
            "The Central Processing Unit (CPU) is the primary hardware component that interprets and executes program instructions, consisting of the Arithmetic Logic Unit (ALU), Control Unit (CU), and internal registers."
        ),
        (
            "What is RAM in a computer?",
            "RAM is temporary primary memory.",
            "RAM (Random Access Memory) is fast, volatile memory used by the CPU to hold currently active programs and data.",
            "Random Access Memory (RAM) is high-speed volatile storage that provides read and write access to running applications and the operating system, losing its contents when the system powers off."
        ),
        (
            "What is ROM?",
            "ROM is permanent read-only memory.",
            "ROM (Read-Only Memory) is non-volatile memory containing crucial startup firmware that cannot be easily modified.",
            "Read-Only Memory (ROM) is non-volatile semiconductor memory that permanently stores essential firmware instructions, such as the BIOS or UEFI, needed to boot the computer hardware."
        ),
        (
            "What is the difference between RAM and ROM?",
            "RAM is temporary memory, while ROM is permanent.",
            "RAM is volatile read-write memory for running tasks, whereas ROM is non-volatile memory that stores permanent startup code.",
            "RAM is high-speed volatile memory that loses data on power-off and can be read and written freely, while ROM is non-volatile storage that retains data permanently and is mostly read-only."
        ),
        (
            "What is cache memory?",
            "Cache memory is extremely fast temporary memory near the CPU.",
            "Cache is high-speed memory located inside or near the CPU that stores frequently used data to speed up execution.",
            "Cache memory is a small, ultra-fast static RAM buffer placed between the CPU and main RAM to minimize memory latency by caching recently accessed data and instructions across L1, L2, and L3 levels."
        ),
        (
            "What is an operating system in simple terms?",
            "An operating system manages computer hardware and software.",
            "An operating system is the core software that coordinates hardware components and provides an environment for running apps.",
            "An Operating System (OS) is system software that acts as an intermediary between computer hardware and user applications, managing memory, processes, storage devices, and system security."
        ),
        (
            "What is binary code?",
            "Binary code is data represented as 0s and 1s.",
            "Binary is a base-2 numbering system made of zeros and ones that digital computers understand natively.",
            "Binary code is the fundamental machine-level representation of data and instructions in digital computers, using combinations of two discrete electrical states: 0 (off/low voltage) and 1 (on/high voltage)."
        ),
        (
            "What is a bit and a byte?",
            "A bit is 0 or 1, and a byte is 8 bits.",
            "A bit is the smallest unit of digital data, and a group of 8 bits forms one byte.",
            "A bit (binary digit) is the basic indivisible unit of computer information holding 0 or 1, while a byte consists of 8 contiguous bits, capable of representing 256 distinct values such as a single text character."
        ),
        (
            "What is a motherboard?",
            "The motherboard is the main circuit board connecting all components.",
            "A motherboard is the central printed circuit board that connects the CPU, RAM, storage, and other peripherals together.",
            "The motherboard is the foundational printed circuit board (PCB) of a computer that provides electrical buses, power distribution, and physical sockets to interconnect the processor, memory, expansion cards, and storage devices."
        ),
        (
            "What is a Hard Disk Drive (HDD)?",
            "An HDD is a magnetic data storage device.",
            "A Hard Disk Drive is non-volatile storage that records data magnetically onto rotating platters.",
            "A Hard Disk Drive (HDD) is a secondary storage device that uses mechanical magnetic heads reading and writing data across rapidly spinning circular disks to store files permanently."
        ),
        (
            "What is a Solid State Drive (SSD)?",
            "An SSD is fast flash storage without moving parts.",
            "A Solid State Drive is modern non-volatile storage that uses flash memory chips to store data much faster than an HDD.",
            "A Solid State Drive (SSD) is an electronic data storage device utilizing NAND flash memory, providing significantly faster read/write speeds, lower power draw, and greater physical durability than mechanical hard drives."
        ),
        (
            "What is BIOS in a computer?",
            "BIOS is basic startup firmware.",
            "BIOS (Basic Input/Output System) is built-in firmware that initializes hardware when you turn on a computer.",
            "The Basic Input/Output System (BIOS) is low-level firmware stored on a motherboard ROM chip that runs the Power-On Self-Test (POST), detects hardware components, and loads the operating system bootloader."
        ),
        (
            "What is an input device?",
            "An input device sends data into a computer.",
            "An input device is a hardware peripheral used to enter data or control signals into a computer, like a keyboard or mouse.",
            "An input device is any piece of peripheral hardware that converts human actions or real-world physical signals into digital data that the computer system can interpret and process."
        ),
        (
            "What is an output device?",
            "An output device displays or delivers processed data.",
            "An output device presents processed data from the computer to the user, such as a monitor or printer.",
            "An output device is peripheral equipment that converts processed machine data into human-perceivable forms, including visual displays, printed paper, audio speakers, or physical tactile feedback."
        ),
        (
            "What is computer software?",
            "Software is a set of instructions for computers.",
            "Software is the collection of programs, data, and instructions that tell computer hardware what to do.",
            "Computer software comprises the intangible programs, scripts, and operating instructions that run on computer hardware, broadly divided into system software and application software."
        ),
        (
            "What is computer hardware?",
            "Hardware refers to the physical parts of a computer.",
            "Hardware is the tangible, physical equipment of a computer system like the keyboard, monitor, and circuits.",
            "Computer hardware encompasses all physical, electronic, and electromechanical components of a computing device, including processing units, memory chips, circuit boards, and external peripherals."
        ),
        (
            "What is a peripheral device?",
            "A peripheral is an external device connected to a computer.",
            "A peripheral is auxiliary hardware connected externally to expand a computer's input, output, or storage capabilities.",
            "A peripheral device is an auxiliary hardware unit connected to a host computer through ports or wireless links to supply input, output, or secondary storage without being part of the central core architecture."
        ),
        (
            "What is the system bus?",
            "The bus is a communication pathway for data.",
            "A system bus is a set of physical wires that transfers data and signals between the CPU, memory, and devices.",
            "A system bus is a high-speed communication channel composed of address, data, and control lines that transfers digital signals between the processor, primary memory, and peripheral controllers."
        ),
        (
            "What is a GPU?",
            "A GPU is a graphics processing chip.",
            "A Graphics Processing Unit (GPU) is a specialized chip designed to quickly render images, video, and parallel computations.",
            "A Graphics Processing Unit (GPU) is a massively parallel processor optimized for handling multiple mathematical computations concurrently, widely used in 3D graphics rendering, video encoding, and machine learning."
        ),
        (
            "What is clock speed in a CPU?",
            "Clock speed is the operating frequency of a processor.",
            "Clock speed measures how many cycles a CPU can execute per second, typically measured in gigahertz (GHz).",
            "CPU clock speed, expressed in gigahertz (GHz), defines the operating frequency of the internal oscillator that synchronizes processor operations, indicating billions of clock cycles executed per second."
        ),
        (
            "What is a computer port?",
            "A port is a physical or virtual connection point.",
            "A computer port is a physical socket or software interface used to connect external devices and transfer data.",
            "In hardware, a port is a physical connection interface (like USB or HDMI) for external peripherals; in networking, a port is a logical endpoint number identifying a specific network application or service."
        ),
        (
            "What is virtual memory?",
            "Virtual memory is secondary storage used as extra RAM.",
            "Virtual memory is an OS technique that uses hard drive space to extend available physical RAM when memory runs low.",
            "Virtual memory is a memory management capability of an operating system that maps virtual addresses to physical storage, allowing programs to exceed physical RAM limits by swapping pages to and from disk."
        ),
        (
            "What is an algorithm?",
            "An algorithm is a step-by-step problem-solving method.",
            "An algorithm is a finite, well-defined sequence of instructions designed to solve a specific problem or perform a task.",
            "An algorithm is a formal, deterministic sequence of unambiguous logical instructions that receives input, executes defined steps, and produces a correct output within a finite number of operations."
        ),
        (
            "What is a file system?",
            "A file system organizes files on a storage drive.",
            "A file system is software that controls how data is named, stored, and retrieved on a storage disk.",
            "A file system is a structured subsystem of an operating system (such as NTFS, ext4, or FAT32) that manages how data blocks are organized, indexed, retrieved, and protected on physical storage media."
        )
    ],
    "Programming": [
        (
            "What is a programming language?",
            "A programming language is a tool for writing computer instructions.",
            "A programming language is a formal language of instructions used by developers to build software programs.",
            "A programming language is a formal system of notation with defined syntax and semantics used by software developers to write programs that computers can compile or interpret into machine execution."
        ),
        (
            "What is a variable?",
            "A variable is a named storage container for data.",
            "A variable is a named memory location used in a program to hold values that can change during execution.",
            "A variable is a symbolic name bound to a specific memory storage address that holds a typed value whose contents can be retrieved, evaluated, or altered throughout program runtime."
        ),
        (
            "What is a data type?",
            "A data type specifies the kind of value a variable can hold.",
            "A data type tells the compiler or interpreter what type of data a variable holds and what operations can be performed on it.",
            "A data type is an attribute of data that specifies to the compiler or interpreter the size of memory allocation, the valid range of values, and the set of operations permissible on that variable."
        ),
        (
            "What is a compiler?",
            "A compiler translates source code into machine code all at once.",
            "A compiler is a program that translates an entire source code file into executable machine language before running.",
            "A compiler is a software translation tool that analyzes entire high-level program source code, performs syntax checking and optimization, and generates equivalent low-level machine code or bytecode ahead of execution."
        ),
        (
            "What is an interpreter?",
            "An interpreter runs source code line by line.",
            "An interpreter is a program that reads, translates, and executes code directly line by line at runtime.",
            "An interpreter is a language processor that parses and directly executes program statements line-by-line in real time without requiring prior compilation into a standalone binary file."
        ),
        (
            "What is the difference between a compiler and an interpreter?",
            "A compiler converts code before execution; an interpreter translates code line-by-line during execution.",
            "Compilers translate the whole program at once producing an executable file, while interpreters execute instructions line-by-line in real time.",
            "A compiler analyzes source code in its entirety to produce an optimized standalone executable binary before runtime, whereas an interpreter reads, parses, and executes instructions sequentially on the fly."
        ),
        (
            "What is a loop in programming?",
            "A loop repeats a block of code multiple times.",
            "A loop is a control structure that repeats a set of instructions as long as a specified condition is true.",
            "A loop is a control flow mechanism that iteratively executes a code block until a termination condition is satisfied, preventing code duplication and enabling automated data processing."
        ),
        (
            "What is an infinite loop?",
            "An infinite loop repeats forever without stopping.",
            "An infinite loop is a loop whose exit condition is never satisfied, causing it to run continuously until interrupted.",
            "An infinite loop is an execution cycle where the loop condition remains perpetually true or lacks a valid break statement, consuming CPU resources until the process crashes or is manually terminated."
        ),
        (
            "What is a function in programming?",
            "A function is a reusable block of code that performs a task.",
            "A function is an organized, reusable code block that accepts inputs, performs an operation, and returns a result.",
            "A function is a modular, self-contained block of program statements designed to accomplish a specific task, accepting zero or more arguments, executing logic, and optionally returning a computed value."
        ),
        (
            "What are parameters and arguments in functions?",
            "Parameters are variable placeholders in the definition; arguments are actual values passed in.",
            "Parameters are the variables listed in a function definition, while arguments are the real values passed when calling the function.",
            "Parameters are identifiers declared in a function signature that define expected inputs, whereas arguments are the concrete values or references supplied to that function during an actual invocation."
        ),
        (
            "What is recursion in programming?",
            "Recursion is when a function calls itself.",
            "Recursion is a technique where a function solves a problem by calling itself with smaller sub-problems until reaching a base case.",
            "Recursion is an algorithmic paradigm where a function invokes itself iteratively with modified parameters until a defined base condition halts the call chain, unwinding the call stack with results."
        ),
        (
            "What is a base condition in recursion?",
            "A base condition is the stopping rule in recursion.",
            "A base condition is the rule in a recursive function that stops further recursive calls and prevents an infinite loop.",
            "A base condition is a terminal check evaluated at the start of a recursive function that directly returns a value without making further self-calls, thereby preventing call stack exhaustion."
        ),
        (
            "What is a syntax error?",
            "A syntax error is a violation of language grammar rules.",
            "A syntax error occurs when code breaks the grammatical rules of the programming language, preventing it from running.",
            "A syntax error is a compile-time or parse-time failure caused by improper character sequences, missing punctuation, or invalid structure that violates the formal grammar of the programming language."
        ),
        (
            "What is a runtime error?",
            "A runtime error occurs while a program is running.",
            "A runtime error happens when valid code encounters an unexpected condition during execution, causing the program to crash.",
            "A runtime error is an exceptional state encountered during program execution—such as division by zero, null pointer access, or missing files—that aborts program execution unless handled gracefully."
        ),
        (
            "What is a logical error?",
            "A logical error causes wrong output without crashing.",
            "A logical error occurs when code runs without crashing but produces incorrect or unexpected results due to flawed logic.",
            "A logical error is a defect in algorithmic design or formula implementation that allows the program to compile and execute without exceptions, but leads to incorrect, unintended, or inaccurate program outputs."
        ),
        (
            "What is debugging?",
            "Debugging is finding and fixing code errors.",
            "Debugging is the process of identifying, tracing, and resolving bugs or defects in software code.",
            "Debugging is a systematic software engineering process of inspecting code, analyzing execution state, setting breakpoints, and isolating defects to ensure the program behaves according to specifications."
        ),
        (
            "What is variable scope?",
            "Scope is where a variable can be accessed in code.",
            "Variable scope defines the region of code where a declared variable is visible and accessible.",
            "Scope determines the lifetime and visibility boundary of an identifier in a program, commonly categorized into local, function, block, module, or global scope."
        ),
        (
            "What is a constant in programming?",
            "A constant is a variable whose value cannot change.",
            "A constant is an identifier bound to a fixed value that remains unchanged throughout program execution.",
            "A constant is an immutable identifier whose assigned value is set once and cannot be modified or reallocated during program runtime, preventing unintended side effects."
        ),
        (
            "What is type casting?",
            "Type casting converts a value from one data type to another.",
            "Type casting is converting a variable from one data type into a compatible different data type, such as integer to float.",
            "Type casting is an explicit or implicit operation that transforms data stored in one representation into another format, such as widening an integer to a float or parsing a string to an integer."
        ),
        (
            "What is an array in programming?",
            "An array is a collection of elements stored together.",
            "An array is a data structure containing multiple elements of the same type stored in contiguous memory locations.",
            "An array is a fixed-size or dynamic sequential collection of homogenous elements stored in adjacent memory blocks, allowing direct constant-time access to any item using an integer index."
        ),
        (
            "What is conditional branching in programming?",
            "Conditional branching decides which code block to run based on a condition.",
            "Conditional branching uses if-else or switch statements to execute different code paths depending on boolean conditions.",
            "Conditional branching directs program control flow along distinct execution branches by evaluating boolean expressions using constructs such as if, else if, else, and switch statements."
        ),
        (
            "What is pseudocode?",
            "Pseudocode is plain language describing code steps.",
            "Pseudocode is an informal, human-readable outline of a program algorithm that does not follow strict programming syntax.",
            "Pseudocode is a high-level, language-agnostic description of an algorithm written in structured natural language, designed to clarify logic and architectural design before writing actual source code."
        ),
        (
            "What is an IDE?",
            "An IDE is a software application for writing and testing code.",
            "An Integrated Development Environment (IDE) is a software suite providing a code editor, compiler, debugger, and build tools in one interface.",
            "An Integrated Development Environment (IDE) is a comprehensive developer toolkit combining source code editing, syntax highlighting, intelligent code completion, build automation, and integrated debugging."
        ),
        (
            "What is a memory leak?",
            "A memory leak is unused memory that is not released.",
            "A memory leak happens when a program allocates memory dynamically but fails to release it back to the system after use.",
            "A memory leak is a resource management defect where dynamically allocated memory is no longer referenced by the program yet remains unreleased, gradually depleting available system memory."
        ),
        (
            "What is clean code?",
            "Clean code is code that is easy to read and maintain.",
            "Clean code is well-structured, readable, and self-explanatory code that follows standards and is simple to maintain.",
            "Clean code is source code written with clear naming conventions, modular architecture, comprehensive comments, and minimal complexity, making it readable, testable, and maintainable by any engineer."
        )
    ],
    "Python": [
        (
            "What is Python?",
            "Python is a popular programming language.",
            "Python is a high-level, interpreted programming language known for its clear and readable syntax.",
            "Python is a versatile, high-level, dynamically typed, and interpreted programming language that emphasizes code readability, supporting multiple paradigms including object-oriented, procedural, and functional programming."
        ),
        (
            "What are the key features of Python?",
            "Python is simple, readable, interpreted, and open-source.",
            "Python is beginner-friendly, platform-independent, dynamically typed, and has a massive ecosystem of libraries.",
            "Python offers clear concise syntax, automatic memory management via garbage collection, cross-platform portability, extensive standard libraries, and rich community support across web development, data science, and AI."
        ),
        (
            "What is PEP 8 in Python?",
            "PEP 8 is the official Python style guide.",
            "PEP 8 is the style guide for Python code that outlines conventions for formatting, naming, and readability.",
            "Python Enhancement Proposal 8 (PEP 8) is the standard style guide establishing best practices for Python coding conventions, including 4-space indentation, naming standards (snake_case, CamelCase), and code layout."
        ),
        (
            "What is a Python list?",
            "A list is an ordered, changeable collection of items.",
            "A list in Python is an ordered, mutable sequence that can hold elements of different data types.",
            "A list in Python is a built-in mutable sequence type indexed by integers, created with square brackets, supporting dynamic resizing, duplicate items, and heterogeneous data elements."
        ),
        (
            "What is a Python tuple?",
            "A tuple is an ordered, unchangeable collection of items.",
            "A tuple is an ordered, immutable collection in Python used to store data that should not be modified after creation.",
            "A tuple is an immutable, ordered collection defined using parentheses, commonly used to hold fixed groupings of related values with faster iteration and lower memory overhead than lists."
        ),
        (
            "What is the difference between a list and a tuple in Python?",
            "Lists are mutable; tuples are immutable.",
            "Lists can be changed after creation using square brackets, while tuples cannot be modified and use parentheses.",
            "Python lists are mutable dynamic sequences that permit element insertion, deletion, and modification, whereas tuples are immutable fixed sequences that offer integrity protection and slight performance benefits."
        ),
        (
            "What is a Python dictionary?",
            "A dictionary is a collection of key-value pairs.",
            "A dictionary in Python is an unordered or insertion-ordered mutable collection that maps unique keys to values.",
            "A dictionary is a built-in associative hash map that associates unique, hashable keys with arbitrary values, offering average constant-time O(1) complexity for key lookups, insertions, and deletions."
        ),
        (
            "What is a Python set?",
            "A set is an unordered collection of unique elements.",
            "A set in Python is a mutable collection that contains only unique, non-duplicate values without fixed ordering.",
            "A set is an unordered collection of distinct, hashable objects implemented via hash tables, supporting mathematical set operations such as unions, intersections, differences, and subset checks in O(1) average time."
        ),
        (
            "What is list comprehension in Python?",
            "List comprehension is a concise way to create lists.",
            "List comprehension provides a compact syntax to generate a new list by applying an expression to items in an iterable.",
            "List comprehension is a clean Pythonic construct that transforms and filters iterables into new lists in a single line of readable code, such as `[x*2 for x in items if x > 0]`."
        ),
        (
            "What is a lambda function in Python?",
            "A lambda is a small anonymous function.",
            "A lambda function is a single-line anonymous function defined with the `lambda` keyword without using `def`.",
            "A lambda function is an inline, unnamed function restricted to a single evaluated expression that automatically returns its result, often passed as an argument to higher-order functions like map, filter, or sorted."
        ),
        (
            "What are *args and **kwargs in Python?",
            "*args passes positional arguments; **kwargs passes keyword arguments.",
            "*args allows a function to accept any number of positional arguments as a tuple, while **kwargs accepts arbitrary keyword arguments as a dictionary.",
            "The `*args` syntax unpacks variable positional arguments into a tuple inside a function, while `**kwargs` unpacks variable named keyword arguments into a dictionary, enabling flexible function signatures."
        ),
        (
            "What is a Python generator?",
            "A generator produces values one at a time using yield.",
            "A generator is a function that yields a sequence of values lazily on demand instead of storing them all in memory at once.",
            "A generator is a special iterator function that maintains its execution state and produces values iteratively using the `yield` statement, significantly reducing memory consumption for large data sequences."
        ),
        (
            "What does the yield keyword do in Python?",
            "Yield pauses a function and returns a value.",
            "The `yield` keyword temporarily suspends a generator function, returns a value to the caller, and remembers the execution state for the next call.",
            "Unlike `return` which terminates a function, `yield` outputs a value from a generator function while preserving its local variables and execution pointer so it can resume upon the next iteration."
        ),
        (
            "What is a decorator in Python?",
            "A decorator modifies or enhances a function without altering its code.",
            "A decorator is a function that takes another function as input and extends its behavior using the `@decorator` syntax.",
            "A decorator is a higher-order function that wraps another function or method to inject pre- or post-execution logic (such as logging, timing, or authentication) without directly modifying the underlying source code."
        ),
        (
            "What is the GIL in Python?",
            "The GIL is the Global Interpreter Lock in CPython.",
            "The Global Interpreter Lock (GIL) is a mutex in CPython that allows only one native thread to execute Python bytecode at a time.",
            "The GIL (Global Interpreter Lock) is a synchronization mechanism in the CPython implementation that prevents concurrent execution of multiple threads on multi-core processors, protecting reference counts from race conditions."
        ),
        (
            "How do you handle exceptions in Python?",
            "Exceptions are handled using try, except, and finally blocks.",
            "You handle errors in Python by wrapping risky code in a `try` block and catching errors in an `except` block.",
            "Exception handling in Python isolates fault-prone code within a `try` block, catches specific error types in `except` clauses, optionally runs `else` when no error occurs, and guarantees cleanup inside `finally`."
        ),
        (
            "What is a Python virtual environment?",
            "A virtual environment is an isolated space for project packages.",
            "A virtual environment is a self-contained directory containing a specific Python version and set of packages for a project.",
            "A virtual environment (created with `venv` or `virtualenv`) provides an isolated runtime directory tree for a project, preventing dependency version conflicts between different Python projects on the same machine."
        ),
        (
            "What is the difference between deepcopy and shallow copy in Python?",
            "Shallow copy copies references; deepcopy duplicates nested objects recursively.",
            "A shallow copy creates a new container but references child objects, whereas a deep copy duplicates the container and all nested objects recursively.",
            "A shallow copy (`copy.copy`) creates a new outer collection while maintaining shared references to internal nested objects, while a deep copy (`copy.deepcopy`) creates an entirely independent duplicate of the entire hierarchy."
        ),
        (
            "What is the __init__ method in Python?",
            "__init__ is the constructor method of a class.",
            "The `__init__` method is the constructor in Python that automatically initializes attributes when a new object is instantiated.",
            "`__init__` is a special dunder (double underscore) initializer method in Python classes that is invoked automatically during object instantiation to configure initial state and instance attributes."
        ),
        (
            "What is the purpose of self in Python classes?",
            "Self represents the current instance of the class.",
            "The `self` parameter refers to the current object instance and is used to access its attributes and methods.",
            "In Python, `self` is the explicit first parameter of instance methods that binds the method call to the specific object instance, providing access to that instance's unique attributes and methods."
        ),
        (
            "What is pass in Python?",
            "Pass is a null placeholder statement.",
            "The `pass` keyword is a placeholder that does nothing when code is syntactically required but no action is needed.",
            "The `pass` statement is a no-operation (NOP) placeholder used in empty functions, classes, loops, or conditional blocks to satisfy Python's indentation requirements without executing any logic."
        ),
        (
            "What is pip in Python?",
            "Pip is the official package manager for Python.",
            "Pip is the command-line tool used to install, update, and manage third-party Python libraries from PyPI.",
            "Pip is the standard package installer for Python that downloads and installs software packages and their dependencies directly from the Python Package Index (PyPI) or local repositories."
        ),
        (
            "What is the difference between is and == in Python?",
            "== checks value equality; is checks memory identity.",
            "The `==` operator compares whether two values are equal, while `is` checks whether two variables point to the exact same object in memory.",
            "The `==` operator invokes the object's `__eq__` method to compare equivalence of content or values, whereas the `is` operator tests object identity by verifying whether both references share the same memory address."
        ),
        (
            "How does memory management work in Python?",
            "Python manages memory automatically using reference counting and garbage collection.",
            "Python allocates memory through a private heap and automatically frees unused memory using reference counting and a cyclic garbage collector.",
            "Python uses an internal private heap managed by the Python Memory Manager, freeing memory primarily through reference counting supplemented by a cyclic generational garbage collector that identifies circular references."
        ),
        (
            "What are docstrings in Python?",
            "Docstrings are documentation strings placed inside functions or classes.",
            "Docstrings are string literals written with triple quotes right after defining a function, class, or module to document its purpose.",
            "A docstring is a documentation string enclosed in triple quotes (`'''` or `\"\"\"`) placed immediately below a module, function, class, or method declaration, retrievable at runtime via the `__doc__` attribute."
        )
    ],
    "C/C++": [
        (
            "What is C?",
            "C is a foundational procedural programming language.",
            "C is a structured, procedural programming language known for low-level memory access and high performance.",
            "C is a general-purpose, procedural programming language developed in 1972 at Bell Labs that provides low-level hardware control, pointers, and direct memory manipulation, serving as the basis for modern operating systems."
        ),
        (
            "What is C++?",
            "C++ is an extension of C with object-oriented programming.",
            "C++ is an extension of the C language that adds object-oriented, generic, and functional programming capabilities.",
            "C++ is a high-performance, multi-paradigm programming language created by Bjarne Stroustrup that extends C with classes, inheritance, polymorphism, templates, exception handling, and the Standard Template Library (STL)."
        ),
        (
            "What is a pointer in C/C++?",
            "A pointer is a variable that stores a memory address.",
            "A pointer is a variable whose value is the direct physical address of another variable in memory.",
            "A pointer is a variable data type that holds the memory address of another object or function, allowing direct memory access, dynamic memory allocation, and efficient array or structure manipulation."
        ),
        (
            "What is the difference between a pointer and a reference in C++?",
            "A pointer holds a memory address; a reference is an alias to an existing variable.",
            "Pointers can be reassigned and can be null, whereas references cannot be null and must be initialized when created.",
            "A pointer has its own memory location storing an address and can point to null or be reassigned, while a C++ reference acts as a permanent, non-null alias to an existing object that cannot be rebound."
        ),
        (
            "What is dynamic memory allocation in C?",
            "Dynamic memory allocation allocates memory at runtime on the heap.",
            "Dynamic memory allocation in C uses functions like malloc and calloc to allocate memory on the heap during program execution.",
            "Dynamic memory allocation allows a program to request memory of variable size from the system heap at runtime using standard library functions like `malloc()`, `calloc()`, and `realloc()`, which must be manually freed with `free()`."
        ),
        (
            "What is the difference between malloc() and calloc()?",
            "malloc allocates uninitialized memory; calloc allocates memory initialized to zero.",
            "The `malloc()` function allocates a single memory block without clearing it, while `calloc()` allocates multiple blocks and initializes all bytes to zero.",
            "`malloc()` takes a single byte-size argument and returns uninitialized memory containing garbage values, whereas `calloc()` takes the number of elements and their size, allocating memory and zeroing every byte."
        ),
        (
            "What does free() do in C?",
            "The free function releases dynamically allocated heap memory.",
            "In C, `free()` returns memory previously allocated by malloc or calloc back to the system to prevent memory leaks.",
            "The `free()` function deallocates a block of heap memory pointed to by a pointer returned from `malloc()`, `calloc()`, or `realloc()`, making that memory address available for future allocations."
        ),
        (
            "What is the difference between new/delete and malloc/free?",
            "new/delete are C++ operators that call constructors; malloc/free are C functions that only allocate raw memory.",
            "The `new` and `delete` operators in C++ allocate memory and invoke class constructors and destructors, while `malloc()` and `free()` allocate and release raw bytes without object initialization.",
            "In C++, `new` and `delete` are type-safe language operators that automatically calculate size, allocate memory, and call constructors or destructors, whereas C's `malloc` and `free` are library functions handling raw void pointers."
        ),
        (
            "What is a segmentation fault?",
            "A segmentation fault is an error from accessing illegal memory.",
            "A segmentation fault occurs when a program tries to read or write to a restricted memory location it does not own.",
            "A segmentation fault (SIGSEGV) is an operating system error triggered when a process attempts an illegal memory access, such as dereferencing a null or dangling pointer or writing to read-only memory."
        ),
        (
            "What is a dangling pointer?",
            "A dangling pointer points to deleted or freed memory.",
            "A dangling pointer is a pointer that continues to point to a memory location after the storage has been deallocated.",
            "A dangling pointer arises when memory pointed to by a pointer is deallocated (via `free` or `delete`) or when an automatic local variable goes out of scope, leaving the pointer addressing invalid memory."
        ),
        (
            "What is a memory leak in C/C++?",
            "A memory leak occurs when heap memory is not freed.",
            "A memory leak happens when dynamically allocated memory is no longer needed but never released using free or delete.",
            "A memory leak is an issue where memory allocated on the heap is not deallocated before all pointers referencing it are lost, causing the program to consume increasing amounts of system RAM over time."
        ),
        (
            "What is a structure (struct) in C?",
            "A struct is a user-defined collection of different data types.",
            "A `struct` in C is a composite data type that groups related variables of different types together under a single name.",
            "A structure (`struct`) in C is a user-defined composite data type that groups logically related variables of differing data types into a contiguous block of memory, accessed using the dot or arrow operator."
        ),
        (
            "What is the difference between a struct and a union in C?",
            "A struct gives each member its own memory; a union shares one memory space.",
            "In a `struct`, every member has a distinct memory location, while in a `union`, all members share the exact same memory space.",
            "A `struct` allocates enough contiguous memory to store all its declared members simultaneously, whereas a `union` allocates only enough memory for its largest member, allowing only one member value to be stored at a time."
        ),
        (
            "What is a header file in C/C++?",
            "A header file contains declarations and prototypes.",
            "A header file (like .h or .hpp) contains function declarations, macros, and type definitions shared across multiple source files.",
            "A header file is a text file containing declarations of functions, classes, macros, and global constants, included in source code via `#include` directives to facilitate modularity and compilation separation."
        ),
        (
            "What does the preprocessor do in C/C++?",
            "The preprocessor modifies source code before actual compilation.",
            "The preprocessor handles directives like #include, #define, and conditional compilation before the compiler translates the code.",
            "The preprocessor is the initial stage of the C/C++ compilation pipeline that processes preprocessor directives (beginning with `#`), expanding macros, including header files, and conditionally compiling code blocks."
        ),
        (
            "What is function overloading in C++?",
            "Function overloading is having multiple functions with the same name but different parameters.",
            "Function overloading in C++ allows multiple functions to share the same name as long as their parameter counts or types differ.",
            "Function overloading is a compile-time polymorphism feature in C++ where two or more functions in the same scope share an identical name but have distinct parameter signatures, resolved by the compiler based on arguments."
        ),
        (
            "What is an inline function in C++?",
            "An inline function suggests expanding the function code at the call site.",
            "An inline function is a function defined with the `inline` keyword to reduce function call overhead by inserting code directly.",
            "An inline function advises the C++ compiler to substitute the function's body directly at each call site, eliminating the overhead of creating a new stack frame for small, frequently called routines."
        ),
        (
            "What is a virtual function in C++?",
            "A virtual function enables runtime polymorphism in classes.",
            "A virtual function is a member function in a base class that can be overridden in derived classes to achieve dynamic binding.",
            "A virtual function is declared with the `virtual` keyword in a base class, instructing the C++ compiler to resolve function calls dynamically at runtime using a virtual method table (vtable), enabling polymorphism."
        ),
        (
            "What is a pure virtual function?",
            "A pure virtual function is a function with no implementation, set to 0.",
            "A pure virtual function is a virtual function declared with `= 0` that derived classes must implement, making the base class abstract.",
            "A pure virtual function has no body in the base class and is defined with `= 0`, transforming the containing class into an abstract class that cannot be directly instantiated and enforcing implementation in subclasses."
        ),
        (
            "What is an abstract class in C++?",
            "An abstract class is a class that cannot be instantiated directly.",
            "An abstract class in C++ contains at least one pure virtual function and serves as an interface for child classes.",
            "An abstract class is a class designed specifically to act as a foundational base class, containing at least one pure virtual function, which mandates that derived concrete classes provide full implementations."
        ),
        (
            "What is the Standard Template Library (STL) in C++?",
            "The STL is a built-in library of template classes and algorithms.",
            "The C++ STL provides ready-to-use data structures like vectors and maps along with algorithms like sorting and searching.",
            "The Standard Template Library (STL) is a rich collection of generic C++ template classes and functions categorized into containers (vector, list, map), iterators, and algorithms (sort, search, transform)."
        ),
        (
            "What is a destructor in C++?",
            "A destructor cleans up an object when it is destroyed.",
            "A destructor is a special member function prefixed with a tilde (~) that runs automatically when an object goes out of scope.",
            "A destructor is a special member function named `~ClassName()` that is invoked automatically when an object's lifetime ends, responsible for releasing acquired heap memory, file handles, and system resources."
        ),
        (
            "What is RAII in C++?",
            "RAII ties resource management to object lifetime.",
            "Resource Acquisition Is Initialization (RAII) binds resource allocation to constructor execution and deallocation to the destructor.",
            "RAII (Resource Acquisition Is Initialization) is a core C++ design idiom where resources (memory, sockets, mutexes) are acquired during object construction and automatically released during destruction when exiting scope."
        ),
        (
            "What is a smart pointer in C++?",
            "A smart pointer automatically manages heap memory.",
            "A smart pointer is an object that wraps a raw pointer and automatically deallocates memory when no longer referenced.",
            "Smart pointers (such as `std::unique_ptr`, `std::shared_ptr`, and `std::weak_ptr` introduced in C++11) wrap raw pointers within RAII semantics to provide automatic, exception-safe heap memory management."
        ),
        (
            "What is the difference between stack and heap memory in C++?",
            "Stack memory is automatic and fast; heap memory is manual and dynamic.",
            "Stack memory handles local variables automatically with fast allocation, while heap memory is dynamically allocated at runtime and managed manually.",
            "Stack memory is a contiguous memory region managed automatically by CPU architecture for function call frames and local variables, whereas heap memory is a large pool of dynamic storage allocated at runtime via pointers."
        )
    ],
    "Java": [
        (
            "What is Java?",
            "Java is a popular object-oriented programming language.",
            "Java is a class-based, object-oriented programming language designed to have minimal implementation dependencies.",
            "Java is a high-level, class-based, object-oriented programming language developed by Sun Microsystems under the 'Write Once, Run Anywhere' (WORA) principle, executing via bytecode on any Java Virtual Machine."
        ),
        (
            "What is the difference between JDK, JRE, and JVM?",
            "JDK is for development, JRE is for running apps, and JVM executes bytecode.",
            "JDK is the complete development kit, JRE provides the libraries to run Java apps, and JVM executes the compiled bytecode.",
            "The JDK (Java Development Kit) includes compilers and debugging tools; the JRE (Java Runtime Environment) bundles libraries and the JVM; and the JVM (Java Virtual Machine) interprets or JIT-compiles bytecode into native machine code."
        ),
        (
            "Why is Java called platform independent?",
            "Java is platform independent because it compiles to bytecode that runs on any JVM.",
            "Java code compiles into bytecode instead of machine code, allowing it to execute on any operating system with a JVM.",
            "Java achieves platform independence because the Java compiler converts source code into architecture-neutral bytecode (.class files), which any platform-specific Java Virtual Machine can execute without recompilation."
        ),
        (
            "What is the JIT compiler in Java?",
            "The JIT compiler compiles bytecode to machine code at runtime for speed.",
            "The Just-In-Time (JIT) compiler inside the JVM converts frequently executed bytecode into native machine code to optimize performance.",
            "The Just-In-Time (JIT) compiler is a component of the JVM that analyzes bytecode during execution and compiles hotspot code blocks directly into native machine instructions, dramatically accelerating execution speed."
        ),
        (
            "What is garbage collection in Java?",
            "Garbage collection automatically frees unused memory.",
            "Java Garbage Collection is an automatic memory management process that cleans up unreferenced objects from the heap.",
            "Garbage collection is an autonomous JVM process that tracks object references on the heap and deallocates memory occupied by unreachable objects, eliminating manual memory deallocation errors."
        ),
        (
            "What is the difference between == and equals() in Java?",
            "== checks reference identity; equals() checks value equality.",
            "The `==` operator compares memory addresses of objects, while the `.equals()` method compares the actual contents or values.",
            "In Java, `==` compares primitive values or tests whether two object references point to the exact same memory location, while `.equals()` is a method meant to be overridden to compare logical equality of object state."
        ),
        (
            "What is a String pool in Java?",
            "The String pool is a storage area in the heap for cached string literals.",
            "The String Constant Pool is a special memory region in the Java heap that caches unique string literals to save memory.",
            "The String Constant Pool is a dedicated memory space within the Java heap where string literals are stored; when a duplicate literal is created, Java returns the existing reference instead of allocating a new object."
        ),
        (
            "Why are Strings immutable in Java?",
            "Strings are immutable for security, synchronization, and caching.",
            "Strings cannot be changed after creation in Java to ensure thread safety, security, and string pool optimization.",
            "Strings are immutable in Java to protect security parameters (such as network connections and file paths), facilitate safe multi-threaded sharing without synchronization, and enable string pool caching."
        ),
        (
            "What is the difference between String, StringBuilder, and StringBuffer?",
            "String is immutable, StringBuilder is fast and non-thread-safe, and StringBuffer is thread-safe.",
            "String is immutable, StringBuilder is mutable and faster for single threads, while StringBuffer is mutable and synchronized for multi-threading.",
            "`String` creates immutable objects; `StringBuilder` creates mutable character sequences optimized for single-threaded performance; and `StringBuffer` provides thread-safe mutable sequences through synchronized methods."
        ),
        (
            "What is the static keyword in Java?",
            "Static belongs to the class rather than individual instances.",
            "The `static` keyword means a variable or method belongs to the class itself rather than to individual object instances.",
            "In Java, the `static` keyword denotes members (variables, methods, blocks, or nested classes) that belong to the class globally, shared across all instances and accessible without creating an object."
        ),
        (
            "What is method overloading in Java?",
            "Method overloading is defining methods with the same name but different parameters.",
            "Method overloading allows a class to have multiple methods with the exact same name as long as their parameter lists differ.",
            "Method overloading is compile-time polymorphism in Java where a single class defines multiple methods sharing the same identifier but differing in parameter count, order, or data types."
        ),
        (
            "What is method overriding in Java?",
            "Method overriding is redefining a parent method in a child class.",
            "Method overriding occurs when a subclass provides a specific implementation of a method already declared in its parent class.",
            "Method overriding is runtime polymorphism in Java where a subclass provides a concrete implementation of an inherited non-static method having the identical signature, return type, and visibility as in the superclass."
        ),
        (
            "What is an abstract class in Java?",
            "An abstract class is a class that cannot be directly instantiated.",
            "An abstract class in Java is declared with the `abstract` keyword and can contain both abstract and concrete methods.",
            "An abstract class in Java serves as a partial template that cannot be instantiated directly, capable of defining both abstract methods (to be implemented by subclasses) and fully implemented concrete methods."
        ),
        (
            "What is an interface in Java?",
            "An interface is a contract containing method blueprints.",
            "An interface in Java is an abstract type used to specify behavior that implementing classes must define.",
            "An interface is a reference type in Java that defines a contract of method declarations (and default/static methods since Java 8) that any implementing class must satisfy, supporting multiple inheritance of type."
        ),
        (
            "What is the difference between an abstract class and an interface in Java?",
            "Abstract classes can have state and constructors; interfaces define contracts and support multiple implementation.",
            "A class can extend only one abstract class but can implement multiple interfaces; abstract classes can have instance variables and constructors.",
            "An abstract class allows stateful instance variables, constructors, and access modifiers with single inheritance, whereas an interface supports multiple inheritance of behavior, having public abstract methods by default."
        ),
        (
            "What is the final keyword in Java?",
            "Final makes variables unchangeable, methods un-overridable, and classes un-extendable.",
            "In Java, a final variable cannot be reassigned, a final method cannot be overridden, and a final class cannot be inherited.",
            "The `final` modifier enforces immutability and restrictions: final variables cannot be reassigned after initialization, final methods cannot be overridden by subclasses, and final classes cannot be extended."
        ),
        (
            "What is exception handling in Java?",
            "Exception handling manages runtime errors using try-catch blocks.",
            "Exception handling is a mechanism in Java that catches runtime errors using try, catch, finally, throw, and throws to keep the app running.",
            "Exception handling is a robust Java framework using an object hierarchy rooted at `Throwable` (checked and unchecked exceptions) to intercept runtime failures gracefully via `try-catch-finally` constructs."
        ),
        (
            "What is the difference between checked and unchecked exceptions in Java?",
            "Checked exceptions are verified at compile time; unchecked exceptions occur at runtime.",
            "Checked exceptions (like IOException) must be handled or declared in the method signature, while unchecked exceptions (like NullPointerException) happen at runtime.",
            "Checked exceptions inherit from `Exception` (excluding `RuntimeException`) and are checked by the compiler requiring mandatory handling, whereas unchecked exceptions inherit from `RuntimeException` and occur during execution."
        ),
        (
            "What is the finally block in Java?",
            "The finally block always runs whether an exception occurs or not.",
            "A `finally` block is placed after try-catch to execute cleanup code like closing connections regardless of whether an exception was thrown.",
            "The `finally` block in Java guarantees execution of vital cleanup routines (such as closing database connections or file streams) after the `try` and `catch` blocks complete, even if an unhandled exception or return occurs."
        ),
        (
            "What is the Java Collections Framework?",
            "The Collections Framework is a set of classes and interfaces for storing data.",
            "The Java Collections Framework provides standardized data structures like List, Set, and Map along with utility algorithms.",
            "The Java Collections Framework is a unified architecture representing and manipulating data collections, including core interfaces (`Collection`, `List`, `Set`, `Queue`, `Map`) and concrete implementations (`ArrayList`, `HashSet`, `HashMap`)."
        ),
        (
            "What is the difference between ArrayList and LinkedList in Java?",
            "ArrayList uses a dynamic array; LinkedList uses a doubly-linked list.",
            "ArrayList is faster for random access via index, while LinkedList is faster for inserting and removing elements in the middle.",
            "`ArrayList` is backed by a resizable contiguous array offering fast O(1) random access but slower O(n) element shifting on middle insertions, while `LinkedList` uses doubly-linked nodes allowing fast O(1) node insertion once positioned."
        ),
        (
            "What is a HashMap in Java?",
            "A HashMap stores key-value pairs using hashing.",
            "HashMap is a collection class in Java that stores key-value pairs with fast average lookup time using hash codes.",
            "A `HashMap` is an associative collection implemented via an array of linked buckets (or red-black trees in Java 8+) that hashes keys to determine bucket positions, providing average O(1) time complexity for get and put operations."
        ),
        (
            "What is multithreading in Java?",
            "Multithreading is running multiple threads concurrently.",
            "Multithreading allows a Java program to execute two or more threads concurrently for maximum CPU utilization.",
            "Multithreading is a concurrent execution feature in Java where multiple lightweight sub-processes (threads) execute independently within a shared memory process space, implemented via `Thread` or `Runnable`."
        ),
        (
            "What is synchronization in Java?",
            "Synchronization prevents multiple threads from accessing shared resources simultaneously.",
            "Synchronization in Java ensures that only one thread can access a shared block of code or resource at a time.",
            "Synchronization uses monitor locks and the `synchronized` keyword to control concurrent thread access to critical sections, preventing race conditions and ensuring data consistency across shared memory."
        ),
        (
            "What are Generics in Java?",
            "Generics allow classes and methods to operate on specified types safely.",
            "Generics enable you to create classes, interfaces, and methods with type parameters, catching type errors at compile time.",
            "Generics introduce compile-time type safety to the Java language by allowing types (classes and interfaces) to be parameterized, eliminating explicit type casting and catching class cast exceptions before runtime."
        )
    ],
    "OOP": [
        (
            "What is Object-Oriented Programming (OOP)?",
            "OOP is a programming model organized around objects.",
            "OOP is a programming paradigm that organizes software design around objects containing data and behaviors.",
            "Object-Oriented Programming (OOP) is a development paradigm that models real-world entities into modular software objects that bundle data attributes (state) with methods (behavior)."
        ),
        (
            "What are the four pillars of OOP?",
            "Encapsulation, Abstraction, Inheritance, and Polymorphism.",
            "The four foundational principles of OOP are Encapsulation, Abstraction, Inheritance, and Polymorphism.",
            "The four cornerstones of Object-Oriented Programming are Encapsulation (data hiding), Abstraction (hiding complexity), Inheritance (code reuse), and Polymorphism (multiple forms of behavior)."
        ),
        (
            "What is a class in OOP?",
            "A class is a blueprint for creating objects.",
            "A class is a user-defined template that defines the properties and methods that its objects will have.",
            "A class is an extensible program-code-template for creating objects, providing initial values for state (member variables) and implementations of behavior (member functions or methods)."
        ),
        (
            "What is an object in OOP?",
            "An object is an instance of a class.",
            "An object is a self-contained entity created from a class blueprint that contains actual data and behaviors.",
            "An object is a concrete runtime instance of a class that occupies physical memory, possessing a specific state defined by its attributes and exhibiting behaviors defined by its class methods."
        ),
        (
            "What is encapsulation?",
            "Encapsulation is bundling data and restricting direct access to it.",
            "Encapsulation is the practice of bundling data with methods and hiding internal state using private variables and public getters/setters.",
            "Encapsulation is an OOP principle that packages fields and related methods within a class while restricting direct external access to internal implementation details using access modifiers (private, protected)."
        ),
        (
            "What is abstraction in OOP?",
            "Abstraction is hiding complex implementation and showing only essentials.",
            "Abstraction means displaying only essential features of an object to the outside world while hiding the internal details.",
            "Abstraction is an architectural principle that hides complex background mechanics and exposes only relevant, high-level operational interfaces to the user, typically implemented using abstract classes and interfaces."
        ),
        (
            "What is the difference between encapsulation and abstraction?",
            "Encapsulation hides data; abstraction hides complexity.",
            "Encapsulation focuses on wrapping data safely and controlling access, whereas abstraction focuses on exposing what an object does rather than how it does it.",
            "Encapsulation is about information hiding and containment (keeping state private and safe), while abstraction is about design simplification (exposing an interface while concealing underlying operational complexity)."
        ),
        (
            "What is inheritance in OOP?",
            "Inheritance allows a child class to inherit properties from a parent class.",
            "Inheritance is an OOP mechanism where a new class adopts fields and methods from an existing class to promote code reuse.",
            "Inheritance is a hierarchical relationship mechanism where a subclass inherits fields, methods, and behaviors from a superclass, fostering code reuse and establishing an 'is-a' relationship."
        ),
        (
            "What are the types of inheritance?",
            "Single, multiple, multilevel, hierarchical, and hybrid inheritance.",
            "Common inheritance types include single, multilevel, hierarchical, multiple, and hybrid inheritance.",
            "Inheritance structures include Single (one parent to one child), Multilevel (chained derivation), Hierarchical (one parent to many children), Multiple (multiple parents to one child), and Hybrid (combination of models)."
        ),
        (
            "Why does Java not support multiple inheritance with classes?",
            "To avoid ambiguity like the Diamond Problem.",
            "Java disallows multiple class inheritance to prevent conflicting method implementations from multiple parents, known as the Diamond Problem.",
            "Java forbids multiple inheritance of classes to prevent the architectural ambiguity of the Diamond Problem, where a subclass inherits conflicting implementations of the same method from two different parent classes."
        ),
        (
            "What is polymorphism in OOP?",
            "Polymorphism allows one entity to take multiple forms.",
            "Polymorphism is the ability of a method or object to behave differently based on the context or object calling it.",
            "Polymorphism (meaning 'many forms') allows objects of different types to respond to the same interface or method call in their own specialized manner, divided into compile-time and runtime polymorphism."
        ),
        (
            "What is compile-time polymorphism?",
            "Compile-time polymorphism is resolved during compilation, like method overloading.",
            "Compile-time (static) polymorphism happens when the compiler determines which method to call based on signatures, such as method overloading.",
            "Compile-time polymorphism (static binding) is resolved during the compilation phase where method execution is bound to declarations based on argument types and count, as seen in method and operator overloading."
        ),
        (
            "What is runtime polymorphism?",
            "Runtime polymorphism is resolved during execution, like method overriding.",
            "Runtime (dynamic) polymorphism occurs when a subclass overrides a parent method and the exact method call is resolved at runtime.",
            "Runtime polymorphism (dynamic method dispatch) is resolved during program execution when an overridden method invocation on a superclass reference executes the implementation of the actual instantiated subclass object."
        ),
        (
            "What is a constructor in OOP?",
            "A constructor is a special method that initializes an object.",
            "A constructor is a member function called automatically when an object is created to set up its initial values.",
            "A constructor is a specialized class method bearing the same name as the class that is automatically invoked upon memory allocation to initialize an object's instance variables and dependencies."
        ),
        (
            "What is constructor overloading?",
            "Constructor overloading is having multiple constructors with different parameters.",
            "Constructor overloading allows a class to have more than one constructor with different parameter lists to initialize objects in various ways.",
            "Constructor overloading is a technique of defining multiple constructors within the same class differing in argument count or types, providing flexible options for object initialization."
        ),
        (
            "What is a copy constructor?",
            "A copy constructor creates a new object as a copy of an existing one.",
            "A copy constructor initializes a new object using the values of another existing object of the same class.",
            "A copy constructor is an overloaded constructor that accepts a reference to an existing object of the identical class to instantiate a separate object with duplicated attribute states."
        ),
        (
            "What is the super or base keyword in OOP?",
            "Super refers to the immediate parent class.",
            "The `super` keyword is used in a child class to call constructors or methods of its parent class.",
            "The `super` (or `base` in C#) reference keyword allows a derived subclass to explicitly access overridden methods, accessible properties, or invoked constructors of its immediate superclass."
        ),
        (
            "What is method overriding?",
            "Method overriding is redefining an inherited method in a child class.",
            "Method overriding occurs when a subclass provides its own specific logic for a method inherited from its parent class.",
            "Method overriding is a feature where a derived class provides a customized implementation of a method defined in its base class with an identical name, parameters, and return type, supporting dynamic polymorphism."
        ),
        (
            "What is the difference between composition and inheritance?",
            "Inheritance is an 'is-a' relationship; composition is a 'has-a' relationship.",
            "Inheritance derives a new class from an existing class, while composition builds a class by including objects of other classes.",
            "Inheritance establishes a tight 'is-a' structural coupling between parent and child classes, whereas composition creates a flexible 'has-a' relationship by containing references to independent helper objects."
        ),
        (
            "What is coupling in software design?",
            "Coupling measures how dependent classes are on each other.",
            "Coupling is the degree of interdependence between different software modules; low coupling is preferred.",
            "Coupling denotes the extent to which one module or class relies on the knowledge or internal workings of another, where loose coupling minimizes ripple effects when changing code."
        ),
        (
            "What is cohesion in OOP?",
            "Cohesion measures how focused a class is on a single purpose.",
            "Cohesion refers to how closely related and focused the responsibilities inside a single class or module are; high cohesion is preferred.",
            "Cohesion evaluates the degree to which elements within a class or module belong together functionally, where high cohesion signifies a class with a single, tightly defined responsibility."
        ),
        (
            "What are access modifiers in OOP?",
            "Access modifiers set the visibility of classes and members.",
            "Access modifiers (public, private, protected) control which parts of a program can view or call a class and its members.",
            "Access modifiers are language keywords that enforce encapsulation by specifying the accessibility scope of classes, variables, and methods across packages and inheritance hierarchies."
        ),
        (
            "What does the private access modifier do?",
            "Private restricts access to within the same class only.",
            "The `private` modifier ensures that members are accessible only within the class where they are declared.",
            "The `private` keyword provides the highest level of encapsulation restriction, ensuring that members cannot be directly read or called by any outside class or subclass."
        ),
        (
            "What does the protected access modifier do?",
            "Protected allows access within the same package and by subclasses.",
            "The `protected` modifier makes members accessible inside the declaring class, its package, and any derived child classes.",
            "The `protected` access specifier permits member access within the declaring class, any derived child classes regardless of package, and other classes residing within the same package."
        ),
        (
            "What are the SOLID principles in OOP?",
            "SOLID is a set of five design principles for maintainable software.",
            "SOLID stands for Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion.",
            "SOLID represents five foundational object-oriented design principles formulated by Robert C. Martin to create robust, decoupled, easily maintainable, and extensible software systems."
        )
    ],
    "Data Structures": [
        (
            "What is a data structure?",
            "A data structure is a way of organizing and storing data.",
            "A data structure is a specialized format for organizing, storing, and managing data efficiently in a computer.",
            "A data structure is a specialized organizational model designed to store, access, and manipulate data efficiently according to specific algorithmic constraints and time-space tradeoffs."
        ),
        (
            "What is the difference between linear and non-linear data structures?",
            "Linear structures arrange data sequentially; non-linear structures arrange data hierarchically.",
            "In linear data structures (arrays, lists) elements form a single sequence, whereas in non-linear structures (trees, graphs) elements connect in branching relationships.",
            "Linear data structures store elements sequentially with single predecessors and successors (arrays, stacks, queues), while non-linear data structures store elements hierarchically or interconnectedly (trees, graphs)."
        ),
        (
            "What is an array?",
            "An array is a collection of elements stored in contiguous memory.",
            "An array is a linear data structure storing fixed-size elements of the same data type in sequential memory locations.",
            "An array is a foundational indexed collection of elements of identical data types allocated in contiguous memory blocks, offering O(1) random access via index arithmetic."
        ),
        (
            "What are the advantages and disadvantages of arrays?",
            "Arrays have fast access but fixed size.",
            "Arrays provide instant O(1) element access by index, but have fixed capacity and costly insertions and deletions.",
            "Advantages of arrays include constant-time O(1) random lookup and cache friendliness; disadvantages include fixed allocation limits and O(n) element shifting during insertions and deletions."
        ),
        (
            "What is a Linked List?",
            "A linked list is a sequence of nodes connected by pointers.",
            "A linked list is a linear data structure where each node stores a data element and a pointer reference to the next node.",
            "A linked list is a dynamic linear data structure composed of nodes containing payload data and one or more pointer references to adjacent nodes, supporting dynamic sizing without contiguous memory allocation."
        ),
        (
            "What is the difference between an Array and a Linked List?",
            "Arrays have fixed contiguous memory; linked lists have dynamic scattered memory.",
            "Arrays allow instant index lookup but have fixed size, while linked lists grow dynamically but require traversing nodes sequentially.",
            "Arrays use contiguous memory providing O(1) random access but static resizing, whereas linked lists use non-contiguous heap nodes providing dynamic resizing and O(1) head insertion but O(n) sequential access."
        ),
        (
            "What is a Doubly Linked List?",
            "A doubly linked list has pointers to both the next and previous nodes.",
            "A doubly linked list is a linked list where each node holds references to both its successor and predecessor nodes.",
            "A doubly linked list is a linear data structure where each node contains data along with two directional pointers: one to the next node and one to the previous node, enabling bidirectional traversal."
        ),
        (
            "What is a Stack?",
            "A stack is a Last-In, First-Out (LIFO) data structure.",
            "A stack is a linear collection where elements are added and removed from only one end, following LIFO order.",
            "A stack is an abstract data type adhering to the Last-In First-Out (LIFO) principle, supporting primary operations `push` (insert), `pop` (remove), and `peek` (inspect) exclusively at the top element."
        ),
        (
            "What are real-world examples of a Stack?",
            "Undo operations, call stacks, and browser back buttons.",
            "Common uses of a stack include undo-redo in text editors, browser history navigation, and function call execution stacks.",
            "Real-world applications of stacks include compiler syntax parsing, call stack maintenance during recursion, browser back-forward page tracking, and multi-level undo operations in graphical software."
        ),
        (
            "What is a Queue?",
            "A queue is a First-In, First-Out (FIFO) data structure.",
            "A queue is a linear collection where elements are added at the rear and removed from the front, following FIFO order.",
            "A queue is an abstract linear data structure operating under the First-In First-Out (FIFO) rule, inserting elements at the back (enqueue) and removing them from the front (dequeue)."
        ),
        (
            "What is a Circular Queue?",
            "A circular queue connects the last position back to the first.",
            "A circular queue is a linear queue where the last memory slot connects back to the first to reuse freed space.",
            "A circular queue is an optimized ring buffer implementation of a queue that wraps the rear pointer to the beginning of the array using modulo arithmetic, preventing memory waste in fixed-size buffers."
        ),
        (
            "What is a Priority Queue?",
            "A priority queue serves elements based on priority rather than arrival order.",
            "A priority queue is an abstract data structure where each item has a priority value, and higher-priority items are dequeued first.",
            "A priority queue is a specialized queue container where every element is assigned a priority rating, ensuring that the highest-priority item is dequeued before lower-priority items, commonly implemented with heaps."
        ),
        (
            "What is a Hash Table?",
            "A hash table maps keys to values using a hash function.",
            "A hash table is a data structure that uses a hash function to map keys to bucket indexes for rapid lookups.",
            "A hash table is an associative data structure that computes an integer hash code from keys to index into an array of buckets, offering average O(1) time complexity for insert, search, and delete operations."
        ),
        (
            "What is a hash collision and how is it resolved?",
            "A collision occurs when two keys produce the same hash; it is resolved with chaining or open addressing.",
            "A collision happens when different keys generate the same bucket index, solved using techniques like separate chaining or open addressing.",
            "A hash collision occurs when a hash function maps two distinct keys to the same bucket index; it is resolved via separate chaining (storing colliding nodes in linked lists) or open addressing (linear/quadratic probing)."
        ),
        (
            "What is a Tree data structure?",
            "A tree is a non-linear hierarchical data structure of connected nodes.",
            "A tree is a hierarchical collection of nodes starting with a root node where each node connects to child nodes.",
            "A tree is an acyclic, connected, non-linear data structure comprising a root node, child nodes, and connecting edges, organizing data into hierarchical parent-child relationships."
        ),
        (
            "What is a Binary Tree?",
            "A binary tree is a tree where each node has at most two children.",
            "A binary tree is a hierarchical structure where every parent node has a maximum of two child nodes, called left and right.",
            "A binary tree is a specialized tree data structure where each node possesses at most two child references, designated as the left child and the right child."
        ),
        (
            "What is a Binary Search Tree (BST)?",
            "A BST is a binary tree where left children are smaller and right children are larger.",
            "A Binary Search Tree is a binary tree where left child values are less than the parent and right child values are greater.",
            "A Binary Search Tree (BST) is an ordered binary tree where the key in any node is strictly greater than all keys in its left subtree and strictly less than all keys in its right subtree, enabling O(log n) average lookups."
        ),
        (
            "What are tree traversals?",
            "Tree traversals are methods to visit every node in a tree.",
            "Tree traversal refers to visiting all nodes in a tree, commonly using Inorder, Preorder, Postorder, or Level-order traversal.",
            "Tree traversals are systematic algorithmic processes for visiting each node in a tree exactly once, divided into depth-first (Inorder: L-Root-R, Preorder: Root-L-R, Postorder: L-R-Root) and breadth-first (Level-order)."
        ),
        (
            "What is a Graph data structure?",
            "A graph is a collection of vertices connected by edges.",
            "A graph is a non-linear data structure consisting of nodes (vertices) and lines (edges) connecting pairs of vertices.",
            "A graph is a mathematical network data structure $G = (V, E)$ consisting of a set of vertices $V$ interconnected by directed or undirected, weighted or unweighted edges $E$."
        ),
        (
            "What is the difference between BFS and DFS?",
            "BFS explores level by level; DFS explores as deep as possible first.",
            "Breadth-First Search (BFS) visits neighbor nodes layer by layer using a queue, while Depth-First Search (DFS) dives deep along each branch using a stack.",
            "BFS traverses graph nodes level-by-level using a queue (finding shortest paths in unweighted graphs), while DFS explores as far as possible along each branch before backtracking, implemented recursively or via a stack."
        ),
        (
            "What is a Heap?",
            "A heap is a specialized complete binary tree satisfying the heap property.",
            "A heap is a complete binary tree where parent nodes are either always greater than (Max-Heap) or smaller than (Min-Heap) their children.",
            "A heap is a tree-based data structure satisfying the complete binary tree property and the heap order invariant: in a Min-Heap, parent values are <= children; in a Max-Heap, parent values are >= children."
        ),
        (
            "What is Big-O notation?",
            "Big-O notation measures the performance and scalability of an algorithm.",
            "Big-O notation describes the worst-case time or space complexity of an algorithm as the input size grows.",
            "Big-O notation is a mathematical asymptotic metric that classifies algorithms by their upper-bound computational complexity, describing how runtime or memory requirements scale with input size $n$."
        ),
        (
            "What is O(1) time complexity?",
            "O(1) means constant time regardless of input size.",
            "O(1) indicates that an operation takes the same amount of time to execute no matter how large the input dataset is.",
            "Constant time complexity $O(1)$ signifies an algorithm whose execution time remains invariant and unaffected by the growth of input size $n$, such as indexing an array or pushing onto a stack."
        ),
        (
            "What is O(n) time complexity?",
            "O(n) means linear time that grows directly with input size.",
            "O(n) indicates that an algorithm's execution time increases proportionally to the number of elements in the input.",
            "Linear time complexity $O(n)$ describes an algorithmic process where running time scales in direct proportion to input size $n$, such as a linear scan through an unsorted array."
        ),
        (
            "What is the time complexity of binary search?",
            "Binary search has O(log n) time complexity.",
            "Binary search takes logarithmic time, O(log n), because it cuts the search space in half with every comparison.",
            "Binary search operates with O(log n) time complexity on sorted arrays by repeatedly halving the active search interval, requiring at most log2(n) iterations to locate an element or determine its absence."
        )
    ],
    "Database & SQL": [
        (
            "What is a database?",
            "A database is an organized collection of stored data.",
            "A database is a structured electronic system for storing, managing, and retrieving data efficiently.",
            "A database is an organized, systematically managed digital repository of structured or semi-structured data accessed and manipulated electronically through a Database Management System (DBMS)."
        ),
        (
            "What is a DBMS?",
            "A DBMS is software used to manage databases.",
            "A Database Management System (DBMS) is software that enables users to create, maintain, query, and secure databases.",
            "A Database Management System (DBMS) is system software that controls the creation, maintenance, querying, and access authorization of databases, ensuring data integrity, concurrency, and durability."
        ),
        (
            "What is an RDBMS?",
            "An RDBMS is a relational database management system using tables.",
            "An RDBMS is a database system that stores data in related tables of rows and columns, like MySQL or PostgreSQL.",
            "A Relational Database Management System (RDBMS) is a database model based on relational theory that organizes data into tables (relations) with rows (tuples) and columns (attributes), enforcing integrity constraints."
        ),
        (
            "What is SQL?",
            "SQL is the standard language for relational databases.",
            "Structured Query Language (SQL) is the standard programming language used to communicate with and manipulate relational databases.",
            "Structured Query Language (SQL) is an ANSI/ISO standard declarative language used to define schemas, insert, update, query, and administer relational database management systems."
        ),
        (
            "What is the difference between SQL and NoSQL?",
            "SQL databases are relational and tabular; NoSQL databases are non-relational and flexible.",
            "SQL databases use structured tables and predefined schemas, while NoSQL databases store data in flexible formats like JSON documents, key-values, or graphs.",
            "SQL databases are relational, schema-enforced, vertically scalable systems adhering to ACID properties, while NoSQL databases are distributed, schema-flexible, horizontally scalable systems (document, key-value, column, graph)."
        ),
        (
            "What is a primary key?",
            "A primary key uniquely identifies each record in a table.",
            "A primary key is a column or set of columns that uniquely identifies every row in a table and cannot contain null values.",
            "A primary key is a relational constraint applied to one or more table attributes that uniquely identifies each tuple in the relation, strictly enforcing uniqueness and disallowing NULL values."
        ),
        (
            "What is a foreign key?",
            "A foreign key links a record to the primary key of another table.",
            "A foreign key is a table column that references the primary key of another table to establish a relationship between them.",
            "A foreign key is a referential constraint in a relational table that matches the primary key of another table, ensuring referential integrity by preventing orphaned records."
        ),
        (
            "What are the different types of SQL commands?",
            "DDL, DML, DQL, DCL, and TCL.",
            "SQL commands are categorized into DDL (structure), DML (data modification), DQL (querying), DCL (permissions), and TCL (transactions).",
            "SQL commands comprise Data Definition Language (DDL: CREATE, ALTER), Data Manipulation Language (DML: INSERT, UPDATE, DELETE), Data Query Language (DQL: SELECT), Data Control Language (DCL: GRANT, REVOKE), and Transaction Control Language (TCL: COMMIT, ROLLBACK)."
        ),
        (
            "What is the difference between DROP, TRUNCATE, and DELETE?",
            "DROP deletes the table, TRUNCATE removes all rows quickly, and DELETE removes rows with conditions.",
            "DROP removes the whole table structure, TRUNCATE empties all table data without logging every row, and DELETE deletes specified rows and can be rolled back.",
            "`DROP` removes both the table data and schema definition; `TRUNCATE` rapidly deallocates all data pages resetting identity seeds without logging individual row deletions; `DELETE` is a DML statement that removes rows matching a WHERE filter with full transaction logging."
        ),
        (
            "What is a JOIN in SQL?",
            "A JOIN combines rows from two or more tables based on a related column.",
            "A JOIN clause is used in SQL to retrieve and combine related data from multiple tables based on common matching columns.",
            "An SQL JOIN is an operation that correlates tuples from two or more relational tables by evaluating predicate conditions across shared keys, returning a unified tabular result set."
        ),
        (
            "What are the different types of JOINs in SQL?",
            "INNER, LEFT, RIGHT, and FULL OUTER JOIN.",
            "SQL supports INNER JOIN (matching rows), LEFT JOIN (all left rows), RIGHT JOIN (all right rows), and FULL JOIN (all rows from both).",
            "Relational JOINs include INNER JOIN (only intersecting matches), LEFT OUTER JOIN (all left rows plus matching right rows), RIGHT OUTER JOIN (all right rows plus matching left rows), and FULL OUTER JOIN (all records from both tables matching when possible)."
        ),
        (
            "What is database normalization?",
            "Normalization is organizing data to reduce redundancy.",
            "Normalization is the process of structuring a database schema to eliminate data redundancy and prevent anomalies.",
            "Database normalization is a systematic design technique that decomposes complex relations into smaller, well-structured tables adhering to normal forms (1NF through BCNF/5NF) to minimize redundancy and eliminate insert, update, and delete anomalies."
        ),
        (
            "What is First Normal Form (1NF)?",
            "1NF requires atomic values and unique records.",
            "A table is in 1NF if every column holds only atomic (indivisible) values and each record is unique.",
            "First Normal Form (1NF) mandates that every attribute of a relation contains only atomic, indivisible scalar values with no repeating groups or nested arrays, and that each row is uniquely identifiable by a primary key."
        ),
        (
            "What is Second Normal Form (2NF)?",
            "2NF is in 1NF and removes partial dependencies on composite keys.",
            "A table is in 2NF if it satisfies 1NF and all non-key columns depend entirely on the full primary key.",
            "Second Normal Form (2NF) requires a relation to be in 1NF with all non-prime attributes fully functionally dependent on the complete primary key, eliminating partial key dependencies in composite primary keys."
        ),
        (
            "What is Third Normal Form (3NF)?",
            "3NF is in 2NF and eliminates transitive dependencies.",
            "A table is in 3NF if it meets 2NF and no non-key column depends on another non-key column.",
            "Third Normal Form (3NF) requires a relation to be in 2NF with no transitive functional dependencies, meaning no non-prime attribute depends on another non-prime attribute (every determinant must be a candidate key)."
        ),
        (
            "What are ACID properties in databases?",
            "Atomicity, Consistency, Isolation, and Durability.",
            "ACID properties guarantee that database transactions are processed reliably: Atomicity, Consistency, Isolation, and Durability.",
            "ACID represents four fundamental guarantees for database transactions: Atomicity (all-or-nothing), Consistency (state validity), Isolation (concurrency control), and Durability (permanent persistence upon commit)."
        ),
        (
            "What is a database transaction?",
            "A transaction is a single logical unit of database work.",
            "A transaction is a sequence of one or more SQL operations treated as a single indivisible unit of work.",
            "A database transaction is a discrete unit of database execution comprising one or more read and write operations that must succeed completely or be rolled back entirely to maintain data consistency."
        ),
        (
            "What is an index in a database?",
            "An index is a lookup structure that speeds up query retrieval.",
            "An index is a database data structure that allows the database engine to find specific rows much faster without scanning the entire table.",
            "A database index is an auxiliary data structure (typically a B-Tree or Hash index) created on table columns that accelerates data retrieval queries at the expense of additional storage and slower write operations."
        ),
        (
            "What is the difference between a clustered and non-clustered index?",
            "A clustered index defines physical row order; a non-clustered index creates a separate lookup pointer.",
            "A clustered index determines the physical order of data rows in the table, while a non-clustered index is a separate structure pointing to the actual data.",
            "A clustered index dictates the actual physical sorting order of table data on disk (only one permitted per table), whereas a non-clustered index maintains an independent B-Tree whose leaf nodes point to the physical row locations."
        ),
        (
            "What is a database view?",
            "A view is a virtual table based on a SQL query.",
            "A view is a saved SELECT query that acts as a virtual table without storing the data physically.",
            "A view is a virtual database table defined by a stored SQL query expression that presents data from one or more underlying tables dynamically without duplicating physical data storage."
        ),
        (
            "What is a stored procedure?",
            "A stored procedure is a saved, reusable batch of SQL statements.",
            "A stored procedure is a prepared SQL code block stored on the database server that can be called repeatedly.",
            "A stored procedure is a precompiled collection of SQL statements and procedural logic stored directly within the database management system, executed by application calls to improve performance and security."
        ),
        (
            "What is a database trigger?",
            "A trigger is an automated SQL action executed on table events.",
            "A trigger is a stored program that runs automatically in response to INSERT, UPDATE, or DELETE events on a table.",
            "A database trigger is a procedural block of code that fires automatically in response to specified Data Manipulation Language (DML) events on a given table, commonly used for audit logging and complex constraint enforcement."
        ),
        (
            "What is the difference between WHERE and HAVING clauses in SQL?",
            "WHERE filters individual rows; HAVING filters aggregated groups.",
            "The WHERE clause filters rows before grouping, whereas the HAVING clause filters groups created by GROUP BY.",
            "The `WHERE` clause filters individual records prior to aggregation, while the `HAVING` clause filters aggregated results produced by `GROUP BY` using aggregate functions like COUNT, SUM, or AVG."
        ),
        (
            "What is SQL injection?",
            "SQL injection is a security attack inserting malicious SQL commands into queries.",
            "SQL injection is a cyber vulnerability where an attacker inserts harmful SQL code through user inputs to manipulate the database.",
            "SQL injection (SQLi) is an input validation vulnerability where malicious SQL fragments are injected into application data inputs, allowing unauthorized execution of arbitrary queries, data tampering, or authentication bypass."
        ),
        (
            "How do you prevent SQL injection?",
            "Use parameterized queries and prepared statements.",
            "You prevent SQL injection by using prepared statements with parameterized queries, input validation, and ORM frameworks.",
            "SQL injection is mitigated by using parameterized queries and prepared statements that treat inputs strictly as literal data, avoiding dynamic string concatenation and enforcing least-privilege database user permissions."
        )
    ],
    "Operating Systems": [
        (
            "What is an Operating System?",
            "An OS is system software that manages hardware and software resources.",
            "An operating system acts as an interface between computer hardware and user applications, controlling memory, CPU, and storage.",
            "An Operating System (OS) is core system software that manages physical hardware resources, provides abstraction layers (files, processes, sockets), and offers execution environments for application programs."
        ),
        (
            "What is a process in an operating system?",
            "A process is a program in execution.",
            "A process is an active instance of a computer program loaded into memory along with its program counter, registers, and resources.",
            "A process is a dynamic program instance in execution possessing its own dedicated address space, execution state, process control block (PCB), memory segments (text, data, heap, stack), and OS resources."
        ),
        (
            "What is a thread in an operating system?",
            "A thread is a lightweight unit of execution within a process.",
            "A thread is the smallest sequence of programmed instructions that can be managed independently by an OS scheduler within a process.",
            "A thread is a lightweight execution stream within a host process that shares code, data, and open file descriptors with sibling threads while maintaining its own program counter, register set, and private call stack."
        ),
        (
            "What is the difference between a process and a thread?",
            "Processes have independent memory; threads share the memory of their process.",
            "A process is an independent program with its own memory space, while a thread is a lighter execution unit sharing memory with other threads in the same process.",
            "A process possesses an isolated virtual address space and heavy creation overhead, whereas threads exist inside a process sharing the same address space and heap, making inter-thread communication faster but susceptible to race conditions."
        ),
        (
            "What is context switching in an OS?",
            "Context switching is saving the state of a process to switch to another.",
            "Context switching is the process where the CPU saves the state of a running task and loads the saved state of another task to run it.",
            "Context switching is an OS kernel operation that preserves the execution context (registers, program counter, PCB) of an active process or thread and restores another, allowing preemptive multitasking with some CPU overhead."
        ),
        (
            "What is deadlock in an operating system?",
            "Deadlock is when processes are blocked forever waiting for each other's resources.",
            "A deadlock is a situation where two or more processes cannot proceed because each is holding a resource that another process needs.",
            "Deadlock is a concurrency failure where a set of processes are permanently blocked because each process holds a shared resource while awaiting an exclusive resource held by another process in the set."
        ),
        (
            "What are the four necessary conditions for deadlock?",
            "Mutual exclusion, hold and wait, no preemption, and circular wait.",
            "The four conditions for deadlock are Mutual Exclusion, Hold and Wait, No Preemption, and Circular Wait.",
            "Known as the Coffman conditions, deadlock requires all four simultaneously: Mutual Exclusion (exclusive access), Hold and Wait (holding while requesting), No Preemption (resources cannot be forcibly taken), and Circular Wait (cyclic dependency chain)."
        ),
        (
            "What is CPU scheduling?",
            "CPU scheduling decides which ready process gets CPU time.",
            "CPU scheduling is the operating system process that determines which task in the ready queue gets the CPU and for how long.",
            "CPU scheduling is the mechanism by which the OS kernel selects a process from the ready queue to allocate CPU execution time, balancing throughput, latency, fairness, and processor utilization."
        ),
        (
            "What are common CPU scheduling algorithms?",
            "FCFS, SJF, Round Robin, and Priority Scheduling.",
            "Common algorithms include First-Come First-Served, Shortest Job First, Round Robin, and Priority Scheduling.",
            "Standard scheduling algorithms include First-Come First-Served (FCFS), Shortest Job First (SJF), Round Robin (time quantum slicing), Priority Scheduling, and Multi-Level Feedback Queues (MLFQ)."
        ),
        (
            "What is Round Robin scheduling?",
            "Round Robin assigns a fixed time slice to each process cyclically.",
            "Round Robin is a preemptive CPU scheduling algorithm where each process is given a small fixed time slice (quantum) in turn.",
            "Round Robin is a fair, preemptive scheduling algorithm designed for time-sharing systems where every ready process is granted a fixed CPU duration (time quantum) in cyclic FIFO order."
        ),
        (
            "What is virtual memory in an OS?",
            "Virtual memory lets programs use more memory than physical RAM.",
            "Virtual memory is a memory management technique that uses hard drive space to act as additional RAM.",
            "Virtual memory is a memory management scheme that maps uniform virtual address spaces to physical RAM and secondary swap space, enabling processes to run without requiring contiguous or full physical memory residency."
        ),
        (
            "What is paging in an operating system?",
            "Paging divides memory into fixed-size blocks.",
            "Paging is a memory management scheme that divides physical memory into frames and virtual memory into pages of the same size.",
            "Paging is a non-contiguous storage allocation scheme that partitions virtual address spaces into fixed-size blocks called pages and physical RAM into frames, mapping them through a process page table."
        ),
        (
            "What is a page fault?",
            "A page fault occurs when requested data is not in physical RAM.",
            "A page fault is an interrupt raised by the hardware when a program tries to access a virtual page that is not currently loaded into RAM.",
            "A page fault is a hardware interrupt triggered by the Memory Management Unit (MMU) when a program accesses a virtual memory page not currently mapped to physical RAM, prompting the OS to retrieve it from swap storage."
        ),
        (
            "What is thrashing in an operating system?",
            "Thrashing is when the OS spends more time swapping pages than executing code.",
            "Thrashing occurs when memory is overcommitted and the system spends most of its time swapping pages in and out of disk rather than running programs.",
            "Thrashing is a state of severe resource contention where physical RAM is saturated, causing the operating system to expend excessive CPU cycles executing page fault swaps rather than productive application instructions."
        ),
        (
            "What is the difference between paging and segmentation?",
            "Paging uses fixed-size memory blocks; segmentation uses variable-size logical blocks.",
            "Paging divides memory into fixed-size pages, while segmentation divides memory into variable-size blocks based on logical modules like functions or data.",
            "Paging partitions memory into invisible, uniform, fixed-size units (pages/frames) handled by hardware, while segmentation divides memory into variable-length blocks reflecting programmer logical divisions (code, data, stack)."
        ),
        (
            "What is a system call in an OS?",
            "A system call is an interface between a user program and the OS kernel.",
            "A system call is a programmatic way for an application to request privileged services from the operating system kernel.",
            "A system call is a software-initiated trap instruction that switches the CPU from user mode to privileged kernel mode, allowing applications to request services such as file I/O, process creation, or network operations."
        ),
        (
            "What is the difference between user mode and kernel mode?",
            "User mode has restricted hardware access; kernel mode has complete, unrestricted access.",
            "User mode runs regular applications with limited permissions, while kernel mode runs the operating system core with full access to hardware.",
            "Modern processors implement dual-mode operation: User Mode executes application code with restricted memory and instruction privileges, while Kernel Mode executes privileged OS instructions with unrestricted hardware access."
        ),
        (
            "What is the kernel of an operating system?",
            "The kernel is the central core of the operating system.",
            "The kernel is the foundational core of the OS that directly manages CPU, memory, hardware drivers, and system calls.",
            "The kernel is the primary, essential software component of an operating system that resides permanently in memory, directly managing hardware devices, process lifecycles, memory allocation, and interrupt handling."
        ),
        (
            "What is a semaphore in OS?",
            "A semaphore is a signaling variable used to synchronize processes.",
            "A semaphore is an integer variable used for synchronization that controls access to common shared resources using wait and signal operations.",
            "A semaphore is a protected synchronization variable introduced by Dijkstra with atomic operations `wait()` (P) and `signal()` (V), used to manage resource pools (counting semaphore) or mutual exclusion (binary semaphore)."
        ),
        (
            "What is a mutex?",
            "A mutex is a mutual exclusion lock for protecting shared resources.",
            "A mutex (mutual exclusion) is a locking mechanism that allows only one thread to access a critical section at a time.",
            "A mutex is a binary locking primitive owned exclusively by the thread that acquires it, ensuring that only one thread can execute a critical section at any moment and preventing race conditions."
        ),
        (
            "What is the difference between a mutex and a semaphore?",
            "A mutex is a locking mechanism; a semaphore is a signaling mechanism.",
            "A mutex can be unlocked only by the thread that locked it, whereas a semaphore can be signaled and incremented by any thread.",
            "A mutex is a strict mutual exclusion lock with ownership semantics (only the locking thread can release it), whereas a semaphore is an integer signaling mechanism without ownership, capable of coordinating multiple concurrent slots."
        ),
        (
            "What is a critical section?",
            "A critical section is code where shared resources are accessed.",
            "A critical section is a segment of code that accesses shared variables or resources and must not be executed by more than one thread at a time.",
            "A critical section is an execution code block that accesses shared mutable state or resources, requiring synchronization protocols to ensure mutual exclusion, progress, and bounded waiting."
        ),
        (
            "What is inter-process communication (IPC)?",
            "IPC is a mechanism allowing processes to communicate and share data.",
            "Inter-Process Communication (IPC) refers to methods provided by the OS for separate processes to exchange data and coordinate actions.",
            "Inter-Process Communication (IPC) is a set of kernel-supported protocols—such as pipes, message queues, shared memory, and sockets—that allow distinct processes with isolated address spaces to exchange information."
        ),
        (
            "What is spooling in an operating system?",
            "Spooling buffers data in temporary storage for slower devices.",
            "SPOOLing (Simultaneous Peripheral Operations On-Line) holds data in a buffer or disk queue until a slow device, like a printer, is ready to process it.",
            "SPOOLing is an I/O management technique that buffers data destined for slow peripherals (such as printers) onto disk storage, decoupling high-speed CPU execution from mechanical peripheral processing."
        ),
        (
            "What is a device driver?",
            "A device driver is software that lets the OS communicate with hardware.",
            "A device driver is a specialized software program that allows the operating system to interact with and control a specific hardware device.",
            "A device driver is a privileged kernel-level software module that translates generic OS input/output commands into device-specific register operations and electrical hardware signals."
        )
    ],
    "Computer Networks": [
        (
            "What is a computer network?",
            "A computer network is a group of connected computing devices.",
            "A computer network is a collection of interconnected computers and devices that communicate and share data and resources.",
            "A computer network is a digital telecommunications infrastructure that links autonomous computing nodes via transmission media and communication protocols to exchange data packets and share computational resources."
        ),
        (
            "What is the OSI model?",
            "The OSI model is a 7-layer framework for network communication.",
            "The Open Systems Interconnection (OSI) model is a conceptual 7-layer architectural framework that standardizes network communication functions.",
            "The OSI model is a standard conceptual framework developed by the International Organization for Standardization (ISO) that decomposes telecommunications into 7 distinct layers: Physical, Data Link, Network, Transport, Session, Presentation, and Application."
        ),
        (
            "What are the 7 layers of the OSI model?",
            "Physical, Data Link, Network, Transport, Session, Presentation, and Application.",
            "The 7 layers are Physical, Data Link, Network, Transport, Session, Presentation, and Application.",
            "From bottom to top, the 7 OSI layers are: 1. Physical (bits), 2. Data Link (frames), 3. Network (packets/IP), 4. Transport (segments/TCP), 5. Session (dialogue), 6. Presentation (formatting/encryption), and 7. Application (user services)."
        ),
        (
            "What is the TCP/IP model?",
            "The TCP/IP model is a practical 4-layer networking framework.",
            "The TCP/IP model is the practical networking architecture used by the internet, organized into four layers: Network Access, Internet, Transport, and Application.",
            "The TCP/IP protocol suite is the foundational networking model of the modern Internet, consisting of four layers: Network Access (Link), Internet (IP), Transport (TCP/UDP), and Application (HTTP, DNS, FTP)."
        ),
        (
            "What is an IP address?",
            "An IP address is a unique numerical label for a device on a network.",
            "An Internet Protocol (IP) address is a unique identifier assigned to every device connected to a network that uses IP communication.",
            "An IP address is a numerical network layer identifier assigned to interfaces on an IP network, enabling routing and packet addressing across local and global networks (IPv4 32-bit, IPv6 128-bit)."
        ),
        (
            "What is the difference between IPv4 and IPv6?",
            "IPv4 uses 32-bit addresses; IPv6 uses 128-bit addresses.",
            "IPv4 provides about 4.3 billion addresses using 32-bit numbers, while IPv6 uses 128-bit hexadecimal notation to provide a vastly larger address space.",
            "IPv4 uses 32-bit addresses formatted as dotted-decimal octets (yielding ~4.3 billion addresses), while IPv6 uses 128-bit hexadecimal addressing, solving address exhaustion and adding native security and simplified headers."
        ),
        (
            "What is TCP?",
            "TCP is a reliable, connection-oriented transport protocol.",
            "Transmission Control Protocol (TCP) is a reliable transport protocol that ensures ordered, error-checked delivery of data streams.",
            "Transmission Control Protocol (TCP) is a core transport-layer protocol that guarantees ordered, error-checked, flow-controlled, and congestion-controlled delivery of data packets via virtual connections."
        ),
        (
            "What is UDP?",
            "UDP is a fast, connectionless transport protocol.",
            "User Datagram Protocol (UDP) is a lightweight, connectionless protocol that sends packets without guaranteeing delivery or order.",
            "User Datagram Protocol (UDP) is a minimal, connectionless transport protocol that transmits independent datagrams without handshake overhead, packet ordering, or retransmissions, ideal for real-time video, gaming, and VoIP."
        ),
        (
            "What is the difference between TCP and UDP?",
            "TCP is reliable and connection-oriented; UDP is fast and connectionless.",
            "TCP establishes a connection and guarantees delivery with error checking, while UDP sends packets quickly without verification or order guarantees.",
            "TCP utilizes a 3-way handshake, sequence numbers, and acknowledgments to ensure reliable, ordered byte streams, whereas UDP offers low-latency, connectionless best-effort transmission without delivery guarantees."
        ),
        (
            "What is the TCP three-way handshake?",
            "The three-way handshake establishes a TCP connection using SYN, SYN-ACK, and ACK.",
            "The three-way handshake is a method used by TCP to initiate a connection between client and server using SYN, SYN-ACK, and ACK packets.",
            "The TCP three-way handshake establishes a synchronized virtual connection: the client sends a SYN packet with an initial sequence number, the server responds with SYN-ACK, and the client returns an ACK."
        ),
        (
            "What is DNS?",
            "DNS translates domain names into IP addresses.",
            "The Domain Name System (DNS) is the internet's phonebook, translating human-readable names like google.com into numeric IP addresses.",
            "The Domain Name System (DNS) is a hierarchical distributed naming system that resolves human-friendly domain names (e.g., example.com) into machine-routable IP addresses (e.g., 93.184.216.34)."
        ),
        (
            "What is DHCP?",
            "DHCP automatically assigns IP addresses to network devices.",
            "Dynamic Host Configuration Protocol (DHCP) automatically assigns IP addresses and network configuration settings to devices on a network.",
            "Dynamic Host Configuration Protocol (DHCP) is an application-layer network protocol that dynamically allocates IP addresses, subnet masks, default gateways, and DNS server parameters to network clients."
        ),
        (
            "What is a MAC address?",
            "A MAC address is a unique hardware identifier for a network interface.",
            "A Media Access Control (MAC) address is a permanent physical address burned into a network interface card (NIC) by the manufacturer.",
            "A MAC address is a globally unique 48-bit (6-octet) physical hardware identifier assigned to a Network Interface Controller (NIC) for communication at the Data Link layer (OSI layer 2) within a local network."
        ),
        (
            "What is the difference between a MAC address and an IP address?",
            "A MAC address is permanent physical hardware; an IP address is logical and network-assigned.",
            "A MAC address identifies the physical network card on a local network, while an IP address identifies the device's location on the global or local IP network.",
            "A MAC address is a static physical identifier operating at the Data Link layer for local frame delivery, whereas an IP address is a dynamic logical address operating at the Network layer for inter-network packet routing."
        ),
        (
            "What is a router?",
            "A router forwards data packets between different networks.",
            "A router is a networking device that connects different networks together and directs data packets toward their destination using IP addresses.",
            "A router is a Layer-3 internetworking device that analyzes packet IP destination headers, consults routing tables, and forwards data packets across disparate network segments using dynamic routing protocols."
        ),
        (
            "What is a network switch?",
            "A switch connects devices within the same local network.",
            "A network switch is a device that connects multiple devices within a local area network (LAN) and directs data packets using MAC addresses.",
            "A network switch is a Layer-2 networking device that forwards data frames to specific connected ports based on inspection of destination MAC addresses maintained in its internal MAC address table."
        ),
        (
            "What is the difference between a router and a switch?",
            "A router connects different networks using IP; a switch connects local devices using MAC addresses.",
            "Routers work at Layer 3 to route packets between different networks, while switches work at Layer 2 to connect devices within the same local network.",
            "A switch operates at OSI Layer 2 using MAC addresses to forward frames between devices in a single local broadcast domain, whereas a router operates at Layer 3 using IP addresses to route packets across separate subnets."
        ),
        (
            "What is a subnet mask?",
            "A subnet mask divides an IP address into network and host parts.",
            "A subnet mask is a 32-bit number that separates the network portion of an IP address from the individual host portion.",
            "A subnet mask is a 32-bit bitmask used in IPv4 networking that distinguishes the network routing prefix from the local host identifier, defining the boundaries of an IP subnet."
        ),
        (
            "What is HTTP?",
            "HTTP is the protocol used to transfer web pages.",
            "Hypertext Transfer Protocol (HTTP) is the foundation protocol of the World Wide Web used to transfer web resources between browsers and servers.",
            "Hypertext Transfer Protocol (HTTP) is an application-layer, stateless request-response protocol running over TCP (port 80) that enables distributed hypermedia communication on the World Wide Web."
        ),
        (
            "What is HTTPS?",
            "HTTPS is secure HTTP encrypted with SSL/TLS.",
            "Hypertext Transfer Protocol Secure (HTTPS) is the secure version of HTTP that encrypts web traffic using SSL/TLS.",
            "HTTPS is HTTP layered over the Transport Layer Security (TLS) protocol on port 443, providing bidirectional encryption, data integrity, and server authentication for secure internet communications."
        ),
        (
            "What is a firewall?",
            "A firewall filters network traffic based on security rules.",
            "A firewall is a network security system that monitors and controls incoming and outgoing traffic based on predetermined security rules.",
            "A firewall is a barrier security mechanism implemented in hardware or software that inspects data packets against configured security policies, permitting or blocking traffic to protect network perimeters."
        ),
        (
            "What is a VPN?",
            "A VPN creates an encrypted tunnel across public networks.",
            "A Virtual Private Network (VPN) creates an encrypted, secure connection over a public network like the internet.",
            "A Virtual Private Network (VPN) extends a private network across a public network by encapsulating and encrypting data packets within secure virtual tunnels, masking user IP addresses and protecting data in transit."
        ),
        (
            "What is bandwidth in networking?",
            "Bandwidth is the maximum data transfer capacity of a network.",
            "Bandwidth measures the maximum amount of data that can be transmitted over a network connection in a given amount of time.",
            "Network bandwidth defines the maximum theoretical rate of digital data throughput that can be transmitted across a communication link, commonly expressed in bits per second (Mbps or Gbps)."
        ),
        (
            "What is latency in computer networking?",
            "Latency is the time delay for data to travel across a network.",
            "Latency is the time it takes for a data packet to travel from its source to its destination across a network.",
            "Network latency is the time delay incurred in transmitting a data packet from its point of origin to its destination, influenced by propagation delay, serialization delay, queuing delay, and routing hops."
        ),
        (
            "What is ping in computer networking?",
            "Ping tests connectivity between two devices using ICMP echo requests.",
            "Ping is a network utility tool used to test whether a remote host is reachable and measure round-trip transit time.",
            "Ping is a diagnostic command-line utility that transmits Internet Control Message Protocol (ICMP) Echo Request packets to a target IP address and measures the round-trip time (RTT) for Echo Reply receipts."
        )
    ],
    "Web Development": [
        (
            "What is web development?",
            "Web development is the process of building websites and web applications.",
            "Web development encompasses creating, building, and maintaining websites and web apps that run in web browsers.",
            "Web development is the discipline of engineering, constructing, and maintaining interactive websites and web applications running over the internet via client-server architectures."
        ),
        (
            "What is frontend development?",
            "Frontend is the client-side user interface of a website.",
            "Frontend development refers to building the visible parts of a website that users interact with, using HTML, CSS, and JavaScript.",
            "Frontend development (client-side) involves designing and coding the visual layout, interactivity, user interface components, and responsive experiences rendered directly in user web browsers."
        ),
        (
            "What is backend development?",
            "Backend is the server-side logic and database layer.",
            "Backend development focuses on server logic, databases, APIs, and business rules that power a web application behind the scenes.",
            "Backend development (server-side) encompasses the server architecture, business logic, data persistence, user authentication, and API endpoints that supply dynamic data to client applications."
        ),
        (
            "What is a full-stack developer?",
            "A full-stack developer works on both frontend and backend.",
            "A full-stack developer is a programmer proficient in both client-side frontend technologies and server-side backend systems.",
            "A full-stack software engineer possesses end-to-end expertise across user interfaces (HTML/CSS/JS), backend services (Python, Node, Java), database management, and system deployment pipelines."
        ),
        (
            "What is client-server architecture?",
            "It is a model where clients request resources and servers provide them.",
            "Client-server architecture is a computing model where client applications request services and centralized servers fulfill them.",
            "Client-server architecture is a distributed computing structure that partitions workloads between service requestors (clients like web browsers) and centralized service providers (web/application servers)."
        ),
        (
            "What is a web server?",
            "A web server is software or hardware that serves web content.",
            "A web server is a system that stores website files and serves them to users over HTTP/HTTPS upon request.",
            "A web server is software (such as Nginx, Apache, or Caddy) or dedicated hardware that processes incoming HTTP/HTTPS requests and delivers static assets or routes requests to backend application servers."
        ),
        (
            "What is responsive web design?",
            "Responsive web design makes websites adapt to different screen sizes.",
            "Responsive web design is an approach where a website automatically adjusts its layout and content to look good on phones, tablets, and desktops.",
            "Responsive web design (RWD) is a design methodology employing fluid grid layouts, flexible images, and CSS media queries to dynamically adjust interface presentation across diverse screen resolutions and devices."
        ),
        (
            "What is a cookie in web development?",
            "A cookie is small data stored in the browser by a website.",
            "A cookie is a small piece of text data saved by the browser to remember state like user logins or preferences.",
            "An HTTP cookie is a small data snippet sent by a web server and stored locally in the client browser, automatically transmitted back on subsequent requests to maintain stateful session management."
        ),
        (
            "What is LocalStorage in web browsers?",
            "LocalStorage is persistent browser key-value storage.",
            "LocalStorage is a Web Storage API that allows websites to store key-value pairs in the browser that persist even when closed.",
            "The browser `localStorage` API provides persistent client-side key-value storage (typically up to 5-10MB per origin) that retains data across browser restarts without sending data with every HTTP request."
        ),
        (
            "What is the difference between LocalStorage and SessionStorage?",
            "LocalStorage persists indefinitely; SessionStorage clears when the browser tab closes.",
            "LocalStorage keeps data permanently until cleared, while SessionStorage deletes data as soon as the specific browser tab is closed.",
            "`localStorage` retains key-value data with no expiration until explicitly removed, whereas `sessionStorage` maintains data strictly within the lifecycle of the current browser tab and clears upon closing."
        ),
        (
            "What is CORS in web development?",
            "CORS is a security mechanism controlling cross-origin web requests.",
            "Cross-Origin Resource Sharing (CORS) is a browser security feature that regulates how resources are requested from a different domain.",
            "Cross-Origin Resource Sharing (CORS) is a browser-enforced HTTP-header-based security protocol that permits or restricts web applications on one domain from requesting resources hosted on another domain."
        ),
        (
            "What is a single-page application (SPA)?",
            "An SPA loads a single web page and updates content dynamically without reloading.",
            "A Single-Page Application (SPA) is a web app that loads one initial HTML page and dynamically rewrites page content as the user interacts.",
            "A Single-Page Application (SPA) is a web architecture where the browser loads a single HTML shell and uses client-side JavaScript (React, Vue, Angular) to dynamically update views without full page refreshes."
        ),
        (
            "What is the difference between SSR and CSR?",
            "SSR renders HTML on the server; CSR renders HTML in the browser using JavaScript.",
            "Server-Side Rendering (SSR) generates full HTML on the server before sending it, while Client-Side Rendering (CSR) downloads empty HTML and builds it in the browser.",
            "Server-Side Rendering (SSR) compiles dynamic HTML on the backend server for faster initial page loads and better SEO, while Client-Side Rendering (CSR) renders views client-side using JavaScript frameworks."
        ),
        (
            "What is a RESTful web service?",
            "A RESTful service is a web API following REST principles.",
            "A RESTful web service is an API that uses standard HTTP methods (GET, POST, PUT, DELETE) to manage resources via URLs.",
            "A RESTful web service is an architectural style for network applications that uses stateless communication, standard HTTP verbs, and URI resource identifiers to manipulate resource representations (typically JSON)."
        ),
        (
            "What is a WebSocket?",
            "A WebSocket provides two-way real-time communication over a single connection.",
            "WebSocket is a computer communications protocol that provides full-duplex, real-time communication channels over a single TCP connection.",
            "WebSocket is a persistent, bidirectional, full-duplex communication protocol operating over a single TCP connection initiated via an HTTP handshake, ideal for real-time chat, gaming, and live data streaming."
        ),
        (
            "What is a CDN in web development?",
            "A CDN is a distributed network of servers delivering web content quickly.",
            "A Content Delivery Network (CDN) is a geographically distributed network of servers that caches and delivers content close to users.",
            "A Content Delivery Network (CDN) is a geographically distributed network of caching proxy servers that delivers web assets (images, scripts, stylesheets) from edge locations nearest to users, minimizing latency."
        ),
        (
            "What is caching in web applications?",
            "Caching stores copies of files or data in fast storage for quick access.",
            "Caching is the process of temporarily storing copies of web data to serve future requests faster and reduce server load.",
            "Web caching is a performance optimization mechanism that stores copies of responses, assets, or query results in intermediate high-speed stores (browser, CDN, Redis) to reduce backend computation and latency."
        ),
        (
            "What is SEO in web development?",
            "SEO is optimizing websites to rank higher in search engines.",
            "Search Engine Optimization (SEO) is the practice of improving a website's structure and content to increase organic search engine visibility.",
            "Search Engine Optimization (SEO) involves structuring web architecture, semantic markup, meta tags, page speed, and crawlability to improve a website's indexing and organic ranking on search engines."
        ),
        (
            "What is an SSL certificate?",
            "An SSL certificate encrypts connections and authenticates website identity.",
            "An SSL certificate is a digital certificate that authenticates a website's identity and enables encrypted HTTPS connections.",
            "A Secure Sockets Layer (SSL) or TLS digital certificate binds a cryptographic public key to an organization's identity, enabling encrypted HTTPS data transmission and browser trust verification."
        ),
        (
            "What is WebAssembly (Wasm)?",
            "WebAssembly runs high-performance compiled code in web browsers.",
            "WebAssembly is a binary code format that allows languages like C++ and Rust to run at near-native speed in web browsers.",
            "WebAssembly (Wasm) is a low-level, binary instruction format designed as a portable compilation target for languages such as C, C++, and Rust, executing at near-native speed inside secure browser sandboxes."
        ),
        (
            "What is a Progressive Web App (PWA)?",
            "A PWA is a web app that offers native mobile-like features.",
            "A Progressive Web App (PWA) is a web application that uses service workers to provide offline functionality, push notifications, and app installation.",
            "A Progressive Web App (PWA) is a web application built with modern web APIs (Service Workers, Web App Manifest) that delivers app-like experiences, offline capabilities, push notifications, and home-screen installability."
        ),
        (
            "What is a Service Worker in web apps?",
            "A service worker is a background script that enables caching and offline features.",
            "A Service Worker is a client-side JavaScript script that runs in the background to intercept network requests, cache assets, and handle push alerts.",
            "A Service Worker is an event-driven programmable network proxy script running independently from web pages in the browser background, intercepting HTTP requests, enabling offline caching, and receiving background push messages."
        ),
        (
            "What is semantic HTML?",
            "Semantic HTML uses meaningful tags that describe content.",
            "Semantic HTML means using HTML elements like <header>, <nav>, and <article> that clearly describe their meaning to browsers and developers.",
            "Semantic HTML is the practice of using HTML markup tags (e.g., `<header>`, `<article>`, `<section>`, `<footer>`) that convey the structural and contextual meaning of content, enhancing accessibility and SEO."
        ),
        (
            "What is MVC architecture in web development?",
            "MVC separates an app into Model, View, and Controller.",
            "Model-View-Controller (MVC) is an architectural pattern that divides an application into data (Model), user interface (View), and logic (Controller).",
            "Model-View-Controller (MVC) is a software design pattern separating application concerns into the Model (business data logic), View (presentation and rendering), and Controller (request routing and user input coordination)."
        ),
        (
            "What is microfrontend architecture?",
            "Microfrontends divide frontend web apps into independently deployable units.",
            "Microfrontend architecture breaks down a large frontend application into smaller, semi-independent micro-apps worked on by different teams.",
            "Microfrontends is an architectural approach where a monolithic frontend codebase is decomposed into independent, smaller frontend modules that can be developed, tested, and deployed autonomously by cross-functional teams."
        )
    ],
    "HTML/CSS/JavaScript": [
        (
            "What is HTML?",
            "HTML is the standard markup language for creating web pages.",
            "Hypertext Markup Language (HTML) is the foundational language used to structure web pages and their content.",
            "HTML (Hypertext Markup Language) is the standard markup language that defines the semantic structure, elements, and content layout of documents rendered by web browsers."
        ),
        (
            "What is CSS?",
            "CSS is a stylesheet language used to style web pages.",
            "Cascading Style Sheets (CSS) is used to control the visual design, colors, fonts, and layouts of HTML documents.",
            "Cascading Style Sheets (CSS) is a styling language used to describe the visual presentation, color schemes, typography, and responsive layouts of HTML markup across various display media."
        ),
        (
            "What is JavaScript?",
            "JavaScript is a programming language that adds interactivity to web pages.",
            "JavaScript is a high-level scripting language used to create dynamic, interactive features on websites.",
            "JavaScript is a lightweight, interpreted or JIT-compiled, prototype-based, multi-paradigm programming language that powers dynamic client-side browser behavior and server-side execution via Node.js."
        ),
        (
            "What is the HTML DOM?",
            "The DOM is an object-oriented tree representation of an HTML document.",
            "The Document Object Model (DOM) is a programming interface that represents an HTML document as a tree of nodes that JavaScript can manipulate.",
            "The Document Object Model (DOM) is a standardized tree-like API representation of an HTML document created by the browser, exposing objects, properties, and methods that scripts use to modify page structure and styles dynamically."
        ),
        (
            "What is the CSS Box Model?",
            "The Box Model comprises content, padding, border, and margin.",
            "The CSS Box Model is the foundational layout design where every HTML element is treated as a box made of Content, Padding, Border, and Margin.",
            "The CSS Box Model represents the rectangular space occupied by every rendered HTML element, consisting of four nested layers from inside out: Content area, internal Padding, outer Border, and external Margin."
        ),
        (
            "What is the difference between margin and padding in CSS?",
            "Margin is space outside the border; padding is space inside the border.",
            "Margin creates transparent space outside an element's border, while padding creates space inside the border around the content.",
            "Margin defines the external clearance space surrounding an element separating it from neighbors, whereas padding specifies the internal spacing between an element's content and its bounding border."
        ),
        (
            "What is CSS Flexbox?",
            "Flexbox is a one-dimensional layout model for aligning items.",
            "CSS Flexbox (Flexible Box Layout) is a CSS layout mode designed for arranging and distributing space among items in a row or column.",
            "CSS Flexible Box Layout (Flexbox) is a one-dimensional layout mechanism providing efficient item alignment, distribution, and proportional sizing along a primary axis and cross axis within a container."
        ),
        (
            "What is CSS Grid?",
            "CSS Grid is a two-dimensional layout system for rows and columns.",
            "CSS Grid is a powerful layout module that allows developers to design complex web layouts using both rows and columns simultaneously.",
            "CSS Grid Layout is a robust two-dimensional layout system capable of handling both rows and columns concurrently, providing declarative grid template areas and fractional unit scaling."
        ),
        (
            "What is the difference between let, const, and var in JavaScript?",
            "var is function-scoped; let and const are block-scoped, with const being immutable.",
            "var has function scope and is hoisted; let has block scope and can be reassigned; const has block scope and cannot be reassigned.",
            "`var` provides function-scoped, hoisted variables; `let` introduces modern block-scoped variables that can be reassigned; `const` defines block-scoped constants whose binding cannot be rebound."
        ),
        (
            "What is hoisting in JavaScript?",
            "Hoisting moves variable and function declarations to the top of their scope.",
            "Hoisting is JavaScript's default behavior of moving declarations to the top of the current scope before code execution.",
            "Hoisting is a JavaScript interpreter behavior where variable declarations (`var`) and function declarations are moved to the top of their enclosing scope during the compilation phase prior to code execution."
        ),
        (
            "What is a closure in JavaScript?",
            "A closure is a function that remembers its outer lexical environment.",
            "A closure is a function that retains access to variables from its parent scope even after the parent function has finished executing.",
            "A closure is the combination of a function bundled together with references to its lexical environment, allowing an inner function to access an outer enclosing function's variables even after the outer function has returned."
        ),
        (
            "What is an arrow function in JavaScript?",
            "An arrow function is a compact function syntax with lexical this.",
            "Arrow functions provide a concise syntax `() => {}` and do not have their own `this` binding.",
            "Introduced in ES6, arrow functions offer a concise syntactic alternative for declaring functions using the `=>` token, featuring lexical scoping of the `this` identifier without their own `arguments` or prototype objects."
        ),
        (
            "What is the difference between == and === in JavaScript?",
            "== compares value with type conversion; === compares value and type strictly.",
            "The `==` operator checks equality with type coercion, while `===` checks both value and data type without coercion.",
            "The loose equality operator `==` performs implicit type coercion before comparing values, whereas the strict equality operator `===` evaluates equality without type conversion, returning false if types differ."
        ),
        (
            "What is a Promise in JavaScript?",
            "A Promise represents the future result of an asynchronous operation.",
            "A Promise is an object representing the eventual completion (or failure) of an asynchronous operation and its resulting value.",
            "A JavaScript `Promise` is an object representing the eventual outcome of an asynchronous operation, existing in one of three states: pending, fulfilled with a value, or rejected with a reason/error."
        ),
        (
            "What is async/await in JavaScript?",
            "Async/await is syntactic sugar for working with Promises cleanly.",
            "Async and await are keywords that make asynchronous code look and behave more like synchronous code, built on top of Promises.",
            "The `async/await` syntax provides clean syntactic sugar over JavaScript Promises, enabling developers to write asynchronous, non-blocking code in a clear sequential structure with standard `try/catch` error handling."
        ),
        (
            "What is the Event Loop in JavaScript?",
            "The Event Loop coordinates asynchronous callbacks with the call stack.",
            "The Event Loop continuously checks the call stack and executes waiting callbacks from the task queue when the stack is empty.",
            "The JavaScript Event Loop is a concurrency mechanism that constantly monitors the call stack and task/microtask queues, pushing completed asynchronous callbacks onto the execution stack when it becomes idle."
        ),
        (
            "What is event bubbling in JavaScript?",
            "Event bubbling propagates an event from the target element up to its parents.",
            "Event bubbling is a type of event propagation where an event triggers on the innermost child first and bubbles upward through parent elements.",
            "Event bubbling is the default phase of DOM event propagation where an event triggered on a target element propagates upward through its ancestor hierarchy in the DOM tree unless stopped with `stopPropagation()`."
        ),
        (
            "What is event delegation in JavaScript?",
            "Event delegation handles events on multiple children using one parent listener.",
            "Event delegation is a technique of adding a single event listener to a parent element to manage events for all current and future child elements.",
            "Event delegation is an efficient DOM pattern leveraging event bubbling where a single event handler attached to a common parent element intercepts and processes events triggered by any of its descendant elements."
        ),
        (
            "What is NaN in JavaScript?",
            "NaN stands for Not-a-Number.",
            "NaN represents a value that is not a valid number resulting from an invalid mathematical calculation.",
            "`NaN` is a property of the global object representing 'Not-a-Number', resulting from undefined numerical operations (such as `0 / 0` or parsing an invalid string) having a data type of `number`."
        ),
        (
            "What is the difference between null and undefined in JavaScript?",
            "null is intentional emptiness; undefined means a variable has not been assigned a value.",
            "Undefined means a variable was declared but not given a value; null is an assigned value representing intentional absence of an object.",
            "`undefined` is a primitive type automatically assigned to declared variables that lack initialization, whereas `null` is an explicit assignment representing the deliberate absence of any object reference."
        ),
        (
            "What is the CSS z-index property?",
            "z-index controls the stack order of positioned elements.",
            "The `z-index` property determines which overlapping elements appear in front of or behind others along the Z-axis.",
            "The CSS `z-index` property specifies the vertical stack order of positioned elements (relative, absolute, fixed, or sticky), where elements with higher integer values render in front of elements with lower values."
        ),
        (
            "What are CSS pseudo-classes?",
            "Pseudo-classes style elements in specific states, like :hover.",
            "A CSS pseudo-class is a keyword added to a selector that specifies a special state of the selected element, such as `:hover` or `:focus`.",
            "A CSS pseudo-class is a selector addition preceded by a single colon (e.g., `:hover`, `:active`, `:nth-child()`) that applies styles dynamically based on user interaction, state, or document tree position."
        ),
        (
            "What is the difference between display: none and visibility: hidden?",
            "display: none removes the element from layout; visibility: hidden hides it while keeping its space.",
            "With `display: none`, the element is completely removed from the page flow; with `visibility: hidden`, the element is invisible but still occupies its physical space.",
            "`display: none` removes the element entirely from the document render tree without taking up layout space, whereas `visibility: hidden` hides the element visually while preserving its layout dimensions and position."
        ),
        (
            "What is JSON?",
            "JSON is a lightweight data format for exchanging information.",
            "JavaScript Object Notation (JSON) is a text-based, human-readable data format widely used for transmitting data between clients and servers.",
            "JSON (JavaScript Object Notation) is a standardized, language-independent, lightweight data-interchange text format based on key-value pairs and ordered arrays, universally used in modern web APIs."
        ),
        (
            "What is localStorage vs sessionStorage in JavaScript?",
            "localStorage stays permanently; sessionStorage clears when the session/tab closes.",
            "localStorage persists data across browser sessions and restarts, whereas sessionStorage only persists data until the current tab or window is closed.",
            "Both are HTML5 web storage mechanisms holding key-value strings, but `localStorage` maintains persistent data with no expiration, while `sessionStorage` scopes data strictly to the lifespan of the current window tab."
        )
    ],
    "APIs": [
        (
            "What is an API?",
            "An API is an Application Programming Interface that lets programs communicate.",
            "An Application Programming Interface (API) is a set of rules and protocols that allows different software applications to communicate with each other.",
            "An Application Programming Interface (API) is a formal software intermediary that defines specifications, endpoints, data formats, and protocols enabling distinct software systems to exchange data and invoke operations."
        ),
        (
            "What is a REST API?",
            "A REST API is a web API that follows REST architectural principles.",
            "A REST (Representational State Transfer) API is a web service that uses HTTP methods and URLs to manage resources, usually in JSON format.",
            "A REST API is an architectural style for network-based systems adhering to six constraints (statelessness, client-server, cacheability, uniform interface, layered system, code on demand) operating primarily over HTTP."
        ),
        (
            "What are the most common HTTP methods used in REST APIs?",
            "GET, POST, PUT, PATCH, and DELETE.",
            "The common HTTP methods are GET (read), POST (create), PUT (replace), PATCH (partial update), and DELETE (remove).",
            "Core RESTful HTTP methods include GET (retrieve resource representation), POST (create new subordinate resource), PUT (replace entire resource), PATCH (apply partial modifications), and DELETE (remove resource)."
        ),
        (
            "What is the difference between PUT and PATCH in REST APIs?",
            "PUT replaces the entire resource; PATCH modifies specific fields.",
            "PUT is used to overwrite a complete resource representation, while PATCH is used to update only specific selected fields of an existing resource.",
            "The `PUT` method is idempotent and replaces the entire target resource with the supplied payload, whereas the `PATCH` method applies partial delta updates to existing resource attributes."
        ),
        (
            "What does idempotency mean in APIs?",
            "An operation is idempotent if repeating it multiple times produces the same result.",
            "An API method is idempotent if making the same request multiple times leaves the system in the exact same state as making it once.",
            "Idempotence is an API property where identical multiple requests produce the exact same side-effect on the server as a single request (e.g., GET, PUT, and DELETE are idempotent; POST is typically non-idempotent)."
        ),
        (
            "What is an API endpoint?",
            "An API endpoint is a specific URL where an API receives requests.",
            "An API endpoint is the digital location or URL where a web service accepts requests to access specific resources.",
            "An API endpoint is a distinct Uniform Resource Identifier (URI) hosted on a server that represents a specific resource or functional entry point accepting incoming client HTTP requests."
        ),
        (
            "What are HTTP status codes?",
            "HTTP status codes indicate the result of a client request.",
            "HTTP status codes are 3-digit numbers returned by a server indicating whether a request was successful, failed, or requires further action.",
            "HTTP status codes are standardized three-digit integers grouped into five classes (1xx Informational, 2xx Success, 3xx Redirection, 4xx Client Error, 5xx Server Error) signaling the outcome of an HTTP request."
        ),
        (
            "What is the meaning of HTTP status code 200 OK?",
            "200 OK means the request was successful.",
            "Status code 200 OK indicates that the client request was successfully processed and the server returned the requested data.",
            "The HTTP 200 OK status code signifies that the client's HTTP request has succeeded completely, and the response payload contains the expected resource data."
        ),
        (
            "What is the meaning of HTTP status code 201 Created?",
            "201 Created means a new resource was successfully created.",
            "Status code 201 Created indicates that the request succeeded and resulted in the creation of a new resource on the server.",
            "The HTTP 201 Created response indicates that the request succeeded and led to the creation of one or more new resources, typically returned following successful POST or PUT operations."
        ),
        (
            "What is the meaning of HTTP status code 400 Bad Request?",
            "400 Bad Request means the server could not understand the client's request.",
            "Status code 400 indicates that the server cannot process the request due to client errors like malformed syntax or invalid data.",
            "The HTTP 400 Bad Request status code indicates that the server cannot or will not process the request due to perceived client-side errors, such as invalid request body framing or malformed routing."
        ),
        (
            "What is the meaning of HTTP status code 401 Unauthorized?",
            "401 Unauthorized means the request lacks valid authentication credentials.",
            "Status code 401 indicates that access is denied because the user is not authenticated or provided invalid credentials.",
            "The HTTP 401 Unauthorized status indicates that the request lacks valid authentication credentials for the requested target resource, requiring the client to authenticate."
        ),
        (
            "What is the meaning of HTTP status code 403 Forbidden?",
            "403 Forbidden means the authenticated client does not have permission.",
            "Status code 403 indicates that the server knows who you are, but you do not have permission to access the resource.",
            "The HTTP 403 Forbidden code denotes that the server understands the client's authenticated identity, but explicitly refuses authorization to access the specific resource."
        ),
        (
            "What is the meaning of HTTP status code 404 Not Found?",
            "404 Not Found means the requested resource does not exist.",
            "Status code 404 indicates that the server cannot find the requested URL or resource.",
            "The HTTP 404 Not Found response code indicates that the server cannot locate a current representation for the target URI requested by the client."
        ),
        (
            "What is the meaning of HTTP status code 500 Internal Server Error?",
            "500 means an unexpected error occurred on the server.",
            "Status code 500 indicates that the server encountered an unexpected condition that prevented it from fulfilling the request.",
            "The HTTP 500 Internal Server Error status indicates that the server encountered an unhandled exception or critical unexpected failure while attempting to execute the client request."
        ),
        (
            "What is a webhook?",
            "A webhook is an automated event-driven notification sent to a URL.",
            "A webhook is an automated HTTP callback sent by a server to notify another system immediately when a specific event happens.",
            "A webhook is an event-driven HTTP push notification mechanism where a provider server automatically dispatches a POST payload containing event data to a pre-configured subscriber URL upon event occurrence."
        ),
        (
            "What is the difference between an API and a Webhook?",
            "An API is polled by the client; a webhook pushes data automatically from the server.",
            "With an API, you pull data by sending requests; with a webhook, the server pushes data to you automatically when an event occurs.",
            "In standard API polling, the client repeatedly requests updates from a server; in contrast, a webhook utilizes a reverse-API push model where the server immediately sends data when events happen."
        ),
        (
            "What is an API gateway?",
            "An API gateway is a management entry point that routes client requests to services.",
            "An API Gateway is a server that acts as a single front door for microservices, handling routing, security, rate limiting, and analytics.",
            "An API Gateway is an architectural component that serves as a single reverse-proxy entry point for client applications, managing traffic routing, authentication, SSL termination, rate limiting, and protocol translation."
        ),
        (
            "What is rate limiting in APIs?",
            "Rate limiting limits how many requests a user can make in a given time.",
            "Rate limiting is a security and performance control that restricts the number of API requests a client can submit within a specified time window.",
            "Rate limiting is a traffic-shaping control mechanism that constrains the frequency of requests a client can make within a defined time frame, protecting backend services from denial-of-service and abuse."
        ),
        (
            "What is an API token?",
            "An API token is a secure credential used to authenticate API requests.",
            "An API token is a unique alphanumeric string passed in request headers that authenticates and identifies the calling client.",
            "An API token is a secure cryptographic identifier or opaque string passed within HTTP headers (e.g., `Authorization: Bearer <token>`) that authenticates the client and verifies authorized permissions."
        ),
        (
            "What is JWT (JSON Web Token)?",
            "JWT is a compact, URL-safe token format for authentication.",
            "A JSON Web Token (JWT) is a standard format for securely transmitting digitally signed claims as a JSON object between parties.",
            "JSON Web Token (JWT) is an open RFC 7519 standard defining a compact, self-contained token consisting of a Header, Payload, and Signature, used for stateless authentication and authorization."
        ),
        (
            "What is SOAP in web services?",
            "SOAP is a standardized protocol for exchanging XML-based messages.",
            "Simple Object Access Protocol (SOAP) is a strict, protocol-based web service standard that uses XML for messaging over HTTP or SMTP.",
            "SOAP is a formal, XML-based protocol specification for exchanging structured information in decentralized network environments, enforcing strict WSDL contracts and enterprise-grade WS-Security standards."
        ),
        (
            "What is the difference between REST and SOAP?",
            "REST is a lightweight architectural style using JSON; SOAP is a strict protocol using XML.",
            "REST is flexible, faster, and typically uses JSON over HTTP, while SOAP is a rigid protocol with strict standards that uses XML messages.",
            "REST is an architectural style emphasizing lightweight formats (JSON), statelessness, and HTTP verb alignment, whereas SOAP is a strict standard protocol using XML messaging with built-in compliance and acid transactions."
        ),
        (
            "What is GraphQL?",
            "GraphQL is a query language that lets clients request exact data.",
            "GraphQL is an API query language developed by Facebook that allows clients to request exactly the data fields they need and nothing more.",
            "GraphQL is an open-source data query and manipulation language for APIs that provides a declarative type-system schema, allowing clients to fetch precisely the fields they require in a single round-trip request."
        ),
        (
            "What is API documentation?",
            "API documentation is a technical guide explaining how to use an API.",
            "API documentation is a developer manual providing instructions, endpoint descriptions, parameters, and examples for integrating an API.",
            "API documentation is a comprehensive technical reference containing architectural guidelines, endpoint signatures, authentication mechanisms, request-response schemas, and code samples (e.g., Swagger/OpenAPI)."
        ),
        (
            "What is Swagger or OpenAPI?",
            "Swagger/OpenAPI is a standard framework for describing and testing REST APIs.",
            "OpenAPI is a standardized specification for describing RESTful APIs, and Swagger provides interactive tools to document and test them.",
            "OpenAPI is a vendor-neutral specification format (JSON/YAML) for describing RESTful interfaces, accompanied by Swagger UI tooling that automatically renders interactive web documentation for testing endpoints."
        )
    ],
    "Software Engineering": [
        (
            "What is Software Engineering?",
            "Software engineering is the systematic approach to developing software.",
            "Software engineering is the disciplined application of engineering principles to design, develop, test, and maintain software systems.",
            "Software engineering is a systematic, disciplined, quantifiable engineering approach applied to the complete lifecycle of software development, operation, and maintenance to produce reliable, scalable systems."
        ),
        (
            "What is the Software Development Life Cycle (SDLC)?",
            "SDLC is the step-by-step process of planning, building, and maintaining software.",
            "The SDLC is a structured framework detailing the phases involved in software development from initial planning through deployment and maintenance.",
            "The Software Development Life Cycle (SDLC) is a structured multi-phase methodology outlining the sequential or iterative stages of software development: Requirements Analysis, Design, Implementation, Testing, Deployment, and Maintenance."
        ),
        (
            "What are the main phases of the SDLC?",
            "Planning, Analysis, Design, Coding, Testing, Deployment, and Maintenance.",
            "The phases are Requirements Gathering, System Design, Coding/Implementation, Quality Testing, Deployment, and Ongoing Maintenance.",
            "The standard SDLC phases are: 1. Requirements Engineering, 2. Architectural Design, 3. Software Implementation, 4. Quality Assurance & Testing, 5. Production Deployment, and 6. Maintenance & Evolution."
        ),
        (
            "What is the Waterfall model?",
            "The Waterfall model is a linear sequential development process.",
            "The Waterfall model is a traditional software methodology where each phase must finish completely before the next phase begins.",
            "The Waterfall model is a non-iterative, linear-sequential software development methodology where progress flows steadily downward through discrete phases (Requirements, Design, Coding, Verification, Maintenance)."
        ),
        (
            "What is Agile methodology?",
            "Agile is an iterative, flexible approach to software development.",
            "Agile is a software development methodology based on iterative development, frequent feedback, and cross-functional collaboration.",
            "Agile is an iterative, customer-centric project management methodology that emphasizes rapid delivery of working software through short sprint cycles, continuous user feedback, and adaptive planning."
        ),
        (
            "What is the difference between Agile and Waterfall?",
            "Waterfall is linear and rigid; Agile is iterative and flexible.",
            "Waterfall plans the entire project upfront in sequential stages, while Agile delivers working features incrementally in short iterations with continuous adaptation.",
            "Waterfall is a predictive, document-driven methodology requiring full specification before construction, whereas Agile is an adaptive, empirical framework dividing development into incremental sprints welcoming changing requirements."
        ),
        (
            "What is Scrum in Agile?",
            "Scrum is a popular Agile framework based on short sprints.",
            "Scrum is an Agile management framework where cross-functional teams deliver working software increments during fixed cycles called sprints.",
            "Scrum is an iterative Agile delivery framework structured around defined team roles (Product Owner, Scrum Master, Developers), time-boxed iterations (Sprints, typically 2 weeks), and ceremonies (Daily Standups, Retrospectives)."
        ),
        (
            "What is a Sprint in Scrum?",
            "A Sprint is a short, time-boxed iteration in Scrum.",
            "A Sprint is a fixed time period (usually 1 to 4 weeks) in which a Scrum team completes a set amount of planned work.",
            "A Sprint is a time-boxed iterative execution cycle (commonly 2 weeks) during which a development team commits to building and delivering a potentially shippable product increment from the sprint backlog."
        ),
        (
            "What is CI/CD?",
            "CI/CD automates software integration, testing, and deployment.",
            "Continuous Integration (CI) and Continuous Deployment (CD) automate the building, testing, and releasing of code into production.",
            "CI/CD represents automated DevOps practices where Continuous Integration automatically builds and tests developer code upon commit, and Continuous Delivery/Deployment automates packaging and releasing to production."
        ),
        (
            "What is unit testing?",
            "Unit testing tests individual functions or components in isolation.",
            "Unit testing is the practice of writing automated tests that verify individual units or functions of code work correctly.",
            "Unit testing is a software testing level where smallest testable units of source code (individual functions, methods, or classes) are validated in complete isolation from external dependencies, often using mocks and stubs."
        ),
        (
            "What is integration testing?",
            "Integration testing tests how different modules work together.",
            "Integration testing verifies that multiple software modules or services function together correctly as an integrated system.",
            "Integration testing evaluates how combined software components interact, uncovering interface defects between interconnected modules, database layers, third-party APIs, and microservices."
        ),
        (
            "What is regression testing?",
            "Regression testing ensures new changes didn't break existing features.",
            "Regression testing is re-running tests after code changes to confirm that existing functionality remains intact and bug-free.",
            "Regression testing is quality assurance verification executed after code modifications, bug fixes, or enhancements to confirm that existing software functionality has not been inadvertently degraded or broken."
        ),
        (
            "What is code refactoring?",
            "Refactoring is restructuring existing code without changing its external behavior.",
            "Code refactoring is improving the internal structure, readability, and design of code without altering its outward functionality.",
            "Code refactoring is a disciplined engineering technique of modifying internal software architecture to improve code quality, reduce technical debt, and simplify maintainability without changing its observable external behavior."
        ),
        (
            "What is technical debt?",
            "Technical debt is the future cost of choosing a quick, messy solution now.",
            "Technical debt represents the future rework required when opting for easy or suboptimal code rather than clean, sustainable design.",
            "Technical debt is a software development metaphor describing the implied future cost of additional engineering effort incurred by choosing an expedient, substandard architectural solution over an optimal one."
        ),
        (
            "What is a design pattern?",
            "A design pattern is a reusable solution to a common software problem.",
            "A design pattern is a general, proven template for solving recurring design problems in software architecture.",
            "A design pattern is a formalized, battle-tested architectural blueprint for resolving commonly recurring design challenges within software engineering, categorized into Creational, Structural, and Behavioral patterns."
        ),
        (
            "What is the Singleton design pattern?",
            "Singleton ensures a class has only one instance and provides global access.",
            "The Singleton pattern restricts the instantiation of a class to one single object and provides a global point of access to it.",
            "The Singleton design pattern is a creational pattern that guarantees a class has only one operating instance throughout the application runtime, providing a synchronized global access point."
        ),
        (
            "What is the Factory design pattern?",
            "The Factory pattern creates objects without specifying the exact class to instantiate.",
            "The Factory pattern delegates the responsibility of object instantiation to a specialized method or class rather than calling constructors directly.",
            "The Factory Method pattern is a creational design pattern that defines an interface for creating objects, delegating the actual instantiation logic to concrete subclasses based on input parameters."
        ),
        (
            "What is Test-Driven Development (TDD)?",
            "TDD is writing tests before writing the actual code.",
            "Test-Driven Development (TDD) is a development practice where you write automated tests first, run them until they fail, then write minimal code to pass.",
            "Test-Driven Development (TDD) is an iterative development process governed by the Red-Green-Refactor cycle: write a failing unit test first, produce minimal code to pass the test, then refactor the implementation cleanly."
        ),
        (
            "What is black-box testing?",
            "Black-box testing tests software without looking at internal code.",
            "Black-box testing evaluates an application's inputs and outputs without any knowledge of its internal code implementation.",
            "Black-box testing is a software testing methodology where test cases are derived strictly from functional specifications without examining the underlying source code architecture or internal logic."
        ),
        (
            "What is white-box testing?",
            "White-box testing tests the internal code logic and structure.",
            "White-box testing inspects internal source code paths, logic branches, and data structures to ensure thorough test coverage.",
            "White-box testing (structural testing) evaluates an application's internal code mechanics, verifying control flow paths, statement coverage, branch conditions, and exception handlers using knowledge of source code."
        ),
        (
            "What is pair programming?",
            "Pair programming is two developers writing code together at one workstation.",
            "Pair programming is an Agile technique where two programmers work together on the same code: one drives while the other reviews.",
            "Pair programming is a collaborative software development practice where two developers share a single workstation, alternating roles between the 'Driver' (who writes code) and the 'Navigator' (who reviews and plans ahead)."
        ),
        (
            "What is code review?",
            "Code review is team members checking another developer's code before merging.",
            "A code review is a peer evaluation where team members inspect newly written code for bugs, quality, and standards compliance.",
            "A code review is a formal quality assurance gate where engineers systematically inspect pull requests submitted by peers to catch defects, verify architecture, ensure style compliance, and share domain knowledge."
        ),
        (
            "What is semantic versioning (SemVer)?",
            "SemVer is a 3-part versioning system: Major.Minor.Patch.",
            "Semantic Versioning (SemVer) formats software versions as MAJOR.MINOR.PATCH to clearly communicate breaking changes and updates.",
            "Semantic Versioning (SemVer) is a formal release numbering standard (MAJOR.MINOR.PATCH) where MAJOR increments for incompatible API changes, MINOR for backwards-compatible features, and PATCH for bug fixes."
        ),
        (
            "What is software maintainability?",
            "Maintainability is how easily software can be modified and fixed.",
            "Maintainability is a measure of how easily a software system can be updated, corrected, improved, or adapted to new environments.",
            "Software maintainability evaluates the effort and cost required to modify a software product to fix defects, enhance performance, adapt to new platforms, or meet evolving business requirements."
        ),
        (
            "What is DRY in software engineering?",
            "DRY stands for Don't Repeat Yourself.",
            "The DRY (Don't Repeat Yourself) principle states that every piece of knowledge or logic should have a single, unambiguous representation.",
            "Don't Repeat Yourself (DRY) is a foundational software philosophy aimed at reducing duplicate code and logic by replacing redundancies with reusable abstractions, functions, and modules."
        )
    ],
    "Git/GitHub": [
        (
            "What is Git?",
            "Git is a distributed version control system.",
            "Git is a free, open-source distributed version control system designed to track changes in source code during development.",
            "Git is a decentralized distributed version control system (DVCS) that records changes to project files over time, enabling multiple developers to work collaboratively, branch freely, and maintain complete repository histories locally."
        ),
        (
            "What is GitHub?",
            "GitHub is a cloud platform for hosting and managing Git repositories.",
            "GitHub is a cloud-based hosting service that lets developers store, manage, review, and collaborate on Git code repositories.",
            "GitHub is an online hosting platform and collaboration portal for Git repositories, providing web interfaces, pull request code reviews, issue tracking, continuous integration (Actions), and project management."
        ),
        (
            "What is the difference between Git and GitHub?",
            "Git is the local version control tool; GitHub is the online hosting platform.",
            "Git is a command-line software tool for tracking code changes, while GitHub is a web-based service for hosting Git repositories online.",
            "Git is the underlying command-line distributed version control software running locally on a developer's machine, whereas GitHub is a remote cloud service that hosts Git repositories and provides collaborative workflows."
        ),
        (
            "What does git init do?",
            "git init creates a new empty Git repository.",
            "The `git init` command initializes a new, empty Git repository in the current directory, creating a hidden .git folder.",
            "`git init` creates a new Git repository within the target directory by setting up the internal `.git` metadata directory containing object stores, template files, and initial branch references."
        ),
        (
            "What does git clone do?",
            "git clone copies an existing remote repository to your local machine.",
            "The `git clone` command downloads a complete copy of an existing remote Git repository to your local computer.",
            "`git clone <url>` copies a remote repository, including its complete commit history, branches, and tags, establishing an automatic `origin` remote tracking link in a newly created local directory."
        ),
        (
            "What is the Git staging area?",
            "The staging area is a preparation zone for changes before committing.",
            "The Git staging area (or index) is a workspace where you organize and preview file changes before saving them in a commit.",
            "The Git staging area (also known as the index) is an intermediate storage buffer where file modifications are prepared, reviewed, and formatted using `git add` prior to finalizing them into the repository history."
        ),
        (
            "What does git add do?",
            "git add stages changes for the next commit.",
            "The `git add` command moves modified files from your working directory into the Git staging area.",
            "`git add <file>` stages modified or untracked files into Git's index, packaging their current state so they will be incorporated into the next commit snapshot."
        ),
        (
            "What does git commit do?",
            "git commit saves staged changes to the repository history.",
            "The `git commit` command permanently records a snapshot of staged changes into the Git repository along with a descriptive message.",
            "`git commit -m '<message>'` records a permanent cryptographic snapshot of staged changes into the local repository DAG (directed acyclic graph), associating it with an author, timestamp, parent commit, and commit message."
        ),
        (
            "What does git push do?",
            "git push uploads local commits to a remote repository.",
            "The `git push` command sends committed changes from your local Git branch to a remote server like GitHub.",
            "`git push <remote> <branch>` uploads local branch commits to the corresponding remote repository branch, synchronizing the remote reference with local changes."
        ),
        (
            "What does git pull do?",
            "git pull fetches and merges changes from a remote repository.",
            "The `git pull` command downloads updates from a remote repository and immediately integrates them into your current local branch.",
            "`git pull` performs a combined `git fetch` followed by a `git merge`, retrieving commits from the tracked remote branch and integrating them into the currently checked-out local branch."
        ),
        (
            "What is the difference between git fetch and git pull?",
            "git fetch downloads changes without merging; git pull downloads and merges them immediately.",
            "The `git fetch` command downloads new commits from a remote without modifying your working files, while `git pull` downloads and automatically merges them.",
            "`git fetch` updates remote tracking branches without altering local working branches or code, whereas `git pull` immediately executes a merge of remote commits into the current active branch."
        ),
        (
            "What is a branch in Git?",
            "A branch is an independent line of development.",
            "A Git branch is a lightweight, movable pointer to a specific commit that allows you to work on features without affecting the main code.",
            "A Git branch is a lightweight movable pointer referencing the tip of a commit lineage, enabling developers to isolate feature development, experiments, and bug fixes from the production codebase."
        ),
        (
            "What does git checkout or git switch do?",
            "It switches between branches or restores working tree files.",
            "The `git checkout` command lets you navigate between different branches or inspect past commits in your repository.",
            "`git checkout <branch>` (or modern `git switch`) updates files in the working tree to match the specified branch or commit, updating the HEAD pointer to point to the selected reference."
        ),
        (
            "What is git merge?",
            "git merge combines changes from one branch into another.",
            "The `git merge` command integrates commit history from a source branch into your current active branch.",
            "`git merge <branch>` combines independent lines of development by creating a merge commit (or executing a fast-forward merge) that integrates commits from the target branch into the current checked-out branch."
        ),
        (
            "What is a merge conflict in Git?",
            "A merge conflict occurs when conflicting changes cannot be merged automatically.",
            "A merge conflict happens when Git cannot automatically combine changes because two branches edited the same line of a file differently.",
            "A merge conflict occurs when Git attempts to integrate two branches that contain competing modifications on the identical lines of a file, halting execution and requiring human intervention to select resolved lines."
        ),
        (
            "What is git rebase?",
            "git rebase reapplies commits on top of another base branch.",
            "The `git rebase` command moves or replays a sequence of branch commits onto the tip of a new base branch to create a linear history.",
            "`git rebase <base>` rewrites commit history by detaching branch commits, updating the branch origin to the tip of the specified base, and sequentially reapplying each commit for a clean, linear project history."
        ),
        (
            "What is the difference between git merge and git rebase?",
            "Merge preserves complete history with a merge commit; rebase creates a clean linear history.",
            "Git merge combines branches with a new merge commit preserving branch lines, whereas rebase rewrites commits onto another branch to make history linear.",
            "`git merge` preserves historical accuracy by creating a dual-parent merge commit without rewriting past SHAs, while `git rebase` creates a clean, linear commit history by replaying commits as new objects."
        ),
        (
            "What is a Pull Request (PR)?",
            "A Pull Request proposes merging code changes into a main branch.",
            "A Pull Request is a GitHub collaboration feature where a developer submits proposed code changes for review before merging them into the main branch.",
            "A Pull Request (PR) is a collaborative review mechanism on platforms like GitHub where a contributor proposes merging a feature branch into a target branch, facilitating code review, CI test runs, and discussion."
        ),
        (
            "What is .gitignore?",
            "A .gitignore file specifies untracked files that Git should ignore.",
            "A `.gitignore` file is a text file containing patterns of filenames and folders that Git should purposely not track or commit.",
            "A `.gitignore` file contains rules and glob patterns instructing Git to ignore specified files, directories, temporary build outputs, virtual environments, and sensitive keys from version tracking."
        ),
        (
            "What is git stash?",
            "git stash temporarily saves uncommitted changes so you can switch branches.",
            "The `git stash` command shelves your modified uncommitted work temporarily, giving you a clean working directory without committing.",
            "`git stash` saves uncommitted modifications (staged and unstaged working tree changes) onto an internal storage stack, resetting the working directory to match the HEAD commit so you can switch tasks cleanly."
        ),
        (
            "What is git status?",
            "git status displays the state of your working directory and staging area.",
            "The `git status` command shows which files are modified, staged, or untracked in your current Git project.",
            "`git status` inspects the working tree and staging index, displaying untracked files, staged changes ready for commit, unstaged modifications, and branch synchronization status relative to remote tracking."
        ),
        (
            "What is git log?",
            "git log shows the commit history of a repository.",
            "The `git log` command displays a chronological list of commits in the current branch including commit IDs, authors, and dates.",
            "`git log` queries and outputs the repository commit history in reverse chronological order, showing commit SHAs, author identity, timestamps, commit descriptions, and branch pointer positions."
        ),
        (
            "What is a commit hash in Git?",
            "A commit hash is a unique SHA-1 identifier for a commit.",
            "A commit hash is a 40-character hexadecimal string that uniquely identifies a specific commit snapshot in Git.",
            "A Git commit hash is a unique 160-bit (40-hex-character) cryptographic SHA-1 checksum generated from commit contents, parent commit references, author metadata, and tree state to guarantee repository integrity."
        ),
        (
            "What is git reset?",
            "git reset undoes changes by moving the branch pointer back.",
            "The `git reset` command moves the current HEAD branch pointer to a specified past commit, optionally unstaging or discarding changes.",
            "`git reset` adjusts the current branch pointer to a specified commit state, available in `--soft` (keeps changes staged), `--mixed` (default, keeps changes unstaged), and `--hard` (discards all working tree changes)."
        ),
        (
            "What is git revert?",
            "git revert creates a new commit that undoes a previous commit.",
            "The `git revert` command creates a new commit that applies inverse changes to safely undo a previous commit without rewriting history.",
            "`git revert <commit>` safely cancels the effects of an existing commit by calculating its inverse diff and generating a brand new commit, preserving history without destructive rewriting on shared branches."
        )
    ],
    "AI & Machine Learning": [
        (
            "What is Artificial Intelligence (AI)?",
            "AI is computer systems capable of performing tasks requiring human intelligence.",
            "Artificial Intelligence is a field of computer science focused on building smart machines capable of learning, reasoning, and problem solving.",
            "Artificial Intelligence (AI) is a multidisciplinary domain of computer science dedicated to engineering computational systems that simulate cognitive functions such as pattern recognition, reasoning, perception, and decision-making."
        ),
        (
            "What is Machine Learning (ML)?",
            "Machine Learning is AI that learns from data without explicit programming.",
            "Machine Learning is a subset of AI where computers use statistical algorithms to learn patterns and make predictions from data.",
            "Machine Learning (ML) is an algorithmic subfield of AI that builds mathematical models trained on empirical data to make predictions, infer patterns, or optimize performance without hardcoded heuristic rules."
        ),
        (
            "What is Deep Learning (DL)?",
            "Deep Learning is machine learning based on multi-layered neural networks.",
            "Deep Learning is a specialized branch of machine learning that uses deep artificial neural networks with many layers to process complex data.",
            "Deep Learning (DL) is a subset of machine learning inspired by biological neurology, utilizing deep artificial neural network architectures with multiple hidden layers to extract hierarchical feature representations."
        ),
        (
            "What is the difference between AI, ML, and DL?",
            "AI is the broad field, ML is learning from data, and DL is deep neural networks.",
            "AI is the overarching concept of smart machines; ML is the technique of learning from data; DL is a subset of ML using multi-layered neural networks.",
            "Artificial Intelligence is the broad umbrella discipline; Machine Learning is the specific sub-discipline focusing on statistical learning models; Deep Learning is a specialized sub-branch of ML utilizing deep layered neural networks."
        ),
        (
            "What is Supervised Learning?",
            "Supervised learning trains models on labeled input-output data.",
            "Supervised learning is an ML approach where a model is trained using labeled examples to learn the relationship between inputs and outputs.",
            "Supervised learning is a machine learning paradigm where algorithms learn a mapping function from input features to target labels using training datasets containing known ground-truth input-output pairs."
        ),
        (
            "What is Unsupervised Learning?",
            "Unsupervised learning finds hidden patterns in unlabeled data.",
            "Unsupervised learning is an ML approach where algorithms discover hidden patterns, groupings, or structures in data without labeled outputs.",
            "Unsupervised learning is a machine learning methodology where models analyze unlabeled datasets without explicit supervisor feedback, discovering inherent structures, clusters, or latent dimensionality."
        ),
        (
            "What is Reinforcement Learning?",
            "Reinforcement learning trains agents through rewards and penalties.",
            "Reinforcement learning is an ML technique where an autonomous agent learns optimal behaviors by taking actions in an environment to maximize cumulative rewards.",
            "Reinforcement Learning (RL) is an interactive learning paradigm where an agent learns an optimal policy through trial-and-error interactions with a dynamic environment, receiving scalar reward or penalty signals."
        ),
        (
            "What is the difference between classification and regression?",
            "Classification predicts categories; regression predicts continuous numbers.",
            "Classification predicts discrete class labels like spam or not spam, while regression predicts continuous numeric values like house prices.",
            "Classification algorithms assign input features to discrete categorical classes (binary or multi-class), whereas regression algorithms estimate continuous numerical values along a continuous scale."
        ),
        (
            "What is overfitting in machine learning?",
            "Overfitting is when a model memorizes training data and fails on new data.",
            "Overfitting occurs when an ML model learns training noise and details too well, performing great on training data but poorly on unseen test data.",
            "Overfitting is a modeling failure where an overly complex model learns spurious patterns and noise in the training set, achieving minimal training loss but demonstrating poor generalization performance on test data."
        ),
        (
            "What is underfitting in machine learning?",
            "Underfitting is when a model is too simple to learn the data patterns.",
            "Underfitting happens when a model is too basic to capture the underlying relationships in the data, performing poorly on both training and test sets.",
            "Underfitting occurs when an algorithm is too simplistic (high bias) or insufficiently trained to capture the underlying structure of the data, resulting in poor predictive performance on both training and test sets."
        ),
        (
            "What is the bias-variance tradeoff?",
            "It is the balance between model simplicity (bias) and sensitivity (variance).",
            "The bias-variance tradeoff balances underfitting (high bias from too-simple models) and overfitting (high variance from overly sensitive models).",
            "The bias-variance tradeoff is a central machine learning problem balancing underfitting errors (bias: erroneous assumptions) and overfitting errors (variance: sensitivity to training fluctuations) to minimize total generalization error."
        ),
        (
            "What is an Artificial Neural Network (ANN)?",
            "An ANN is a computing system inspired by biological brain networks.",
            "An Artificial Neural Network is a machine learning architecture made of interconnected artificial neurons organized in input, hidden, and output layers.",
            "An Artificial Neural Network (ANN) is a computational model inspired by biological neural networks, consisting of interconnected node layers where each node applies weighted linear combinations and activation functions."
        ),
        (
            "What is an activation function in neural networks?",
            "An activation function introduces non-linearity to a neuron's output.",
            "An activation function determines whether a neuron should fire by transforming the weighted sum of inputs into a non-linear output.",
            "An activation function introduces non-linear mathematical transformations (e.g., ReLU, Sigmoid, Tanh) into neural network nodes, enabling the network to learn complex non-linear patterns in high-dimensional data."
        ),
        (
            "What is ReLU in deep learning?",
            "ReLU is an activation function that outputs zero for negative inputs and the input itself for positive inputs.",
            "Rectified Linear Unit (ReLU) is a popular activation function defined as f(x) = max(0, x), widely used for its computational simplicity and speed.",
            "Rectified Linear Unit (ReLU) is a widely adopted piecewise linear activation function defined by f(x) = max(0, x), which alleviates the vanishing gradient problem and accelerates training convergence."
        ),
        (
            "What is backpropagation in neural networks?",
            "Backpropagation calculates gradients of the loss function to update weights.",
            "Backpropagation is an algorithm that computes the gradient of the error with respect to each weight, propagating backwards to update network parameters.",
            "Backpropagation is an efficient training algorithm that applies the mathematical chain rule of calculus backward through network layers, calculating partial derivatives of the loss function to guide gradient descent weight updates."
        ),
        (
            "What is gradient descent?",
            "Gradient descent is an optimization algorithm that minimizes the loss function.",
            "Gradient descent is an iterative optimization method used in machine learning to find the parameter weights that minimize prediction error.",
            "Gradient descent is a first-order iterative optimization algorithm that updates model parameters in the opposite direction of the loss function gradient, navigating parameter space to locate a local or global minimum."
        ),
        (
            "What is a loss function?",
            "A loss function measures the error between predicted and actual values.",
            "A loss function evaluates how well an ML model performs by calculating the mathematical difference between predicted outputs and real target values.",
            "A loss function (or cost function) is a mathematical objective metric that quantifies the discrepancy between model predictions and true observed values, serving as the optimization target minimized during training."
        ),
        (
            "What is a training, validation, and test dataset split?",
            "Training teaches the model; validation tunes hyperparameters; test evaluates final performance.",
            "Data is split into training (learn patterns), validation (tune parameters and avoid overfitting), and testing (unbiased final evaluation).",
            "Dataset partitioning divides data into a Training set (for learning model weights), a Validation set (for hyperparameter tuning and model selection), and a Test set (for unbiased final performance evaluation)."
        ),
        (
            "What is cross-validation in machine learning?",
            "Cross-validation tests model accuracy by splitting data into multiple rotating folds.",
            "Cross-validation (like k-fold) evaluates a model's generalization by dividing data into k subsets, training on k-1 folds and testing on the remaining fold iteratively.",
            "K-Fold cross-validation is a statistical resampling technique that partitions data into $k$ equal subsets, iteratively training on $k-1$ folds while validating on the remaining fold to generate an aggregated, robust performance estimate."
        ),
        (
            "What is a Convolutional Neural Network (CNN)?",
            "A CNN is a deep learning network designed for image and visual processing.",
            "A Convolutional Neural Network is a specialized deep neural network that uses convolutional filters to automatically extract visual features from images.",
            "A Convolutional Neural Network (CNN) is a deep neural architecture tailored for spatial grid data (such as images), employing parameterized convolution filters, pooling layers, and fully connected heads to extract visual features."
        ),
        (
            "What is Natural Language Processing (NLP)?",
            "NLP is AI focused on understanding and generating human language.",
            "Natural Language Processing (NLP) is a branch of AI that enables computers to read, interpret, understand, and generate human languages.",
            "Natural Language Processing (NLP) is an interdisciplinary field of artificial intelligence and computational linguistics dedicated to enabling computers to process, analyze, comprehend, and generate human language."
        ),
        (
            "What is a Large Language Model (LLM)?",
            "An LLM is a massive deep learning model trained on vast amounts of text.",
            "A Large Language Model (LLM) is a Transformer-based neural network with billions of parameters trained on vast text datasets to generate natural human text.",
            "A Large Language Model (LLM) is a foundational neural network architecture (predominantly Transformer-based with billions of parameters) pre-trained on massive web-scale text corpora to perform language understanding and generation."
        ),
        (
            "What is transfer learning in machine learning?",
            "Transfer learning reuses a model trained on one task for a related task.",
            "Transfer learning is a technique where a pre-trained model is fine-tuned on a smaller specific dataset instead of training from scratch.",
            "Transfer learning is a machine learning paradigm that leverages feature representations and weights learned by a model pre-trained on a massive dataset, adapting them via fine-tuning to a new, specialized domain task."
        ),
        (
            "What is precision and recall in classification?",
            "Precision measures accuracy of positive predictions; recall measures coverage of actual positives.",
            "Precision is the proportion of positive predictions that were correct, while recall is the proportion of actual positive cases the model found.",
            "Precision ($TP / (TP + FP)$) measures the accuracy of positive predictions, whereas Recall ($TP / (TP + FN)$) quantifies the model's sensitivity in capturing all actual positive instances."
        ),
        (
            "What is an epoch in deep learning?",
            "An epoch is one complete pass through the entire training dataset.",
            "In machine learning, an epoch represents one complete cycle where the neural network sees every sample in the training dataset once.",
            "An epoch is a hyperparameter defining one complete forward and backward training pass of the entire dataset through a neural network during model optimization."
        )
    ],
    "Cybersecurity": [
        (
            "What is cybersecurity?",
            "Cybersecurity is the protection of computer systems and networks from attacks.",
            "Cybersecurity is the practice of protecting systems, networks, and data from digital attacks, theft, and unauthorized access.",
            "Cybersecurity is the discipline and body of technologies, processes, and controls designed to defend computer systems, networks, hardware devices, and digital assets against cyberattacks and unauthorized exploitation."
        ),
        (
            "What is the CIA Triad in cybersecurity?",
            "Confidentiality, Integrity, and Availability.",
            "The CIA Triad represents the three core security pillars: Confidentiality (privacy), Integrity (accuracy), and Availability (accessibility).",
            "The CIA Triad is a foundational information security benchmark comprising Confidentiality (restricting access to authorized users), Integrity (preventing unauthorized modification), and Availability (ensuring uptime access)."
        ),
        (
            "What is the difference between authentication and authorization?",
            "Authentication verifies who you are; authorization verifies what you are allowed to do.",
            "Authentication confirms a user's identity through credentials, while authorization determines what resources the authenticated user has permission to access.",
            "Authentication (AuthN) is the security process of verifying the identity of a subject (user or service), whereas Authorization (AuthZ) verifies the permissions, roles, and privileges granted to that verified identity."
        ),
        (
            "What is encryption in cybersecurity?",
            "Encryption converts readable data into unreadable ciphertext for security.",
            "Encryption is the process of scrambling readable plaintext into unreadable ciphertext using a mathematical key so only authorized parties can read it.",
            "Encryption is a cryptographic process that transforms readable plaintext into obfuscated ciphertext using a mathematical algorithm and cryptographic key, ensuring confidentiality in transit and at rest."
        ),
        (
            "What is the difference between symmetric and asymmetric encryption?",
            "Symmetric uses one shared key; asymmetric uses a public and private key pair.",
            "Symmetric encryption uses the exact same key to encrypt and decrypt, while asymmetric encryption uses a public key to encrypt and a private key to decrypt.",
            "Symmetric encryption (e.g., AES) relies on a single shared secret key for encryption and decryption, whereas asymmetric encryption (e.g., RSA) uses mathematically linked key pairs: a public key for encryption and private key for decryption."
        ),
        (
            "What is hashing in cybersecurity?",
            "Hashing is a one-way conversion of data into a fixed-length string.",
            "Hashing is a one-way cryptographic function that transforms data into a unique fixed-length hash value that cannot be reversed.",
            "Cryptographic hashing is a deterministic one-way algorithm (e.g., SHA-256, bcrypt) that maps arbitrary-length data into a fixed-size digest, designed to be computationally infeasible to invert."
        ),
        (
            "What is the difference between encryption and hashing?",
            "Encryption is reversible two-way; hashing is irreversible one-way.",
            "Encryption converts data into ciphertext that can be decrypted back with a key, while hashing creates a one-way fingerprint that cannot be reversed.",
            "Encryption is a bidirectional process designed to protect confidentiality where ciphertext can be decoded back into plaintext with the correct key, whereas hashing is a unidirectional mathematical digest used for integrity."
        ),
        (
            "What is a firewall in cybersecurity?",
            "A firewall blocks unauthorized network traffic based on security rules.",
            "A firewall is a network defense system that monitors and filters incoming and outgoing network traffic according to predefined security rules.",
            "A firewall is a defensive security boundary implemented in software or hardware that inspects network packets, enforcing access control policies by blocking or allowing traffic based on ports, protocols, and IP addresses."
        ),
        (
            "What is phishing?",
            "Phishing is a fraudulent attempt to steal sensitive information through deceptive messages.",
            "Phishing is a social engineering attack where attackers impersonate trustworthy entities via email or websites to trick victims into revealing passwords or credit cards.",
            "Phishing is a social engineering attack where malicious actors impersonate legitimate organizations via deceptive emails, SMS, or websites to lure users into revealing sensitive credentials, financial data, or downloading malware."
        ),
        (
            "What is malware?",
            "Malware is malicious software designed to harm or exploit computer systems.",
            "Malware (malicious software) is any harmful code, program, or file designed to damage, exploit, or gain unauthorized access to computers.",
            "Malware (malicious software) is an umbrella term encompassing intrusive code—including viruses, worms, trojans, ransomware, spyware, and adware—engineered by cybercriminals to compromise system integrity and steal data."
        ),
        (
            "What is ransomware?",
            "Ransomware is malware that encrypts files and demands payment for the decryption key.",
            "Ransomware is malicious software that locks or encrypts a victim's files, demanding a ransom payment in exchange for the decryption key.",
            "Ransomware is an extortion-based malware strain that systematically encrypts files on infected target systems, demanding cryptocurrency payments in exchange for decryptor keys while threatening data publication."
        ),
        (
            "What is a Denial of Service (DoS) attack?",
            "A DoS attack floods a system with traffic to make it unavailable to users.",
            "A DoS attack overwhelms a server or network with excessive traffic so that legitimate users cannot access its services.",
            "A Denial of Service (DoS) attack is a cyberattack that seeks to make a machine or network resource unavailable to intended users by flooding the target with fake traffic or exploiting system crashes."
        ),
        (
            "What is a Distributed Denial of Service (DDoS) attack?",
            "A DDoS attack uses multiple compromised machines to flood and crash a target.",
            "A DDoS attack coordinates many internet-connected compromised computers (botnets) to flood a target server with traffic until it crashes.",
            "A Distributed Denial of Service (DDoS) attack is a large-scale cyber offensive where an attacker commands distributed networks of compromised machines (botnets) to overwhelm target servers with traffic."
        ),
        (
            "What is a Man-in-the-Middle (MitM) attack?",
            "A MitM attack is when an attacker intercepts communication between two parties.",
            "A Man-in-the-Middle attack occurs when a hacker secretly intercepts and potentially alters communication between two trusting parties without their knowledge.",
            "A Man-in-the-Middle (MitM) attack is a security vulnerability where an attacker positions themselves between two communicating endpoints to eavesdrop on, intercept, or modify transmitted data."
        ),
        (
            "What is Cross-Site Scripting (XSS)?",
            "XSS is an attack that injects malicious scripts into trusted websites.",
            "Cross-Site Scripting (XSS) is a vulnerability where attackers inject malicious JavaScript into web pages viewed by other users.",
            "Cross-Site Scripting (XSS) is a client-side code injection flaw where an attacker embeds malicious client scripts into trusted web pages, executing in victims' browsers to hijack sessions or steal cookies."
        ),
        (
            "What is Cross-Site Request Forgery (CSRF)?",
            "CSRF tricks an authenticated user into submitting unwanted actions.",
            "Cross-Site Request Forgery (CSRF) is an attack that forces a logged-in user's browser to execute unwanted actions on a trusted web application.",
            "Cross-Site Request Forgery (CSRF) is an exploit where an unauthorized web application tricks an authenticated victim's browser into transmitting unauthorized HTTP commands to a vulnerable target site."
        ),
        (
            "What is Multi-Factor Authentication (MFA)?",
            "MFA requires two or more verification factors to log in.",
            "Multi-Factor Authentication (MFA) is a security process requiring users to supply at least two different pieces of evidence to verify identity.",
            "Multi-Factor Authentication (MFA) is an access control method requiring users to provide two or more distinct validation credentials: something you know (password), something you have (OTP token), or something you are (biometrics)."
        ),
        (
            "What is a VPN and how does it improve security?",
            "A VPN encrypts internet traffic and hides your IP address.",
            "A Virtual Private Network (VPN) encrypts internet connections to shield user online activity and data from snooping on untrusted networks.",
            "A VPN enhances cybersecurity by encapsulating and encrypting all network packets within a secure tunnel, masking the user's origin IP address and safeguarding data from interception on public Wi-Fi."
        ),
        (
            "What is Zero Trust security?",
            "Zero Trust is a security model that never trusts and always verifies.",
            "Zero Trust is a modern security architecture that requires every user and device, inside or outside the network, to be authenticated and authorized continuously.",
            "Zero Trust is a strategic cybersecurity paradigm operating under the principle 'never trust, always verify', requiring continuous strict identity verification, least privilege access, and microsegmentation for all users and devices."
        ),
        (
            "What is penetration testing?",
            "Penetration testing is authorized simulated cyberattacks to find security weaknesses.",
            "Penetration testing (pen testing) is an authorized, controlled security assessment where ethical hackers test systems to discover vulnerabilities.",
            "Penetration testing is an authorized security audit where certified ethical hackers perform simulated cyberattacks against an organization's infrastructure to identify, exploit, and remediate security vulnerabilities."
        ),
        (
            "What is a zero-day vulnerability?",
            "A zero-day is a security flaw that is unknown to the software vendor.",
            "A zero-day vulnerability is a newly discovered security flaw that the developers have had zero days to patch, leaving systems exposed to exploits.",
            "A zero-day vulnerability is a previously undisclosed software flaw unknown to the product vendor, meaning zero patches exist to mitigate it and leaving systems vulnerable to immediate zero-day exploits."
        ),
        (
            "What is a digital signature?",
            "A digital signature verifies the authenticity and integrity of a digital message.",
            "A digital signature uses asymmetric cryptography to prove that a message or document came from a specific sender and was not altered.",
            "A digital signature is a mathematical cryptographic mechanism binding a private key to a document hash, enabling the recipient with the corresponding public key to verify sender authenticity and data integrity."
        ),
        (
            "What is salting in password storage?",
            "Salting adds random data to passwords before hashing them.",
            "Salting is the practice of adding unique random strings to passwords before hashing to protect against rainbow table attacks.",
            "Password salting is a cryptographic defense that prepends or appends a unique cryptographically random string to plaintext passwords prior to hashing, ensuring identical passwords yield unique hashes and neutralizing rainbow tables."
        ),
        (
            "What is social engineering in cybersecurity?",
            "Social engineering is manipulating people into giving up confidential information.",
            "Social engineering is psychological manipulation of individuals into disclosing sensitive information or performing security actions.",
            "Social engineering is the non-technical exploitation of human psychology (trust, urgency, fear) to trick individuals into divulging confidential credentials, granting physical access, or bypassing security controls."
        ),
        (
            "What is a security patch?",
            "A security patch is a software update that fixes security vulnerabilities.",
            "A security patch is a software update released by developers to fix discovered vulnerabilities and prevent exploits.",
            "A security patch is a targeted code update released by software vendors designed specifically to remediate identified security flaws, weaknesses, and potential exploit vectors in released applications."
        )
    ],
    "Cloud Computing": [
        (
            "What is cloud computing?",
            "Cloud computing is on-demand delivery of computing services over the internet.",
            "Cloud computing is the delivery of computing services—including servers, storage, databases, and software—over the internet on a pay-as-you-go basis.",
            "Cloud computing is an on-demand computing paradigm that provides shared configurable pools of computing resources (servers, storage, networks, applications) accessible over the internet with pay-as-you-go pricing."
        ),
        (
            "What are the three main cloud service models?",
            "IaaS, PaaS, and SaaS.",
            "The primary cloud computing models are Infrastructure as a Service (IaaS), Platform as a Service (PaaS), and Software as a Service (SaaS).",
            "The three foundational cloud service tiers are IaaS (Infrastructure: raw VMs/networking), PaaS (Platform: managed runtimes/databases), and SaaS (Software: end-user software delivered over the web)."
        ),
        (
            "What is Infrastructure as a Service (IaaS)?",
            "IaaS provides virtualized hardware, storage, and networking over the cloud.",
            "IaaS provides fundamental compute, storage, and networking resources on demand, like AWS EC2 or Google Compute Engine.",
            "Infrastructure as a Service (IaaS) delivers raw, virtualized hardware resources—including virtual machines, block storage, and software-defined networks—giving customers full operating system control."
        ),
        (
            "What is Platform as a Service (PaaS)?",
            "PaaS provides a managed platform for developing and running apps without managing servers.",
            "PaaS gives developers hardware and software tools over the internet to build applications without worrying about underlying infrastructure.",
            "Platform as a Service (PaaS) offers a fully managed development and deployment environment (e.g., Heroku, AWS Elastic Beanstalk) managing OS patching and scaling so developers can focus solely on application code."
        ),
        (
            "What is Software as a Service (SaaS)?",
            "SaaS delivers complete applications over the web on a subscription basis.",
            "SaaS is a software distribution model where a complete application is hosted by a vendor and accessible to users via web browsers, like Gmail or Google Drive.",
            "Software as a Service (SaaS) delivers centrally hosted, fully managed end-user software applications over web browsers or mobile apps, eliminating local installation, maintenance, and manual updates."
        ),
        (
            "What is the difference between Public, Private, and Hybrid clouds?",
            "Public is shared, Private is dedicated to one organization, and Hybrid combines both.",
            "Public clouds serve multiple customers; private clouds are dedicated exclusively to one business; hybrid clouds blend both.",
            "Public clouds provide multi-tenant shared infrastructure over the internet (AWS/GCP); Private clouds offer dedicated single-tenant infrastructure; Hybrid clouds orchestrate workloads across both environments."
        ),
        (
            "What are the major cloud service providers?",
            "AWS, Microsoft Azure, and Google Cloud Platform (GCP).",
            "The dominant cloud providers are Amazon Web Services (AWS), Microsoft Azure, and Google Cloud Platform (GCP).",
            "The leading hyperscale cloud providers are Amazon Web Services (AWS), Microsoft Azure, Google Cloud Platform (GCP), alongside IBM Cloud, Oracle Cloud Infrastructure (OCI), and Alibaba Cloud."
        ),
        (
            "What is a virtual machine (VM) in the cloud?",
            "A VM is a software-based computer running inside a physical server.",
            "A virtual machine is an emulation of a physical computer running its own operating system on top of a hypervisor.",
            "A Virtual Machine (VM) is an isolated software-defined computing instance running a guest operating system on physical server hardware abstracted by a virtualization layer called a hypervisor."
        ),
        (
            "What is a container in cloud computing?",
            "A container packages an application and its dependencies together to run anywhere.",
            "A container is a lightweight package that bundles software code with all its dependencies so it runs reliably across different environments.",
            "A container is a lightweight, standalone executable software package that bundles application code, runtime, system tools, and libraries, sharing the host OS kernel via namespaces and cgroups (e.g., Docker)."
        ),
        (
            "What is the difference between a virtual machine and a container?",
            "VMs have full guest operating systems; containers share the host operating system kernel.",
            "Virtual machines virtualize hardware and run complete separate OS instances, while containers are lightweight and share the host operating system kernel.",
            "Virtual machines include a full guest OS with heavy memory footprint and boot times, whereas containers share the underlying host operating system kernel, providing lightweight footprint and near-instant startup."
        ),
        (
            "What is Docker?",
            "Docker is a platform for building, sharing, and running containerized apps.",
            "Docker is an open-source containerization platform that allows developers to package and run applications in isolated containers.",
            "Docker is an open-source containerization runtime and platform that standardizes software packaging, enabling developers to build, ship, and run distributed applications in lightweight portable containers."
        ),
        (
            "What is Kubernetes?",
            "Kubernetes is an open-source system for automating container management.",
            "Kubernetes (K8s) is a container orchestration platform that automates deploying, scaling, and managing containerized applications.",
            "Kubernetes is an open-source container orchestration system originally developed by Google that automates deployment, horizontal scaling, self-healing, load balancing, and management of containerized workloads."
        ),
        (
            "What is serverless computing?",
            "Serverless runs code on demand without provisioning or managing servers.",
            "Serverless computing is a cloud execution model where cloud providers automatically manage server infrastructure, charging only when code runs.",
            "Serverless computing (Function-as-a-Service / FaaS, e.g., AWS Lambda) is an event-driven execution architecture where developers deploy isolated functions, and the cloud provider manages dynamic server allocation and billing per millisecond."
        ),
        (
            "What is AWS Lambda?",
            "AWS Lambda is a serverless compute service from Amazon.",
            "AWS Lambda is an event-driven serverless service that runs code automatically in response to events without managing servers.",
            "AWS Lambda is Amazon's flagship serverless computing service that executes code in response to system triggers (HTTP requests, S3 uploads, database events), automatically managing runtime execution and scaling to zero."
        ),
        (
            "What is cloud elasticity?",
            "Elasticity is the ability to dynamically scale computing resources up or down on demand.",
            "Cloud elasticity is a system's ability to automatically expand or shrink computing resources in real time to match changing workloads.",
            "Cloud elasticity is the automated capability of a cloud environment to dynamically provision and de-provision computing, storage, and network resources in real time according to immediate traffic demands."
        ),
        (
            "What is cloud scalability?",
            "Scalability is the capability to handle growing workloads by adding resources.",
            "Scalability is the infrastructure's capacity to handle increased traffic and workload by adding more capacity (vertically or horizontally).",
            "Cloud scalability is the architectural capacity of an infrastructure to accommodate growing workloads through planned capacity upgrades, either scaling vertically (upgrading CPU/RAM) or horizontally (adding nodes)."
        ),
        (
            "What is the difference between horizontal and vertical scaling?",
            "Horizontal adds more machines; vertical adds more power to the existing machine.",
            "Vertical scaling (scale-up) adds more CPU or RAM to an existing server, while horizontal scaling (scale-out) adds more server instances to distribute the load.",
            "Vertical scaling (scale up) increases the hardware capacity (CPU, RAM, disk) of a single server, while horizontal scaling (scale out) adds more server nodes to a distributed cluster behind a load balancer."
        ),
        (
            "What is a load balancer in cloud computing?",
            "A load balancer distributes incoming network traffic across multiple servers.",
            "A load balancer distributes incoming application traffic evenly across multiple healthy servers to prevent overload and ensure high availability.",
            "A load balancer is an architectural appliance (Layer 4 or Layer 7) that distributes incoming network requests across a pool of backend servers using algorithms like round-robin or least connections to optimize throughput."
        ),
        (
            "What is object storage in the cloud?",
            "Object storage stores data as discrete objects with metadata, like AWS S3.",
            "Object storage is a scalable storage architecture that manages data as individual objects with unique IDs and metadata, ideal for unstructured data.",
            "Cloud object storage (such as Amazon S3 or Google Cloud Storage) stores data as independent objects consisting of file data, custom metadata, and a globally unique identifier, offering massive scalability for unstructured files."
        ),
        (
            "What is high availability in cloud computing?",
            "High availability ensures systems remain operational with minimal downtime.",
            "High availability (HA) means designing cloud infrastructure with redundancy so that services remain accessible even if components fail.",
            "High availability (HA) is an architectural characteristic that guarantees systems remain operational with minimal downtime (e.g., 99.99% uptime) through automated failover, redundant components, and multi-region replication."
        ),
        (
            "What is disaster recovery in cloud computing?",
            "Disaster recovery is policies and procedures to restore systems after a disaster.",
            "Cloud disaster recovery involves backing up critical data and maintaining standby infrastructure to restore operations quickly after a catastrophic failure.",
            "Disaster recovery (DR) is a strategic business continuity plan and technical framework that uses cloud replication, automated snapshots, and redundant failover regions to restore systems within specified RTO and RPO targets."
        ),
        (
            "What are RTO and RPO in disaster recovery?",
            "RTO is recovery time limit; RPO is acceptable data loss limit.",
            "Recovery Time Objective (RTO) is how quickly systems must be restored; Recovery Point Objective (RPO) is the maximum age of data that can be lost.",
            "Recovery Time Objective (RTO) defines the targeted maximum acceptable duration of system downtime after failure; Recovery Point Objective (RPO) defines the maximum acceptable age of lost data measured in time."
        ),
        (
            "What is multi-tenancy in cloud computing?",
            "Multi-tenancy is sharing the same computing infrastructure securely across multiple customers.",
            "Multi-tenancy is an architecture where multiple different customers (tenants) share the same physical resources or application while keeping their data isolated.",
            "Multi-tenancy is a cloud software architecture where a single physical hardware pool or software application instance serves multiple client organizations (tenants), while strictly maintaining data isolation and security."
        ),
        (
            "What is edge computing?",
            "Edge computing processes data closer to where it is generated rather than in a distant data center.",
            "Edge computing brings data processing, storage, and computation closer to the devices generating the data to reduce latency.",
            "Edge computing is a distributed computing paradigm that relocates data computation and storage closer to the physical location where data is produced (IoT devices, cell towers), dramatically reducing latency and bandwidth use."
        ),
        (
            "What is DevOps in the cloud?",
            "DevOps combines development and operations to deliver software faster.",
            "DevOps is a set of practices combining software development and IT operations to shorten the development lifecycle and deliver continuous software updates.",
            "DevOps is an organizational culture and operational philosophy that unifies software development (Dev) and IT operations (Ops) through automated CI/CD pipelines, infrastructure-as-code, and shared responsibility."
        )
    ],
    "Flutter": [
        (
            "What is Flutter?",
            "Flutter is an open-source UI software development kit by Google.",
            "Flutter is Google's UI toolkit used for building natively compiled cross-platform applications for mobile, web, and desktop from a single codebase.",
            "Flutter is an open-source UI framework developed by Google that enables cross-platform application development across iOS, Android, Web, and Desktop using the Dart programming language and a reactive widget architecture."
        ),
        (
            "What programming language is used to build Flutter apps?",
            "Flutter uses the Dart programming language.",
            "Flutter applications are written using Dart, an object-oriented, client-optimized programming language developed by Google.",
            "Flutter applications are programmed exclusively in Dart, an object-oriented, class-based language featuring both Just-In-Time (JIT) compilation for hot reload and Ahead-Of-Time (AOT) compilation for native production binaries."
        ),
        (
            "What is a Widget in Flutter?",
            "A widget is the basic building block of a Flutter user interface.",
            "In Flutter, almost everything is a widget; widgets describe what the user interface view should look like given their current configuration.",
            "A Widget in Flutter is an immutable declaration of a user interface element, serving as the foundational building block of the visual hierarchy that the Flutter rendering engine inflates into the render tree."
        ),
        (
            "What is the difference between a StatelessWidget and a StatefulWidget?",
            "StatelessWidget cannot change state; StatefulWidget can change state dynamically.",
            "A StatelessWidget is immutable and never changes during runtime, while a StatefulWidget can rebuild and update its appearance dynamically when internal state changes.",
            "A `StatelessWidget` is an immutable component whose properties cannot change once built, whereas a `StatefulWidget` is paired with a mutable `State` object that tracks dynamic state and triggers UI rebuilds via `setState()`."
        ),
        (
            "What does the setState() method do in Flutter?",
            "setState() notifies the framework that the internal state has changed and triggers a UI rebuild.",
            "Calling `setState()` in a StatefulWidget informs Flutter that the object's state changed, causing it to rerun the `build` method to refresh the UI.",
            "`setState()` is a core method in a `StatefulWidget` that executes a callback updating mutable variables and marks the widget element dirty, scheduling a rebuild of the widget subtree to reflect state changes."
        ),
        (
            "What is Hot Reload in Flutter?",
            "Hot Reload injects updated code into the running app instantly without losing state.",
            "Hot Reload is a Flutter developer feature that loads code changes into the running Dart Virtual Machine in seconds without restarting the app or losing current state.",
            "Hot Reload leverages Dart's JIT compilation to inject updated source code files directly into the active Dart VM, triggering automatic widget rebuilds in milliseconds while preserving the current app navigation and state."
        ),
        (
            "What is the difference between Hot Reload and Hot Restart in Flutter?",
            "Hot Reload keeps app state; Hot Restart destroys state and restarts the app.",
            "Hot Reload quickly updates code while keeping the current app state intact, whereas Hot Restart resets the app state completely and starts execution from the beginning.",
            "Hot Reload injects code changes while preserving the existing application state and widget memory, while Hot Restart recompiles the application, clears the state cache, and reruns the `main()` entrypoint from scratch."
        ),
        (
            "What is the build() method in Flutter?",
            "The build() method returns the widget tree that describes the UI.",
            "The `build()` method is called by the Flutter framework to render and return the widget hierarchy that represents the UI on the screen.",
            "The `build(BuildContext context)` method is a mandatory lifecycle function that evaluates current configuration and state, returning an immutable widget tree describing the visual representation for the given element."
        ),
        (
            "What is BuildContext in Flutter?",
            "BuildContext is a handle to the location of a widget in the widget tree.",
            "BuildContext is an object that identifies where a widget is situated within the overall Flutter widget tree.",
            "`BuildContext` is an abstraction representing the unique location and position of a specific widget within the global element tree, used to locate parent widgets, navigate routes, and access inherited themes."
        ),
        (
            "What is a Scaffold widget in Flutter?",
            "Scaffold provides the basic visual layout structure for a screen.",
            "The `Scaffold` widget implements the standard Material Design visual layout structure, offering slots for an AppBar, Body, Drawer, and FloatingActionButton.",
            "`Scaffold` is a top-level Material Design container widget providing a standardized structural framework with built-in properties for app bars, bottom navigation bars, drawers, floating action buttons, and snackbars."
        ),
        (
            "What is the difference between Column and Row widgets in Flutter?",
            "Column arranges children vertically; Row arranges children horizontally.",
            "A `Column` widget lays out its child widgets in a vertical list, while a `Row` widget lays out its child widgets in a horizontal line.",
            "`Column` is a multi-child layout widget that arranges child elements along the vertical axis (Y-axis), whereas `Row` positions child elements linearly along the horizontal axis (X-axis)."
        ),
        (
            "What is an Expanded widget in Flutter?",
            "Expanded makes a child widget fill the available space in a Row or Column.",
            "The `Expanded` widget expands a child of a Row, Column, or Flex so that the child fills all available free space along the main axis.",
            "`Expanded` is a layout widget that wraps children inside a `Flex`, `Row`, or `Column`, forcing the wrapped widget to expand and consume remaining available space along the main axis according to its `flex` factor."
        ),
        (
            "What is a Container widget in Flutter?",
            "A Container is a convenient widget combining painting, positioning, and sizing.",
            "A `Container` widget combines common layout, styling, padding, margins, borders, and background colors into a single versatile widget.",
            "A `Container` is a multi-purpose compositional widget that orchestrates common layout and painting behaviors, packaging sizing (width/height), padding, margin, decoration (borders/gradients), and transformation."
        ),
        (
            "What is pubspec.yaml in a Flutter project?",
            "pubspec.yaml is the project configuration and dependency management file.",
            "The `pubspec.yaml` file defines metadata, third-party package dependencies, fonts, and assets for a Flutter project.",
            "`pubspec.yaml` is the foundational YAML configuration file for Flutter and Dart projects that declares project metadata, SDK version constraints, external library dependencies from pub.dev, image assets, and custom fonts."
        ),
        (
            "What is state management in Flutter?",
            "State management is how you manage and share data across widgets.",
            "State management refers to techniques and architectures used to handle, update, and synchronize user data across different screens and widgets in a Flutter app.",
            "State management encompasses architectural patterns and libraries (Provider, Riverpod, Bloc) designed to maintain, update, and broadcast reactive application state reliably across decoupled widget hierarchies."
        ),
        (
            "What are popular state management approaches in Flutter?",
            "Provider, Riverpod, Bloc, and GetX.",
            "Common state management solutions in Flutter include Provider, Riverpod, BLoC (Business Logic Component), and GetX.",
            "Widely adopted Flutter state management architectures include Provider (InheritedWidget wrapper), Riverpod (compile-safe reactive state), BLoC/Cubit (stream-based reactive event architecture), and GetX."
        ),
        (
            "What is the BLoC pattern in Flutter?",
            "BLoC separates business logic from UI using streams.",
            "Business Logic Component (BLoC) is an architecture pattern that uses reactive programming and Dart streams to separate business logic from the user interface.",
            "The BLoC (Business Logic Component) pattern is an architectural standard created by Google that decouples UI rendering from business logic by routing user events into sinks and emitting state updates via reactive streams."
        ),
        (
            "What is an InheritedWidget in Flutter?",
            "InheritedWidget is a base class that lets data propagate down the widget tree efficiently.",
            "An `InheritedWidget` is a special Flutter widget that allows child widgets located deep in the tree to access shared data without passing it through every constructor.",
            "`InheritedWidget` is an efficient low-level Flutter base class that enables data to propagate down the widget tree, allowing registered dependent child widgets to rebuild automatically when the inherited data changes."
        ),
        (
            "What is Navigator in Flutter?",
            "Navigator manages a stack of screens/routes in a Flutter app.",
            "The `Navigator` widget manages app screens as a stack of route objects, using push and pop operations to move between pages.",
            "`Navigator` is a routing and navigation manager in Flutter that treats application screens as a LIFO stack of `Route` objects, providing methods like `push()` and `pop()` to transition between views."
        ),
        (
            "What is a FutureBuilder in Flutter?",
            "FutureBuilder is a widget that builds UI based on the latest snapshot of a Future.",
            "A `FutureBuilder` is a widget that listens to an asynchronous Future and automatically rebuilds its UI as the data loads, succeeds, or errors.",
            "`FutureBuilder` is a convenience widget that connects to a Dart `Future`, managing asynchronous state transitions and rendering different UI widgets depending on whether the connection is waiting, completed, or errored."
        ),
        (
            "What is a StreamBuilder in Flutter?",
            "StreamBuilder is a widget that rebuilds itself whenever new data arrives on a Stream.",
            "A `StreamBuilder` widget listens to an ongoing Stream of data events and updates its UI in real time every time a new event is emitted.",
            "`StreamBuilder` is an interactive widget that subscribes to a multi-event Dart `Stream`, automatically executing its builder function to render updated UI snapshots whenever new data or errors are emitted."
        ),
        (
            "What are Keys in Flutter?",
            "Keys preserve state when widgets move around the widget tree.",
            "Keys in Flutter provide unique identifiers for widgets to help the framework preserve their state when widgets are moved, reordered, or deleted.",
            "`Key` objects provide unique identifiers used by the Flutter element reconciliation algorithm to match widgets with existing element nodes, crucial for preserving state in stateful reorderable lists."
        ),
        (
            "What is the rendering engine behind Flutter?",
            "Flutter uses the Impeller and Skia graphics rendering engines.",
            "Flutter previously used Skia and now uses Impeller, a custom graphics engine that compiles directly to native platform shaders.",
            "Flutter renders interfaces directly onto platform canvases using its high-performance graphics engines: traditionally Skia and modernly Impeller, which precompiles shaders to eliminate runtime frame jank on iOS and Android."
        ),
        (
            "What are platform channels in Flutter?",
            "Platform channels let Flutter communicate with native Android and iOS code.",
            "Platform channels provide a messaging bridge between Dart code in Flutter and native code written in Java/Kotlin or Objective-C/Swift.",
            "Platform channels (MethodChannel, EventChannel) establish a bidirectional asynchronous message-passing bridge allowing Flutter Dart code to invoke host platform native APIs (Kotlin, Swift) and receive native callbacks."
        ),
        (
            "What is the difference between main() and runApp() in Flutter?",
            "main() starts the program; runApp() attaches the root widget to the screen.",
            "The `main()` function is the starting entry point of the Dart program, while `runApp()` initializes the Flutter engine and inflates the root widget.",
            "`main()` is the standard Dart execution entrypoint function, inside of which `runApp(Widget app)` is called to bind the given root widget to the Flutter framework and initialize the top-level render tree."
        )
    ],
    "Firebase": [
        (
            "What is Firebase?",
            "Firebase is a comprehensive app development platform by Google.",
            "Firebase is Google's Backend-as-a-Service (BaaS) platform providing databases, authentication, cloud storage, hosting, and analytics for web and mobile apps.",
            "Firebase is a cloud-based Backend-as-a-Service (BaaS) suite developed by Google that supplies developers with managed backend infrastructure, including databases, user authentication, serverless functions, and file storage."
        ),
        (
            "What is Cloud Firestore?",
            "Cloud Firestore is a flexible, scalable NoSQL cloud document database.",
            "Cloud Firestore is Firebase's flexible NoSQL document-oriented cloud database designed for mobile, web, and server development with real-time sync.",
            "Cloud Firestore is a scalable, cloud-hosted NoSQL document database from Firebase that organizes data into documents and collections, providing real-time data listeners, offline caching, and robust security rules."
        ),
        (
            "What is the Firebase Realtime Database?",
            "The Realtime Database is a cloud-hosted NoSQL database that stores data as one large JSON tree.",
            "Firebase Realtime Database is an original Firebase NoSQL database that syncs data between clients in real time and stores everything in a giant JSON tree.",
            "Firebase Realtime Database is a cloud-hosted NoSQL database that persists data as a single monolithic JSON tree, offering low-latency WebSocket synchronization across connected client devices."
        ),
        (
            "What is the difference between Cloud Firestore and Realtime Database?",
            "Firestore uses collections and documents; Realtime Database uses a single JSON tree.",
            "Cloud Firestore offers richer querying, deeper scaling, and document-collection structures, while Realtime Database is simpler with faster latency for basic JSON data.",
            "Cloud Firestore organizes data into modular collections and documents with advanced compound querying and multi-region scalability, whereas Realtime Database stores data in a large nested JSON tree with limited querying."
        ),
        (
            "What is Firebase Authentication?",
            "Firebase Authentication provides ready-to-use user sign-in and security.",
            "Firebase Authentication is a managed service that provides secure user login using passwords, phone numbers, and providers like Google, Apple, and GitHub.",
            "Firebase Authentication is an end-to-end identity management service supporting email/password logins, SMS verification, and OAuth federated identity providers (Google, Facebook, Apple) using industry-standard JWT tokens."
        ),
        (
            "What are Firebase Cloud Functions?",
            "Cloud Functions run serverless backend code in response to events.",
            "Firebase Cloud Functions allow you to run serverless backend JavaScript, TypeScript, or Python code automatically in response to database or HTTP events.",
            "Firebase Cloud Functions is a serverless execution environment that automatically triggers backend code execution in response to platform events (Firestore modifications, Auth creations, Analytics logs) or direct HTTP requests."
        ),
        (
            "What is Firebase Cloud Storage?",
            "Cloud Storage stores and serves user-generated files like photos and videos.",
            "Firebase Cloud Storage is a secure object storage service built for uploading and downloading user-generated files such as images, audio, and videos.",
            "Firebase Cloud Storage is a scalable object storage solution backed by Google Cloud Storage, engineered specifically for uploading, storing, and serving large user-generated media files with automatic network resumption."
        ),
        (
            "What are Firebase Security Rules?",
            "Security Rules define who can read and write data in Firebase.",
            "Firebase Security Rules determine how your Firestore, Storage, and Realtime Database data is protected from unauthorized access.",
            "Firebase Security Rules provide a declarative language executed on Google servers that evaluates incoming database and storage operations against authorization parameters (such as `request.auth`) to enforce data security."
        ),
        (
            "What is Firebase Cloud Messaging (FCM)?",
            "FCM is a cross-platform messaging service for sending push notifications.",
            "Firebase Cloud Messaging (FCM) is a free cross-platform messaging solution that lets you reliably send push notifications and messages to client devices.",
            "Firebase Cloud Messaging (FCM) is an enterprise-grade cross-platform push messaging service that enables server backends to deliver targeted notifications and background data payloads across Android, iOS, and Web clients."
        ),
        (
            "What is Firebase Hosting?",
            "Firebase Hosting provides fast, secure static web hosting.",
            "Firebase Hosting is a managed cloud hosting service for static websites, single-page applications, and microservices served over a global CDN.",
            "Firebase Hosting is a production-grade web hosting service delivering static HTML, CSS, JavaScript assets, and serverless web applications through a global Content Delivery Network (CDN) with free automated SSL certificates."
        ),
        (
            "What is Firebase Crashlytics?",
            "Crashlytics is a real-time crash reporting tool for mobile apps.",
            "Firebase Crashlytics is a lightweight real-time crash reporter that helps developers track, prioritize, and fix app stability issues.",
            "Firebase Crashlytics is an automated real-time crash reporting solution that monitors application crashes, aggregates stack traces, highlights root causes, and categorizes crash severity to maintain app reliability."
        ),
        (
            "What is Firebase Remote Config?",
            "Remote Config lets you change app behavior and appearance without publishing an update.",
            "Firebase Remote Config is a cloud service that lets you dynamically alter app features and look-and-feel without releasing a new app store version.",
            "Firebase Remote Config is a dynamic cloud-managed key-value store that allows developers to change application behavior, feature flags, and UI presentation on the fly without republishing an update to the app store."
        ),
        (
            "What is Firebase Analytics?",
            "Firebase Analytics tracks user behavior and app usage metrics.",
            "Google Analytics for Firebase provides free, unlimited reporting on user engagement, events, and demographics in mobile and web apps.",
            "Google Analytics for Firebase is an app measurement solution that captures user engagement events, conversion funnels, user retention metrics, and audience demographics to optimize user experience and marketing campaigns."
        ),
        (
            "What is Firebase Performance Monitoring?",
            "It tracks the speed and performance of your mobile and web apps.",
            "Firebase Performance Monitoring gives developers insights into app speed, screen rendering traces, and network request latencies.",
            "Firebase Performance Monitoring is an automated diagnostic service that profiles client application runtime performance, tracking app startup duration, HTTP network latency, and UI frame rendering drops."
        ),
        (
            "What is the Firebase Emulator Suite?",
            "The Emulator Suite lets you run Firebase services locally for development and testing.",
            "The Firebase Local Emulator Suite is a set of local development tools that emulate Firestore, Auth, Functions, and Storage on your computer.",
            "The Firebase Local Emulator Suite is a local developer testing environment that mimics core Firebase cloud services (Firestore, Auth, Functions, Storage) locally, enabling offline prototyping and automated testing."
        ),
        (
            "What are documents and collections in Cloud Firestore?",
            "Collections are containers of documents; documents store key-value data.",
            "In Cloud Firestore, a collection is a group of documents, and each document contains fields with key-value data.",
            "In the Cloud Firestore data model, Collections are lightweight containers that hold Documents, while Documents are lightweight JSON-like units containing structured fields, nested maps, and subcollections."
        ),
        (
            "How does offline data persistence work in Firebase?",
            "Firebase caches data locally so apps work without an internet connection.",
            "Firebase automatically stores a local copy of active database documents so apps can read and write data seamlessly even when offline.",
            "Firebase implements local offline persistence by caching synchronized documents and pending writes in local device storage, executing local queries instantly and synchronizing updates when internet connectivity resumes."
        ),
        (
            "What is Firebase App Check?",
            "App Check protects your Firebase resources from abuse by verifying traffic origin.",
            "Firebase App Check helps protect your backend resources (like Firestore and Storage) by ensuring requests originate only from your authentic app.",
            "Firebase App Check is a security layer that leverages platform attestation services (e.g., Apple DeviceCheck, Google Play Integrity, reCAPTCHA) to ensure incoming API traffic originates from authentic, untampered applications."
        ),
        (
            "What is a Firebase Custom Token?",
            "A Custom Token is a signed JWT created by your server to authenticate users.",
            "A Firebase Custom Token is a signed JSON Web Token created on your backend server to integrate custom login systems with Firebase Auth.",
            "A Firebase Custom Token is a cryptographically signed JWT minted by a trusted backend server using the Firebase Admin SDK, allowing users authenticated via legacy or external systems to log into Firebase services."
        ),
        (
            "What is the Firebase Admin SDK?",
            "The Admin SDK lets servers interact with Firebase with elevated administrative privileges.",
            "The Firebase Admin SDK is a server-side library that provides programmatic access to Firebase services with full administrative privileges.",
            "The Firebase Admin SDK is a server-side development toolkit (Node.js, Python, Java, Go) that bypasses client security rules using service account credentials, used for backend integrations and automated administrative tasks."
        ),
        (
            "What are Firebase Extensions?",
            "Firebase Extensions are pre-packaged backend solutions that automate common tasks.",
            "Firebase Extensions are ready-to-use, configurable bundles of code that deploy automated tasks like image resizing or Stripe payments with a few clicks.",
            "Firebase Extensions are pre-built, configurable serverless solutions that deploy pre-tested Cloud Functions into your project to perform tasks like resizing images, translating text, sending emails, or processing payments."
        ),
        (
            "What is the difference between Firebase Client SDK and Admin SDK?",
            "Client SDK runs on user devices with restricted rules; Admin SDK runs on servers with full access.",
            "The Client SDK runs in web and mobile apps restricted by security rules, while the Admin SDK runs in trusted server environments with root access.",
            "The Firebase Client SDK is designed for untrusted mobile and web client environments subject to Firebase Security Rules, whereas the Admin SDK runs in trusted backend server environments with elevated privileges."
        ),
        (
            "What is an index in Cloud Firestore?",
            "An index is a database structure that speeds up Firestore queries.",
            "Firestore uses single-field and composite indexes to ensure high-performance query execution across large collections.",
            "Cloud Firestore maintains automatic single-field indexes on all document fields and supports composite indexes across multiple attributes, guaranteeing that query performance scales proportionally to the result set."
        ),
        (
            "How does Firebase support real-time data updates?",
            "Firebase uses WebSockets and listeners to push data changes to clients immediately.",
            "Firebase uses persistent network connections and listener callbacks to notify connected apps instantly whenever data changes.",
            "Firebase enables real-time synchronization by maintaining persistent, bidirectional WebSocket channels between clients and the cloud, broadcasting database change deltas immediately to registered client snapshot listeners."
        ),
        (
            "What are Firebase transactional writes?",
            "Transactions are atomic operations that read and write data safely without conflicts.",
            "A Firebase transaction is an atomic set of read and write operations that ensures all changes succeed together or none do, avoiding concurrency race conditions.",
            "Firebase transactions provide atomic, all-or-nothing execution of multiple document reads and writes; if any document modified during the transaction changes concurrently on the server, the transaction retries automatically."
        )
    ],
    "IoT": [
        (
            "What is the Internet of Things (IoT)?",
            "IoT is a network of physical devices connected to the internet to exchange data.",
            "The Internet of Things (IoT) refers to billions of physical devices worldwide connected to the internet, collecting and sharing data.",
            "The Internet of Things (IoT) is an interconnected network of physical objects embedded with sensors, software, actuators, and communication hardware that collect, exchange, and act upon environmental data over the internet."
        ),
        (
            "What are the main components of an IoT system?",
            "Sensors, connectivity, data processing, and user interface.",
            "An IoT system consists of four primary components: sensing devices, network connectivity, data processing/cloud platforms, and a user interface.",
            "A complete IoT architecture comprises four architectural layers: 1. Physical Sensing/Actuation, 2. Network Connectivity (Wi-Fi, Cellular, BLE), 3. Data Ingestion and Cloud Analytics, and 4. User Presentation and Control."
        ),
        (
            "What is a sensor in IoT?",
            "A sensor is a device that detects physical environmental changes and converts them into signals.",
            "A sensor is an electronic hardware device that measures physical parameters like temperature, light, or pressure and converts them into readable digital signals.",
            "An IoT sensor is an electronic input transducer that detects physical, chemical, or biological phenomena in the environment (e.g., temperature, humidity, motion) and converts them into measurable electrical or digital signals."
        ),
        (
            "What is an actuator in IoT?",
            "An actuator converts electrical control signals into physical motion or action.",
            "An actuator is a mechanical device that takes a digital control signal from a computer and performs a physical action, like opening a valve or turning on a motor.",
            "An actuator is an electromechanical output transducer that converts digital control commands or electrical signals into physical mechanical motion, pressure, or state changes (e.g., motors, relays, solenoids)."
        ),
        (
            "What is the difference between a microcontroller and a microprocessor?",
            "A microcontroller integrates CPU, RAM, and ROM on one chip; a microprocessor contains only the CPU.",
            "A microcontroller is a compact all-in-one chip with CPU, memory, and I/O pins for specific tasks, while a microprocessor is a general-purpose CPU requiring external memory.",
            "A microcontroller (MCU, like Arduino) is a self-contained integrated circuit containing a CPU, RAM, ROM/Flash, and I/O peripherals on a single chip; a microprocessor (MPU, like Intel Core) contains only the processor core."
        ),
        (
            "What is Arduino?",
            "Arduino is an open-source electronics prototyping platform based on microcontrollers.",
            "Arduino is an accessible open-source hardware and software platform used to build interactive electronic projects and control sensors and motors.",
            "Arduino is an open-source hardware prototyping ecosystem featuring microcontroller development boards (Atmega328P/ARM) and an integrated development environment (IDE) utilizing a simplified C/C++ dialect for physical computing."
        ),
        (
            "What is a Raspberry Pi?",
            "Raspberry Pi is a low-cost, credit-card-sized single-board computer.",
            "Raspberry Pi is a fully functional, credit-card-sized computer capable of running complete operating systems like Linux.",
            "Raspberry Pi is a family of affordable, credit-card-sized single-board computers (SBCs) featuring ARM processors, RAM, HDMI, USB, and GPIO pins capable of running full desktop operating systems like Linux."
        ),
        (
            "What is the difference between Arduino and Raspberry Pi?",
            "Arduino is a simple microcontroller; Raspberry Pi is a full computer with an OS.",
            "Arduino runs simple embedded code directly on a microcontroller, while Raspberry Pi is a complete computer with an operating system capable of running complex software.",
            "Arduino is a real-time, low-power microcontroller platform ideal for direct hardware sensor reading and electrical interfacing, whereas Raspberry Pi is a full Linux single-board computer capable of complex computing tasks."
        ),
        (
            "What is GPIO in embedded systems and IoT?",
            "GPIO pins are general-purpose pins used for digital input and output.",
            "General-Purpose Input/Output (GPIO) pins are physical pins on a board that can be programmed to receive data from sensors or send signals to devices.",
            "General-Purpose Input/Output (GPIO) pins are uncommitted digital interface pins on a microcontroller or single-board computer whose electrical behavior (input, output, high, low, PWM) is dynamically controllable via software."
        ),
        (
            "What is MQTT in IoT?",
            "MQTT is a lightweight publish-subscribe messaging protocol for IoT.",
            "Message Queuing Telemetry Transport (MQTT) is a lightweight messaging protocol designed for battery-powered devices on low-bandwidth networks.",
            "MQTT (Message Queuing Telemetry Transport) is an ISO standard publish/subscribe network messaging protocol running over TCP, engineered specifically for resource-constrained IoT devices and high-latency, low-bandwidth networks."
        ),
        (
            "How does the MQTT publish-subscribe model work?",
            "Publishers send messages to a topic; subscribers receive messages from topics via a broker.",
            "In MQTT, client devices publish messages to a central broker under specific topics, and any clients subscribed to those topics automatically receive the data.",
            "The MQTT pub/sub pattern decouples data producers from consumers: client nodes publish messages categorized by hierarchical topics to a central MQTT broker, which routes the payloads to all clients subscribed to those topics."
        ),
        (
            "What is CoAP in IoT?",
            "CoAP is a specialized web transfer protocol for constrained IoT devices.",
            "Constrained Application Protocol (CoAP) is a lightweight HTTP-like protocol designed for low-power internet devices using UDP.",
            "The Constrained Application Protocol (CoAP) is a specialized application-layer protocol (RFC 7252) designed for resource-constrained IoT devices, operating over UDP and mirroring RESTful HTTP methods with minimal header overhead."
        ),
        (
            "What is edge computing in IoT?",
            "Edge computing processes IoT sensor data locally instead of sending everything to the cloud.",
            "Edge computing processes and analyzes data directly on local devices or gateways rather than routing it all to distant cloud data centers.",
            "Edge computing in IoT involves performing data ingestion, anomaly detection, and ML inference on local IoT gateways or embedded devices directly at the data source, slashing latency and reducing cloud bandwidth demands."
        ),
        (
            "What is LoRaWAN?",
            "LoRaWAN is a long-range, low-power wireless networking protocol for IoT.",
            "LoRaWAN is a low-power, wide-area networking protocol designed to wirelessly connect battery-operated sensors over long distances.",
            "LoRaWAN (Long Range Wide Area Network) is a low-power, wide-area networking protocol specification designed to wirelessly link battery-operated IoT sensors across distances of 10-15km with minimal power consumption."
        ),
        (
            "What is Zigbee in IoT?",
            "Zigbee is a low-power wireless mesh network standard for smart homes.",
            "Zigbee is a wireless standard based on IEEE 802.15.4 used to create low-power, short-range mesh networks for smart home and industrial devices.",
            "Zigbee is a standardized high-level communication protocol based on IEEE 802.15.4 specifications, utilizing a low-power, low-data-rate mesh network topology for home automation and industrial telemetry."
        ),
        (
            "What is Bluetooth Low Energy (BLE)?",
            "BLE is a power-efficient version of Bluetooth designed for IoT devices.",
            "Bluetooth Low Energy (BLE) is a wireless personal area network technology designed to transmit small amounts of data while using very little battery power.",
            "Bluetooth Low Energy (BLE, Bluetooth Smart) is a wireless personal area network technology optimized for power-constrained peripheral devices, remaining in sleep mode until periodically broadcasting small data packets."
        ),
        (
            "What is an IoT gateway?",
            "An IoT gateway connects IoT devices to the cloud and translates protocols.",
            "An IoT gateway is an intermediate hardware hub that bridges sensor devices with the cloud, handling data filtering and protocol translation.",
            "An IoT gateway is a physical or virtual appliance that bridges edge sensing devices with cloud platforms, handling protocol translation (e.g., Zigbee to IP), data encryption, local edge caching, and traffic management."
        ),
        (
            "What is firmware in an IoT device?",
            "Firmware is permanent software programmed into the device's hardware memory.",
            "Firmware is low-level software programmed directly onto an IoT device's non-volatile memory to control its hardware functions.",
            "Firmware is low-level, permanent computer software programmed into an IoT device's non-volatile ROM or Flash memory, providing the essential operational instructions and hardware abstraction layer."
        ),
        (
            "What is an Over-The-Air (OTA) update in IoT?",
            "An OTA update wirelessly upgrades an IoT device's firmware or software.",
            "Over-The-Air (OTA) updates allow manufacturers to wirelessly distribute and install new firmware or software updates on remote IoT devices.",
            "Over-The-Air (OTA) programming is the automated wireless distribution and installation of new firmware or software patches to deployed, remote IoT devices over Wi-Fi, cellular, or satellite networks without physical access."
        ),
        (
            "What are common security challenges in IoT?",
            "Weak default passwords, lack of encryption, and unpatched firmware.",
            "Major IoT security challenges include weak default credentials, insecure communications, lack of hardware encryption, and difficult patch management.",
            "Key IoT security challenges include hardcoded default credentials, physical tampering vulnerability, unencrypted communications, constrained resources preventing strong cryptography, and unmaintained remote firmware."
        ),
        (
            "What is smart home technology in IoT?",
            "Smart home technology connects household devices for automated remote control.",
            "Smart home technology uses IoT devices to automate and remotely manage home systems like lighting, thermostats, and security cameras.",
            "Smart home technology comprises an integrated ecosystem of consumer IoT devices (smart bulbs, thermostats, locks, appliances) that communicate via home Wi-Fi or Zigbee, controlled centrally through mobile apps or voice assistants."
        ),
        (
            "What is Industrial IoT (IIoT)?",
            "IIoT applies IoT technology to manufacturing, energy, and industrial systems.",
            "Industrial IoT (IIoT) connects industrial machines, sensors, and equipment to improve manufacturing efficiency and predictive maintenance.",
            "Industrial Internet of Things (IIoT) refers to the specialized integration of smart sensors, instrumentation, and networked industrial equipment in manufacturing, energy grids, and supply chains to achieve predictive maintenance."
        ),
        (
            "What is predictive maintenance in IoT?",
            "Predictive maintenance uses sensor data to repair equipment before it breaks.",
            "Predictive maintenance uses real-time sensor monitoring and machine learning to predict when equipment will fail so it can be serviced proactively.",
            "Predictive maintenance is an advanced maintenance strategy that continuously analyzes machine telemetry (vibration, heat, acoustics) using AI models to detect anomalies and schedule repairs before failures happen."
        ),
        (
            "What is a digital twin in IoT?",
            "A digital twin is a virtual digital replica of a physical object or system.",
            "A digital twin is an exact digital simulation of a physical device or process that is continuously updated with real-time sensor data.",
            "A digital twin is an advanced virtual software representation and dynamic simulation of a physical asset, process, or system that ingests real-time IoT sensor telemetry to mirror operational state and simulate scenarios."
        ),
        (
            "What is Pulse Width Modulation (PWM) in IoT hardware?",
            "PWM controls analog power output using fast digital on-off pulses.",
            "Pulse Width Modulation (PWM) is a technique used by microcontrollers to simulate variable analog voltage by rapidly turning a digital signal on and off.",
            "Pulse Width Modulation (PWM) is a digital signal modulation technique that varies the duty cycle (percentage of time high versus low) of a fixed-frequency square wave to simulate continuous variable analog power levels."
        )
    ]
}

def generate_datasets():
    questions = []
    question_id = 1
    
    print("=" * 70)
    print("  GENERATING 525+ IT INTERVIEW QUESTIONS & ANSWERS DATASET")
    print("=" * 70)
    
    categories = list(RAW_DATA.keys())
    print(f"Total categories defined: {len(categories)}")
    
    for cat in categories:
        items = RAW_DATA[cat]
        print(f"  - {cat}: {len(items)} questions")
        for q_text, a1, a2, a3 in items:
            questions.append({
                "id": question_id,
                "question": q_text,
                "category": cat,
                "difficulty": "Easy",
                "answer_1": a1,
                "answer_2": a2,
                "answer_3": a3
            })
            question_id += 1
            
    total_q = len(questions)
    print("=" * 70)
    print(f"Total Questions Generated: {total_q}")
    
    # 1. Export JSON: backend/datasets/it_questions.json and root it_questions.json
    backend_json_path = os.path.join(DATASETS_DIR, "it_questions.json")
    root_json_path = os.path.join(ROOT_DIR, "it_questions.json")
    
    with open(backend_json_path, "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)
        
    with open(root_json_path, "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)
        
    print(f"[OK] Saved JSON to: {backend_json_path}")
    print(f"[OK] Saved JSON to: {root_json_path}")
    
    # 2. Export CSV: backend/datasets/it_questions.csv and root it_questions.csv
    backend_csv_path = os.path.join(DATASETS_DIR, "it_questions.csv")
    root_csv_path = os.path.join(ROOT_DIR, "it_questions.csv")
    
    fieldnames = ["id", "category", "difficulty", "question", "answer_1", "answer_2", "answer_3"]
    for csv_path in [backend_csv_path, root_csv_path]:
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for q in questions:
                writer.writerow(q)
                
    print(f"[OK] Saved CSV to: {backend_csv_path}")
    print(f"[OK] Saved CSV to: {root_csv_path}")
    
    # 3. Export Instruction-Tuning Training Dataset (1,575 examples: 525 * 3)
    train_jsonl_path = os.path.join(DATASETS_DIR, "it_qa_train.jsonl")
    train_json_path = os.path.join(DATASETS_DIR, "it_qa_train.json")
    train_examples = []
    
    for q in questions:
        # Style 1: Very short / direct
        train_examples.append({
            "question_id": q["id"],
            "category": q["category"],
            "answer_type": "short",
            "prompt": f"Answer this IT interview question briefly: {q['question']}",
            "question": q["question"],
            "target": q["answer_1"]
        })
        # Style 2: Standard simple explanation
        train_examples.append({
            "question_id": q["id"],
            "category": q["category"],
            "answer_type": "standard",
            "prompt": f"Explain this IT interview question: {q['question']}",
            "question": q["question"],
            "target": q["answer_2"]
        })
        # Style 3: Slightly detailed explanation
        train_examples.append({
            "question_id": q["id"],
            "category": q["category"],
            "answer_type": "detailed",
            "prompt": f"Provide a detailed answer for this IT interview question: {q['question']}",
            "question": q["question"],
            "target": q["answer_3"]
        })
        
    with open(train_jsonl_path, "w", encoding="utf-8") as f:
        for ex in train_examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
            
    with open(train_json_path, "w", encoding="utf-8") as f:
        json.dump(train_examples, f, indent=2, ensure_ascii=False)
        
    print(f"[OK] Saved Training Dataset ({len(train_examples)} examples) to:")
    print(f"    - {train_jsonl_path}")
    print(f"    - {train_json_path}")
    print("=" * 70)
    return total_q, len(train_examples)

if __name__ == "__main__":
    generate_datasets()

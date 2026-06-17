# Kelvar

Kelvar is an experimental systems and educational programming language built from scratch in Python. It combines the simplicity of Python with powerful concepts inspired by C, C++, and Rust, including memory management, ownership tracking, pointers, custom data structures, visual debugging, and an integrated development environment.Including the complex features of modern programming languages in a most simpler syntax simple than python.

## Features

* Custom Lexer and Tokenizer
* Custom Parser and AST Engine
* Variables and Mutable Variables
* Functions
* Structs and Custom Types
* Arrays and Indexing
* Memory Allocation and Deallocation
* Pointer Support
* Ownership and Move Semantics
* Boolean Logic Operations
* Interactive REPL
* Built-in IDE
* Variable Inspector
* Heap and Memory Visualization
* Runtime Diagnostics

## 1. Installation

Clone the repository and run the entry point script:

# Clone the repository
git clone [https://github.com/terminalwizard875/Kelvar.git](https://github.com/terminalwizard875/Kelvar.git)

cd Kelvar

# Launch the visual IDE
python kelvar_main_entry_point.py


##2. Standalone Build

To compile Kelvar into a standalone Windows .exe application with custom icons:
# Generate high-resolution neon shield icon and PyInstaller spec
python asset_spec_generator.py

# Package application
pyinstaller kelvar.spec


Navigate to dist/KelvarCompilerLabs/ and run KelvarCompilerLabs.exe!

## Example

```kelvar
let mut a = 5

for a in range(0,5) {
    a++
    print(a)
}
```

## Images

<img width="1365" height="767" alt="image" src="https://github.com/user-attachments/assets/a2d3f0db-670c-4d98-890f-e62ba851466e" />

## 📝 Syntax Showcase

## 1. Pointer Arithmetic & Move Safety (The Shadow Shield)
// Allocate memory
let mut p1 = alloc 50
let mut p2 = p1 // Ownership is transferred (moved) to p2!

// The following line triggers a Security Shield Panic!
print *p1 


## 2. OOP & Overloading
class Vector2D {
  fn init(x) {
    this.x = x
    this.y = 0
  }
  fn init(x, y) {
    this.x = x
    this.y = y
  }
  fn __add__(other) {
    return Vector2D(this.x + other.x, this.y + other.y)
  }
}

let mut v1 = Vector2D(5, 10)
let mut v2 = Vector2D(20, 30)
let mut v3 = v1 + v2
print v3.x // Outputs: 25


## 3. Integrated Graphics Canvas
draw_clear()
draw_rect(50, 50, 200, 150, "blue")
draw_circle(150, 125, 40, "yellow")
draw_line(50, 50, 250, 200, "red")


##🗺️ Project Structure

Kelvar/
 ├── kelvar_main_entry_point.py  # Main Entry (CLI & IDE orchestrator)
 ├── asset_spec_generator.py     # Canvas generator & PyInstaller Spec writer
 ├── kelvar/                     # Core Interpreter Modules
 │    ├── __init__.py            # Package manifest
 │    ├── lexer.py               # Tokenizer engine
 │    ├── parser.py              # AST builder
 │    ├── ast_nodes.py           # Node structural architecture
 │    ├── interpreter.py         # Memory & Run evaluation engine
 │    ├── environment.py         # Symbol environment lookup table
 │    └── exceptions.py          # Security panic handlers
 └── ide/                        # Graphical User Interface
      ├── __init__.py
      ├── kelvar_ide.py          # Multi-panel Tkinter workbench
      └── assets/                # Visual icons and logos


## Project Goals

Kelvar aims to make systems programming concepts easier to understand through visual tools, memory inspection, runtime analysis, and a beginner-friendly syntax.

## Roadmap

* [x] Lexer
* [x] Parser
* [x] AST Execution Engine
* [x] Memory Management
* [x] Ownership System
* [x] IDE
* [x] Structs
* [x] Arrays
* [x] Graphics Canvas
* [ ] AI Assistant
* [x] Package Manager
* [ ] Bytecode Virtual Machine
* [ ] Native Compiler

## Inspiration

Kelvar draws inspiration from:

* Python
* C
* C++
* Rust

while introducing its own approach to educational systems programming and visual debugging.

## Status

Kelvar is currently under active development.

## contact info

for any queries or reporting bugs please contact me at :

codemasterx449@gmail.com
       (or)
rejo.security1409@gmail.com

## 🤝 Contributing

Contributions, bug reports, and syntax suggestions are welcome! Feel free to open an issue or submit a pull request.


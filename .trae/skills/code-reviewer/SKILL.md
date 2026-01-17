---
name: "code-reviewer"
description: "Reviews Python code for best practices, bugs, and improvements. Invoke when user asks for code review or before merging changes."
---

# Code Reviewer

This skill reviews Python code and provides feedback on:
- Code style and best practices
- Potential bugs and errors
- Performance improvements
- Security issues
- Readability and maintainability

## Usage
To use this skill, provide the Python code you want to review. The skill will analyze the code and return detailed feedback.

## Example
```python
def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total += num
    return total

# Usage example
result = calculate_sum([1, 2, 3, 4, 5])
print(result)
```

## Encoding Standards

### PEP 8 - Main Coding Style Guide
- **Indentation**: 4 spaces per indentation level, no tabs
- **Line Length**: Maximum 79 characters per line
- **Naming Conventions**:
  - Variables/functions: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_CASE_WITH_UNDERSCORES`
  - Private attributes/methods: `_single_leading_underscore`

### Import Guidelines
- Imports at top of file, after module comments
- Order: Standard library → Third-party → Local
- One import per statement
- Use absolute imports

### Whitespace Usage
- One space around binary operators
- No space before comma, semicolon, colon; one space after
- No space inside parentheses, brackets, braces

### Commenting
- Comments in English, clear and concise
- Docstrings for modules, classes, functions
- Explain "why", not "what"
- Use triple quotes (`"""`) for docstrings

### Best Practices
- Avoid global variables
- Functions/methods should be short and do one thing
- No deep nesting (max 3 levels)
- Use context managers for resource management
- Follow "Single Responsibility Principle"

## Feedback Format
The feedback will be structured as:
1. Overall assessment
2. Specific issues found
3. Recommended improvements
4. Code examples for fixes
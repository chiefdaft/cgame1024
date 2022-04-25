#!/usr/bin/env python3
# importing os module
import os

# Get the size
# of the terminal
size = os.get_terminal_size()


# Print the size
# of the terminal
print(size)
print(size.columns, size.lines)

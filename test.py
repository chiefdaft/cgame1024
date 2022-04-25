#!/usr/bin/env python3
inv = -1
trow = [2,0,0,4]
print(trow)



print(list(filter(lambda c: c != 0, trow[::inv] )))

srow = list(filter(lambda c: c != 0, trow[::inv] ))

ls = len(srow)
m, l  = 0 , 1
while l < ls:
    if srow[m] == srow[l]:
        srow[m] *= 2
        srow[l] = 0
        m += 2
        l += 2
    else:
        m += 1
        l += 1
print(l, srow)

srow += [0 for i in range(len(trow) - ls)]
if inv < 0:
    srow = srow[::inv]

print(srow)
cols, rows = 4, 4
# transpose a matrix
A = [[5, 4, 3, 1],  
     [2, 4, 6, 0],  
     [4, 7, 9, 2],  
     [8, 1, 3, 3]]  

transResult = [[0] * cols for i in range(rows)]

for a in range(len(A)):    
   for b in range(len(A[0])):    
          transResult[b][a] = A[a][b] # store transpose result on empty matrix          
# Printing result in the output  
print("The transpose of matrix A is: ")  
for res in transResult:    
   print(res)  

transResult_T = [[0] * cols for i in range(rows)]

for a in range(len(transResult)):    
   for b in range(len(transResult[0])):    
          transResult_T[b][a] = transResult[a][b]

print("The transpose of matrix T is: ")  
for res in transResult_T:    
   print(res)  

def mirror_v(mx):
    """Miror a matrix vertically"""
    w, h = len(mx[0]), len(mx)
    mirror_mx = [[0] * w for i in range(h)]
    for rowi in range(w):
        mirror_mx[rowi] = mx[rowi][::-1]
    return mirror_mx    
def mirror_v2(mx):
    return map(lambda ro: ro[::-1], mx)
transResult_T= mirror_v2(transResult_T)
print("Mirrored matrix is:") 
for res in transResult_T:    
   print(res)     

# for x in range(0, 128):
#     print("{x:3d} {s:2}".format( x=x, s=chr(x) ))

import tty
import sys
import termios

orig_settings = termios.tcgetattr(sys.stdin)

tty.setcbreak(sys.stdin)
x = 0
while x != chr(27): # ESC
    x=sys.stdin.read(1)[0]
    print("{}You pressed".format('\033[30m'), x)

termios.tcsetattr(sys.stdin, termios.TCSADRAIN, orig_settings)    
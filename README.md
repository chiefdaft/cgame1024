# cgame1024
A small project to learn Python. The aim is to play the game of 1024 on a console.

# Play the game of 1024

Move the tiles by swiping left, right, up- or downward over the watchface.

When two tiles with the same number are squashed together they will add up as exponentials:

**1 + 1 = 2** which is a representation of  **2¹ + 2¹ = 2² = 4**

**2 + 2 = 3** which is a representation of  **2² + 2² = 2³ = 8**

**3 + 3 = 4** which is a representation of  **2³ +  2³ = 2⁴ = 16**

After each move a new tile will be added on a random empty square. The value can be 1 or 2.

So you can continue till you reach **1024** which equals **2⁽¹⁰⁾**. So when you reach tile **10** you have won.

The score is maintained by adding the outcome of the sum of all pairs of squashed tiles (4+16+4+8 etc.)

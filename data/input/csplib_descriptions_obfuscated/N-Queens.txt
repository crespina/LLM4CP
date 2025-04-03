**Overview**

Can $n$ queens (of the same color) be placed on a $n \times n$ chessboard so that no two queens can attack each other?

In chess, a queen attacks other squares in the same row, column, or diagonal. The challenge of the $n$-queens problem is to find a set of $n$ positions on a chessboard where no two queens share the same row, column, or diagonal.

A helpful observation to consider: Suppose a queen is represented by an ordered pair $(\alpha, \beta)$, where $\alpha$ represents the queen’s column, and $\beta$ represents its row on the chessboard. Two queens do not attack each other if and only if they have different values for *all* of $\alpha$, $\beta$, $\alpha - \beta$, and $\alpha + \beta$. The reason this works is that on one diagonal, the sum of the coordinates remains constant, while on the other diagonal, the difference does.

The problem has inherent symmetry. For any solution, rotating or reflecting the chessboard in any of the 8 symmetries (combinations of 90-degree rotations and reflections) produces another solution.

This problem is well studied in the mathematical literature. A 2009 survey by Bell & Stevens provides an outstanding summary of findings.

---

**Complexity**

Here are some important considerations when using the $n$-queens problem as a benchmark:

- The $n$-queens problem is solvable for $n = 1$ and $n \geq 4$ in constant time. Therefore, the decision problem is solvable quickly.
- A solution for any $n \neq 2, 3$ was provided in 1874 by Pauls, and it can be constructed in $O(n)$ time (assuming arithmetic operations on size $n$ are $O(1)$).
- Note that the parameter $n$ for $n$-queens only requires $\log(n)$ bits to specify, so the time complexity is $O(n)$, which is exponential in the input size. This makes it not trivial to provide a compact witness of the solution.
- While solving the decision problem is simple, counting the number of solutions for a given $n$ is much more challenging. Bell & Stevens report that no closed-form expression exists for the number of solutions and that the problem is "beyond #P-complete". However, there are reports of a closed-form solution for the number of solutions (though it's unclear if this conflicts with the earlier finding, or if it’s computationally more efficient than simply enumerating all solutions).
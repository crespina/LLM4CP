Here’s the rewritten version of the problem description:

---

This problem is based on Conway's Game of Life, which was invented by John Horton Conway in the 1960s and popularized by Martin Gardner in his *Scientific American* columns.

Life is played on an infinite squared board, where each square (or cell) is either alive or dead at any given time. A cell has eight neighbors:

The configuration of live and dead cells at time *t* evolves to time *t+1* according to these rules:

- If a cell has exactly three living neighbors at time *t*, it becomes alive at time *t+1*.
- If a cell has exactly two living neighbors at time *t*, it remains in the same state (alive or dead) at time *t+1*.
- Otherwise, the cell dies at time *t+1*.

A stable pattern, or *still-life*, is one that remains unchanged after applying these rules. For instance, an empty board is considered a still-life, as all cells are dead and remain that way.

The challenge here is to find the densest possible still-life pattern for a given *n* x *n* section of the board. This is the pattern with the highest number of live cells that can fit into the section, while all other cells outside of this area remain dead.

(Note: In some definitions, a still-life must be a single *object*—refer to [Mark Niemiec's Definitions of Life Terms](https://conwaylife.com/ref/mniemiec/lifeterm.htm) for this interpretation. In such cases, the 8x8 pattern shown below would be considered a *pseudo still-life*.)

### Examples of optimal solutions

A 3x3 still-life with 6 live cells and an 8x8 still-life with 36 live cells.
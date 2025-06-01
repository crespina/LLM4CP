Given a simple undirected graph \( G = (V, E) \), where \( V \) is the set of vertices and \( E \) is the set of edges, a clique is a subset of \( V \) such that each distinct pair of vertices in the subset is adjacent. The goal is to find the clique with the largest number of vertices in the graph. A related problem is clique enumeration, which involves finding all maximal cliques—those that cannot be extended by adding another vertex.

This problem was studied in the second DIMACS implementation challenge, which provided a set of benchmark instances in a simple file format. The instances vary in size and difficulty, with some being trivial while others remain unsolved. Here's an example of the file format:

<pre>
c Lines that start with "c" are comments. The first line begins with either "p edge" or "p col", followed by the number of vertices and an (often incorrect) number of edges. Each "e" line describes an edge. Some files contain blank lines.
p edge 5 6
e 1 2
e 2 3
e 3 4
e 4 1
e 3 5
e 4 5
</pre>

This represents a graph with 5 vertices (numbered from 1 to 5) and 6 edges. The number of edges listed is not reliable and should be ignored. Some instances may include edges in both directions or loops (vertices that are adjacent to themselves), which should be disregarded for the clique problem.

In this example, the maximum clique has 3 vertices: 3, 4, and 5.

Other datasets, also in this format, are available for further exploration.

The maximum clique problem is equivalent to the maximum independent set and vertex cover problems. It also serves as an intermediate step in solving the maximum common subgraph problem.
Given a simple undirected graph \( G = (V,E) \), where \( V \) represents the vertices and \( E \) the edges, each vertex \( v \) has a degree \( d_v \), indicating the number of edges incident to it. The degree sequence of a graph consists of the degrees of all vertices, listed in non-increasing order.  

A specific structural constraint is imposed: the graph must not contain a certain substructure consisting of four vertices connected by at least five edges. This means that for any set of four vertices, the number of edges among them must be at most four.  

In addition to this restriction, the degree sequences must satisfy the following conditions:  

- The sequence must be non-increasing.  
- Each degree must be greater than zero and follow a specific modularity condition (divisibility by 3).  
- The sum of all degrees must satisfy a modularity condition (divisibility by 12).  
- There must exist a simple graph with this degree sequence that adheres to the structural constraint.  

The task is to generate all valid degree sequences for a given number of vertices \( n \) that satisfy these conditions.  

As an example, for \( n=10 \), a valid degree sequence is:  

    6 6 3 3 3 3 3 3 3 3  

And the adjacency matrix of a corresponding graph is:  

    0 0 0 0 1 1 1 1 1 1  
    0 0 0 0 1 1 1 1 1 1  
    0 0 0 0 0 0 0 1 1 1  
    0 0 0 0 1 1 1 0 0 0  
    1 1 0 1 0 0 0 0 0 0  
    1 1 0 1 0 0 0 0 0 0  
    1 1 0 1 0 0 0 0 0 0  
    1 1 1 0 0 0 0 0 0 0  
    1 1 1 0 0 0 0 0 0 0  
    1 1 1 0 0 0 0 0 0 0  

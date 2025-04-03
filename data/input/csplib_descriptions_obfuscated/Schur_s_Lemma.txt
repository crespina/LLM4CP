The task involves distributing \( n \) labeled items (numbered \( 1, \dots, n \)) among three groups such that for any set of three numbers \( (x, y, z) \) satisfying \( x + y = z \), the three numbers are not all placed in the same group. A valid assignment exists if and only if \( n < 14 \).

A formulation using binary decision variables can represent this as follows:  
Define \( M_{ij} \) as a Boolean variable where \( M_{ij} = 1 \) if item \( i \) is placed in group \( j \), where \( i \in \{1, \dots, n\} \) and \( j \in \{1,2,3\} \). The constraints are:

1. **Exclusive Assignment:** Each item must be placed in exactly one group:
   \[
   M_{i1} + M_{i2} + M_{i3} = 1, \quad \forall i \in \{1, \dots, n\}
   \]
   
2. **Sum Constraint:** If three items satisfy \( x + y = z \), they must not all belong to the same group:
   \[
   M_{xj} + M_{yj} + M_{zj} \leq 2, \quad \forall (x, y, z) \text{ where } x+y=z, \forall j \in \{1,2,3\}
   \]

A natural extension of this problem considers dividing the numbers into \( k \) groups instead of three (\( k > 3 \)). This variation allows exploration of larger values of \( n \) and connects to Ramsey theory concepts.
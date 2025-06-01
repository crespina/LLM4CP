Given the promise of SAT and CSP techniques for solving "classical" planning problems, I decided to propose this puzzle.

You have a collection of 8 identical objects and two empty containers that can hold up to 5 and 3 objects, respectively. The goal is to distribute the objects so that exactly 4 end up in each of two separate containers. Objects can be moved between containers, but each container can only hold up to its fixed capacity at any time.  

What is the minimum number of transfers required to achieve this distribution? The challenge is to represent this as a sequential decision-making problem (encoded into satisfiability or constraint satisfaction) and solve it efficiently, ideally matching or surpassing a straightforward [enumeration](models/enumerate.pl) approach.
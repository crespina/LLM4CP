This problem involves managing a system of signals at a central hub with eight indicators—four for primary operations and four for auxiliary processes. 

- The primary indicators (S1 to S4) can take one of four states: {idle (I), preparing (P), active (A), transitioning (T)}.
- The auxiliary indicators (A1 to A4) can take one of two states: {off (O), on (N)}.

The constraints governing the system involve quaternary relationships between pairs of primary and auxiliary indicators, ensuring proper coordination. Specifically, for each pair (Si, Ai) and (Sj, Aj) (where \( j = (i+1) \mod 4 \)), only the following transitions are allowed:
- (I, O, A, N) – Primary process is inactive while the auxiliary process is active.
- (P, O, T, O) – Primary process is preparing to activate, while the auxiliary process remains off.
- (A, N, I, O) – Primary process is fully active while the auxiliary process is off.
- (T, O, P, O) – Primary process is transitioning, while the auxiliary process remains off.

The objective is to determine all globally consistent 8-tuples that describe valid system states over time, capturing the evolution of the signal coordination sequence.
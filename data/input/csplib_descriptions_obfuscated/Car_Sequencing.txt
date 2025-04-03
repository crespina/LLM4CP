A set of non-identical items needs to be arranged in a sequence for production. Each item may have different optional features, and the assembly process consists of multiple stations responsible for installing these features (e.g., air-conditioning, sunroof, etc.). Each station has a limited capacity and can handle only a certain proportion of the items passing through. If too many consecutive items require the same feature, the corresponding station will be overloaded. Therefore, the items must be sequenced in a way that ensures no station exceeds its capacity.

For example, if a particular station can handle at most half of the passing items, the sequence must be arranged so that at most 1 item in any 2 requires that feature. This problem has been proven to be NP-complete (Gent 1999).

The data file format is as follows:

First line: total number of items, number of optional features, number of item classes.
Second line: for each feature, the maximum number of items that can have it within a given block.
Third line: for each feature, the size of the block to which the maximum applies.
Following lines: for each item class, an index number, the number of items in this class, and a binary indicator (1 or 0) for whether the class requires each feature.
This is an example dataset from (Dincbas et al., ECAI88):

<pre> 10 5 6 1 2 1 2 1 2 3 3 5 5 0 1 1 0 1 1 0 1 1 0 0 0 1 0 2 2 0 1 0 0 1 3 2 0 1 0 1 0 4 2 1 0 1 0 0 5 2 1 1 0 0 0 </pre>
A valid sequence for this set is:

<pre> Class Options req. 0 1 0 1 1 0 1 0 0 0 1 0 5 1 1 0 0 0 2 0 1 0 0 1 4 1 0 1 0 0 3 0 1 0 1 0 3 0 1 0 1 0 4 1 0 1 0 0 2 0 1 0 0 1 5 1 1 0 0 0 </pre>
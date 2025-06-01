A concert is to consist of nine pieces of music of different durations each involving a different combination of the five members of the orchestra.

Players can arrive at the concert immediately before the first piece in which they are involved and depart immediately after the last piece in which they are involved. The problem is to devise an order in which the pieces can be palyed so as to minimize the total time that players are waiting to play, i.e. the total time when players are present but not currently playing.

In the table below, 1 indicates that the player is required for the corresponding  piece, 0 otherwise. The duration (i.e. time required to play each piece) is in some unspecified time units.


Piece      |  1  |  2  |  3  |  4  |  5  |  6  |  7  |  8  |  9  
---------------------------------------------------------------
Player 1   |  1  |  1  |  0  |  1  |  0  |  1  |  1  |  0  |  1  
Player 2   |  1  |  1  |  0  |  1  |  1  |  1  |  0  |  1  |  0  
Player 3   |  1  |  1  |  0  |  0  |  0  |  0  |  1  |  1  |  0  
Player 4   |  1  |  0  |  0  |  0  |  1  |  1  |  0  |  0  |  1  
Player 5   |  0  |  0  |  1  |  0  |  1  |  1  |  1  |  1  |  0  
---------------------------------------------------------------
Duration   |  2  |  4  |  1  |  3  |  3  |  2  |  5  |  7  |  6  



For example, if the nine pieces were played in numerical order as given above, then the total waiting time would be:

Player 1: 1+3+7=11

Player 2: 1+5=6

Player 3: 1+3+3+2=9

Player 4: 4+1+3+5+7=20

Player 5: 3

giving a total of 49 units.  The optimal sequence gives 17 units waiting time.


A very similar problem occurs in devising a schedule for shooting a film. Different days of shooting require different subsets of the cast, and cast members are paid for days they spend on set waiting. The only difference between <EM>talent scheduling problem</EM> and the rehearsal problem is that different cast members are paid at different rates, so that the cost of waiting time depends on who is waiting. The objective is to minimize the total cost of paying cast members to wait.

The first problem, <I>Film1</I>,  is based on  one given by Cheng, Diamond and Lin 

Day       |  1  |  2  |  3  |  4  |  5  |  6  |  7  |  8  |  9  | 10  | 11  | 12  | 13  | 14  | 15  | 16  | 17  | 18  | 19  | 20  | Cost/100  
---------------------------------------------------------------------------------------------------------------------------
Actor 1   |  1  |  1  |  1  |  1  |  0  |  1  |  0  |  1  |  0  |  1  |  1  |  0  |  0  |  0  |  0  |  0  |  0  |  0  |  0  |  0  |  10  
Actor 2   |  1  |  1  |  1  |  0  |  0  |  0  |  1  |  1  |  0  |  1  |  0  |  0  |  1  |  1  |  1  |  0  |  1  |  0  |  0  |  1  |  4  
Actor 3   |  0  |  1  |  1  |  0  |  1  |  0  |  1  |  1  |  0  |  0  |  0  |  0  |  1  |  1  |  1  |  0  |  0  |  0  |  0  |  0  |  5  
Actor 4   |  0  |  0  |  0  |  0  |  0  |  0  |  0  |  0  |  0  |  1  |  1  |  1  |  1  |  0  |  0  |  0  |  0  |  0  |  0  |  0  |  5  
Actor 5   |  0  |  1  |  0  |  0  |  0  |  0  |  1  |  1  |  0  |  0  |  0  |  1  |  0  |  1  |  0  |  0  |  0  |  1  |  1  |  1  |  5  
Actor 6   |  0  |  0  |  0  |  0  |  0  |  0  |  0  |  0  |  0  |  0  |  0  |  0  |  0  |  1  |  1  |  1  |  1  |  1  |  0  |  0  |  40  
Actor 7   |  0  |  0  |  0  |  0  |  1  |  0  |  1  |  1  |  0  |  0  |  0  |  0  |  0  |  0  |  1  |  0  |  0  |  0  |  0  |  0  |  4  
Actor 8   |  0  |  0  |  0  |  0  |  0  |  1  |  1  |  1  |  1  |  0  |  0  |  0  |  0  |  0  |  0  |  0  |  0  |  0  |  0  |  0  |  20  
---------------------------------------------------------------------------------------------------------------------------
Duration  |  2  |  1  |  1  |  1  |  1  |  3  |  1  |  1  |  1  |  2  |  1  |  1  |  2  |  1  |  2  |  1  |  1  |  2  |  1  |  1  



The problem below, <I>Film2</I>, is also based on real film data (although the costs are purely fictitious).  It is easier to solve than <I>Film1</I>.


Day,1,2,3,4,5,6,7,8,9,10,11,12,13,Cost/100
Actor 1,0,0,1,0,0,0,0,0,1,1,1,1,0,40
Actor 2,1,1,0,0,1,1,1,1,1,1,1,0,1,20
Actor 3,0,1,0,0,0,0,0,1,0,0,0,0,0,20
Actor 4,1,0,0,1,1,1,1,1,1,1,0,0,1,10
Actor 5,0,0,0,1,0,0,0,0,0,1,0,0,0,5
Actor 6,1,0,0,0,0,1,1,0,1,1,1,1,0,10
Actor 7,0,1,0,0,1,0,0,0,1,1,1,0,0,5
Actor 8,0,0,0,0,0,1,0,0,0,1,0,0,0,4
Actor 9,0,0,0,0,0,0,0,0,0,0,1,0,1,5
Actor 10,0,0,0,0,0,0,0,0,1,1,0,0,0,4
Duration,1,1,1,1,3,1,1,1,1,1,1,1,1,



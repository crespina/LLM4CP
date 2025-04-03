This problem arises in real-world staff scheduling scenarios, where the goal is to determine a shift assignment for each employee on each day while following a structured rotation pattern. To simplify the problem, only one employee's schedule is explicitly computed, and the schedules for the remaining employees are obtained by cyclically rotating the first schedule. For example, if there are four employees, their weekly assignments rotate such that each employee takes over the schedule of another in the following week, forming a repeating cycle:

|            |        |        |        |        |
|------------|--------|--------|--------|--------|
| Employee 1 | Week 1 | Week 2 | Week 3 | Week 4 |
| Employee 2 | Week 2 | Week 3 | Week 4 | Week 1 |
| Employee 3 | Week 3 | Week 4 | Week 1 | Week 2 |
| Employee 4 | Week 4 | Week 1 | Week 2 | Week 3 |

The number of employees is equal to the number of weeks, ensuring a continuous, cyclic schedule. Additionally, the schedule must be structured so that the first week's assignments follow after the last week, creating a seamless rolling cycle. Each week consists of daily shift assignments, such as "Night," "Day Off," "Early," or "Late."

### Definitions and Constraints

- Let \( w \) be the number of weeks (equal to the number of employees).  
- The scheduling period consists of \( w \times 7 \) days, represented as a set of decision variables.  
- There are four possible shifts:  
  - 0 = Day Off  
  - 1 = Early  
  - 2 = Late  
  - 3 = Night  

The problem must satisfy the following constraints:

1. **Shift Requirements**: Each day requires a specific number of employees per shift (e.g., fewer staff on weekends).  
2. **Shift Repetitions**:  
   - A shift must be assigned for at least a minimum number of consecutive days (e.g., at least 2).  
   - A shift cannot be assigned for more than a maximum number of consecutive days (e.g., at most 4).  
3. **Shift Order**: A forward-rotating principle must be followed, meaning that after an early shift, only the same shift, a later shift, or a day off can follow.  
4. **Equal Weekend Days**: Saturday and Sunday must have the same shift for each employee.  
5. **Rest Days**: Each employee must have at least two rest days within any 14-day period.  

These constraints are based on labor regulations and research on best scheduling practices.

A scheduling instance is described using the format:  
**Schedule-**\( w \)**-**\( M \)**-**\( s_{\min} \)**-**\( s_{\max} \), where:  
- \( w \) is the number of weeks/employees.  
- \( M \) is a matrix specifying required staff per shift per day.  
- \( s_{\min} \) is the minimum number of consecutive days with the same shift.  
- \( s_{\max} \) is the maximum number of consecutive days with the same shift.  

An example requirement table might specify how many employees are needed per shift each day:

| Shift / Day | Mo | Tu | We | Th | Fr | Sa | Su |
|------------|----|----|----|----|----|----|----|
| Day Off    | 2  | 2  | 2  | 2  | 2  | 4  | 4  |
| Early      | 2  | 2  | 2  | 2  | 2  | 2  | 2  |
| Late       | 2  | 2  | 2  | 2  | 2  | 1  | 1  |
| Night      | 2  | 2  | 2  | 2  | 2  | 1  | 1  |

This represents an instance where the schedule covers 8 weeks with 8 employees, determined by the total shift assignments in \( M \).
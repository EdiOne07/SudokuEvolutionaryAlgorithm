# Visualizing the Evolutionary Process

## Evolutionary Algorithm Implementations
This section presents and compares different implementations of an evolutionary algorithm designed to solve Sudoku puzzles. Each implementation varies in its approach to selection, crossover, mutation strategies, and fitness evaluation.

To visualize this process, we will focus on the creation of a child from two parents. The initial Sudoku puzzle is as follows:
```
+=======+=======+=======+
| 0 2 0 | 0 0 0 | 0 3 1 |
| 7 0 0 | 0 0 3 | 0 0 0 |
| 0 0 0 | 1 4 0 | 2 9 0 |
+=======+=======+=======+
| 0 5 2 | 7 6 4 | 0 1 8 |
| 0 6 3 | 0 1 2 | 7 5 9 |
| 0 7 8 | 0 0 0 | 4 0 0 |
+=======+=======+=======+
| 2 0 0 | 3 7 0 | 0 0 5 |
| 0 1 0 | 0 0 0 | 9 0 0 |
| 5 4 0 | 0 8 1 | 0 0 0 |
+=======+=======+=======+
```

### Implementation 1
1. Initialize the population with _**population_size**_ random individuals that all respect the initially given sudoku tiles. These individuals will start out with random values in the empty tiles. The fitness of each individual is calculated as the sum of the number of unique numbers in each row, column, and 3x3 subgrid. The maximum fitness is 243 (9 unique numbers * 9 rows + 9 columns + 9 subgrids).
2. The next generation of individuals is created by selecting two parents (or the same one twice) randomly from the top 20% of the current population. These top parents will create 80% of the next generation's individuals. The other 20% of individuals will have parents that are chosen the entire population.
3. We perform random crossover, iterating over each cell and randomly choosing whether the child inherits the value from the first or second parent.
4. Afterwards, the child mutates _**mutation_amount**_ random tiles on the board, changing their value. Any change on the initially given sudoku tiles is not allowed.
5. Once the new generation is created, we calculate the fitness of each individual and repeat the process from step 2. until a valid solution is found.

#### Top Parents + Child Score of 187:
```
+=======+=======+=======+ + +=======+=======+=======+ = +=======+=======+=======+ ~ +=======+=======+=======+
| 6 2 9 | 5 7 6 | 7 3 1 | + | 8 2 6 | 7 7 5 | 7 3 1 | = | 8 2 9 | 7 7 6 | 7 3 1 | ~ | 8 2 9 | 7 7 6 | 7 3 1 |
| 7 8 5 | 6 9 3 | 1 2 7 | + | 7 1 3 | 9 8 3 | 8 2 4 | = | 7 1 5 | 6 8 3 | 1 2 4 | ~ | 7 1 5 | 6 8 3 | 1 2 4 |
| 1 3 4 | 1 4 7 | 2 9 5 | + | 1 5 5 | 1 4 7 | 2 9 3 | = | 1 3 5 | 1 4 7 | 2 9 5 | ~ | 1 3 5 | 1 4 7 | 2 9 5 |
+=======+=======+=======+ + +=======+=======+=======+ = +=======+=======+=======+ ~ +=======+=======+=======+
| 4 5 2 | 7 6 4 | 4 1 8 | + | 9 5 2 | 7 6 4 | 1 1 8 | = | 9 5 2 | 7 6 4 | 1 1 8 | ~ | 9 5 2 | 7 6 4 | 1 1 8 |
| 9 6 3 | 8 1 2 | 7 5 9 | + | 4 6 3 | 9 1 2 | 7 5 9 | = | 9 6 3 | 8 1 2 | 7 5 9 | ~ | 9 6 3 | 8 1 2 | 7 5 9 |
| 9 7 8 | 2 9 5 | 4 6 2 | + | 3 7 8 | 5 9 1 | 4 6 3 | = | 3 7 8 | 5 9 1 | 4 6 3 | ~ | 3 7 8 | 5 9 1 | 4 6 3 |
+=======+=======+=======+ + +=======+=======+=======+ = +=======+=======+=======+ ~ +=======+=======+=======+
| 2 2 6 | 3 7 7 | 9 4 5 | + | 2 8 7 | 3 7 1 | 7 4 5 | = | 2 2 6 | 3 7 7 | 7 4 5 | ~ | 2 2 6 | 3 7 7 | 7 7 5 |
| 4 1 6 | 2 2 3 | 9 7 9 | + | 3 1 6 | 4 2 3 | 9 7 2 | = | 4 1 6 | 4 2 3 | 9 7 9 | ~ | 4 1 6 | 4 2 3 | 9 7 9 |
| 5 4 1 | 2 8 1 | 3 4 8 | + | 5 4 4 | 2 8 1 | 3 4 3 | = | 5 4 1 | 2 8 1 | 3 4 3 | ~ | 5 4 1 | 2 8 1 | 3 4 3 |
+=======+=======+=======+ + +=======+=======+=======+ = +=======+=======+=======+ ~ +=======+=======+=======+ 
```

##### Problem 
This implementation leads to a situation where the diversity of the population decreases rapidly, resulting in premature convergence to suboptimal solutions. On most of the runs, the algorithm creates more than 100.000 generations before finding a valid solution.
To counter this problem, we have tried to increase the mutation rate and the population size, as well as introducing new random individuals in each generation. However, these adjustments only led to marginal improvements in performance.

#### Implementation 2
1. Initialize the population with _**population_size**_ number of random individuals that all respect the initially given sudoku tiles. The individuals create a complete board by iterating over the rows and filling in the empty tiles with random numbers that do not already exist in the respective row. The fitness function works counterintuitively, calculating the fitness as the sum of the number of duplicates in each column, and 3x3 subgrid. The minimum fitness is 0 (no duplicates).
2. The next generation starts with the top _**elites_size**_ number of individuals from the current population. Then, a tournament selection is performed to select parents for the remaining individuals in the next generation. In each tournament, _**K**_ individuals are randomly chosen from the population, and the one with the best fitness is selected as a parent. This selection process is repeated until we have _**population_size**_ number of parents.
3. The crossover step is done by iterating over all parents in pairs, creating two children from each pair. For each row in the sudoku board, the child inherits that row either from the first or the second parent. This ensures that the children will still respect the uniqueness of numbers in each row.
4. For mutation, we iterate all rows of an individual and swap two random tiles that both haven't been given in the initial sudoku. We do this with the probability of _**mutation_rate**_ for each row, once again ensuring the uniqueness of numbers in each row.
5. Once the new generation is created, we calculate the fitness of each individual and repeat the process from step 2. until a valid solution is found.

#### parent 1: 21, parent 2: 24, child: 24, mutated child: 19
```
+=======+=======+=======+ + +=======+=======+=======+ = +=======+=======+=======+ ~ +=======+=======+=======+
| 9 2 4 | 6 7 8 | 5 3 1 | + | 8 2 4 | 7 9 6 | 5 3 1 | = | 8 2 4 | 7 9 6 | 5 3 1 | ~ | 8 2 4 | 6 9 7 | 5 3 1 |
| 7 9 1 | 5 2 3 | 8 6 4 | + | 7 9 1 | 5 2 3 | 6 8 4 | = | 7 9 1 | 5 2 3 | 6 8 4 | ~ | 7 9 1 | 5 2 3 | 6 8 4 |
| 8 3 5 | 1 4 6 | 2 9 7 | + | 3 6 7 | 1 4 8 | 2 9 5 | = | 8 3 5 | 1 4 6 | 2 9 7 | ~ | 8 3 5 | 1 4 6 | 2 9 7 |
+=======+=======+=======+ + +=======+=======+=======+ = +=======+=======+=======+ ~ +=======+=======+=======+
| 3 5 2 | 7 6 4 | 9 1 8 | + | 3 5 2 | 7 6 4 | 9 1 8 | = | 3 5 2 | 7 6 4 | 9 1 8 | ~ | 3 5 2 | 7 6 4 | 9 1 8 |
| 4 6 3 | 8 1 2 | 7 5 9 | + | 8 6 3 | 4 1 2 | 7 5 9 | = | 8 6 3 | 4 1 2 | 7 5 9 | ~ | 4 6 3 | 8 1 2 | 7 5 9 |
| 6 7 8 | 5 3 9 | 4 1 2 | + | 1 7 8 | 5 3 9 | 4 2 6 | = | 1 7 8 | 5 3 9 | 4 2 6 | ~ | 1 7 8 | 5 3 9 | 4 2 6 |
+=======+=======+=======+ + +=======+=======+=======+ = +=======+=======+=======+ ~ +=======+=======+=======+
| 2 9 6 | 3 7 4 | 1 8 5 | + | 2 9 6 | 3 7 4 | 1 8 5 | = | 2 9 6 | 3 7 4 | 1 8 5 | ~ | 2 9 6 | 3 7 4 | 1 8 5 |
| 3 1 7 | 2 6 5 | 9 8 4 | + | 3 1 7 | 8 5 6 | 9 4 2 | = | 3 1 7 | 2 6 5 | 9 8 4 | ~ | 3 1 7 | 2 6 5 | 9 8 4 |
| 5 4 9 | 6 8 1 | 3 2 7 | + | 5 4 6 | 9 8 1 | 3 2 7 | = | 5 4 6 | 9 8 1 | 3 2 7 | ~ | 5 4 6 | 9 8 1 | 3 2 7 |
+=======+=======+=======+ + +=======+=======+=======+ = +=======+=======+=======+ ~ +=======+=======+=======+
```
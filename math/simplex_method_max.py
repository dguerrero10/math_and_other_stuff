import numpy as np
np.set_printoptions(suppress=True)

# Current limitations:
# 1. Does not work when indicators column is all negative

def simplex_method_maximize(A):
    # Get dimensions of matrix
    A_shape = A.shape
    # Convert matrix to float data type for precise computations
    A = A.astype(float)

    # Print matrix dimensions to screen
    print(f"\nThe dimensions of your matrix is: {A_shape}\n")
    print(A)
    print('\n-------------------------------------------')
    
    # Run algo until no negatives exist in last row
    while np.any((A[-1] < 0)):

        # Locate the most negative indicator
        pivot_col_location = np.argmin(A[-1])

        # Remove last number in indicator column and zero in far right column to perform division
        i = np.delete(A[:,pivot_col_location], -1)
        i_n = np.delete(A[:,-1], -1)
        # print(i_n)

        # Pivot column
        pivot_col = A[:, pivot_col_location]
        
        # Find the pivot by calculating A-jth column / A-last_column
        quotient_v = np.divide(i_n, i)
        # print(quotient_v)
        pivot_var_position = np.argmin(quotient_v)
        # print(pivot_var_position)

        # Put the pivot row as first row
        A[[pivot_var_position]], A[[0]] = A[[0]], A[[pivot_var_position]]
        # Store index 0 in variable for clarity 
        pivot_var_position = 0

        # Get pivot and make it equal to 1
        pivot = A.item(0)
        A[pivot_var_position] = A[pivot_var_position] / pivot
        print(A[pivot_var_position])

        # Get a zero in the pivot column for every position besides pivot
        for indx in range(pivot_var_position, len(pivot_col) -1):
            q = np.sum(pivot_col[indx +1] / pivot_col[pivot_var_position])
            A[indx +1] = np.add(A[pivot_var_position]*-q, A[indx +1])

    print("\nYour answer matrix: \n")
    print(A)
    print("\n")

    # Store numbers in last column into a flat np array
    vector_l = np.squeeze(np.asarray(A[:,-1]))
    # Store the indices of solution variables in regular list
    indices = []
    # Store solutions in regular list
    solution = []
    # Variables to track movement through arrays
    j = 0
    j_n = 0
    # Unpack matrix columns into one dimensioal arrays and ensure that columns solution vars are equal = 1
    for indx in range(np.shape(A)[1]):
        if np.count_nonzero(A[:,indx]) == 1:
            indices.append(indx)
            vector_n = np.squeeze(np.asarray(A[:,indx]))
            solution.append(vector_l[j_n] / vector_n[j])
            j += 1
            j_n += 1

    indices_solutions = tuple(zip(indices, solution))
    return indices_solutions

# Supply a m x n numpy matrix
result = simplex_method_maximize(np.matrix([[16,19,23,15,21,1,0,0,0,0,42000], [15,10,19,23,10,0,1,0,0,0,25000], [9,16,14,12,11,0,0,1,0,0,23000], [18,20,15,17,19,0,0,0,1,0,36000], [-37,-34,-36,-30,-35,0,0,0,0,1,0]]))
# Print final solution to screen
# print(f"Maxium value of objective function: {result[-1][1]}\n")
for indx, solution in result[:-1]:
    print(f"Index of column var: {indx} with max: {solution}")
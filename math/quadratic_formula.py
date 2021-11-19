import math

def quadratic_formula(a, b, c):

     # Calculate + square root
     root = (b**2) - (4*a*c)

     # Calculate denominator 
     denominator = 2*a
    
     # Calculate result of b + square root
     numerator =  -b + math.sqrt(root)
     positive_result = (numerator / denominator)

     # Calculate result of b - square root
     numerator = -b - math.sqrt(root)
     negative_result = (numerator / denominator)

     return (positive_result, negative_result)
    
a = float(input('Input the a variable:  '))
b = float(input('Input the b variable:  '))
c = float(input('Input the c variable:  '))

result = quadratic_formula(a, b, c)

print(f'\nPositive result is: {result[0]}\nNegative reuslt is: {result[1]}\n')
import numpy as np

class StochasticGradientDescent:
    def __init__(self, m, b, learning_rate, minimum_step_size, iterations):
        self.m = m
        self.b = b
        self.learning_rate = learning_rate
        self.minimum_step_size = minimum_step_size
        self.iterations = iterations
        self.step_size_intercept = 0
        self.step_size_slope = 0
        self.terminate = False
        self.counter = 0

    def update_model(self, sum_dX_b, sum_dX_m):
        # Performs updates across the model
        self.update_step_sizes(sum_dX_b, sum_dX_m)
        self.update_parameters()
        self.counter += 1
        return

    def calculate_dX_loss_func(self, x_i, y_i):
        # Terminate if the max amount of iterations have been met OR the step-size is smaller or equal to the minium_step_size
        if (self.counter >= self.iterations) or (abs(self.step_size_slope) <= self.minimum_step_size and self.counter > 1):
            self.terminate = True
            return

        # If the conditions above are not met, calculate partial derivatives
        dXs = self.calculate_partial_dB_dM(x_i, y_i)

        self.update_model(dXs[0], dXs[1])

    def calculate_partial_dB_dM(self, x_i, y_i):
       # Calculate derivative of loss function for the intercept 
       sum_dX_b = -2*(y_i - (self.b + self.m*x_i))

       # Calculate derivative of loss function for the slope
       u = (-2*x_i)
       sum_dX_m = u*(y_i - (self.b + self.m*x_i)) 

       return (sum_dX_b, sum_dX_m) 

    def update_step_sizes(self, sum_dX_b, sum_dX_m):
        # Update the step-sizes for the intercept and slope
        self.step_size_intercept = sum_dX_b * self.learning_rate
        self.step_size_slope = sum_dX_m * self.learning_rate

    def update_parameters(self):
        # Update intercept parameter
        self.b = self.b - self.step_size_intercept
        # Update slope parameter
        self.m = self.m - self.step_size_slope
    
    def entry(self):
        a = [3,4,5,7,8,10,12,13,14,16,18,7]
        b = [1,2,3,4,5,6,7,8,9,10,11,12]

        for y, x in zip(a, b):
            if (self.terminate == True):
                return
            else:
                print(self.step_size_slope)
                print(f'b: {self.b}', f'm:{self.m}')
                self.calculate_dX_loss_func(x, y)
    
stochastic_gradient_descent = StochasticGradientDescent(1, 0, .01, .001, 50)
stochastic_gradient_descent.entry()
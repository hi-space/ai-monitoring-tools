import numpy as np

_PCL_FOCAL_LENGTH = 300
_PCL_CENTER_X = 320
_PCL_CENTER_Y = 240
_PCL_SCALING_FACTOR = 2500.0

def get_rotation_matrix_to_align_a_to_b(a, b):
        """
        http://www.cs.rpi.edu/~trink/Courses/RobotManipulation/lectures/lecture6.pdf
        https://darkpgmr.tistory.com/99
        https://www2.cs.duke.edu/courses/fall13/compsci527/notes/rodrigues.pdf
        """

        def get_skew(x):
            x_skew = np.zeros((3, 3))
            x_skew[0][1] = -x[2]; x_skew[0][2] =  x[1]
            x_skew[1][0] =  x[2]; x_skew[1][2] = -x[0]
            x_skew[2][0] = -x[1]; x_skew[2][1] =  x[0]

            return x_skew

        vecA = np.array(a)
        vecB = np.array(b)

        # rotation vector
        U = np.cross(vecA, vecB)
        U /= np.linalg.norm(U)
        U_hat = get_skew(U)

        # rotation angle 
        cos_tht = np.inner(vecA, vecB) / ( np.linalg.norm(vecA) * np.linalg.norm(vecB) ) 
        tht = np.arccos(cos_tht)

        # rotation_matrix, using Rodrigues' formula
        R = np.eye(vecA.shape[0]) + U_hat * np.sin(tht) + np.matmul(U_hat, U_hat) * (1 - np.cos(tht))
        
        return R

def get_coordinate(x, y, depth):
    Z = depth / _PCL_SCALING_FACTOR
    if Z == 0:
        return None

    X = (x - _PCL_CENTER_X) * Z / _PCL_FOCAL_LENGTH
    Y = (y - _PCL_CENTER_Y) * Z / _PCL_FOCAL_LENGTH
    return (X, Y, Z)

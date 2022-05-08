# ---------------------------------------------------------------------
# Project "Track 3D-Objects Over Time"
# Copyright (C) 2020, Dr. Antje Muntzinger / Dr. Andreas Haja.
#
# Purpose of this file : Kalman filter class
#
# You should have received a copy of the Udacity license together with this program.
#
# https://www.udacity.com/course/self-driving-car-engineer-nanodegree--nd013
# ----------------------------------------------------------------------
#

# imports
import numpy as np

# add project directory to python path to enable relative imports
import os
import sys
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
import misc.params as params

class Filter:
    '''Kalman filter class'''
    def __init__(self):
        pass

    def F(self):
        ############
        # TODO Step 1: implement and return system matrix F
        ############
        #see work from https://classroom.udacity.com/nanodegrees/nd0013/parts/cd2690/modules/d3a07469-74b5-49c2-9c0e-3218c3ecd016/lessons/3210af97-9993-455a-baa7-c60e2217951f/concepts/233b4ae1-58d0-4a53-8307-8994f3e03209
        #have to extend from 2d to 3rd (x, y) to x,y,z
        dt = params.dt
        return np.matrix(
            [
                [1, 0, 0, dt, 0, 0], #x
                [0, 1, 0, 0, dt, 0], #y
                [0, 0, 1, 0, 0, dt], #z
                [0, 0, 0, 1, 0, 0 ], #vx
                [0, 0, 0, 0, 1, 0 ], #vy
                [0, 0, 0, 0, 0, 1 ], #vz
            ]
        )

        ############
        # END student code
        ############

    def Q(self):
        ############
        # TODO Step 1: implement and return process noise covariance Q
        ############
        #see work from https://classroom.udacity.com/nanodegrees/nd0013/parts/cd2690/modules/d3a07469-74b5-49c2-9c0e-3218c3ecd016/lessons/3210af97-9993-455a-baa7-c60e2217951f/concepts/233b4ae1-58d0-4a53-8307-8994f3e03209

        dt = params.dt
        q = params.q
        qt = params.q * dt
        qtt = 1/2 * dt **2  * q
        qttt = 1/3 * dt ** 3 * q
        '''
        return np.matrix(
            [
                [qttt, 0, qtt, 0],
                [0, qttt, 0, qtt],
                [0, 0, qt, 0],
                [0, 0, 0, qt]
            ]
        )
        '''
        #6x6 listed as TODO in project instructiosn
        #https://knowledge.udacity.com/questions/794594
        #converting to use same terms as examples for simplicty
        q1 = qt
        q2 = qtt
        q3 = qttt
        return np.matrix(
            [
                [q3,  0,  0, q2,  0,  0],
                [ 0, q3,  0,  0, q2,  0],
                [ 0,  0, q3,  0,  0, q2],
                [q2,  0,  0, q1,  0, 0],
                [ 0, q2,  0,  0, q1,  0],
                [ 0,  0, q2,  0,  0,  q1],

            ]
        )

        ############
        # END student code
        ############

    def predict(self, track):
        ############
        # TODO Step 1: predict state x and estimation error covariance P to next timestep, save x and P in track
        ############
        #see work from https://classroom.udacity.com/nanodegrees/nd0013/parts/cd2690/modules/d3a07469-74b5-49c2-9c0e-3218c3ecd016/lessons/3210af97-9993-455a-baa7-c60e2217951f/concepts/233b4ae1-58d0-4a53-8307-8994f3e03209
        F = self.F()
        x = F*track.x # state prediction
        P = F*track.P*F.transpose() + self.Q() # covariance prediction
        track.set_x(x)
        track.set_P(P)

        ############
        # END student code
        ############

    def update(self, track, meas):
        ############
        # TODO Step 1: update state x and covariance P with associated measurement, save x and P in track
        ############
        #see work from https://classroom.udacity.com/nanodegrees/nd0013/parts/cd2690/modules/d3a07469-74b5-49c2-9c0e-3218c3ecd016/lessons/3210af97-9993-455a-baa7-c60e2217951f/concepts/233b4ae1-58d0-4a53-8307-8994f3e03209
        # update state and covariance with associated measurement
        x = track.x
        P = track.P
        R = meas.R
        gamma = self.gamma(track, meas)
        H = meas.sensor.get_H(x) # measurement matrix
        S = self.S(track, meas, H)

        K = P*H.T*np.linalg.inv(S) # Kalman gain
        x = x + K*gamma # state update
        I = np.identity(params.dim_state)
        P = (I - K*H) * P # covariance update
        track.set_x(x)
        track.set_P(P)

        ############
        # END student code
        ############
        track.update_attributes(meas)

    def gamma(self, track, meas):
        ############
        # TODO Step 1: calculate and return residual gamma
        ############
        #see work from https://classroom.udacity.com/nanodegrees/nd0013/parts/cd2690/modules/d3a07469-74b5-49c2-9c0e-3218c3ecd016/lessons/3210af97-9993-455a-baa7-c60e2217951f/concepts/233b4ae1-58d0-4a53-8307-8994f3e03209
        x = track.x
        gamma = meas.z - meas.sensor.get_H(x)* x # residual
        return gamma

        ############
        # END student code
        ############

    def S(self, track, meas, H):
        ############
        # TODO Step 1: calculate and return covariance of residual S
        ############
        #see work from https://classroom.udacity.com/nanodegrees/nd0013/parts/cd2690/modules/d3a07469-74b5-49c2-9c0e-3218c3ecd016/lessons/3210af97-9993-455a-baa7-c60e2217951f/concepts/233b4ae1-58d0-4a53-8307-8994f3e03209

        R = meas.R
        P = track.P
        S = H*P*H.T + R # covariance of residual
        return S

        ############
        # END student code
        ############
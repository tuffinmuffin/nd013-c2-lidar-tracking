# ---------------------------------------------------------------------
# Project "Track 3D-Objects Over Time"
# Copyright (C) 2020, Dr. Antje Muntzinger / Dr. Andreas Haja.
#
# Purpose of this file : Classes for track and track management
#
# You should have received a copy of the Udacity license together with this program.
#
# https://www.udacity.com/course/self-driving-car-engineer-nanodegree--nd013
# ----------------------------------------------------------------------
#

# imports
import numpy as np
import collections

# add project directory to python path to enable relative imports
import os
import sys
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
import misc.params as params

class Track:
    '''Track class with state, covariance, id, score'''
    def __init__(self, meas, id):
        print('creating track no.', id)
        M_rot = meas.sensor.sens_to_veh[0:3, 0:3] # rotation matrix from sensor to vehicle coordinates

        ############
        # TODO Step 2: initialization:
        # - replace fixed track initialization values by initialization of x and P based on
        # unassigned measurement transformed from sensor to vehicle coordinates
        # - initialize track state and track score with appropriate values
        ############

        #see https://classroom.udacity.com/nanodegrees/nd0013/parts/cd2690/modules/d3a07469-74b5-49c2-9c0e-3218c3ecd016/lessons/aca6f174-54d6-4a71-ac30-786504a0dcb7/concepts/c7f82542-1069-445f-8519-5032a8597fbd

        #create P
        self.P = np.zeros((params.dim_state, params.dim_state))
        #selects colum 0, 1, 2 and row 0,1,2
        self.P[0:3,0:3] = M_rot * meas.R * M_rot.T
        #set velocity to high uncertainty

        #elements accessed via 0 index
        self.P[3,3] = params.sigma_p44
        self.P[4,4] = params.sigma_p55
        self.P[5,5] = params.sigma_p66

        #create X
        z = np.ones((4,1))
        #augment meas.z with 1
        z[0:3] = meas.z
        self.x = np.zeros((params.dim_state,1))
        self.x[0:3] = (meas.sensor.sens_to_veh * z)[0:3]

        self.state = 'initialized'
        self.score = 1./params.window
        #todo flesh out history tracking. need to track last window # of detects, to create moving averages
        #maybe this will be a starting point?
        self.history = np.zeros(params.window)
        self.history[-1] = 1
        self.score = np.mean(self.history) #same as 1/params.window. 1 of the 6 history is 1 now.

        ############
        # END student code
        ############

        # other track attributes
        self.id = id
        self.width = meas.width
        self.length = meas.length
        self.height = meas.height
        self.yaw =  np.arccos(M_rot[0,0]*np.cos(meas.yaw) + M_rot[0,1]*np.sin(meas.yaw)) # transform rotation from sensor to vehicle coordinates
        self.t = meas.t

    def set_x(self, x):
        self.x = x

    def set_P(self, P):
        self.P = P

    def set_t(self, t):
        self.t = t

    #get max x or y P. Ignore z as this is not expected to be used normally
    def get_max_P(self):
        max_p = max(self.P[0,0], self.P[1,1])
        print(max_p)
        return max_p

    def update_attributes(self, meas):
        # use exponential sliding average to estimate dimensions and orientation
        if meas.sensor.name == 'lidar':
            c = params.weight_dim
            self.width = c*meas.width + (1 - c)*self.width
            self.length = c*meas.length + (1 - c)*self.length
            self.height = c*meas.height + (1 - c)*self.height
            M_rot = meas.sensor.sens_to_veh
            self.yaw = np.arccos(M_rot[0,0]*np.cos(meas.yaw) + M_rot[0,1]*np.sin(meas.yaw)) # transform rotation from sensor to vehicle coordinates

    def track_score_update(self, tracked):
        self.history[:-1] = self.history[1:]
        if tracked:
            self.history[-1] = 1
        else:
            self.history[-1] = 0
        self.score = np.mean(self.history)



###################

class Trackmanagement:
    '''Track manager with logic for initializing and deleting objects'''
    def __init__(self):
        self.N = 0 # current number of tracks
        self.track_list = []
        self.last_id = -1
        self.result_list = []

    def manage_tracks(self, unassigned_tracks, unassigned_meas, meas_list):
        ############
        # TODO Step 2: implement track management:
        # - decrease the track score for unassigned tracks
        # - delete tracks if the score is too low or P is too big (check params.py for parameters that might be helpful, but
        # feel free to define your own parameters)
        ############

        # delete old tracks
        delete_list = []

        # decrease score for unassigned tracks
        for i in unassigned_tracks:
            track = self.track_list[i]
            # check visibility
            if meas_list: # if not empty
                if meas_list[0].sensor.in_fov(track.x):
                    track.track_score_update(False)

            #if track was not detected after being initilizied remove it
            if track.state == 'initialized' and track.score < 1./params.window:
                print("removing init track")
                delete_list.append(track)
                #todo remove after testing if getting hit
                raise Exception("removing initialzied track")
            #track never moved to confirmed before decaying again
            elif track.state == 'tentative' and track.score < 1./params.window:
                delete_list.append(track)
                #todo remove after testing if getting hit
                raise Exception("removing tentative track")


        for track in self.track_list:
            if track.get_max_P() > params.max_P:
                delete_list.append(track)
            elif track.state == 'confirmed' and track.score < params.delete_threshold:
                delete_list.append(track)
                #todo remove after testing if getting hit
                #raise Exception("removing confirmed track")



        for i in delete_list:
            self.track_list.remove(i)

        ############
        # END student code
        ############

        # initialize new track with unassigned measurement
        for j in unassigned_meas:
            if meas_list[j].sensor.name == 'lidar': # only initialize with lidar measurements
                self.init_track(meas_list[j])

    def addTrackToList(self, track):
        self.track_list.append(track)
        self.N += 1
        self.last_id = track.id

    def init_track(self, meas):
        track = Track(meas, self.last_id + 1)
        self.addTrackToList(track)

    def delete_track(self, track):
        print('deleting track no.', track.id)
        self.track_list.remove(track)

    def handle_updated_track(self, track):
        ############
        # TODO Step 2: implement track management for updated tracks:
        # - increase track score
        # - set track state to 'tentative' or 'confirmed'
        ############

        track.track_score_update(True)

        #if detected a 2nd time update to tentative
        if track.state == 'initialized':
            track.state = 'tentative'
        elif track.state == 'tentative' and params.confirmed_threshold < track.score:
            track.state = 'confirmed'

        ############
        # END student code
        ############
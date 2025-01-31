import glob
import json
import os
import sys

#Import ROSClose
from backend.interface import ros_close as rclose



CWD = os.getcwd()

CONFIG = json.load(open(CWD+'/config.json'));

try:
    sys.path.append(glob.glob(CONFIG['CARLA_SIMULATOR_PATH']+'PythonAPI/carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import pathlib

import subprocess

import carla

from ..util.util import *

from abc import ABC, abstractmethod

class Scenario(ABC):

    def __init__(self, name, X, Y, Z, PITCH, YAW, ROLL,
    SPEC_CAM_X, SPEC_CAM_Y, SPEC_CAM_Z,
    RUNNING_TIME) -> None:

        self.scenario_finished = False

        # scenario vehicle spawn coordinates
        self.name = name
        self.X = X
        self.Y = Y
        self.Z = Z
        self.PITCH = PITCH
        self.YAW = YAW
        self.ROLL = ROLL

        self.SPEC_CAM_X = SPEC_CAM_X
        self.SPEC_CAM_Y = SPEC_CAM_Y
        self.SPEC_CAM_Z = SPEC_CAM_Z
        self.SPEC_CAM_PITCH = -90
        self.SPEC_CAM_YAW = 0
        self.SPEC_CAM_ROLL = 0

        self.EGO_VEHICLE_NAME = "ego_vehicle"
        self.TRIGGER_DIST = 30
        self.VEHICLE_MODEL = 'vehicle.toyota.prius'
        self.SPAWNED_VEHICLE_ROLENAME = 'spawned_vehicle'
        self.SPAWNED_VEHICLE_VELOCITY = 5

        self.RUNNING_TIME = RUNNING_TIME

        self.ego_vehicle = None

        try:
            self.metamorphic_test_target_file = open(CWD + "/backend/scenario/test_input/" + self.name + ".json")
            print(self.metamorphic_test_target_file)
            self.metamorphic_tests = json.loads(self.metamorphic_test_target_file.read())
        except Exception as e: print(e)


    @abstractmethod
    def run(self):
        pass


    def start_recording_scenario(self):
        if os.name == 'nt':
            subprocess.Popen(args=['python', str(pathlib.Path(__file__).parent.resolve())+r'\record_stats.py'], stdout=sys.stdout)
        else:
            subprocess.Popen(args=['python', str(pathlib.Path(__file__).parent.resolve())+r'/record_stats.py'], stdout=sys.stdout)


    def  is_scenario_finished(self):
        return self.scenario_finished


    def is_metamorphic_test_running(self):
        return self.metamorphic_test_running


    def get_current_metamorphic_test_index(self):
        index =0
        for test in self.metamorphic_tests:
            # print(test)
            if test['done'] == False:
                return index
            index+=1
        return False

    def all_metamorphic_tests_complete(self):

        result = True
        for test in self.metamorphic_tests:
            # print(test)
            if test['done'] == False:
                result = False
        return result


    def set_test_finished(self, world):

        #Set metamorphic test as done.
        self.metamorphic_tests[self.get_current_metamorphic_test_index()]['done'] = True
        self.metamorphic_test_running = False

        #Completed all tests, hence scenario complete
        if self.all_metamorphic_tests_complete():
            self.scenario_finished = True
            # self.ego_vehicle.destroy()
            #Close the Carla Autoware docker that is setup.
            rclose.ROSClose()

        # self.ego_vehicle.destroy()
        rclose.ROSClose()

        destroy_all_vehicle_actors(world)


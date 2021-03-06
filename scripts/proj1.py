#!/usr/bin/env python

import roslib; roslib.load_manifest('stero_velma')
import rospy
import math
import numpy
import tf
from velma_common import *
from rcprg_planner import *
from rcprg_ros_utils import exitError


TOOL_DIST = 0.272

R = 0.05
r = 0.3
p = 0.4
y = 0
x = 0.5
y = -0.4
z = 1
<<<<<<< HEAD
q_map_goal = {'torso_0_joint':0, 'right_arm_0_joint':1.1, 'right_arm_1_joint':-1.3,
    'right_arm_2_joint':1.45, 'right_arm_3_joint':1.4, 'right_arm_4_joint':1.1, 'right_arm_5_joint':-1.2,
    'right_arm_6_joint':-0.5, 'left_arm_0_joint':0.3, 'left_arm_1_joint':1.8, 'left_arm_2_joint':-1.25,
    'left_arm_3_joint':-0.85, 'left_arm_4_joint':0, 'left_arm_5_joint':0.5, 'left_arm_6_joint':0 }


=======
q_map_goal = {'torso_0_joint':0, 'right_arm_0_joint':1, 'right_arm_1_joint':-1.3,
    'right_arm_2_joint':1, 'right_arm_3_joint':1, 'right_arm_4_joint':1.1, 'right_arm_5_joint':-1.6,
    'right_arm_6_joint':0, 'left_arm_0_joint':0.3, 'left_arm_1_joint':1.8, 'left_arm_2_joint':-1.25,
    'left_arm_3_joint':-0.85, 'left_arm_4_joint':0, 'left_arm_5_joint':0.5, 'left_arm_6_joint':0 }
q_map_goal_2 = {'torso_0_joint':-1.5, 'right_arm_0_joint':1, 'right_arm_1_joint':-1.1,
    'right_arm_2_joint':1, 'right_arm_3_joint':1.2, 'right_arm_4_joint':1.1, 'right_arm_5_joint':-1.6,
    'right_arm_6_joint':0, 'left_arm_0_joint':0.3, 'left_arm_1_joint':1.8, 'left_arm_2_joint':-1.25,
    'left_arm_3_joint':-0.85, 'left_arm_4_joint':0, 'left_arm_5_joint':0.5, 'left_arm_6_joint':0 }

>>>>>>> 2dfdefb2b55f06769a67c317b447077048d159e6

def initialize_velma():
    '''
    Function starts python interface and motors.
    '''
    print "Running python interface for Velma..."
    velma = VelmaInterface()
    print "Waiting for VelmaInterface initialization..."
    if not velma.waitForInit(timeout_s=10.0):
        print "Could not initialize VelmaInterface\n"
        exitError(1)
    print "Initialization ok!\n"

    rospy.sleep(0.5)

    diag = velma.getCoreCsDiag()
    if not diag.motorsReady():
        print "Motors must be homed and ready to use for this test."
        exitError(1)
 
    print "Motors must be enabled every time after the robot enters safe state."
    print "If the motors are already enabled, enabling them has no effect."
    print "Enabling motors..."
    if velma.enableMotors() != 0:
        exitError(1)


def initialize_planner():
    '''
    Function starts planner and connects it with octomap.
    '''
    print "Waiting for Planner initialization..."
    global p
    p = Planner(velma.maxJointTrajLen())
    if not p.waitForInit(timeout_s=10.0):
        print "Could not initialize Planner"
        exitError(2)
    ocl = OctomapListener("/octomap_binary")
    rospy.sleep(0.5)
    octomap = ocl.getOctomap(timeout_s=5.0)
    p.processWorld(octomap)
    print "Planner initialization ok!"


def switch_to_jnt_imp():
    '''
    Function switches to joint impedance mode.
    '''
    print "Switch to jnt_imp mode..."
    velma.moveJointImpToCurrentPos(start_time=0.5)
    error = velma.waitForJoint()
    if error != 0:
        print "The action should have ended without error, but the error code is", error
        exitError(2)


def switch_to_cart_imp():
    '''
    Function switches to cartesian impedance mode.
    '''
    print "Switch to cart_imp mode (no trajectory)..."
    if not velma.moveCartImpRightCurrentPos(start_time=0.2):
        exitError(3)
    rospy.sleep(0.5)
    if velma.waitForEffectorRight() != 0:
        exitError(4)
 
    rospy.sleep(0.5)
 
    diag = velma.getCoreCsDiag()
    if not diag.inStateCartImp():
        print "The core_cs should be in cart_imp state, but it is not"
        exitError(5)


def move_left_fingers(close):
    '''
    Function closes or opens left gripper by moving it's fingers.
    '''
    if close:
    	dest_q = [0.6*math.pi, 0.6*math.pi, 0.6*math.pi, 0]
    else:
        dest_q = [0, 0, 0, 0]
    velma.moveHandLeft(dest_q, [1,1,1,1], [2000,2000,2000,2000], 1000, hold=True)
    if velma.waitForHandLeft() != 0:
        exitError(6)
    rospy.sleep(0.5)
    if not isHandConfigurationClose(velma.getHandLeftCurrentConfiguration(), dest_q):
        exitError(7)


def move_right_fingers(close, check=True):
    '''
    Function closes or opens right gripper by moving it's fingers.
    '''
    if close:
    	dest_q = [0.6*math.pi, 0.6*math.pi, 0.6*math.pi, 0]
    else:
        dest_q = [0, 0, 0, 0]
    velma.moveHandRight(dest_q, [1,1,1,1], [2000,2000,2000,2000], 1000, hold=True)
    if velma.waitForHandRight() != 0:
        exitError(8)
    rospy.sleep(0.5)
<<<<<<< HEAD
    if check:
        if not isHandConfigurationClose(velma.getHandRightCurrentConfiguration(), dest_q):
            exitError(9)
    else:
        if isHandConfigurationClose(velma.getHandRightCurrentConfiguration(), dest_q):
            exitError(10)
=======
    if check and not isHandConfigurationClose(velma.getHandRightCurrentConfiguration(), dest_q):
        exitError(9)
>>>>>>> 2dfdefb2b55f06769a67c317b447077048d159e6


def plan_and_move(q_map_goal):
    '''
    Function plans robot's movement to given goal (values for joints) and executes it.
    '''
    print "Planning motion to the goal."
    print "Moving to valid position, using planned trajectory."
    goal_constraint_1 = qMapToConstraints(q_map_goal, 0.01, group=velma.getJointGroup("impedance_joints"))
    for i in range(15):
        rospy.sleep(0.5)
        js = velma.getLastJointState()
        print "Planning (try", i, ")..."
        traj = p.plan(js[1], [goal_constraint_1], "impedance_joints", num_planning_attempts=10, max_velocity_scaling_factor=0.15, planner_id="RRTConnect")
        if traj == None:
            continue
        print "Executing trajectory..."
        if not velma.moveJointTraj(traj, start_time=0.5, position_tol=10.0/180.0 * math.pi, velocity_tol=10.0/180.0*math.pi):
<<<<<<< HEAD
            exitError(11)
=======
            exitError(10)
>>>>>>> 2dfdefb2b55f06769a67c317b447077048d159e6
        if velma.waitForJoint() == 0:
            break
        else:
            print "The trajectory could not be completed, retrying..."
            continue
 
    rospy.sleep(0.5)
    js = velma.getLastJointState()
    if not isConfigurationClose(q_map_goal, js[1]):
<<<<<<< HEAD
        exitError(12)


=======
        exitError(11)


>>>>>>> 2dfdefb2b55f06769a67c317b447077048d159e6
def move_right_wrist(tf_dest):
    '''
    Function moves robot's right wrist to given transform.
    '''
    print "Moving right wrist to pose defined in world frame..."
    if not velma.moveCartImpRight([tf_dest], [3.0], None, None, None, None, PyKDL.Wrench(PyKDL.Vector(5,5,5), PyKDL.Vector(5,5,5)), start_time=0.5):
<<<<<<< HEAD
        exitError(13)
=======
        exitError(12)
>>>>>>> 2dfdefb2b55f06769a67c317b447077048d159e6
    if velma.waitForEffectorRight() != 0:
        exitError(13)
    rospy.sleep(0.5)
    print "Calculating difference between desiread and reached pose..."
    T_B_T_diff = PyKDL.diff(tf_dest, velma.getTf("B", "Tr"), 1.0)
    print T_B_T_diff
    print T_B_T_diff.vel.Norm()
    print T_B_T_diff.rot.Norm()
    if T_B_T_diff.vel.Norm() > 0.2 or T_B_T_diff.rot.Norm() > 0.2:
<<<<<<< HEAD
        exitError(15)
=======
        exitError(14)
>>>>>>> 2dfdefb2b55f06769a67c317b447077048d159e6


def calculate_tf_dest(Tf_object, correction):
    '''
    Function calculates destination transform, used to pick up or put off an object.
    '''
    tool_tf = velma.getTf("B", "Tr")
    tool_tf.p[2] = Tf_object.p[2]
    tf_diff = PyKDL.diff(tool_tf, Tf_object, 1.0)
    alpha = math.atan2(tf_diff.vel[1], tf_diff.vel[0])
    print tf_diff.vel
    tf_diff.vel[0] -= TOOL_DIST*math.cos(alpha)
    tf_diff.vel[1] -= TOOL_DIST*math.sin(alpha)
    return PyKDL.Frame(PyKDL.Rotation.RPY(0.0, 0.0, alpha), tool_tf.p+tf_diff.vel+correction)


<<<<<<< HEAD
def calculate_base_angle(Tf_object):
    '''
    Function calculates destination base angle.
    '''
    alpha = math.atan2(Tf_object.p[1], Tf_object.p[0])
    #alpha -= 0.5*math.pi
    if (- 0.45*math.pi > alpha):
        alpha =  -0.45*math.pi
    elif (0.45*math.pi < alpha):
        alpha =  0.45*math.pi

    q_map_goal["torso_0_joint"] = alpha
    print alpha


if __name__ == "__main__":
    rospy.init_node('lab1_2')
    rospy.sleep(0.5)

    # Get object's and tables' transforms
    velma = VelmaInterface()
    velma.waitForInit()
    Tf_object1 = velma.getTf("B", "object1")
    Tf_table1 = velma.getTf("B", "table1")
    Tf_table2 = velma.getTf("B", "table2")
    translation_tf = PyKDL.Frame(PyKDL.Rotation.RPY(0, 0, 0), PyKDL.Vector(0, -0.2, 1.19))
    Tf_table2 = Tf_table2 * translation_tf
    # Tf_table2.p[1] += 0.2
    # Tf_table2.p[2] = 1.19

    # Initialize robot
    initialize_velma()
    initialize_planner()
    switch_to_jnt_imp()
 
    # Set robot to it's starting position
    move_left_fingers(close=True)
    move_right_fingers(close=True)
    calculate_base_angle(Tf_table1)
    plan_and_move(q_map_goal)
    move_right_fingers(close=False)
    rospy.sleep(1)

    # Move robot's wrist to the object
    switch_to_cart_imp()
    tool_org_tf = velma.getTf("B", "Tr")
    tf_dest = calculate_tf_dest(Tf_object1, PyKDL.Vector(0, 0, 0.1))
    move_right_wrist(tf_dest)

    # Pick up the object
    move_right_fingers(close=True, check=False)
    move_right_wrist(tool_org_tf)
    # Check, if the object was picked
    if isHandConfigurationClose(velma.getHandRightCurrentConfiguration(), [0.6*math.pi, 0.6*math.pi, 0.6*math.pi, 0]):
        print "Object was not picked."
        exitError(16)

    rospy.sleep(0.5)

    # Move to the second starting position - above the second table
    switch_to_jnt_imp()

    # Put down the object
    calculate_base_angle(Tf_table2)
    plan_and_move(q_map_goal)
    switch_to_cart_imp()
    tool_org_tf = velma.getTf("B", "Tr")
    tf_dest = calculate_tf_dest(Tf_table2, PyKDL.Vector(0, 0, 0.15))

    # Move wrist back to the ending position
    move_right_wrist(tf_dest)
    move_right_fingers(close=False)

    move_right_wrist(tool_org_tf)

    rospy.sleep(0.5)
=======
if __name__ == "__main__":
    rospy.init_node('lab1_2')
    rospy.sleep(0.5)

    # Get object's and tables' transforms
    velma = VelmaInterface()
    velma.waitForInit()
    Tf_object1 = velma.getTf("B", "object1")
    Tf_table1 = velma.getTf("B", "table1")
    Tf_table2 = velma.getTf("B", "table2")
    Tf_table2.p[1] += 0.2
    Tf_table2.p[2] = 1.19

    # Initialize robot
    initialize_velma()
    initialize_planner()
    switch_to_jnt_imp()
 
    # Set robot to it's starting position
    move_left_fingers(close=True)
    move_right_fingers(close=True)
    plan_and_move(q_map_goal)
    move_right_fingers(close=False)

    rospy.sleep(1)

    # Move robot's wrist to the object
    switch_to_cart_imp()
    tool_org_tf = velma.getTf("B", "Tr")
    tf_dest = calculate_tf_dest(Tf_object1, PyKDL.Vector(0, 0, 0.1))
    move_right_wrist(tf_dest)

    # Pick up the object
    move_right_fingers(close=True, check=False)
    move_right_wrist(tool_org_tf)

    rospy.sleep(0.5)

    # Move to the second starting position - above the second table
    switch_to_jnt_imp()

    # Put down the object
    plan_and_move(q_map_goal_2)
    switch_to_cart_imp()
    tool_org_tf = velma.getTf("B", "Tr")
    tf_dest = calculate_tf_dest(Tf_table2, PyKDL.Vector(0, 0, 0.15))

    # Move wrist back to the ending position
    move_right_wrist(tf_dest)
    move_right_fingers(close=False)

    move_right_wrist(tool_org_tf)

    rospy.sleep(0.5)
>>>>>>> 2dfdefb2b55f06769a67c317b447077048d159e6
    #if not isHandConfigurationClose( velma.getHandRightCurrentConfiguration(), dest_q):
    #    exitError(9)

#end plan

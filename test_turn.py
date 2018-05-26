#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import rospy
import math
from time import sleep
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from std_msgs.msg import Int32
from geometry_msgs.msg import Pose


class odmback():
	def __init__(self):
		self.odm_sub = rospy.Subscriber("/odom", Odometry, self.getOdm)
		self.turn_end = rospy.Publisher("messenger", String, queue_size=10, latch=True)
		self.odm = None  # Odometry
		self.rad = None  # Rotation

	def topicDetector(self):
		print("I am waiting for message")
		rospy.Subscriber("start", String, self.turn_callback)

	def getOdm(self,odm):
		self.odm = odm

	def turn_callback(self, msg):
		"""The rotation angle is specified by Odometry"""
		print(msg.data)
		if(self.odm is None):
			return "No odm"

		"""print(self.odm.pose.pose.orientation.w)"""

		self.rad = math.degrees(math.acos(self.odm.pose.pose.orientation.w))
		"""Odometry is defined by arc cosine, 
		so Conversion is necessary to obtain conversion angle."""

		while not rospy.is_shutdown():
			twist_pub = rospy.Publisher('/cmd_vel_mux/input/teleop', Twist, queue_size=10, latch=True)
			self.odm_sub = rospy.Subscriber("/odom", Odometry, self.getOdm)
			self.rad = math.degrees(math.acos(self.odm.pose.pose.orientation.w))
			twist = Twist()
			twist.angular.z = 0.5
			twist.linear.x = 0.0
			twist_pub.publish(twist)

			print("----------------")
			# print("I am turning now")
			print(twist.angular.z)
			print(self.rad)
			print("----------------")


			if (88 <= self.rad):
				self.odm_sub = rospy.Subscriber("/odom", Odometry, self.getOdm)
				self.rad = math.degrees(math.acos(self.odm.pose.pose.orientation.w))
				twist.angular.z = 0.0
				twist.linear.x = 0.0
				twist_pub.publish(twist)
				print("----------------")
				print("I turned")
				print("----------------")
				self.turn_end.publish("turned")
				break


if __name__ == '__main__':
	rospy.init_node('spr_start')
	"""
	
	# Speach and personal recognision start.

	os.system('espeak "{I want to play a riddle game}" -s 50')
	print("SPR start")

	os.system('espeak "{I will wait for 10 seconds}" -s 50')
	print("Waiting for 10 seconds")

	sleep(2)
	# Specify waiting time
	"""
	rate = rospy.Rate(5)
	f = odmback()
	while not rospy.is_shutdown():
		rospy.loginfo(f.topicDetector())
		rate.sleep()
		rospy.spin()


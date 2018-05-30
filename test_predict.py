#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import sleep
import model as M
import os
import sys
import rospy
from std_msgs.msg import String
import numpy as np
import argparse
from PIL import Image
import glob

import pickle
import chainer
import chainer.functions as F
import chainer.links as L
import chainer.serializers
from chainer.datasets import tuple_dataset
from chainer import Chain, Variable, optimizers, serializers
from chainer import training
from chainer.training import extensions
import re
import matplotlib.pyplot as plt

def image2data(pathsAndLabels):
	allData = []
	for pathAndLabel in pathsAndLabels:
		path = pathAndLabel[0]
		label = pathAndLabel[1]
		imagelist = glob.glob(path + "*")
		for imgName in imagelist:
			allData.append([imgName, label])
	allData = np.random.permutation(allData)

	imageData = []
	labelData = []
	for pathAndLabel in allData:
		img = Image.open(pathAndLabel[0])
		try:
			imgData = np.asarray(img).transpose(2,0,1).astype(np.float32)/255.
		except ValueError:
			continue
		imageData.append(imgData)
		labelData.append(np.int32(pathAndLabel[1]))
	data = tuple_dataset.TupleDataset(imageData, labelData)

	return data

def topicDetector():
	print("I am waiting for topic")
	rospy.Subscriber("predict", String, main)

def main(msg):
	node_end = rospy.Publisher("messenger", String, queue_size=10, latch=True)
	print(msg)
	cls_names = ['女', '男']

	model = M.Alex()
	model = L.Classifier(model)

	serializers.load_npz('/home/yoshiwo/my_output_2.model', model)

	pathsAndLabels = []
	pathsAndLabels.append(np.asarray(["/home/yoshiwo/images/predict/", 0]))
	data = image2data(pathsAndLabels)

	f_count = 0
	m_count = 0

	for x, t in data:
		model.to_cpu()
		y = model.predictor(x[None, ...]).data.argmax(axis=1)[0]

		print("予測値 : " + cls_names[y])
		if(y == 0):
			f_count = f_count + 1
		else:
			m_count = m_count + 1

		#plt.imshow(x.transpose(1, 2, 0))
		#plt.show()

	all = str(f_count + m_count) + "people"
	males = str(m_count) +"males"
	females = str(f_count) + "females"
	print(str(all))
	print(str(males))
	print(str(females))
	#os.system('espeak {""} -s 100')
	os.system("espeak -v f5 ' " + all + " ' -s 100")
	os.system("espeak -v f5 ' " + males + "and" + females + " ' -s 100")
	#os.system('espeak "{5 people, 3 males and 2 females}" -s 100')
	node_end.publish("predicted")
	os.system('rosnode kill /spr_predict')

if __name__ == '__main__':
	rospy.init_node('spr_predict')
	rate = rospy.Rate(6)
	while not rospy.is_shutdown():
		topicDetector()
		rate.sleep()
		rospy.spin()

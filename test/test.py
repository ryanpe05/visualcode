# allow imports from parent directory
import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import unittest
from visualCode import visualCode

class SyntaxTesting(unittest.TestCase):

	def setUp(self):
		github_url = "git@gitlab.com:ryanpe05/visualcode.git"
		github_weighting = 0.5
		language = "Python"
		dir_names = github_url.split('/')
		project_name = dir_names[-1].replace('.git', '')
		need_download = True
		for path in os.listdir('.'):
			if path == project_name:
				need_download = False
		if need_download:
			os.system("git clone {}".format(github_url))
		use_github = True
		self.myGraphObject = visualCode(project_name, use_github, github_weighting)

	def tearDown(self):
		# remove the files
		# os.remove("visualCode/test/*.json")
		pass

	def testOne(self):
		found_funcs = self.myGraphObject.func_list.keys()
		found_classes = self.myGraphObject.class_list.keys()
		assert found_classes
# allow imports from parent directory
import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import unittest
from visualCode import VisualCode

class SyntaxTesting(unittest.TestCase):

	def setUp(self):
		github_url = "https://github.com/ryanpe05/visualcode.git"
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
		self.myGraphObject = VisualCode(project_name, use_github, github_weighting)

	def tearDown(self):
		# remove the files
		# os.remove("visualCode/test/*.json")
		pass

	def testClasses(self):
		found_classes = self.myGraphObject.class_list.keys()
		expected_classes = ["VisualCode", "SyntaxTesting"]
		for ind_class in found_classes:
			assert ind_class in expected_classes, "Found unexpected class '{}'".format(ind_class)
		for ind_class in expected_classes:
			assert ind_class in found_classes, "Class '{}'' not found".format(ind_class)

	def testFunctions(self):
		found_funcs = self.myGraphObject.func_list.keys()
		expected_funcs = ["hello_world", "generate_graph", "main", "parseFile", "findUses", "searchFile",
			"fillNetwork", "useGitHub", "convertToJSON", "findComments", "setUp", "tearDown",
			"testClasses", "testFunctions"]
		for ind_func in found_funcs:
			assert ind_func in expected_funcs, "Found unexpected function '{}'".format(ind_func)
		for ind_func in expected_funcs:
			assert ind_func in found_funcs, "Function '{}'' not found".format(ind_func)

if __name__ == "__main__":
	unittest.main() # run all tests

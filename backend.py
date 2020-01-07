from flask import Flask, request, render_template, session, redirect, url_for, flash, redirect, jsonify, send_from_directory
from visualCode import VisualCode
import os
app = Flask(__name__)

@app.route('/', methods=["GET","POST"])
def hello_world():
	if request.method == 'POST':
		github_url = request.form['githubUrl']
		github_weighting = float(request.form['githubWeighting'])
		language = request.form['langSel']
		if "github" in github_url:
			dir_names = github_url.split('/')
			project_name = dir_names[-1].replace('.git', '')
			need_download = True
			for path in os.listdir('.'):
				if path == project_name:
					need_download = False
			if need_download:
				os.system("git clone {}".format(github_url))
			use_github = False
			if github_weighting > 0:
				use_github = True
			VisualCode(project_name, use_github, github_weighting)
		else:
			return "You tried to trick me"
		return redirect("submission")
	return render_template("HomePage.html")

@app.route('/submission')
def generate_graph():
	return render_template("Graph.html")

import json
import re
import os
import sys
import shutil
import uuid
import networkx as nx
# from whoosh.fields import *
# from whoosh.query import *
# from whoosh.index import create_in, open_dir
# from whoosh.qparser import QueryParser

def main():
    pass
    # if len(sys.argv) >= 2:
    #     project_dir = str(sys.argv[1])
    #     if len(sys.argv) == 3:
    #         if str(sys.argv[2]) == '-ng':
    #             use_github = False
    #         else:
    #             use_github = True
    #     else:
    #         use_github = True
    # else:
    #     raise ValueError("You didn't specify a project url")
    # if "github" in project_dir:
    #     dir_names = project_dir.split('/')
    #     project_name = dir_names[-1].replace('.git', '')
    #     need_download = True
    #     for path in os.listdir():
    #         if path == project_name:
    #             need_download = False
    #     if need_download:
    #         os.system("git clone {}".format(project_dir))
    # print("Using {} as the project".format(project_name))
    # visualization = VisualCode(project_name, use_github, github_weighting)

class VisualCode():

    def __init__(self, project_dir, use_github, github_weighting):
        self.project_dir = project_dir
        self.file_list = []
        for (dirpath, dirnames, filenames) in os.walk(project_dir):
            for file in filenames:
                self.file_list.append(os.path.join(dirpath, file))
        self.file_network = nx.DiGraph()
        self.unweighted_network = nx.DiGraph()
        self.parseFile()
        print("Found functions and classes")
        self.findUses()
        print("Found their uses and files")
        self.fillNetwork()
        print("Created network of files and weighting")
        if use_github:
            self.useGitHub(github_weighting)
            print("Added github commit weighting")
        self.convertToJSON()
        print("Converted to JSON for visualization")

    def parseFile(self):
        self.func_list = {}
        self.class_list = {}
        cache_size = 0
        self.file_count = 0
        commit_time = True
        # self.schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT(stored=True))
        # self.instance_uuid = str(uuid.uuid1())
        # if not os.path.exists(self.instance_uuid):
        #     os.mkdir(self.instance_uuid)
        # else:
        #     self.instance_uuid = uuid.uuid1()
        #     if not os.path.exists(self.instance_uuid):
        #         os.mkdir(self.instance_uuid)
        #     else:
        #         print("Couldn't make a unique UUID")
        #         raise NameError
        # self.ix = create_in(self.instance_uuid, self.schema)
        # self.writer = self.ix.writer()
        for file in self.file_list:
            if ".py" in file:
                cache_size += os.path.getsize(file)
                with open(file, 'r') as fp:
                    content = fp.read()
                    line_list = content.splitlines()
                    last_defined = None
                    # limit the whoosh cache to 1 GB
                    if cache_size < 10**9:
                        # mytitle = file.replace(self.project_dir, '')
                        # self.writer.add_document(title=mytitle.decode('utf-8', 'ignore'), path=file.decode('utf-8', 'ignore'), content=content.decode('utf-8', 'ignore'))
                        self.file_count += 1
                    else:
                        print("This many files fit in cache: {}".format(self.file_count))
                    # elif commit_time:
                        # self.writer.commit()
                        # commit_time = False
                        # print("Closed writer")
                    file = file.replace(self.project_dir, '')
                    self.file_network.add_node(file)
                    self.unweighted_network.add_node(file)
                    for line in line_list:
                        line = str(line)
                        # if line does not start with a tab/spaces and is not empty, reset flag
                        if not re.match(r"^(?:\t|    )",line) and not re.match(r"\s*$",line):
                            last_defined = None
                        if re.match(r"\s*def ",line):
                            try:
                                func_name = re.search(r"\s*def ([a-zA-Z0-9_-]*)[:\(]", line).group(1)
                                if self.func_list.get(func_name) is None:
                                    self.func_list[func_name] = {
                                        "defined_in": [file],
                                        "used_in": [],
                                        "class": [last_defined],
                                        "rank": 0
                                    }
                                else:
                                    self.func_list[func_name]["class"] = [last_defined]
                                    self.func_list[func_name]["defined_in"].append(file)
                            except:
                                pass
                        elif re.match(r"\s*class ",line):
                            try:
                                class_name = re.search(r"\s*class ([a-zA-Z0-9_-]*)[:\(]", line).group(1)
                                last_defined = class_name
                                if self.class_list.get(class_name) is None:
                                    self.class_list[class_name] = {
                                        "inherits_from": [],
                                        "defined_in": [],
                                        "inherits_it": [],
                                        "used_in": [],
                                        "rank": 0
                                    }
                                self.class_list[class_name]["defined_in"].append(file)
                                # get class(es) this class inherits from
                                if re.search(r"\s*class [a-zA-Z0-9_-]*\((.*)\):", line):
                                    ancestors = re.split(r"\s*,\s*",
                                        re.search(r"\s*class [a-zA-Z0-9_-]*\((.*)\):",
                                        line).group(1))
                                    if ancestors != "":
                                        for ancestor in ancestors:
                                            if ancestor not in self.class_list[class_name]["inherits_from"]:
                                                self.class_list[class_name]["inherits_from"].append(
                                                    ancestor
                                                )
                            except:
                                pass
        # if commit_time:
        #     self.writer.commit()
        #     commit_time = False
        #     print("Closed writer")
        for ind_class in self.class_list:
            for parent in self.class_list[ind_class]["inherits_from"]:
                if parent in self.class_list:
                    self.class_list[parent]["inherits_it"] = ind_class
        for ind_func in self.func_list:
            temp_arr = []
            for ind_class in self.func_list[ind_func]["class"]:
                if ind_class:
                    temp_arr.append(ind_class)
            self.func_list[ind_func]["class"] = temp_arr

    def findUses(self):
        # first use the cache
        # ix = open_dir(self.instance_uuid)
        # with ix.searcher() as searcher:
        #     for ind_class in self.class_list:
        #         writer = ix.writer()
        #         qp = QueryParser("content", schema=ix.schema)
        #         q = qp.parse(ind_class.decode('utf-8'))
        #         q.normalize()
        #         # myquery = Regex("content", r"\b" + ind_class + r"\b")
        #         results = searcher.search(q, limit=None)
        #         results.fragmenter.charlimit = None
        #         for i in range(results.scored_length()):
        #             file = results[i]
        #             if not file:
        #                 continue
        #             # replicate this in searchFile. Don't append used_in if we are in defined_in
        #             if file.get("title") not in self.class_list[ind_class]["defined_in"]:
        #                 print("Searching")
        #                 self.searchFile(str(file.get("path")))
        #                 writer.delete_by_term("path",file.get("path"))
        #         #writer.delete_by_query(myquery)
        #         writer.commit()
        #     for ind_func in self.func_list:
        #         writer = ix.writer()
        #         #qp = QueryParser("content", schema=ix.schema, termclass=Regex)
        #         #my_regex = r"\b" + ind_func + r"\b"
        #         qp = QueryParser("content", schema=ix.schema)
        #         q = qp.parse(ind_func.decode('utf-8'))
        #         q.normalize()
        #         #myquery = Regex("content", r"\b" + ind_func + r"\b")
        #         results = searcher.search(q, limit=None)
        #         results.fragmenter.charlimit = None
        #         for i in range(results.scored_length()):
        #             file = results[i]
        #             if not file:
        #                 continue
        #             if file.get("title") not in self.func_list[ind_func]["defined_in"]:
        #                 print("Searching")
        #                 self.searchFile(str(file.get("path")))
        #                 writer.delete_by_term("path",file.get("path"))
        #         #writer.delete_by_query(myquery)
        #         writer.commit()
        # then search everything we couldn't search before
        # for file in self.file_list[self.file_count+1:]:
        for file in self.file_list:
            if ".py" in file:
                self.searchFile(file)
        with open("function_list.json", "w+") as func_file:
            json.dump(self.func_list, func_file, indent=4)
        with open("class_list.json", "w+") as class_file:
            json.dump(self.class_list, class_file, indent=4)

    def searchFile(self, filename):
        with open(filename, 'r') as fp:
            file = filename.replace(self.project_dir,'')
            line_list = fp.readlines()
            # a list of things which have been imported
            import_arr = []
            for line in line_list:
                line = str(line)
                direct_import = re.search(r"import (.*)", line)
                # tracking which file/module it comes from may be tough
                from_import = re.match(r"from (.*) import", line)
                if direct_import:
                    try:
                        import_arr.extend(direct_import.group(1).replace(" ","").split(","))
                    except:
                        # malformed import?
                        pass
                # import files
                if from_import:
                    try:
                        import_arr.extend(from_import.group(1).split(","))
                    except:
                        # malformed import?
                        pass
                has_comment = False
                in_multi_comment = False
                for ind_class in self.class_list:
                    try:
                        (in_multi_comment, has_comment, comment_ind) = self.findComments(line, in_multi_comment)
                        # search as word to avoid classes that contain other classes
                        # in their names
                        if re.search(r"\b" + ind_class + r"\b", line) and not in_multi_comment:
                            # we have the class
                            # now is it being used or redefined?
                            # is it in a comment?
                            if has_comment:
                                class_index = line.find(ind_class)
                                if comment_ind < class_index:
                                    # it is in a comment
                                    continue
                            if re.search(r"class\s+" + ind_class, line):
                                # it is redefined
                                if file not in self.class_list[ind_class]["defined_in"]:
                                    self.class_list[ind_class]["defined_in"].append(file)
                            elif re.search(ind_class + r"[\.\(]", line):
                                # it is being used if it was imported or defined here
                                if any(x.replace(".py", "") in import_arr for\
                                        x in self.class_list[ind_class]["defined_in"]) or\
                                        file in self.class_list[ind_class]["defined_in"]:
                                    self.class_list[ind_class]["used_in"].append(file)
                    except Exception as e:
                        print("Failed parsing for class {}".format(ind_class))
                        print(e)
                for ind_func in self.func_list:
                    try:
                        (in_multi_comment, has_comment, comment_ind) = self.findComments(line, in_multi_comment)
                        if re.search(r"\b" + ind_func + r"\b", line) and not in_multi_comment:
                            # we have the class
                            # now is it being used or redefined?
                            # is it in a comment?
                            if has_comment:
                                class_index = line.find(ind_class)
                                if comment_ind < class_index:
                                    # it is in a comment
                                    continue
                            if re.search(r"def\s+" + ind_func, line):
                                # it is redefined
                                if file not in self.func_list[ind_func]["defined_in"]:
                                    self.func_list[ind_func]["defined_in"].append(file)
                            elif re.search(ind_func + r"[\.\(]", line):
                                # it is being used
                                if any(x.replace(".py", "") in import_arr for\
                                        x in self.func_list[ind_func]["defined_in"]) or\
                                        any(y.replace(".py", "") in import_arr for\
                                        y in self.func_list[ind_func]["class"]) or\
                                        file in self.func_list[ind_func]["defined_in"]:
                                    self.func_list[ind_func]["used_in"].append(file)
                    except Exception as e:
                        print("Failed parsing for function {}".format(ind_func))
                        print(e)

    def fillNetwork(self):
        edge_dict = {}
        for function in self.func_list.values():
            max_val = 1.0
            if len(function["defined_in"]) != 1:
                # need to handle > 1 better
                continue
            else:
                def_func = function["defined_in"][0].replace(self.project_dir,'')
                edge_dict[def_func] = {}
            # find every time the file was used
            # add one weight each time
            for link in function["used_in"]:
                link_name = link.replace(self.project_dir,'')
                if link_name not in edge_dict[def_func]:
                    edge_dict[def_func][link_name] = 1.0
                else:
                    edge_dict[def_func][link_name] += 1.0
                max_val = max(max_val, edge_dict[def_func][link_name])
            # scale the weighting by the maximum value
            for link in edge_dict[def_func]:
                edge_dict[def_func][link] /= max_val
                self.file_network.add_weighted_edges_from([(def_func,
                    link, edge_dict[def_func][link])])
                self.unweighted_network.add_edge(def_func, link)
        self.page_rank = nx.pagerank(self.file_network)
        self.unweighted_page_rank = nx.pagerank(self.unweighted_network)
        # with open("weighted_network.json", "w+") as weight_file:
        #     json.dump(self.page_rank, weight_file, indent=4)
        # with open("unweighted_network.json", "w+") as unweight_file:
        #     json.dump(self.unweighted_page_rank, unweight_file, indent=4)

    def useGitHub(self, weighting=0.5):
        self.savedPath = os.getcwd()
        os.chdir(self.project_dir)
        output = os.popen('git log --pretty="short" --name-only').read()
        file_uses = {}
        max_uses = 1.0
        for line in output.splitlines():
            file_match = re.match(r"(.*\.py)", line)
            if file_match:
                possible_file = file_match.group(1)
                # need to append the '/' to match other dictionary
                possible_file = "/" + possible_file
                # only care about the file if it is a file we have data on
                if possible_file in self.page_rank:
                    if possible_file in file_uses:
                        file_uses[possible_file] += 1.0
                        max_uses = max(max_uses, file_uses[possible_file])
                    else:
                        file_uses[possible_file] = 1.0
        for file in file_uses:
            file_uses[file] /= max_uses
        for file in self.page_rank:
            self.page_rank[file] += file_uses.get(file, 0.0)*weighting
            self.unweighted_page_rank[file] += file_uses.get(file, 0.0)*weighting
        os.chdir(self.savedPath)
        with open("github_and_weighted_network.json", "w+") as weight_file:
            json.dump(self.page_rank, weight_file, indent=4)
        # with open("github_and_unweighted_network.json", "w+") as unweight_file:
        #     json.dump(self.unweighted_page_rank, unweight_file, indent=4)

    def convertToJSON(self, size_weighting=100):
        # only weighted now
        # adjust size
        pos=nx.spring_layout(self.file_network, scale=200)
        count = 0
        node_list = []
        # make a lookup dictionary
        id_matcher = {}
        for key in self.page_rank:
            node_size = self.page_rank[key] * size_weighting
            try:
                this_id = "n" + str(count)
                node_json = {
                    "id": this_id,
                    "label": key,
                    "x": pos[key][0],
                    "y": pos[key][1],
                    "size": str(node_size)
                }
                id_matcher[key] = this_id
                count += 1
            except:
                print("No position data for file: {}".format(key))
            node_list.append(node_json)
        count = 0
        edge_list = []
        for edge in self.file_network.edges():
            id_0 = id_matcher[edge[0]]
            id_1 = id_matcher[edge[1]]
            edge_id = "e" + str(count)
            edge_json = {
                "id": edge_id,
                "source": id_0,
                "target": id_1
            }
            edge_list.append(edge_json)
            count += 1
        final_json = {
            "nodes": node_list,
            "edges": edge_list
        }
        with open("static/visualization.json", "w+") as viz_file:
            json.dump(final_json, viz_file, indent=4)


    def findComments(self, line, in_multi_comment):
        if re.search(r"#", line):
            # in a single line comment
            has_comment = True
            comment_ind = line.index("#")
            if comment_ind != 0:
                if line[comment_ind-1] == "\\":
                    # literal "#" sign
                    has_comment = False
        else:
            has_comment = False
            comment_ind = -1
        if re.match(r"\w*'''", line):
            in_multi_comment = not in_multi_comment
        return (in_multi_comment, has_comment, comment_ind)

if __name__== "__main__":
    main()

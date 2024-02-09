import sys
import os
import re
import src.dictionary as dictionary

# filter function for get_files
global Home
Home = '/Users/rcumbee/Desktop/Kronos_GUI'
def list_filter(x: str):
	return x.endswith(".cs")

def data_file_dir(ion, ioniz, neutral):
	return Home + f"/cxdatabase-master/Projectile_Ions/{ion}/charge/{ioniz}/Targets/{neutral}/"

def result_file_dir(ion, ioniz, neutral,method,l_dist,Energy):
	# print(l_dist)
	if l_dist != 'l-resolved':
		dir = Home + f"/Results/{ion}{ioniz}+{neutral}/{method}/{l_dist}/{Energy}"
	elif l_dist == 'l-resolved':
		dir = Home + f"/Results/{ion}{ioniz}+{neutral}/{method}/{Energy}"
	if not os.path.exists(dir):
		os.makedirs(dir)
	return dir


# Returns a list of filenames based on given parameters
def get_files(directory):
	# only return .cs files
	filtered = filter(list_filter, os.listdir(directory))
	return list(filtered)

# Return a list of tuples of the following structure: (filename, method_type)
# Extracts the method type from the filename with a regex match
# Note: If not H-like, ignore n-res cross-section file. 
def get_method_list(file_list: list, ion, ioniz):
	element_dict = dictionary.elements()
	Not_H_Like = int(element_dict[ion])-int(ioniz)
	# print(file_list)

	result_list = list()
	r = re.compile(".*?ec_(.*?).cs$")

	for file_name in file_list:
		x = r.match(file_name)
		if Not_H_Like and "nres" in x.group(1):
			pass
		else:
			result_list.append((file_name, x.group(1)))
	return result_list

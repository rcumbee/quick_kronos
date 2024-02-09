import sys,os
try:
    import tkinter as tk
    from tkinter import ttk, Spinbox,Scrollbar
except ImportError:
    import Tkinter as tk
    from Tkinter import ttk, Spinbox,Scrollbar
# from tkinter import filedialog 
from matplotlib import pyplot as plt
from matplotlib import style
import math as np
import pandas as pd
import csv,subprocess,shutil,re
import src.file_utils as fu
import src.cs_utils as cu
import src.dictionary as dictionary
import src.radcashmulti_Fcn as radcashmulti_Fcn 

# Concerns
# 1) What if file name is not recognized? GUI should handle that.

class Kronos_GUI(tk.Frame):
	"""
	This is the overarching model. Within it, it will load an
	ACXDonorModel for each donor atom/molecule. In theory, you should
	be able to load this in XSPEC and be done with it.

	PARAMETERS
	----------
	None

	ATTRIBUTES
	----------
	DonorList : list of ACXDonorModel
		List of donors, (e.g. H, He, H2...). Add to this list using add_donor
	ebins : ndarray(float)
		Energy bin edges for the resulting spectra
	ebins_checksum : md5sum
		The md5 hash of the energy bins. Stored to easily catch changes
	temperature : float
		The temperature in keV

	NOTES
	-----
	Once initialized, call "add_donor" to add donor elements.

	Provide energy bins using set_ebins, temperature with set_temperature

	Then call calc_spectrum to return total spectrum.
	"""	
	global Home
	Home = '/Users/rcumbee/Desktop/Kronos_GUI'
	def __init__(self, master):
		
		# Initializes the frame
		tk.Frame.__init__(self, master)
		
		# Set default directory (grab from command line arguments)
		IonListDir=Home +'/cxdatabase-master/Projectile_Ions'
		Ion_list = [ item for item in os.listdir(IonListDir) if os.path.isdir \
            (os.path.join(IonListDir, item)) ]
		# print(Ion_list)
		Ion_list.sort() 

		self.ldistList = ["low-energy","statistical",'sl1','ACX1','ACX3','ACX4']

		self.Range_Label = tk.Label(master, text="eV/u")
		self.Range_Label.grid(row=5, column=2)

		self.Energy_Label = tk.Label(master, text="Energy:")
		self.Set_Energy_Button= tk.Button(master, text = 
			'Set Energy', command=self.Choose_Energy)
		self.Energy_Entry = tk.Entry(master)

		self.GaussVar = tk.IntVar()
		self.GausButton = tk.Checkbutton(master, text="Gaussian",variable=self.GaussVar, onvalue=1, offvalue=0,).grid(row=2,column=3)


		self.LowE_Entry = tk.Entry(master)
		self.HighE_Entry = tk.Entry(master)
		self.Resolution_Entry = tk.Entry(master)
		self.Smooth_Points_Entry = tk.Entry(master)


		self.LowE_Entry.grid(row=1, column=5)
		self.HighE_Entry.grid(row=2, column=5)
		self.Resolution_Entry.grid(row=3, column=5)
		self.Smooth_Points_Entry.grid(row=4, column=5)

		self.LowE_Entry_Label = tk.Label(master, text="Minimum Energy: ")
		self.LowE_Entry_Label.grid(row=1, column=4)
		self.HighE_Entry_Label = tk.Label(master, text="Maximum Energy: ")
		self.HighE_Entry_Label.grid(row=2, column=4)
		self.Resolution_Entry_Label = tk.Label(master, text="Energy Resolution: ")
		self.Resolution_Entry_Label.grid(row=3, column=4)
		self.Smooth_Points_Entry_Label = tk.Label(master, text="Smooth Points: ")
		self.Smooth_Points_Entry_Label.grid(row=4, column=4)

		self.TextBox = tk.Text(master,  bg = "white",foreground="red")
		self.TextBox.grid(row=7, column=0,rowspan = 15, columnspan=5)
		self.TextBox.insert(tk.END, " \n")
                                    

		# Set the default ion
		self.ion = tk.StringVar()
		#Initialize Ion List
		self.ion.set(Ion_list[21])

		self.ldist = tk.StringVar()
		self.ldist.set(self.ldistList[0])
		
		# Set the default ioniz & neutral
		self.ioniz = tk.StringVar()
		self.neutral = tk.StringVar()
		self.method = tk.StringVar()

		# Define but not initialize thangs
		self.variable_ion = tk.StringVar(self)
		self.variable_ioniz = tk.StringVar(self)
		self.variable_neutral = tk.StringVar(self)
		self.variable_method = tk.StringVar(self)
		self.variable_ldist = tk.StringVar(self)


		# Set the button listeners
		self.variable_ion.trace('w', self.update_ioniz_options)
		self.variable_ioniz.trace('w', self.update_neutral_options)
		self.variable_neutral.trace('w', self.set_neutral_option)
		self.variable_method.trace('w', self.set_method_option)
		self.variable_ldist.trace('w', self.set_ldist_option)

		# option set
		self.optionmenu_ion = tk.OptionMenu(master, self.variable_ion, *Ion_list)
		self.optionmenu_ioniz = tk.OptionMenu(master, self.variable_ioniz, '')
		self.optionmenu_neutral = tk.OptionMenu(master, self.variable_neutral, '')
		self.optionmenu_method = tk.OptionMenu(master, self.variable_method, '')
		self.optionmenu_ldist = tk.OptionMenu(master, self.variable_ldist, '')

		# default settings in GUI
		self.variable_ion.set(self.ion.get())
		self.variable_ioniz.set(self.ioniz.get())
		self.variable_neutral.set(self.neutral.get())
		self.variable_method.set(self.method.get())
		self.variable_ldist.set(self.ldist.get())


		#
		self.Ion_Label = tk.Label(master, text="Ion: ")
		self.Method_Label = tk.Label(master, text="Method: ")
		self.Neutral_Label = tk.Label(master, text="Neutral: ")
		self.Energy_Label = tk.Label(master, text="Collision Energy (eV/u): ")



		# place buttons and labels into frame
		self.Ion_Label.grid(row=2, column=0)
		self.optionmenu_ion.grid(row=2, column=1)
		self.optionmenu_ioniz.grid(row=2, column=2)
		self.Neutral_Label.grid(row=3, column=0)
		self.optionmenu_neutral.grid(row=3, column=1)
		self.Method_Label.grid(row=4, column=0)
		self.optionmenu_method.grid(row=4, column=1)
		self.optionmenu_ldist.grid(row=4, column=2)

		self.Energy_Label.grid(row=5, column=0)
		# self.Set_Energy_Button.grid(row=2, column=1)
		self.Energy_Entry.grid(row=5, column=1)


		# Initialize the GUI buttons
		Set_Parameters_Button= tk.Button(
			master,
			text = 'Run Cascade',
			command=self.Run_Cascade,
			width=15
		)
		Set_Parameters_Button.grid(row=6, column=1)

		Plot_CS_Button= tk.Button(
			master,
			text = 'Plot Cross Sections',
			command=self.Plot_cross_sections,
			width=15
		)
		Plot_CS_Button.grid(row=6, column=2)

		Plot_line_spectrum_Button= tk.Button(
			master,
			text = 'Plot Line Spectrum',
			command=self.plot_line_spectrum,
			width=15
		)
		Plot_line_spectrum_Button.grid(row=6, column=3)

		QuitButton = tk.Button(
			master,
			text = 'Quit',
			command=master.quit,
			width=15
		)
		QuitButton.grid(row=6, column=4)

		# Pack myself
		self.master.grid()

	def print_percents(func):
		def wrapper(*args, **kwargs):
			print("%" * 60)
			print('\n')
			func(*args, **kwargs)
			print('\n')
			print("%" * 60)
		return wrapper

	def print_stars(func):
		def wrapper(*args, **kwargs):
			print("*" * 60)
			func(*args, **kwargs)
			print("*" * 60)
		return wrapper

	def print_double_stars(func):
		def wrapper(*args, **kwargs):
			print("*" * 60)
			print("*" * 60)
			func(*args, **kwargs)
			print("*" * 60)
			print("*" * 60)

		return wrapper


	@print_percents
	def print_statement(self,statement):
		print (statement)
		return ;

	# Onchange for ion (main) variable
	def update_ioniz_options(self, *args):
		# Get the ion directory
		new_ion = self.variable_ion.get()
		self.ion.set(new_ion)

		IonizListDir = Home+'/cxdatabase-master/Projectile_Ions/'+ new_ion +"/charge"
		# Get list from directory (maybe caching?)
		Ioniz_list = [ int(item) for item in os.listdir(IonizListDir) if \
            os.path.isdir(os.path.join(IonizListDir, item)) ]
		#Initialize the ionization stage. 
		Ioniz_list.sort(reverse=True) 

		self.ioniz.set(Ioniz_list[0])

		# Set the GUI option (I think)
		self.variable_ioniz.set(self.ioniz.get())

		# Something
		menu = self.optionmenu_ioniz['menu']
		menu.delete(0, 'end')

		new_ioniz = self.variable_ioniz.get()
		
		# self.variable_ioniz.set(self.ioniz.get())
		for new_ioniz in Ioniz_list:
			menu.add_command(label=new_ioniz, command=lambda nation=new_ioniz: \
                self.variable_ioniz.set(nation))

		self.update_neutral_options()

	def update_neutral_options(self, *args):
		new_ioniz = self.variable_ioniz.get()
		self.ioniz.set(new_ioniz)

		neutralListDir = Home+'/cxdatabase-master/Projectile_Ions/'+ self.ion.get() + \
            "/charge/" + str(new_ioniz) + "/Targets"
		# print ("update neutral dir", neutralListDir);
		neutral_list = [ item for item in os.listdir(neutralListDir) if \
            os.path.isdir(os.path.join(neutralListDir, item)) ]
		neutral_list.sort()

		#Initialize Neutral 
		self.neutral.set(neutral_list[0])
		self.variable_neutral.set(self.neutral.get())
		
		# ?
		menu = self.optionmenu_neutral['menu']
		menu.delete(0, 'end')

		new_neutral = self.variable_neutral.get()
		
		self.variable_neutral.set(self.neutral.get())
		for new_neutral in neutral_list:
			menu.add_command(label=new_neutral, command=lambda nation= \
                new_neutral: self.variable_neutral.set(nation))

		self.set_neutral_option()

	def set_neutral_option(self, *args):
		self.neutral.set(self.variable_neutral.get())
		self.update_method_options()

	# def Open_Random_files():
	# Regular expression opens all files of a certain type. 
	def update_method_options(self, *args):
		ion,ioniz,neutral,method,l_dist = self.Get_CX_Info()
		directory = fu.data_file_dir(ion,ioniz,neutral)
		file_list = fu.get_files(directory)
		method_lst = fu.get_method_list(file_list,self.ion.get(),self.ioniz.get())

		# Initialize Method from tuple array
		self.method.set(method_lst[0][1])

		# Set the GUI option (I think)
		self.variable_method.set(self.method.get())

		# Something
		menu = self.optionmenu_method['menu']
		
		menu.delete(0, 'end')

		new_method = self.variable_method.get()
		
		for (_filename, new_method) in method_lst:
			menu.add_command(label=new_method, command=lambda nation=new_method\
                : self.variable_method.set(nation))
		self.set_method_option()

	def set_method_option(self, *args):

		self.method.set(self.variable_method.get())
		self.Set_Energy_Range()
		self.update_ldist_option()

	def update_ldist_option(self,*args):
		ion, ioniz, neutral, method,l_dist = self.Get_CX_Info()

		if "nres" in method:
			# self.set_l_distribution()
			llist = self.ldistList

		elif "nres" not in method:	
			llist = list()
			llist.append('l-resolved')

		self.ldist.set(llist[0])
		# print ('line 282',list)
		self.variable_ldist.set(self.ldist.get())

		new_ldist = self.variable_ldist.get()
		self.ldist.set(new_ldist)

		menu = self.optionmenu_ldist['menu']
		menu.delete(0, 'end')

		for (new_ldist) in llist:
			menu.add_command(label=new_ldist, command=lambda nation=new_ldist\
                : self.variable_ldist.set(nation))
		self.set_ldist_option()

	def set_ldist_option(self,*args):
		self.ldist.set(self.variable_ldist.get())

	def Plot_cross_sections(self, *args):
		self.TextBox.insert(tk.END, "Plotting cross-sections \n")
		self.TextBox.update()

		style.use('ggplot')
		df = self.get_cross_sections()
		df.set_index("(eV/u)", inplace= True)
		df.replace(0, np.nan).plot()
		ion,ioniz,neutral,method,l_dist = self.Get_CX_Info()
		# title_str = (ion, ioniz, "CX with ", neutral, "using the ", method, "method").format()
		title_str = ("{0}{1}+ CX with {2}: {3} method").format(ion,ioniz,neutral,method)
		plt.title(title_str)
		plt.ylabel('Cross-sections')
		plt.xlabel('Collision Energy (eV/u)')
		plt.xscale("log")
		plt.yscale("log")

		#plt.xlim(1., 1000.0)
		#plt.ylim(0, 1.0)
		plt.show()

		return()

	def get_cross_sections(self, *args):
		file_path = self.get_file_path()
		f = open(file_path, 'r')

		# We ignore the first 7 commented lines. The point of this is to
		# ignore the "#" on line 8 of the cross-section file so that it can
		# be used as lables.
		for i in range(7): line = f.readline()
		line1 = f.readline()
		#Search for duplicates
		names1=line1.replace('#', '').split()
		# print(names1)
		dupItems = []
		uniqItems = {}
		for x in names1:
			if x not in uniqItems:
				uniqItems[x] = 1
			else:
				if uniqItems[x] == 1:
					dupItems.append(x)
				uniqItems[x] += 1
			# print (uniqItems[x])

		# print("duplicate",dupItems)


		# print(line1)
		df = pd.read_csv(f, sep='\s+', names=line1.replace('#', '').split())
		# print(df)
		return (df)

	# This function returns the cross-sections and the labels. 
	def get_specific_cross_sections(self, *args):
		Energy, index_val = self.get_CX_Energy()
		CX_df = self.get_cross_sections()
		CX_lst = CX_df.loc[index_val].reset_index().values.tolist()
		print (CX_df)
		# print (CX_lst)
		

		return(CX_lst)

	def get_file_path (self, *args):
		# Note that after I run the function once, the folder
		# is now directed to the tmp. This causes issues.
		ion = self.ion.get()
		ioniz = self.ioniz.get()
		neutral = self.neutral.get()
		method = self.method.get()

		FileDir = fu.data_file_dir(ion, ioniz, neutral)

		# return the full path
		method_list = fu.get_method_list(fu.get_files(FileDir),ion,ioniz)
		for (file_name, t_method) in method_list:
			if method == t_method:
				return FileDir + "/" + file_name
		return file_path # Error handle here

	def find_energy_range(self, *args):
		data = self.get_cross_sections()
		Range = str(str(data['(eV/u)'].min()) + "-" + str(data['(eV/u)'].max()))
		return(data['(eV/u)'].min(),data['(eV/u)'].max(),Range)

	def Set_Energy_Range(self, *args):
		min,max,Range = self.find_energy_range()
		self.Energy_Entry.delete(0, 'end')
		self.Energy_Entry.insert(0,1000 )
		self.Range_Label['text'] = "Range: " + Range + " eV/u "

	def Choose_Energy(self, *args):
		min,max,Range = self.find_energy_range()
		Chosen_Energy = self.Energy_Entry.get()
		# 	Verify that a float value within range is chosen. 
		try:
			float(Chosen_Energy)
		except ValueError:
			print ("Please choose a numerical value for the Energy")
			self.TextBox.insert(tk.END, "Please choose an appropriate value for the Energy  \n")
			self.TextBox.insert(tk.END, Range + " eV/u \n\n")
			self.TextBox.update()
			self.Energy_Entry.delete(0, 'end')
			Energy = "Please choose Energy"
			raise
		else: 
			# Within range
			if float(min) < float(Chosen_Energy) < float(max):
				Energy = Chosen_Energy
			else:
				# Outside of Range
				print ("Energy is out of range:", Range, "eV/u")
				self.TextBox.insert(tk.END, "Energy is out of range  \n\n")
				self.TextBox.insert(tk.END, Range + " eV/u \n\n")
				self.TextBox.update()
				self.Energy_Entry.delete(0, 'end')
				Energy = "Please choose Energy"
		return(Energy)	

	# Find energy in file closest to chosen energy. 
	def find_nearest_Energy(self, *args):
		data = self.get_cross_sections()
		# chosen value
		Energy_Value = float(self.Choose_Energy())
		#	Index of actual value
		#	Chooses the first instance of the minimim difference between
		#	choosen energy and energy in file. 
		ind = abs(data["(eV/u)"]-Energy_Value).idxmin()

		#	Value of that index. 
		# closest_Value = data.loc[ind,['(eV/u)']]
		closest_Value = data.loc[ind,'(eV/u)']
		# print ('Line 319',ind,closest_Value)
		return(closest_Value, ind)

	def get_CX_Energy(self, *args):
		Chosen_Energy = self.Choose_Energy()
		Real_Energy, index_value = self.find_nearest_Energy()
		return(Real_Energy,index_value)		

	def eV_to_km_s( *args):
		print ("The conversion to km/s is:")
		
	def convertspeed(E):
		z = ((E/1000.0)/25.0)**0.5 * 2.1877E3
		return z

	def Get_CX_Info(self, *args):
		ion = self.ion.get()
		ioniz = self.ioniz.get()
		neutral = self.neutral.get()
		method = self.method.get()
		l_dist = self.ldist.get()
		return(ion,ioniz,neutral,method,l_dist)

	def gaussian(self, df):
		import math
		print ("Gaussian Convolution in Progress. ")
		NumEnergies = len(df.ene) 
		ion,ioniz,neutral,method,l_dist = self.Get_CX_Info()
		Energy, index_val = self.get_CX_Energy()
		FileDir = fu.result_file_dir(ion,ioniz,neutral,method,l_dist,Energy)


		if not self.HighE_Entry.get():
			maxe = max(df.ene) * 1.3
		else:
			maxe = float(self.HighE_Entry.get())
		if not self.LowE_Entry.get():
			mine = 250
		else:
			mine = float(self.LowE_Entry.get())
		if not self.Resolution_Entry.get():
			delta = 10.
		else:
			delta = float(self.Resolution_Entry.get())
		
		if not self.Smooth_Points_Entry.get():
			datapoints = int((maxe-mine)/delta*4.)
		else:
			print("Smooth Points filled in")
			datapoints = int(self.Smooth_Points_Entry.get())

		self.LowE_Entry.delete(0, 'end')
		self.LowE_Entry.insert(0, mine)
		self.HighE_Entry.delete(0, 'end')
		self.HighE_Entry.insert(0,maxe )
		self.Resolution_Entry.delete(0, 'end')
		self.Resolution_Entry.insert(0,delta )
		self.Smooth_Points_Entry.delete(0, 'end')
		self.Smooth_Points_Entry.insert(0,datapoints )

		df_Energy_Range = df[(df.ene >= mine) & (df.ene <= maxe )]
		df_Energy_Range = df_Energy_Range.reset_index(drop=True)
		NumEnergies = len(df_Energy_Range)

		# with open(FileDir + "/Convolved_Spectrum.dat", 'w') as OutFile:
		# 	for i in range(0, datapoints):
		# 		e = mine + i * (maxe - mine)/datapoints

		# 		# numenergies is a constant # of original points
		# 		emis = 0.0
		# 		for j in range(1, NumEnergies+1):
		# 			expo = math.exp(-((e-df_Energy_Range.ene[int(j)-1])/delta)**2)
		# 			emis = emis + df_Energy_Range.spec[int(j)-1] * expo
		# 		if emis > 0.00000000001:
		# 			OutFile.write(" \n %s %s" % (str(e), str(emis)))
		# 	OutFile.close()
		# return()
		with open(FileDir + "/Convolved_Spectrum.dat", 'w') as OutFile:
			for i in range(0, datapoints):
				e = mine + i * (maxe - mine)/datapoints
				print(e)

				# numenergies is a constant # of original points
				emis = 0.0
				for j in range(1, NumEnergies+1):
					print(e, j, NumEnergies,datapoints,df_Energy_Range.spec[int(j)-1])

					# expo = math.exp(-((e-df_Energy_Range.ene[int(j)-1])/( delta))**2)
					# emis = emis+df_Energy_Range.spec[int(j)-1] * expo
					expo = math.exp(-((e-df_Energy_Range.ene[int(j)-1])/delta)**2)
					emis = emis + df_Energy_Range.spec[int(j)-1] * expo
					# emis = emis + emis/(delta * np.sqrt(2*np.pi))
					# OutFile.write(" \n %s %s" % (str(e), str(emis)))
				if emis >  1e-40:
					OutFile.write(" \n %s %s" % (str(e), str(emis)))
			OutFile.close()
		return()

		
	def plot_line_spectrum(self, *args):
		import time

		ion,ioniz,neutral,method,l_dist = self.Get_CX_Info()
		Energy, index_val = self.get_CX_Energy()
		FileDir = fu.result_file_dir(ion,ioniz,neutral,method,l_dist,Energy)

		# Now we plot.
		if os.path.isfile(FileDir + '/Full_Spectrum.dat'):
			print ("Spectral Data File does exist")
			print(FileDir)
			f = open(FileDir + '/Full_Spectrum.dat', 'r')
			df=pd.read_csv(f,skiprows=1, sep=',')	
			f.close()
			df.columns = ['ene','spec']
			df = df.sort_values(by=['ene'])	
			df = df.reset_index(drop=True)
			# print(df.ene)
			new_df = df[(df['ene']>0)]

			if (self.GaussVar.get() == 1):
				self.TextBox.insert(tk.END, "Plotting Gaussian convolved Spectrum \n")
				self.TextBox.update()
				self.TextBox.insert(tk.END, "The Gaussian convolution parameters can be modified  \n")
				self.TextBox.insert(tk.END, "to produce a convolved spectrum of your choice.  \n")
				self.TextBox.insert(tk.END, "The final convolved spectrum will be saved based on these parameters. \n\n")


				print("Gaussian Convolution")
				self.gaussian(new_df)

				f2 = open(FileDir + '/Convolved_Spectrum.dat', 'r')
				df2=pd.read_csv(f2,skiprows=1, sep='\s+')	
				df2.columns = ['e1','spec1']	
				f2.close()

				title_str = ("{0}{1}+ CX with {2}: {3} method").format(ion,ioniz,neutral,method)
				plt.title(title_str)
				plt.ylabel('Relative Intensity (arb units)')
				plt.xlabel('Photon Energy (eV)')

				plt.stem(df.ene, df.spec, markerfmt=' ')
				(markers, stemlines, baseline) = plt.stem(df.ene, df.spec,use_line_collection=True, markerfmt=' ')
				plt.setp(stemlines, linestyle="-", color="red", linewidth=0.5 )
				plt.setp(baseline, linestyle="-", color="black", linewidth=0.5 )
				plt.plot(df2.e1,df2.spec1, linestyle="-", color="black", linewidth=0.5)
				plt.show()


			elif(self.GaussVar.get() == 0):
				self.TextBox.insert(tk.END, "Plotting line Spectrum \n\n")

				print ("No Gaussian Convolution")
				title_str = ("{0}{1}+ CX with {2}: {3} method").format(ion,ioniz,neutral,method)
				plt.title(title_str)
				plt.ylabel('Relative Intensity (arb units)')
				plt.xlabel('Photon Energy (eV)')

				(markers, stemlines, baseline) = plt.stem(df.ene, df.spec,use_line_collection=True, markerfmt=' ')
				plt.setp(stemlines, linestyle="-", color="red", linewidth=0.5 )
				plt.setp(baseline, linestyle="-", color="black", linewidth=0.5 )

				plt.show()

		else:
			print ("Spectral Data File does not exist")

	@print_stars
	# @print_percents

	def Run_Cascade(self, *args):
		element_dict = dictionary.elements()
		ion, ioniz, neutral, method,l_dist = self.Get_CX_Info()
		ZIon = int(element_dict[ion])
		Energy, index_val = self.get_CX_Energy()
		WorkDir = fu.result_file_dir(ion,ioniz,neutral,method,l_dist,Energy)

		statment = 'Performing the radiative cascade for the following collision system \n' + '%s%s+  + %s using the %s method at %s eV/u' % (ion, ioniz, \
            neutral, method, Energy)
		self.print_statement(statment)
		self.TextBox.insert(tk.END,statment + '\n')
		self.TextBox.update()
		# get the orbital angular momentum quantum numbers dictionary
		dict = dictionary.l_dict()

		CS_lst = self.get_specific_cross_sections()
		# print (CS_lst)

		File_Dir = fu.data_file_dir(ion, ioniz, neutral)
		RADRATHE = File_Dir + "radrathe.dat"
		# print(RADRATHE)

		try:
			shutil.copyfile(RADRATHE, WorkDir + "/radrathe.dat")
		except FileNotFoundError:
			self.TextBox.insert(tk.END, "Radiative data file not found. \n")
			self.TextBox.insert(tk.END, "Cannot perform this calculation without the radiative data file. \n")
			self.TextBox.insert(tk.END, "Please check for 'radrathe.dat' file. \n\n")
			self.TextBox.update()
			raise

		if "nres" in method:
			l_dist = self.ldist.get()
			cu.get_n_res_cs_list(CS_lst)
			nl_cs_lst = cu.calculate_l_distribution(CS_lst,l_dist,ZIon)
			self.TextBox.insert(tk.END, "using n-resolved cross-sections  \n")
			self.TextBox.insert(tk.END, "Please verify your choice for l-distribution.  \n\n")
			self.TextBox.update()
			print ("Looking at N-resolved cross-sections.")
			#write input cross-section file for this specific energy
			# in the format 
			# n, l, s, cross-section ()

			output = open(WorkDir + "/input_CS.dat", 'w')
			outarr = zip(nl_cs_lst[0],nl_cs_lst[1],nl_cs_lst[2],nl_cs_lst[3])
			output.write('\n'.join('%3s %3s %3s %15s ' % x for x in outarr))
			output.close()

		# If the CS files are not n-resolved, then they should be ready for 
		# radiative cascade. 
		elif "nres" not in method:	
			# First, we want to read the n,l,s and the cross-section from the file.
			# For this stage, we then write an init.dat file, and perform the calculations.
			# self.TextBox.insert(tk.END,statment + '\n')
			self.TextBox.insert(tk.END, "using nls-resolved cross-sections.  \n\n")

			init_Arr = [[] for _ in range(7)]
			for i in range(1,len(CS_lst)-1):

			# for element in name:
			# 	m = re.match("(^[A-Z]\d[A-Z]\d)", element)
			# 	if m:
			# 		print(m.groups())

			# Regular expression 
			# We use a regualr expression (r) to read the components of the
			# index The index should be formed as follows: 9l(2L)

				r_LS = re.compile("([0-9]+)([a-zA-Z]+)\(([0-9]+)([a-zA-Z]+)\)$")
				r_LS2 = re.compile("([0-9]+)([a-zA-Z]+)\(([0-9]+)([a-zA-Z]+)\)([0-9]+)")

				rel_LS = r_LS.match(CS_lst[i][0].strip())
				match_LS = re.match(r_LS, CS_lst[i][0].strip())

				rel_LS2 = r_LS2.match(CS_lst[i][0].strip())
				match_LS2 = re.match(r_LS2, CS_lst[i][0].strip())

				if match_LS:
					# print ('regular expressionn', rel_LS)
					sdict = dictionary.s_dict()
					if rel_LS:
						init_Arr[0].append(rel_LS.group(1))
						init_Arr[1].append(dict[rel_LS.group(2)])
						init_Arr[2].append(sdict[rel_LS.group(3)])
						init_Arr[3].append(dict[(rel_LS.group(4)).lower()])
						init_Arr[4].append(1) #counter
						init_Arr[5].append(CS_lst[i][1]*1e-16)
				elif match_LS2:
					# print ('regular expressionn', rel_LS2)
					sdict = dictionary.s_dict()
					if rel_LS2:
						init_Arr[0].append(int(rel_LS2.group(1))) #n
						init_Arr[1].append(dict[rel_LS2.group(2)]) #l
						init_Arr[2].append(rel_LS2.group(3)) #S
						init_Arr[3].append(dict[(rel_LS2.group(4)).lower()]) #L
						init_Arr[4].append(rel_LS2.group(5)) #counter
						init_Arr[5].append(CS_lst[i][1]*1e-16)
			
			output = open(WorkDir + "/input_CS.dat", 'w')
			if rel_LS :
				outarr = zip(init_Arr[0],init_Arr[1],init_Arr[2],init_Arr[4])
				outarr = zip(init_Arr[0],init_Arr[1],init_Arr[3],init_Arr[2],init_Arr[4],init_Arr[5])
				# sorted(outarr)
				output.write('\n'.join('%3s %3s %3s %3s %3s %15s ' % x for x in outarr))
			elif rel_LS2:
				# want n, l, L, (2S + 1), Counter, CS
				outarr = zip(init_Arr[0],init_Arr[1],init_Arr[3],init_Arr[2],init_Arr[4],init_Arr[5])
				outarr = sorted(outarr, key = lambda x:(x[0],x[1],x[2],x[3],x[4]))
				output.write('\n'.join('%3s %3s %3s %3s %3s %15s ' % x for x in outarr))
				output.write('# n, l, L, S, Counter, CS \n')

			output.close()

			num_Spins = len(set(init_Arr[2]))

		radcashmulti_Fcn.cascade(ion, ioniz, neutral,method,l_dist,Energy)
		self.print_statement("Radiative Cascade Complete")
		self.TextBox.insert(tk.END, "Radiative Cascade Complete  \n")
		print(ion, ZIon,ioniz, neutral, method,l_dist)
		self.TextBox.insert(tk.END, "\n")

if __name__ == "__main__":
	root = tk.Tk()
	root.title("KRONOS CX DATABASE")
	app = Kronos_GUI(root)
	app.mainloop()

def main():
	root = tk.Tk()
	root.title("KRONOS CX DATABASE")
	app = Kronos_GUI(root)
	app.mainloop()
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import os
import src.dictionary as dictionary
import src.file_utils as fu

# initial constants
NI = 'ni'
LI = 'li'
LLI = 'lli'
SI = 'Si'
COUNTI = 'Counti'
# final constants
NF = 'nf'
LF = 'lf'
LLF = 'llf'
SF = 'Sf'
COUNTF = 'Countf'
E = 'E'
A = 'A'
# regular constants
N = 'n'
L = 'l'
LL = 'll'
S = 'S'
COUNT = 'Count'
CS = 'CS'

# curr_dir == os.getcwd()


##################### 
# helper functions! #
#####################

# f2s takes in a float, converts to an integer, then a string
# Probably a better way to do this 
def f2s(a):
    return str(int(a))

def concatenator(array):
    return "-".join(map(f2s, array))


#####################
# class definitions #
#####################
class State(object):

    def __init__(self, name, cross_value):
        self.name = name
        self.CS = cross_value
        self.probability_sum = 0
        self.ratio = 0
        self.photon = 0

    def GetName(self):
        return self.name

    # takes a value, and sums it with the existing value
    def UpdateCross(self, value):
        self.CS += value

    def GetCross(self):
        return self.CS

    def UpdateProb(self, value):
        self.probability_sum += value

    def GetProb(self):
        return self.probability_sum

    # Calculates the final intensity 
    def Calc_intensity(self, a_val):
        return self.CS * a_val / self.probability_sum

    # Converts energy from Radrathe file in () to energy in KeV
    def Energy_to_KeV(self, ene):
        return 1.0E8/ene/8065.5

    def __str__(self):
        return "Exists"
        # return f'cross_section: {self.CS}, predecessors: {self.predecessors}, descendants: {self.descendants}'

def read_Radrathe(path):
    WorkDir = path

    # Step 1: Read in Radrathe
    RR_file_path = WorkDir + "/radrathe.dat"
    f = open(RR_file_path, 'r')
    RR_df = pd.read_csv(
        f,
        sep='\s+',
        comment='#',
        header=None
        # names=[NI, LI, SI,NF, LF, SF,  E, A]
    )
    RR_df = RR_df.round(8)

    # Here, we define the names based on the number of columns. 
    if len(RR_df. columns) == 8:
        RR_df.columns = [NI, LI, SI,NF, LF, SF,  E, A]
    elif len(RR_df. columns) == 6:
        RR_df.columns = [NI, LI,NF, LF,  E, A]
    elif     len(RR_df. columns) == 12:
        RR_df.columns = [NI, LI, LLI, SI, COUNTI, NF, LF, LLF, SF, COUNTF, E, A]
    else:
        print ("Can not read in this RADRATHE file.")
        sys.exit()
    return(RR_df)

def read_Cascade(path ):
    # Step 2: Read in init_CS
    WorkDir = path

    CS_file_path = WorkDir + "/input_CS.dat"
    f = open(CS_file_path, 'r')
    CS_df = pd.read_csv(
        f,
        sep='\s+',
        comment='#',
        header=None
        # names=[N, L, S, CS]
    )
    # Here, we define the names based on the number of columns. 

    if len(CS_df. columns) == 4:
        CS_df.columns = [N, L, S, CS]
    elif len(CS_df. columns) == 3:
        CS_df.columns = [N, L, CS]
    elif len(CS_df. columns) == 6:
        CS_df.columns = [N, L, LL, S, COUNT, CS]
    else:
        print ("Can not read in the CS file. ")
    return (CS_df)

def cascade(ion, ioniz, neutral,method, l_dist,Energy):
##############
# Processing #
##############
    WorkDir = fu.result_file_dir(ion, ioniz, neutral,method, l_dist,Energy)

    RR_df = read_Radrathe(WorkDir)
    CS_df = read_Cascade(WorkDir)

    #--------------------------------------------------------------------------
    # Verify that the shape of the Radrathe and Cross-section files are the same.
    # If they are not- remove appropriate columns. 
    #--------------------------------------------------------------------------

    if len(CS_df.columns) == len(RR_df.columns)/2.0 :
        print ("")
    elif len(CS_df.columns) < len(RR_df.columns)/2.0 :
        if RR_df['lli'].eq(RR_df['li']).all(): 
            RR_df=RR_df.drop(columns=['lli', 'Counti','llf',  'Countf'])
        else:
            print ("Error: Mismatch between Radrathe and CS file")
            print ("Mismatch between Radrathe and CS file", len(CS_df.columns), len(RR_df.columns))
    elif len(CS_df.columns) == 6 and len(RR_df.columns) == 8:
        print ("Mismatch between Nist and AUTOSTRUCTURE radrathe", len(CS_df.columns), len(RR_df.columns))
        if CS_df['Count'].eq(CS_df['Count'].iloc[0]).all():
            CS_df=CS_df.drop(columns=['Count','ll'])
        else: 
            print ("Error: Mismatch between Radrathe and CS file")
            print ("Mismatch between Radrathe and CS file", len(CS_df.columns), len(RR_df.columns))

    #--------------------------------------------------------------------------
    # Create a map of concatenated CS quantum values to query against.
    # These are unique
    #--------------------------------------------------------------------------
    CS_map = dict()
    for index, row in CS_df.iterrows():
        if len(CS_df. columns) == 4:
            key = concatenator([row.n, row.l, row.S]) 
        elif len(CS_df. columns) == 6:
            key = concatenator([row.n, row.l, row.ll, row.S,row.Count])   
        elif     len(CS_df. columns) == 3:
            key = concatenator([row.n, row.l])
        else:
            print("First Loop, missing init & final")
        CS_map[key] = row[CS] # row[CS] is the same as row.CS
        
    # Create a string from concatenated initial values
    # Check to see if these concatenated strings exist in the CS quantum value set
    # Add the values to the list
    Init_Cross_section_List = list()
    Intensity_List = list()
    for index, row in RR_df.iterrows():
        # initial set
        tmp = concatenator([row.ni, row.li, row.Si, ])
        
        if tmp in CS_map:
            cross_section = CS_map[tmp]
            Init_Cross_section_List.append(cross_section)
            Intensity_List.append(cross_section*row[A])
        else:
            Init_Cross_section_List.append(0) # placeholder for now
            Intensity_List.append(0)

    # Add a new column to the panda dataframe
    RR_df["Initial_CrossSection"] = Init_Cross_section_List
    RR_df["Initial_Intensity"] = Intensity_List
    print('RRDF')
    RR_df

    # These have to be in descending order in regards to NI value from here
    RR_df.sort_values(by = NI, axis=0, ascending=False, inplace=True)

    # Calculate branching ratios
    # initializes initial cross-section
    state_hash_map = dict()
    for index, row in RR_df.iterrows():
        if len(RR_df. columns) == 8+2:
            initial = concatenator([row.ni, row.li, row.Si])
            final = concatenator([row.nf, row.lf, row.Sf])   
        elif len(RR_df. columns) == 6+2:
            initial = concatenator([row.ni, row.li])
            final = concatenator([row.nf, row.lf])     
        elif     len(RR_df. columns) == 12+2:
            initial = concatenator([row.ni, row.li, row.lli, row.Si, row.Counti])
            final = concatenator([row.nf, row.lf, row.llf, row.Sf, row.Countf])
        else:
            print("First Loop, missing init & final")
        # Get the initial state if it exists, create if it doesn't
        if initial in state_hash_map:
            state_init = state_hash_map[initial]
        else:
            cross_temp = 0
            if initial in CS_map:
                cross_temp = CS_map[initial]
            # create state
            state_init = state_hash_map[initial] = State(initial, cross_temp)


        # Get the final state if it exists, create if it doesn't
        if final in state_hash_map:
            state_fin = state_hash_map[final]
        else:
            cross_temp = 0
            if final in CS_map:
                cross_temp = CS_map[final]
            state_fin = state_hash_map[final] = State(final, cross_temp)

        # sum the probabilities and store in initial
        # calculate branching ratios
        state_init.UpdateProb(row[A])

    # when we're done with above loop, we have a sum of all A values
    # from initial to all finals

    # In this loop, we sum the cross sections for each final state
    # Calculates CS_new
    # Calculates Photon Intensity. 

    Spectrum_df = pd.DataFrame(columns=['initial', 'final', 'Energy', 'Intensity'])

    for index, row in RR_df.iterrows():
        if len(RR_df. columns) == 8 +2:
            initial = concatenator([row.ni, row.li, row.Si])
            final = concatenator([row.nf, row.lf, row.Sf])   
        elif len(RR_df. columns) == 6 +2:
            initial = concatenator([row.ni, row.li])
            final = concatenator([row.nf, row.lf])     
        elif     len(RR_df. columns) == 12 +2:
            initial = concatenator([row.ni, row.li, row.lli, row.Si, row.Counti])
            final = concatenator([row.nf, row.lf, row.llf, row.Sf, row.Countf])
        else: 
            print ('Final loop. Missing init and final ')

        state_init = state_hash_map[initial]
        state_fin = state_hash_map[final]
        state_fin.UpdateCross(state_init.GetCross() * row[A]/state_init.GetProb())

        if state_fin.GetCross() > 1e-40 and state_init.GetCross() > 0.0: 
            energy = state_init.Energy_to_KeV(row[E])
            intensity = state_init.Calc_intensity(row[A])
            # Spectrum_df = Spectrum_df.append({'initial': initial, 'final': final, 'Energy': energy, 'Intensity': intensity}, ignore_index=True )
            # df = pd.concat([df, pd.DataFrame.from_records([{ 'a': 1, 'b': 2 }])])
            Spectrum_df = pd.concat([Spectrum_df, pd.DataFrame.from_records([{'initial': initial, 'final': final, 'Energy': energy, 'Intensity': intensity}])])



    # Spectrum_df.sort_values('Energy', 0, False, True)
    Spectrum_df.sort_values(by= 'Energy', axis=0, ascending=False, inplace=True)
    Spectrum_df.to_csv(WorkDir + '/Spec_Data_py.dat', index = False, header = False)

    final_spec = Spectrum_df[['Energy', 'Intensity']]
    final_spec=final_spec.sort_values(by='Energy', ascending=True, na_position='first')
    final_spec.to_csv(WorkDir + '/Full_Spectrum.dat', index = False, header = False)

    print(final_spec)

    return(final_spec)


    


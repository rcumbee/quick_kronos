import re
import math
def get_n_res_cs_list(n_cs_list):
	result_list = list()

	cs_list = [[] for _ in range(2)]

	r = re.compile(".*?n=(.*)")

	for cs in n_cs_list:
		if "=" in cs[0]:
			x = r.match(cs[0])
			cs_list[0].append(x.group(1))
			cs_list[1].append(cs[1])
	return(cs_list)


def calculate_l_distribution(n_cs_list,ldist,Z):
	List_n = get_n_res_cs_list(n_cs_list)
	nl_cs_list = [[] for _ in range(4)]
	for index, n in enumerate(List_n[0]):
		for l in reversed(range(int(n))):
			n_cs = List_n[1][index]
			if ldist == "low-energy":
				cs_fcn_stat = lowEnergy(n,l)
			elif ldist =="statistical":
				cs_fcn_stat = statistical(n,l)
			elif ldist == "sl1":
				cs_fcn_stat = SL1(n,l)
			elif ldist == "ACX1":
				cs_fcn_stat = ACX1(n,l)
			elif ldist == "ACX3":
				cs_fcn_stat = lowEnergyModifiedACX(n,l)
			elif ldist == "ACX4":
				cs_fcn_stat = ACX4(n,l,Z)
			nl_cs = n_cs*cs_fcn_stat
			nl_cs_list[0].append(n)
			nl_cs_list[1].append(l)
			nl_cs_list[2].append(2)
			nl_cs_list[3].append(nl_cs)
	return(nl_cs_list)

def statistical(n, l): #See Krasnopolsky et al. (2004) and Equation 3.51 of Janev and Winter (1985)
	return ((2.0*float(l)+1.0)/(float(n)**2.0))

def lowEnergy(n, l): #See Krasnopolsky et al. (2004)
	return ((2.0*float(l)+1.0)*((math.factorial(float(n)-1.0))**2.0)/((math.factorial(float(n)\
		+float(l)))*(math.factorial(float(n)-1.0-float(l)))))


def lowEnergyModifiedACX(n, l): #See Smith et al. (2014) and Eq. 3.50a of Janev and Winter (1985)
	if int(n)==1: return 0 #no population of n=1 states allowed
	else: 
		return ((float(l))*(float(l) + 1.0)*(2.0*float(l)+1.0) * ((math.factorial(float(n) - 1.0)) \
		* (math.factorial(float(n) - 2.0)))/((math.factorial(float(n) + float(l))) * \
		(math.factorial(float(n)-float(l) - 1.0))))

def ACX1(n, l): #See Smith et al. (2014)
	return(1.0/float(n))

def ACX4(n, l,Z): #See Smith et al. (2014) and Eq. 3.59 from Janev and Winter (1985)
	return((2.0 * float(l) + 1.0 )/float(Z) * math.exp((-float(l) * (float(l) + 1))/float(Z)))	

# def separableACX(l, q): #See Smith et al. (2014)...only distribution function with charge.
# 	return (((2.0*float(l) +1.0)/q)*math.exp((-float(l)*(float(l)+1.0))/q))

def SL1(n, lPrime): #See Mullen et al. (2016)
	n = int(n)
	lPrime = int(lPrime)
	l = lPrime + 1
	if lPrime == n-1:
		return 0
	elif lPrime == 1:
		return (lowEnergy(n, l) + lowEnergy(n,0)) #maintain normalization of distr. function
	else:
		return lowEnergy(n, l)


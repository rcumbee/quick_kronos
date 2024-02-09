#Read in Cross_sections
csfname = 'fe20+he_sec_mclz.cs'


def rename_duplicates( old ):
    seen = {}
    for x in old:
        if x in seen:
            seen[x] += 1
            yield "%s%d" % (x, seen[x])
        else:
            seen[x] = 1
            yield x


def rename_duplicates2( old ):
	dups = {}

	for i, val in enumerate(old):
		if val not in dups:
			# Store index of first occurrence and occurrence value
			dups[val] = [i, 1]
			old[dups[val][0]] +=str(1)
			print(dups[val],i,val)
		else:
			# Special case for first occurrence
			# if dups[val][1] == 1:
			# 	old[dups[val][0]] += str(dups[val][1])

			# Increment occurrence value, index value doesn't matter anymore
			dups[val][1] += 1

			# Use stored occurrence value
			old[i] += str(dups[val][1])

	return (old)

def convert(lst): #list to string
    return '        '.join(lst) 

with open(csfname, 'r') as file:
    # read a list of lines into data
    data = file.readlines()

names=data[7].split()
names_list = list(rename_duplicates2(names))
rename_duplicates2(names)
converted_names = convert(names_list)
data[7] = str(converted_names + '\n')


with open('fe20+he_sec_mclz1.cs', 'w') as file:
    file.write(''.join( x for x in data))


# Convert .nist.in
# nifname = "fe19.nist.in"



# #Read in Radrathe
# rrfname = 'radrathe.dat'



# print list(rename_duplicates(l))
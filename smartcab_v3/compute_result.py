from sys import argv

script, filename = argv

file = open(filename, 'r')

totalreward = None
rewards = []
reached = 0
time = []
for line in file:
	line = line.rstrip("\n")
	if line.startswith("Simulator"):
		rewards.append(totalreward)
		totalreward = 0
	elif line in ['-0.5', '-1.0','2.0']:
		totalreward += float(line)
	elif line.endswith('destination!'):
		reached += 1
	elif len(line.split(" ")) == 2:
		left = float(line.split(" ")[0])
		total = float(line.split(" ")[1])
		time.append(left/total)

print min(rewards[1:])
print sum(rewards[1:])/100
print max(rewards[1:])
#print reached
#print sum(time)

notes = [12, 8, 15, 5, 10, 19,]
nb = 0

for x in notes:
	if x>=10:
		nb = nb + 1
		print ("bien joué tu as eu " , x)
	else:
		print("dommage tu as %d" % (x)) 

		print()

print(nb)

myFile = open('item.csv')
print("The content of CSV file is:")
text = myFile.readline()
while text != "":
    print(text, end="")
    text = myFile.readline()



	
myFile.close()


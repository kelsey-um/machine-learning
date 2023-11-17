import random as r
import numpy as np
import math as m
import csv

qwerty = ['q','w','e','r','t','y','u','i','o','p',
          'a','s','d','f','g','h','j','k','l',';',
          'z','x','c','v','b','n','m',',','.','?',
                            ' ']

dvorak = ['\'',',','.','p','y','f','g','c','r','l',
          'a','o','e','u','i','d','h','t','n','s',
          ';','q','j','k','x','b','m','w','v','z',
                            ' ']

colemak = ['q','w','f','p','g','j','l','u','y',';',
          'a','r','s','t','d','h','n','e','i','o',
          'z','x','c','v','b','k','m',',','.','/',
                            ' ']

def printKeyboard(keyboard):

    print("\nPrinting keyboard (using _ instead of whitespace for clarity)\n\n")
    
    for i in range(30):
        
        if(keyboard[i] == ' '): #to check if char is spacebar  in that case _ is printed instead
            print('_  ', end=' ')
        else:
            print(keyboard[i]," ",end = ' ')

        if(i == 9 or i == 19): #skipping line to keep with shape of keyboard
            print()

    if(keyboard[30] == ' '):
        print("\n\t\t","_","\n\n")
    else: 
        print("\n\t\t",keyboard[30],"\n\n") #printing char thats on the spacebar key

def openDataset(keyboard, filename):

    text =''

    with open(filename, 'r', encoding='utf-8') as f:
        contents = f.read().replace("\n", " ").lower()

    for char in contents:
        if char in keyboard:
            text += char

    print("The dataset has",len(text),"characters\n")
    return text

def euclideanDistance(coordinate1, coordinate2):

    difference = np.array(coordinate2) - np.array(coordinate1)

    return np.linalg.norm(difference)

def distanceMoved(keyboard,text): #fitness function

    distanceMoved = 0
    
    #the position of each key
    keyCoordinates = {0: (-0.032, 0), 1: (0.968, 0), 2: (1.968, 0), 3: (2.968, 0), 4: (3.968, 0), 5: (4.968, 0), 6: (5.968, 0), 7: (6.968, 0), 8: (7.968, 0), 9: (8.968, 0),
                      10: (0,1), 11: (1,1), 12: (2,1), 13: (3,1), 14: (4,1), 15: (5,1), 16: (6,1), 17: (7,1), 18: (8,1), 19: (9,1),
                      20: (0.118, 2), 21: (1.118, 2), 22: (2.118, 2), 23: (3.118, 2), 24: (4.118, 2), 25: (5.118, 2), 26: (6.118, 2), 27: (7.118, 2), 28: (8.118, 2), 29: (9.118, 2),
                      30: (4.5, 3)}

    #position of fingers
    fingers={1: (0,1), 2: (1,1), 3: (2,1), 4: (3,1), 5: (4.5,3), 7: (6,1), 8: (7,1), 9: (8,1), 10: (9,1)}

    #where each finger is allowed to move
    fingerAllowed = {1: [0,10,20], 2: [1,11,21], 3: [2,12,22], 4: [3,13,23,4,14,24], 5: [30], 7: [5,15,25,6,16,26], 8:[7,17,27], 9:[8,18,28], 10:[9,19,29]}

    for letter in text: #iterate over text

        letterCoordinate = keyCoordinates[keyboard.index(letter)] #get coordinate of letter

        if(letterCoordinate not in fingers.values()): #if finger is not already on key, find which finger can move to that key
            
            locationOfKey = list(keyCoordinates.keys())[list(keyCoordinates.values()).index(letterCoordinate)] #location of key that has the letter

            fingerNumber = next(key for key, value in fingerAllowed.items() if locationOfKey in value) #finger that needs to be moved

            currentCoordinate = fingers[fingerNumber] #getting current coordinate of finger
            newCoordinate = keyCoordinates[locationOfKey] #getting the coordinate of where finger will move

            distanceMoved += euclideanDistance(currentCoordinate, newCoordinate) #calculating distance between currentCoordinate and newCoordinate
            
            fingers[fingerNumber] = newCoordinate #setting new position of finger

    return distanceMoved

def createFirstPopulation(size, keyboard): #size is size of population and keyboard is the list of chars that will be randomised
    
    population = [r.sample(keyboard, len(keyboard)) for i in range(size)]

    return population

def sortPopulation(population, text):
    
    sorted_population = sorted(population, key=lambda x: distanceMoved(x, text))

    return sorted_population

def generationsLoop(population, text, iterations, elitism, mutate, mutateChoice, crossoverChoice): #sort list of population based on the distance moved
    
    populationSize = len(population)

    for i in range(1,iterations+1):

        print("Generation", i)

        sorted_population = sortPopulation(population, text)
        
        population = [] 

        population = sorted_population[:m.floor(populationSize*elitism)] #taking best % of layouts from generated list - elitism

        #filling the rest of the % by combining two keyboards from the top % of the population
        for i in range(int(populationSize*(1-elitism))):
            
            parent1 = r.choice(sorted_population[:m.floor(populationSize * 0.5)]) #parents are taken from top 50%
            parent2 = r.choice(sorted_population[:m.floor(populationSize * 0.5)])

            #crossover
            if(crossoverChoice == 1):
                child = singlePointCrossover(parent1, parent2)
            elif(crossoverChoice == 2):
                child = twoPointCrossover(parent1, parent2)

            #mutation
            if r.random() < mutate:
                if(mutateChoice == 1):
                    child = swap(child)
                
                elif(mutateChoice == 2):
                    child = scramble(child)
                
                elif(mutateChoice == 3):
                    child = invert(child)

            population.append(child)

    sorted_final = sortPopulation(population, text)
    return sorted_final 

def generationsLoopFile(population, text, iterations, elitism, mutate, mutateChoice, crossoverChoice,fileName): #to be used when data is recorded to a csv file

    f = open(fileName, 'w', encoding='UTF8')
    writer = csv.writer(f, lineterminator='\n')

    populationSize = len(population)

    for i in range(1,iterations+1):

        sorted_population = sortPopulation(population, text)
        
        bestDistance = distanceMoved(sorted_population[0], text)
        writer.writerow([int(bestDistance)])
        
        population = [] 

        population = sorted_population[:m.floor(populationSize*elitism)] #taking best % of layouts from generated list

        #filling the rest of the % by combining two keyboards from the top 50% of the population
        for i in range(int(populationSize*(1-elitism))):
            
            parent1 = r.choice(sorted_population[:m.floor(populationSize * 0.5)])
            parent2 = r.choice(sorted_population[:m.floor(populationSize * 0.5)])

            if(crossoverChoice == 1):
                child = singlePointCrossover(parent1, parent2)
            elif(crossoverChoice == 2):
                child = twoPointCrossover(parent1, parent2)

            if r.random() < mutate:
                if(mutateChoice == 1):
                    child = swap(child)
                
                elif(mutateChoice == 2):
                    child = scramble(child)
                
                elif(mutateChoice == 3):
                    child = invert(child)

            population.append(child)

    f.close()

    sorted_final = sortPopulation(population, text)
    return sorted_final  

def singlePointCrossover(parent1, parent2):

    child = ['-'] * len(parent1)

    crossoverPoint = r.randint(1,29) #random number to perform crossover

    #first part
    for i in range(crossoverPoint):
        child[i] = parent1[i]

    #second part
    i+=1
    child_i = i

    while '-' in child:
        
        if i > 30:
            i = 0

        char = parent2[i]

        if char in child:
            i+= 1
            
        else:
            child[child_i] = parent2[i]
            child_i += 1
            i +=1

    return child

def twoPointCrossover(parent1, parent2):

    child = ['-'] * len(parent1)

    crossoverPoint1 = r.randint(1,20) #random number to perform crossover
    crossoverPoint2 = r.randint(crossoverPoint1+1 ,len(child)-1)

    i=0

    #first part - from first parent
    for i in range(crossoverPoint1):
        child[i] = parent1[i]

    #second part
    i+=1
    child_i = i

    while child_i < crossoverPoint2:
        
        if i > 30:
            i = 0

        char = parent2[i]

        if char in child:
            i+= 1
            
        else:
            child[child_i] = parent2[i]
            child_i += 1
            i +=1

    #check which letters have not been added and add them
    #third part - from first parent
    for letter in parent1:
        if letter not in child:
            child[child_i] = letter
            child_i +=1
        if(child_i == 31):
            break

    return child

#mutate functions
def swap(keyboard): #two positions at random and value is swapped
    
    random1 = r.randint(0, len(keyboard)-1)

    while True: #to make sure numbers are not the same
        random2 = r.randint(0,len(keyboard)-1)
        if random1 != random2:
            break

    keyboard[random1], keyboard[random2] = keyboard[random2], keyboard[random1]

    return keyboard

def scramble(keyboard): #scrambling part of the list

    random1 = r.randint(0, len(keyboard)-1)

    while True: #to make sure numbers are not the same
        random2 = r.randint(0,len(keyboard)-1)
        if random1 != random2:
            break

    if random1 > random2: #to make sure random1 is smaller
        random1, random2 = random2, random1

    copy = keyboard[random1: random2]
    r.shuffle(copy)
    keyboard[random1:random2] = copy
    
    return keyboard

def invert(keyboard):

    random1 = r.randint(0, len(keyboard)-1)
    
    while True: #to make sure numbers are not the same
        random2 = r.randint(0,len(keyboard)-1)
        if random1 != random2:
            break

    if random1 > random2: #to make sure random1 is smaller
        random1, random2 = random2, random1

    keyboard[random1:random2] = reversed(keyboard[random1:random2])

    return keyboard

def testCases():
    text = openDataset(qwerty, 'book.txt') #opening text file

    #single point crossover

    #effect of population size

    #test 1:
    print("Started test A\n")
    population = createFirstPopulation(10, qwerty)
    final = generationsLoopFile(population, text, 100, 0.1, 0.4, 2, 1, "A.csv")
    finalDistance = distanceMoved(final[0], text)
    finalkeyboard = " ".join(final[0])

    with open("A.txt", 'w') as f:
        f.write(finalkeyboard)
        f.write('\n')
        f.write(str(finalDistance))

      
    #test 2:
    print("Started test B\n") 
    population = createFirstPopulation(100, qwerty)
    final = generationsLoopFile(population, text, 100, 0.1, 0.4, 2, 1, "B.csv")
    finalDistance = distanceMoved(final[0], text)
    finalkeyboard = " ".join(final[0])

    with open("B.txt", 'w') as f:
        f.write(finalkeyboard)
        f.write('\n')
        f.write(str(finalDistance))

    #effect of mutation rate

    #test1
    print("Started test C\n")
    population = createFirstPopulation(100, qwerty)
    final = generationsLoopFile(population, text, 100, 0.1, 0, 2, 1, "C.csv")
    finalDistance = distanceMoved(final[0], text)
    finalkeyboard = " ".join(final[0])

    with open("C.txt", 'w') as f:
        f.write(finalkeyboard)
        f.write('\n')
        f.write(str(finalDistance))
    
    #test2
    print("Started test D\n")
    population = createFirstPopulation(100, qwerty)
    final = generationsLoopFile(population, text, 100, 0.1, 0.4, 2, 1, "D.csv")
    finalDistance = distanceMoved(final[0], text)
    finalkeyboard = " ".join(final[0])

    with open("D.txt", 'w') as f:
        f.write(finalkeyboard)
        f.write('\n')
        f.write(str(finalDistance))

    #test3
    print("Started test E\n")
    population = createFirstPopulation(100, qwerty)
    final = generationsLoopFile(population, text, 100, 0.1, 1, 2, 1, "E.csv")
    finalDistance = distanceMoved(final[0], text)
    finalkeyboard = " ".join(final[0])

    with open("E.txt", 'w') as f:
        f.write(finalkeyboard)
        f.write('\n')
        f.write(str(finalDistance))


    #elitism rate

    #test1
    print("Started test F\n")
    population = createFirstPopulation(100, qwerty)
    final = generationsLoopFile(population, text, 100, 0, 0.4, 2, 1, "F.csv")
    finalDistance = distanceMoved(final[0], text)
    finalkeyboard = " ".join(final[0])

    with open("F.txt", 'w') as f:
        f.write(finalkeyboard)
        f.write('\n') 
        f.write(str(finalDistance))  

    #test2
    print("Started test G\n")
    population = createFirstPopulation(100, qwerty)
    final = generationsLoopFile(population, text, 100, 0.1, 0.4, 2, 1, "G.csv")
    finalDistance = distanceMoved(final[0], text)
    finalkeyboard = " ".join(final[0])

    with open("G.txt", 'w') as f:
        f.write(finalkeyboard)
        f.write('\n')
        f.write(str(finalDistance))  

    #test3
    print("Started test H\n")
    population = createFirstPopulation(100, qwerty)
    final = generationsLoopFile(population, text, 100, 0.5, 0.4, 2, 1, "H.csv")
    finalDistance = distanceMoved(final[0], text)
    finalkeyboard = " ".join(final[0])

    with open("H.txt", 'w') as f:
        f.write(finalkeyboard)
        f.write('\n')
        f.write(str(finalDistance))


    #different mutations

    #test1
    print("Started test I\n")
    population = createFirstPopulation(100, qwerty)
    final = generationsLoopFile(population, text, 100, 0.1, 1, 1, 1, "I.csv")
    finalDistance = distanceMoved(final[0], text)
    finalkeyboard = " ".join(final[0])

    with open("I.txt", 'w') as f:
        f.write(finalkeyboard)
        f.write('\n')
        f.write(str(finalDistance))

    #test2
    print("Started test J\n")
    population = createFirstPopulation(100, qwerty)
    final = generationsLoopFile(population, text, 100, 0.1, 1, 2, 1, "J.csv")
    finalDistance = distanceMoved(final[0], text)
    finalkeyboard = " ".join(final[0])

    with open("J.txt", 'w') as f:
        f.write(finalkeyboard)
        f.write('\n')
        f.write(str(finalDistance))
    
    #test3
    print("Started test K\n")
    population = createFirstPopulation(100, qwerty)
    final = generationsLoopFile(population, text, 100, 0.1, 1, 3, 1, "K.csv")
    finalDistance = distanceMoved(final[0], text)
    finalkeyboard = " ".join(final[0])

    with open("K.txt", 'w') as f:
        f.write(finalkeyboard)
        f.write('\n')
        f.write(str(finalDistance))

    
    #two point crossover

    #effect of population size
    
    #test 1:
    print("Started test L\n")
    population = createFirstPopulation(10, qwerty)
    final = generationsLoopFile(population, text, 100, 0.1, 0.4, 2, 2, "L.csv")
    finalDistance = distanceMoved(final[0], text)
    finalkeyboard = " ".join(final[0])

    with open("L.txt", 'w') as f:
        f.write(finalkeyboard)
        f.write('\n')
        f.write(str(finalDistance))

    #test 2:
    print("Started test M\n")
    population = createFirstPopulation(100, qwerty)
    final = generationsLoopFile(population, text, 100, 0.1, 0.4, 2, 2, "M.csv")
    finalDistance = distanceMoved(final[0], text)
    finalkeyboard = " ".join(final[0])

    with open("M.txt", 'w') as f:
        f.write(finalkeyboard)
        f.write('\n')
        f.write(str(finalDistance))

    #effect of mutation rate
    
    #test1
    print("Started test N\n")
    population = createFirstPopulation(100, qwerty)
    final = generationsLoopFile(population, text, 100, 0.1, 0, 2, 2, "N.csv")
    finalDistance = distanceMoved(final[0], text)
    finalkeyboard = " ".join(final[0])

    with open("N.txt", 'w') as f:
        f.write(finalkeyboard)
        f.write('\n')
        f.write(str(finalDistance))

    #test2
    print("Started test O\n")
    population = createFirstPopulation(100, qwerty)
    final = generationsLoopFile(population, text, 100, 0.1, 0.4, 2, 2, "O.csv")
    finalDistance = distanceMoved(final[0], text)
    finalkeyboard = " ".join(final[0])

    with open("O.txt", 'w') as f:
        f.write(finalkeyboard)
        f.write('\n')
        f.write(str(finalDistance))

    #test3
    print("Started test P\n")
    population = createFirstPopulation(100, qwerty)
    final = generationsLoopFile(population, text, 100, 0.1, 0.8, 2, 2, "P.csv")
    finalDistance = distanceMoved(final[0], text)
    finalkeyboard = " ".join(final[0])

    with open("P.txt", 'w') as f:
        f.write(finalkeyboard)
        f.write('\n')
        f.write(str(finalDistance))


    #elitism rate

    #test1
    print("Started test Q\n")
    population = createFirstPopulation(100, qwerty)
    final = generationsLoopFile(population, text, 100, 0, 0.4, 2, 2, "Q.csv")
    finalDistance = distanceMoved(final[0], text)
    finalkeyboard = " ".join(final[0])

    with open("Q.txt", 'w') as f:
        f.write(finalkeyboard)
        f.write('\n')
        f.write(str(finalDistance))  

    #test2
    print("Started test R\n")
    population = createFirstPopulation(100, qwerty)
    final = generationsLoopFile(population, text, 100, 0.1, 0.4, 2, 2, "R.csv")
    finalDistance = distanceMoved(final[0], text)
    finalkeyboard = " ".join(final[0])

    with open("R.txt", 'w') as f:
        f.write(finalkeyboard)
        f.write('\n')
        f.write(str(finalDistance))  

    #test3
    print("Started test S\n")
    population = createFirstPopulation(100, qwerty)
    final = generationsLoopFile(population, text, 100, 0.5, 0.4, 2, 2, "S.csv")
    finalDistance = distanceMoved(final[0], text)
    finalkeyboard = " ".join(final[0])

    with open("S.txt", 'w') as f:
        f.write(finalkeyboard)
        f.write('\n')
        f.write(str(finalDistance))


    #different mutations

    #test1
    print("Started test T\n")
    population = createFirstPopulation(100, qwerty)
    final = generationsLoopFile(population, text, 100, 0.1, 1, 1, 2, "T.csv")
    finalDistance = distanceMoved(final[0], text)
    finalkeyboard = " ".join(final[0])

    with open("T.txt", 'w') as f:
        f.write(finalkeyboard)
        f.write('\n')
        f.write(str(finalDistance))

    #test2
    print("Started test U\n")
    population = createFirstPopulation(100, qwerty)
    final = generationsLoopFile(population, text, 100, 0.1, 1, 2, 2, "U.csv")
    finalDistance = distanceMoved(final[0], text)
    finalkeyboard = " ".join(final[0])

    with open("U.txt", 'w') as f:
        f.write(finalkeyboard)
        f.write('\n')
        f.write(str(finalDistance))

    #test3
    print("Started test V\n")
    population = createFirstPopulation(100, qwerty)
    final = generationsLoopFile(population, text, 100, 0.1, 1, 3, 2, "V.csv")
    finalDistance = distanceMoved(final[0], text)
    finalkeyboard = " ".join(final[0])

    with open("V.txt", 'w') as f:
        f.write(finalkeyboard)
        f.write('\n')
        f.write(str(finalDistance))

print("\nDesigning a keyboard using genetic alogrithms\n")

while True:
    print("Choose an option")
    print("1. Use default values")
    print("2. Enter custom values")
    print("3. Test cases (will take a considerable amount of time to execute)")
    userChoice = input()

    if (userChoice.isnumeric()) and (int(userChoice) > 0 or int(userChoice) <= 2):
        break
        
    else:
        print("Input is not valid. Please try again.\n")

if int(userChoice) == 1: #default values

    populationSize = 100
    generationsAmount = 100
    elitismRate = 0.1
    mutateProb = 0.4
    mutateChoice = 2
    crossoverChoice = 2

    print("\nStarting execution\n")
    text = openDataset(qwerty, 'book.txt') #opening text file

    print("Population size:", populationSize)
    print("Number of generations:", generationsAmount)
    print("Elitism:", int((elitismRate*100)), "%")
    print("Probability of mutation:", int((mutateProb*100)), "%")
    
    print("Mutation type: ", end = "")
    if(mutateChoice == 1):
        print("Swap")
    elif(mutateChoice == 2):
        print("Scramble")
    elif(mutateChoice == 3):
        print("Invert")
    
    print("Crossover Type: ", end = "")
    if(crossoverChoice == 1):
        print("Single Point Crossover\n")
    elif(crossoverChoice == 2):
        print("Two Point Crossover\n")

    population = createFirstPopulation(populationSize, qwerty)
    final = generationsLoop(population, text, generationsAmount, elitismRate, mutateProb, mutateChoice, crossoverChoice)
    printKeyboard(final[0])

elif int(userChoice) == 2:

    while True: #population size
        
        print("\nEnter size of population")
        populationSize = input()

        if (populationSize.isnumeric() and int(populationSize) != 0):
            populationSize = int(populationSize)
            break
        
        else:
            print("Input is not valid. Please try again.\n")

    while True: #num of generations

        print("\nEnter number of generations")
        generationsAmount = input()

        if (generationsAmount.isnumeric() and int(generationsAmount) != 0):
            generationsAmount = int(generationsAmount)
            break
        else:
            print("Input is not valid. Please try again.")

    while True: #elitism

        print("\nEnter percentage of elitism between 0 and 100")
        elitismRate = input()

        if(elitismRate.isnumeric() and (int(elitismRate) <= 100 and int(elitismRate) >= 0)):
            elitismRate = int(elitismRate) / 100
            break
        else:
            print("Input is not valid. Please try again.")
        
    while True: #mutation

        print("\nEnter probability of mutation between 0 and 100")
        mutateProb = input()

        if(mutateProb.isnumeric() and (int(mutateProb) <= 100 and int(elitismRate) >= 0)):
            mutateProb = int(mutateProb) / 100
            break
        else:
            print("Input is not valid. Please try again.")

    while True: #mutation choice

        print("\nEnter mutation choice")
        print("1. Swap")
        print("2. Scramble")
        print("3. Invert")
        mutateChoice = input()

        if(mutateChoice.isnumeric() and (int(mutateChoice) > 0 and int(mutateChoice) <= 3)):
            mutateChoice = int(mutateChoice)
            break
        else:
            print("Input is not valid. Please try again.")

    while True: #crossover choice

        print("\nEnter crossover choice")
        print("1. Single Point Crossover")
        print("2. Two Point Crossover")
        crossoverChoice = input()

        if(crossoverChoice.isnumeric() and (int(crossoverChoice)> 0 and int(crossoverChoice) <= 2)):
            crossoverChoice = int(crossoverChoice)
            break
        else:
            print("Input is not valid. Please try again.")

    print("\nStarting execution\n")
    text = openDataset(qwerty, 'book.txt') #opening text file

    print("Population size:", populationSize)
    print("Number of generations:", generationsAmount)
    print("Elitism:", int((elitismRate*100)), "%")
    print("Probability of mutation:", int((mutateProb*100)), "%")
    
    print("Mutation type: ", end = "")
    if(mutateChoice == 1):
        print("Swap")
    elif(mutateChoice == 2):
        print("Scramble")
    elif(mutateChoice == 3):
        print("Invert")
    
    print("Crossover type: ", end = "")
    if(crossoverChoice == 1):
        print("Single Point Crossover\n")
    elif(crossoverChoice == 2):
        print("Two Point Crossover\n")

    population = createFirstPopulation(populationSize, qwerty)
    final = generationsLoop(population, text, generationsAmount, elitismRate, mutateProb, mutateChoice, crossoverChoice)
    
    printKeyboard(final[0])

elif int(userChoice) == 3:
   
    print("\nStarting execution\n")
    testCases()    
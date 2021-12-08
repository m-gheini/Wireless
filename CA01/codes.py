import random as rand
import cmath
import math
import numpy as np
import matplotlib.pyplot as plt

QPSKmappingDict = {
    (0,0) : complex(1,1),
    (0,1) : complex(-1,1),
    (1,0) : complex(1,-1),
    (1,1) : complex(-1,-1)
}
QAMmappingDict = {
    (0,0,0,0) : complex(-3,3),
    (0,0,0,1) : complex(-3,1),
    (0,0,1,0) : complex(-3,-3),
    (0,0,1,1) : complex(-3,-1),
    (0,1,0,0) : complex(-1,3),
    (0,1,0,1) : complex(-1,1),
    (0,1,1,0) : complex(-1,-3),
    (0,1,1,1) : complex(-1,-1),
    (1,0,0,0) : complex(3,3),
    (1,0,0,1) : complex(3,1),
    (1,0,1,0) : complex(3,-3),
    (1,0,1,1) : complex(3,-1),
    (1,1,0,0) : complex(1,3),
    (1,1,0,1) : complex(1,1),
    (1,1,1,0) : complex(1,-3),
    (1,1,1,1) : complex(1,-1)
}
QPSKunpackDict = {
    (1,1) : (0,0),
    (-1,1) : (0,1),
    (1,-1) : (1,0),
    (-1,-1) : (1,1) 
}
QAMunpackDict = {
    (-3,3) : (0,0,0,0),
    (-3,1) : (0,0,0,1),
    (-3,-3) : (0,0,1,0),
    (-3,-1) : (0,0,1,1),
    (-1,3) : (0,1,0,0),
    (-1,1) : (0,1,0,1),
    (-1,-3) : (0,1,1,0),
    (-1,-1) : (0,1,1,1),
    (3,3) : (1,0,0,0),
    (3,1) : (1,0,0,1),
    (3,-3) : (1,0,1,0),
    (3,-1) : (1,0,1,1),
    (1,3) : (1,1,0,0),
    (1,1) : (1,1,0,1),
    (1,-3) : (1,1,1,0),
    (1,-1) : (1,1,1,1)
}
QPSKdots = (complex(1,1),complex(-1,1),complex(1,-1),complex(-1,-1))
QAMdots = (complex(-3,3),complex(-3,1),complex(-3,-3),complex(-3,-1),complex(-1,3),complex(-1,1),complex(-1,-3),
           complex(-1,-1),complex(3,3),complex(3,1),complex(3,-3),complex(3,-1),complex(1,3),complex(1,1),
           complex(1,-3),complex(1,-1))

def produceData(size):
    data = []
    for i in range (size):
        bit = rand.randint(0,1);
        data.append(bit)
    return data

def addParityBits(data):
    extendedResult = []
    p0 = p1 = p2 = 0
    firstPart = [data[0], data[1], data[3]]
    secondPart = [data[0], data[3], data[2]]
    thirdPart = [data[1], data[3], data[2]]
    if(firstPart.count(1)%2 != 0):
        p0 = 1
    if(secondPart.count(1)%2 != 0):
        p1 = 1
    if(thirdPart.count(1)%2 != 0):
        p2 = 1
    extendedResult.extend((p0,p1,data[0],p2,data[1],data[2],data[3]))
    return extendedResult

def hammingCode(data):
    result = []
    for i in range(0, len(data), 4):
        newPart = data[i:i+4]
        addedParityPart = addParityBits(newPart)
        result.extend(tuple(addedParityPart[0:7]))
    return result

def calNormFactor(complexNum):
    return 1/abs(complexNum)

def mapToComplex(data, modulation):
    mappedData = []
    if modulation == "QPSK" :
        for i in range(0, len(data), 2):
            complexForm = QPSKmappingDict[(data[i], data[i+1])]
            mappedData.append(calNormFactor(complexForm) * complexForm)
    elif modulation == "16QAM" :
        for i in range(0, len(data), 4):
            complexForm = QAMmappingDict[(data[i], data[i+1], data[i+2], data[i+3])]
            mappedData.append(calNormFactor(complexForm) * complexForm)
    return mappedData

def produceH(size):
    h = []
    randNumbers = np.random.normal(0, 1, size)
    for i in range(0, size, 2):
        hI = randNumbers[i]
        hQ = randNumbers[i+1]
        h.append((1/math.sqrt(2)) * complex(hI,hQ))
    return h

def produceN(size, snr):
    n = []
    randNumbers = np.random.normal(0, 1/math.sqrt(snr), size)
    for i in range(0, size, 2):
        nI = randNumbers[i]
        nQ = randNumbers[i+1]
        n.append((1/math.sqrt(2)) * complex(nI,nQ))
    return n

def produceY(h, x, n):
    y = []
    for i in range(len(x)):
        y.append((h[i] * x[i] + n[i])/h[i])
    return y

def module(inData, snrList, modulationType, codingType):
    result = dict()
    if codingType == "Hamming":
        codedData = hammingCode(inData)
    else:
        codedData = inData
    x = mapToComplex(codedData, modulationType)
    h = produceH(len(codedData))
    for snr in snrList:
        n = produceN(len(codedData), snr)
        y = produceY(h, x, n)
        result[snr] = y
    return result

def computeDistance(p1, p2):
    return math.sqrt( ((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2) )

def getMinDistPoint(x, y, modulation):
    minDistance = math.inf
    minDistPoint = (math.inf, math.inf)
    if modulation == "QPSK":
        for dot in QPSKdots:
            normDot = calNormFactor(dot) * dot
            distance = computeDistance((x,y), (normDot.real,normDot.imag))
            if distance < minDistance:
                minDistance = distance
                minDistPoint = dot
    elif modulation == "16QAM":
        for dot in QAMdots:
            normDot = calNormFactor(dot) * dot
            distance = computeDistance((x,y), (normDot.real,normDot.imag))
            if distance <= minDistance:
                minDistance = distance
                minDistPoint = dot
    return minDistPoint

def getProbableData(outData, modulation):
    result = []
    if modulation == "QPSK":
        for i in range(len(outData)):
            gotDot = getMinDistPoint(outData[i].real, outData[i].imag, modulation)
            result.extend(QPSKunpackDict[gotDot.real, gotDot.imag])
    elif modulation == "16QAM":
        for i in range(len(outData)):
            gotDot = getMinDistPoint(outData[i].real, outData[i].imag, modulation)
            result.extend(QAMunpackDict[gotDot.real, gotDot.imag])
    return result

def getErrors(codedData):
    e0 = e1 = e2 = 0
    firstPart = [codedData[0],codedData[2],codedData[4],codedData[6]]
    secondPart = [codedData[1],codedData[2],codedData[5],codedData[6]]
    thirdPart = [codedData[3], codedData[4],codedData[5],codedData[6]]
    if(firstPart.count(1)%2 != 0):
        e0 = 1
    if(secondPart.count(1)%2 != 0):
        e1 = 1
    if(thirdPart.count(1)%2 != 0):
        e2 = 1
    return e0, e1, e2

def makeErrorFreeData(codedData):
    errorFreeData = []
    e0, e1, e2 = getErrors(codedData)
    d0 = codedData[2]
    d1 = codedData[4]
    d2 = codedData[5]
    d3 = codedData[6]
    if(e0 == e1 == 1 and e2 == 0):
        d0 = 1 - d0
    elif(e0 == e2 == 1 and e1 == 0):
        d1 = 1 - d1
    elif(e1 == e2 == 1 and e0 == 0):
        d2 = 1 - d2
    elif(e0 == e1 == e2 == 1):
        d3 = 1 - d3
    errorFreeData.extend((d0, d1, d2, d3))
    return errorFreeData

def decodeData(codedData):
    result = []
    for i in range(0, len(codedData), 7):
        newPart = codedData[i:i+7]
        errorFreePart = makeErrorFreeData(newPart)
        result.extend(tuple(errorFreePart[0:4]))
    return result

def seperateComplexNum(numList):
    X = [x.real for x in numList]
    Y = [x.imag for x in numList]
    return X, Y

def plotReceivedSignal(x, y, snr, modulation, coding):
    if modulation == "QPSK":
        plt.plot([calNormFactor(dot)*dot.real for dot in QPSKdots], [calNormFactor(dot)*dot.imag for dot in QPSKdots], 'ro')
    elif modulation == "16QAM":
        plt.plot([calNormFactor(dot)*dot.real for dot in QAMdots], [calNormFactor(dot)*dot.imag for dot in QAMdots], 'ro')
    plt.scatter(x, y, s = 20)
    plt.title("Received Signal For SNR = %s, modulation = %s, coding = %s" % (snr,modulation,coding),fontweight = "bold")
    plt.xlabel("Real Part")
    plt.ylabel("Imaginary Part")
    plt.show()

def transferDataAndPlotReceivedSignal(size, snrList, modulationType, codingType):
    inData = produceData(size)
    receivedData = module(inData, snrList, modulationType, codingType)
    for snr in snrList:
        real, imag = seperateComplexNum(receivedData[snr])
        plotReceivedSignal(real, imag, snr, modulationType, codingType)

def getCntFalse(inputData, probableData):
    cnt = 0
    for i in range (len(inputData)):
        if inputData[i] != probableData[i]:
            cnt += 1
    return cnt

def computeMeanErrorV1(size, snrList, moduleType, codingType):
    result = dict()
    inData = produceData(size)
    receivedData = module(inData, snrList, moduleType, codingType)
    for snr in snrList:
        probableIn = getProbableData(receivedData[snr], moduleType)
        if codingType == "Hamming":
            decoded = decodeData(probableIn)
        else:
            decoded = probableIn
        cnt = getCntFalse(inData, decoded)
        result[snr] = (cnt/size)*100
    return result

def computeMeanErrorV2(size, loopSize, snrList, moduleType, codingType):
    result = dict()
    for i in range(loopSize):
        inData = produceData(size)
        receivedData = module(inData, snrList, moduleType, codingType)
        for snr in snrList:
            probableIn = getProbableData(receivedData[snr], moduleType)
            if codingType == "Hamming":
                decoded = decodeData(probableIn)
            else:
                decoded = probableIn
            cnt = getCntFalse(inData, decoded)
            if snr not in result:
                result[snr] = (cnt)
            else: 
                result[snr] += (cnt)
    for k in result.keys():
        result[k] = (result[k]/(size*loopSize))*100
    return result

def plotMeanOfError(result, version, moduleType, codingType):
    x = result.keys()
    y = result.values()
    plt.plot(x, y, 'o--')
    plt.title("Mean Of Error Based On SNR - version: %s, modulation: %s, coding: %s" % (version, moduleType, codingType) ,fontweight = "bold")
    plt.xlabel("SNR")
    plt.ylabel("Mean Of Error (%)")
    plt.show()

def computeAndPlotMeanErrorV1(size, snrList, moduleType, codingType):
    result = computeMeanErrorV1(size, snrList, moduleType, codingType)
    plotMeanOfError(result, "1", moduleType, codingType)

def computeAndPlotMeanErrorV2(size, loopSize, snrList, moduleType, codingType):
    result = computeMeanErrorV2(size, loopSize, snrList, moduleType, codingType)
    plotMeanOfError(result, "2", moduleType, codingType)

#TESTING

#Q1: Plot received signal
#Modulation : QPSK, coding : None
# transferDataAndPlotReceivedSignal(20000, [0.1, 1, 10, 100, 1000], "QPSK", "None")

#Modulation : QPSK, coding : Hamming
# transferDataAndPlotReceivedSignal(20000, [0.1, 1, 10, 100, 1000], "QPSK", "Hamming")

#Modulation : 16QAM, coding : None
# transferDataAndPlotReceivedSignal(20000, [0.1, 1, 10, 100, 1000], "16QAM", "None")

#Modulation : 16QAM, coding : Hamming
# transferDataAndPlotReceivedSignal(20000, [0.1, 1, 10, 100, 1000], "16QAM", "Hamming")

#Q2: Plot mean of error based on SNR

SNRs = [0.1,1,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100]

#Version : 1, Modulation : QPSK, Coding : None
# computeAndPlotMeanErrorV1(20000,SNRs,"QPSK","None")

#Version : 2, Modulation : QPSK, Coding : None
# computeAndPlotMeanErrorV2(20000,10,SNRs,"QPSK","None")

#Q3: Using Hamming code

#Version : 1, Modulation : QPSK, Coding : Hamming
# computeAndPlotMeanErrorV1(20000,SNRs,"QPSK","Hamming")

#Version : 2, Modulation : QPSK, Coding : Hamming
# computeAndPlotMeanErrorV2(20000,10,SNRs,"QPSK","Hamming")

#Q4: Using 16QAM modulation

#Version : 1, Modulation : 16QAM, Coding : None
# computeAndPlotMeanErrorV1(20000,SNRs,"16QAM","None")

#Version : 2, Modulation : 16QAM, Coding : None
# computeAndPlotMeanErrorV2(20000,10,SNRs,"16QAM","None")

#Version : 1, Modulation : 16QAM, Coding : Hamming
# computeAndPlotMeanErrorV1(20000,SNRs,"16QAM","Hamming")

#Version : 2, Modulation : 16QAM, Coding : Hamming
# computeAndPlotMeanErrorV2(20000,10,SNRs,"16QAM","Hamming")

def plotAllV1():
    result1 = computeMeanErrorV1(2000, SNRs, "QPSK", "None")
    result2 = computeMeanErrorV1(2000, SNRs, "QPSK", "Hamming")
    result3 = computeMeanErrorV1(2000, SNRs, "16QAM", "None")
    result4 = computeMeanErrorV1(2000, SNRs, "16QAM", "Hamming")
    x = result1.keys()
    y1 = result1.values()
    y2 = result2.values()
    y3 = result3.values()
    y4 = result4.values()
    plt.plot(x, y1, color='r', label='QPSK-None')
    plt.plot(x, y2, color='g', label='QPSK-Hamming')
    plt.plot(x, y3, color='b', label='16QAM-None')
    plt.plot(x, y4, color='y', label='16QAM-Hamming')
    plt.ylabel("Mean Of Error(%)")
    plt.xlabel("SNR")
    plt.title("Mean Of Error Based On SNR - version: 1", fontweight = "bold")
    plt.legend()
    plt.show()

# plotAllV1()

def plotAllV2():
    result1 = computeMeanErrorV2(20000, 10, SNRs, "QPSK", "None")
    result2 = computeMeanErrorV2(20000, 10, SNRs, "QPSK", "Hamming")
    result3 = computeMeanErrorV2(20000, 10, SNRs, "16QAM", "None")
    result4 = computeMeanErrorV2(20000, 10, SNRs, "16QAM", "Hamming")
    x = result1.keys()
    y1 = result1.values()
    y2 = result2.values()
    y3 = result3.values()
    y4 = result4.values()
    plt.plot(x, y1, color='r', label='QPSK-None')
    plt.plot(x, y2, color='g', label='QPSK-Hamming')
    plt.plot(x, y3, color='b', label='16QAM-None')
    plt.plot(x, y4, color='y', label='16QAM-Hamming')
    plt.ylabel("Mean Of Error(%)")
    plt.xlabel("SNR")
    plt.title("Mean Of Error Based On SNR - version: 2", fontweight = "bold")
    plt.legend()
    plt.show()

# plotAllV2()


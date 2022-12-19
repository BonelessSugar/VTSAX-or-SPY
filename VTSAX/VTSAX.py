import csv

#WHAT THIS DOES:
#Outputs stock value of buying monthly cashflows at different times per month and as a lump sump,
#either fixed monthly payments or roth ira contributions
#monthly: (highest stock price of month, lowest stock price of month, and stock price at start of month)
#from Jan 1 2001 - Dec 31 2020 of VTSAX
#includes dividends reinvested and expense ratio

#LIMITATIONS:

#Ex-Div Date,Pay Date,Amount
#12/21/2001,1/2/2002,0.095
#pay date is always either within the same year of the ex-div date,
#or on jan 02 of the next year for VTSAX only, doesn't work with SPY for example
#bc SPY will have ex-div date of 12/17/2021, pay date of 1/31/2022

#currently only works with start month of Jan and end month of Dec,
#but can change years (as long as theyre within the history of the CSVs)

#EX DIV DATE:
#have to own stock before this date to get paid
#PAY DATE:
#the date you are paid a dividend cash per share you owned before EX DIV DATE
#AMOUNT:
#the dollars per share you are paid out on the PAY DATE

#creates a dictionary of dividend dates and values
VTSAXdiv = {}
with open('VTSAX dividends in dollars ver2.csv', newline='') as csvfile:
    lineCount = 0
    spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    # go to each row in the csv
    #row = ['12/21/2000,1/2/2001,0.179']
    for row in spamreader:
        # make sure the contents are numbers and not the key
        if lineCount != 0:
            # access the contents of the single item list
            #contents = 12/21/2000,1/2/2001,0.179
            for contents in row:
                #turn it into a searchable list
                #filterContent = [['12', '21', '2000'], ['1', '2', '2001'], '0.179']
                filterContent = contents.split(",")
                filterContent[0] = filterContent[0].split("/")
                filterContent[1] = filterContent[1].split("/")
                divYear = int(filterContent[0][2])
                divMonth = int(filterContent[0][0])
                divDay = int(filterContent[0][1])
                payYear = int(filterContent[1][2])
                payMonth = int(filterContent[1][0])
                payDay = int(filterContent[1][1])
                price = float(filterContent[2])
                #{divYear: {divMonth: [divMonth, divDay, $perShare, payYear, payMonth, payDay]}}
                if divYear not in VTSAXdiv:
                    VTSAXdiv.update({divYear: {divMonth: [divMonth, divDay, price, payYear, payMonth, payDay]}})
                if divMonth not in VTSAXdiv[divYear]:
                    VTSAXdiv[divYear].update({divMonth: [divMonth, divDay, price, payYear, payMonth, payDay]})
        lineCount += 1

#stores Roth IRA limit in dictionary for each year
rothList = {}
for i in range(2001,2022):
    amount = 0
    if i == 2001:
        amount = 2000
    elif i < 2005:
        amount = 3000
    elif i < 2008:
        amount = 4000
    elif i < 2013:
        amount = 5000
    elif i < 2019:
        amount = 5500
    else:
        amount = 6000
    rothList.update({i: amount})

#create a dictionary of the highest stock price of the month,
#lowest stock price of the month, stock price at start of month, and
#the stock price of the business day after the pay date of the dividend
VTSAXlist = {}
#nextDay is the day after div pay date, 1 = it's time to store the stock price for buying
nextDay = 0
#maybe prevYear can be 0 instead of -1?
prevYear = -1
#prevMonth has to be -1, explained later on
prevMonth = -1
with open('VTSAX history.csv', newline='') as csvfile:
    lineCount = 0
    spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    for row in spamreader:
        if lineCount != 0:
            for contents in row:
                filterContent = contents.split(",")
                filterContent[0] = filterContent[0].split("-")
                year = int(filterContent[0][0])
                month = int(filterContent[0][1])
                day = int(filterContent[0][2])
                price = float(filterContent[1])
                if year not in VTSAXlist:
                    VTSAXlist.update({year: {month: [[price,day],[price,day],[price,day],[0,0], 0]}})
                if month not in VTSAXlist[year]:
                    VTSAXlist[year].update({month: [[price,day],[price,day],[price,day],[0,0], 0]})
                # {year: {month: [[high price, day], [low price, day], [start price, day], [payPrice, payDay], endMoPrice}}
                #add high price
                if price > VTSAXlist[year][month][0][0]:
                    VTSAXlist[year][month][0][0] = price
                    VTSAXlist[year][month][0][1] = day
                #add low price
                if price < VTSAXlist[year][month][1][0]:
                    VTSAXlist[year][month][1][0] = price
                    VTSAXlist[year][month][1][1] = day
                #add endMoPrice
                VTSAXlist[year][month][4] = price
                #add payPrice
                # FOR DIV:
                # YOU ARE PAID AT END OF DAY
                # YOU BUY AT END OF NEXT DAY
                #adds the price to the day
                if nextDay == 1:
                    VTSAXlist[year][month][3][0] = price
                    VTSAXlist[year][month][3][1] = day
                    nextDay = 0
                #the next payDay is always [2001][1][2], [2001][1][1] doesnt exist because it's a
                #stock holiday, so the day after it is always the day I want if it's in the next year
                if prevYear == year - 1:
                    nextDay = 1
                    prevYear = -1
                #checks the div months, ex div date is always a multiple of 3 (3,6,9,12)
                if month % 3 == 0:
                    ##12/21/2001,1/2/2002,0.095
                    if year != VTSAXdiv[year][month][3]:
                        prevYear = year
                    ##9/27/2002,10/4/2002,0.073
                    #10/1, 10/2, 10/3, 10/4
                    elif month != VTSAXdiv[year][month][4]:
                        prevMonth = month
                    ##6/21/2002,6/28/2002,0.063
                    ##day after pay date would be 7/1/2002
                    elif day == VTSAXdiv[year][month][5]:
                        nextDay = 1
                ##9/27/2002,10/4/2002,0.073
                ##can't have prevMonth set to 0 bc this condition, otherwise all Jan dates would apply
                if prevMonth == month - 1:
                    ##10/1, 10/2, 10/3, 10/4
                    if day == VTSAXdiv[year][prevMonth][5]:
                        nextDay = 1
                        prevMonth = -1
        lineCount += 1

#calculates price of total shares with monthly deposit
def timeMarket(vary, stYr, enYr, moDe):
    #moDep = monthly deposit
    moDep = moDe
    #divStockMoney = (stock count day before ex div date) * ($ per share)
    divStockMoney = 0
    #running total of how many shares you own
    stockCount = 0
    startYear = stYr
    endYear = enYr
    endYearPrice = 0
    for yearKey in VTSAXlist:
        #go through every year
        if (yearKey >= startYear) and (yearKey <= endYear):
            if isRoth == True:
                moDep = rothList[yearKey] / 12
            #go through every month
            for monthKey in VTSAXlist[yearKey]:
                #check if it's a div month
                if monthKey % 3 == 0:
                    #if buyDay < divCheckDay
                    # {year: {month: [[high price, day], [low price, day], [start price, day], [payPrice, payDay], endMoPrice}}
                    # {divYear: {divMonth: [divMonth, divDay, $perShare, payYear, payMonth, payDay]}}
                    if VTSAXlist[yearKey][monthKey][vary][1] < VTSAXdiv[yearKey][monthKey][1]:
                        #buy stock then store div money value
                        #VTSAXlist[yearKey][monthKey][vary][0] = stock price at low, high, or start
                        stockCount += moDep / VTSAXlist[yearKey][monthKey][vary][0]
                        divStockMoney = stockCount * VTSAXdiv[yearKey][monthKey][2]
                    else:
                        #otherwise store div money value then buy stock
                        divStockMoney = stockCount * VTSAXdiv[yearKey][monthKey][2]
                        stockCount += moDep / VTSAXlist[yearKey][monthKey][vary][0]
                    #if day after pay date is in the same month as ex div date
                    #if a value exists (is not 0), then this is the day you buy the stock with div money
                    if VTSAXlist[yearKey][monthKey][3][0] > 0:
                        #VTSAXlist[yearKey][monthKey][3][0] = stock price at buy day
                        stockCount += divStockMoney / VTSAXlist[yearKey][monthKey][3][0]
                #if day after pay date is the date you are buying the stock with the dividend money
                elif VTSAXlist[yearKey][monthKey][3][0] > 0:
                    stockCount += divStockMoney / VTSAXlist[yearKey][monthKey][3][0]
                    stockCount += moDep / VTSAXlist[yearKey][monthKey][vary][0]
                #if it's not a dividend month or a month you're using div money to buy stocks
                else:
                    #just buy stocks with your monthly cashflow
                    stockCount += moDep / VTSAXlist[yearKey][monthKey][vary][0]
            # subtract expense ratio at end of year
            #VTSAX expense ratio = 0.04%
            stockCount *= 0.9996
            #store end of year stock price
            endYearPrice = VTSAXlist[yearKey][12][4]
    #return the value of your shares at Dec 31 2020 share value
    return stockCount * endYearPrice

#calculates price of total shares with annual deposit
def timeMarketYr(stYr, enYr, yearD):
    divStockMoney = 0
    stockCount = 0
    endYearPrice = 0
    #yearD = yearly deposit
    for yearKey in VTSAXlist:
        # go through every year
        if (yearKey >= stYr) and (yearKey <= enYr):
            if isRoth == True:
                yearD = rothList[yearKey]
            #always add stock count first
            stockCount += yearD / VTSAXlist[yearKey][1][2][0]
            # go through every month
            for monthKey in VTSAXlist[yearKey]:
                #see if youre storing div share count this month (%3)
                if monthKey % 3 == 0:
                    #store div count
                    divStockMoney = stockCount * VTSAXdiv[yearKey][monthKey][2]
                    # if day after pay date is in the same month as ex div date
                    # if a value exists (is not 0), then this is the day you buy the stock with div money
                    if VTSAXlist[yearKey][monthKey][3][0] > 0:
                        # VTSAXlist[yearKey][monthKey][3][0] = stock price at buy day
                        stockCount += divStockMoney / VTSAXlist[yearKey][monthKey][3][0]
                # if day after pay date is the date you are buying the stock with the dividend money
                elif VTSAXlist[yearKey][monthKey][3][0] > 0:
                    stockCount += divStockMoney / VTSAXlist[yearKey][monthKey][3][0]
            # subtract expense ratio at end of year
            # VTSAX expense ratio = 0.04%
            stockCount *= 0.9996
            # store end of year stock price
            endYearPrice = VTSAXlist[yearKey][12][4]
    # return the value of your shares at end of year share price
    return stockCount * endYearPrice

#checks that the input is a valid year
def yearField(startEnd):
    yr = input(startEnd + " year: ")
    if startEnd == "Start":
        aN = "a "
    else:
        aN = "an "
    while (not yr.isdigit()) or (int(yr) < 2001) or (int(yr) > 2021):
        yr = input("Please input " + aN + startEnd.lower() + " year between 2001 and 2021: ")
    return int(yr)

#checks that monthly deposit is positive and is only two digits after decimal
def isDollars():
    monthDe = input("Monthly Deposit: ")
    myLoop = True
    while myLoop:
        if "," in monthDe:
            monthDe = monthDe.replace(",","")
        try:
            float(monthDe)
        except:
            monthDe = input("Please input a number for your monthly deposit: ")
            continue
        if "." in monthDe:
            if monthDe.index(".") + 3 < len(monthDe):
                print("There may only be two digits past the decimal.")
                monthDe = input("Please input a number for your monthly deposit: ")
                continue
        myLoop = False
    return float(monthDe)

#inputs for start year, end year, and monthly deposit or roth contribution
strYr = yearField("Start")
endYr = yearField("End")
while endYr < strYr:
    print("End year cannot be before start year.")
    endYr = yearField("End")
contLoop = 0
monDe = 0
isRoth = False
while contLoop == 0:
    rothMonth = input("Roth IRA limit or fixed cashflow? (roth/fixed): ")
    if (rothMonth.lower() == "roth"):
        isRoth = True
    elif (rothMonth.lower() == "fixed"):
        monDe = isDollars()
    else:
        print("Please enter roth or fixed.")
        continue
    contLoop = 1

#buy at high/low/start of monthly stock price
#0 = high, 1 = low, 2 = start
print('High: ${:,.2f}'.format(timeMarket(0, strYr, endYr, monDe)))
print('Start: ${:,.2f}'.format(timeMarket(2, strYr, endYr, monDe)))
print('Lump Sum: ${:,.2f}'.format(timeMarketYr(strYr, endYr, (monDe * 12))))
print('Low: ${:,.2f}'.format(timeMarket(1, strYr, endYr, monDe)))

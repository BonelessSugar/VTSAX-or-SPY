import csv
# 1.
# asks user VTSAX or SPY
fund = input("VTSAX or SPY: ")
fund = fund.upper()
while (fund != "VTSAX") and (fund != "SPY"):
    fund = input("Please enter either VTSAX or SPY: ")
    fund = fund.upper()

# 2.
# creates a dictionary of dividend dates and values
fundDiv = {}
with open(fund + ' dividend.csv', newline='') as csvfile:
    lineCount = 0
    spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    # go to each row in the csv
    # row = ['12/21/2000,0.179']
    for row in spamreader:
        # make sure the contents are numbers and not the key
        if lineCount != 0:
            # access the contents of the single item list
            # contents = 12/21/2000,0.179
            for contents in row:
                # turn it into a searchable list
                # filterContent = [['12', '21', '2000'], '0.179']
                filterContent = contents.split(",")
                filterContent[0] = filterContent[0].split("/")
                year = int(filterContent[0][2])
                month = int(filterContent[0][0])
                day = int(filterContent[0][1])
                price = float(filterContent[1])
                # {divYear: {divMonth: [divDay, $perShare]}}
                if year not in fundDiv:
                    fundDiv.update({year: {month: [day, price]}})
                if month not in fundDiv[year]:
                    fundDiv[year].update({month: [day, price]})
        lineCount += 1

# 3.
# dictionary of the highest stock price of the month,
# lowest stock price of the month, stock price at start of month,
# stock price at end of month, and stock price at dividend reinvestment date
fundStock = {}
with open(fund + ' stock.csv', newline='') as csvfile:
    lineCount = 0
    spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    for row in spamreader:
        if lineCount != 0:
            for contents in row:
                filterContent = contents.split(",")
                filterContent[0] = filterContent[0].split("/")
                year = int(filterContent[0][2])
                month = int(filterContent[0][0])
                day = int(filterContent[0][1])
                price = float(filterContent[1])
                if year not in fundStock:
                    fundStock.update({year: {month: [[price, day], [price, day], [price, day], [0, 0], [0, 0]]}})
                if month not in fundStock[year]:
                    fundStock[year].update({month: [[price, day], [price, day], [price, day], [0, 0], [0, 0]]})
                # {year: {month: [[high price, day], [low price, day], [start price, day], [end price, day], [div price, day]}}
                # add high price
                if price > fundStock[year][month][0][0]:
                    fundStock[year][month][0][0] = price
                    fundStock[year][month][0][1] = day
                # add low price
                if price < fundStock[year][month][1][0]:
                    fundStock[year][month][1][0] = price
                    fundStock[year][month][1][1] = day
                # add end of month price
                fundStock[year][month][3][0] = price
                fundStock[year][month][3][1] = day
                # add div price
                if month in fundDiv[year]:
                    if day == fundDiv[year][month][0]:
                        fundStock[year][month][4][0] = price
                        fundStock[year][month][4][1] = day
        lineCount += 1

# 4.
# stores Roth IRA limit in dictionary for each year
rothList = {}
for i in range(1982, 2022):
    amount = 0
    if i < 2002:
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

# 5.
# checks that the input is a valid year
def yearField(startEnd):
    year = input(startEnd + " year: ")
    if startEnd == "Start":
        aN = "a "
    else:
        aN = "an "
    if fund == "VTSAX":
        startYear = 2001
    else:
        # fund == "SPY":
        startYear = 1994
    while (not year.isdigit()) or (int(year) < startYear) or (int(year) > 2021):
        year = input("Please input " + aN + startEnd.lower() + " year between " + str(startYear) + " and 2021: ")
    return int(year)

# 6.
# checks that monthly deposit is positive and is only two digits after decimal
def isDollars(monthOrYear):
    if monthOrYear != 0:
        monthDe = input(monthOrYear.capitalize() + "ly Deposit: ")
    else:
        monthDe = input("Initial investment: ")
    myLoop = True
    while myLoop:
        if "-" in monthDe:
            monthDe = input(monthOrYear.capitalize() + "ly deposit cannot be negative. Please input zero or a positive number: ")
            continue
        if "," in monthDe:
            monthDe = monthDe.replace(",", "")
        try:
            float(monthDe)
        except:
            monthDe = input("Please input a number: ")
            continue
        if float(monthDe) < 0:
            monthDe = input("Please input zero or a positive number: ")
            continue
        if "." in monthDe:
            if monthDe.index(".") + 3 < len(monthDe):
                print("There may only be two digits past the decimal.")
                monthDe = input("Please input a number: ")
                continue
        myLoop = False
    return float(monthDe)

# 7.
# calculates price of total shares
def timeMarket(vary, startYear, endYear, deposit, isRoth, startStock):
    # running total of how many shares you own
    stockCount = startStock
    # FIRST ONLY DOING MONTHLY DEPOSIT
    for yearKey in fundStock:
        # go through every year
        if (yearKey >= startYear) and (yearKey <= endYear):
            # go through every month
            for monthKey in fundStock[yearKey]:
                if isRoth:
                    deposit = rothList[yearKey] / 12
                # check if it's a div month
                if monthKey in fundDiv[yearKey]:
                    # {year: {month: [[high price, day], [low price, day], [start price, day], [end price, day], [div price, day]}}
                    # {divYear: {divMonth: [divDay, $perShare]}}
                    # if buyDay < divCheckDay
                    if fundStock[yearKey][monthKey][vary][1] < fundDiv[yearKey][monthKey][0]:
                        # buy stock
                        # then add stock count * dividend per share
                        # then cash of dividends / price per share at dividend date
                        # VTSAXlist[yearKey][monthKey][vary][0] = stock price at low, high, or start
                        stockCount += deposit / fundStock[yearKey][monthKey][vary][0]
                        stockCount = stockCount + ((stockCount * fundDiv[yearKey][monthKey][1]) / fundStock[yearKey][monthKey][4][0])
                    else:
                        # otherwise add div shares then buy stock
                        stockCount = stockCount + ((stockCount * fundDiv[yearKey][monthKey][1]) / fundStock[yearKey][monthKey][4][0])
                        stockCount += deposit / fundStock[yearKey][monthKey][vary][0]
                # if it's not a dividend month
                else:
                    # just buy stocks with your monthly cashflow
                    stockCount += deposit / fundStock[yearKey][monthKey][vary][0]
    # return the value of your shares at Dec 31 2020 share value
    return stockCount * fundStock[endYear][12][3][0]

# 7.5
def timeMarketYear(vary, startYear, endYear, deposit, isRoth, startStock):
    # running total of how many shares you own
    stockCount = startStock
    # THIS IS YEARLY DEPOSIT
    for yearKey in fundStock:
        # go through every year
        if (yearKey >= startYear) and (yearKey <= endYear):
            varyStock = fundStock[yearKey][1][2][0]
            varyMonth = 1
            varyDay = 1
            if isRoth:
                deposit = rothList[yearKey]
            # create the high, low, start, end stock price and month
            # {year: {month: [[high price, day], [low price, day], [start price, day], [end price, day], [div price, day]}}
            for monthKey in fundStock[yearKey]:
                # for high
                if vary == 0:
                    if fundStock[yearKey][monthKey][vary][0] > varyStock:
                        varyStock = fundStock[yearKey][monthKey][vary][0]
                        varyMonth = monthKey
                        varyDay = fundStock[yearKey][monthKey][vary][1]
                # for low
                if vary == 1:
                    if fundStock[yearKey][monthKey][vary][0] < varyStock:
                        varyStock = fundStock[yearKey][monthKey][vary][0]
                        varyMonth = monthKey
                        varyDay = fundStock[yearKey][monthKey][vary][1]
            # start is default
            # for end
            if vary == 3:
                varyStock = fundStock[yearKey][12][vary][0]
                varyMonth = 12
                varyDay = fundStock[yearKey][12][vary][1]
            # go through every month
            for monthKey in fundStock[yearKey]:
                # check if it's a div month
                if monthKey in fundDiv[yearKey]:
                    # {year: {month: [[high price, day], [low price, day], [start price, day], [end price, day], [div price, day]}}
                    # {divYear: {divMonth: [divDay, $perShare]}}
                    # if the buy month is on the div month
                    if varyMonth == monthKey:
                        # if buyDay < divCheckDay
                        if varyDay < fundDiv[yearKey][monthKey][0]:
                            # buy stock then add div
                            stockCount += deposit / fundStock[yearKey][monthKey][vary][0]
                            stockCount = stockCount + ((stockCount * fundDiv[yearKey][monthKey][1]) / fundStock[yearKey][monthKey][4][0])
                        # buy day >= divCheckDay
                        # add div then buy stock
                        else:
                            stockCount = stockCount + ((stockCount * fundDiv[yearKey][monthKey][1]) / fundStock[yearKey][monthKey][4][0])
                            stockCount += deposit / fundStock[yearKey][monthKey][vary][0]
                    # otherwise buy month isnt on div month
                    # and just add div to stock count
                    else:
                        stockCount = stockCount + ((stockCount * fundDiv[yearKey][monthKey][1]) / fundStock[yearKey][monthKey][4][0])
                # if it's not a dividend month
                elif varyMonth == monthKey:
                    stockCount += deposit / fundStock[yearKey][monthKey][vary][0]
    # return the value of your shares at Dec 31 2020 share value
    return stockCount * fundStock[endYear][12][3][0]

# 8
# inputs for start year, end year, and monthly deposit or roth contribution
strYr = yearField("Start")
endYr = yearField("End")
while endYr < strYr:
    print("End year cannot be before start year.")
    endYr = yearField("End")

# 8.5
# ask user for intiial investment
startStock = isDollars(0) / fundStock[strYr][1][2][0]

# 9
# ask user for lump sum or monthly DCA
monthOrYear = input("Would you like to invest annually or monthly? (year/month): ")
monthOrYear = monthOrYear.lower()
while (monthOrYear != "year") and (monthOrYear != "month"):
    monthOrYear = input("Please input year or month: ")
    monthOrYear = monthOrYear.lower()

# 10
contLoop = 0
monDe = 0
isRoth = False
while contLoop == 0:
    rothMonth = input("Roth IRA limit or fixed cashflow? (roth/fixed): ")
    if rothMonth.lower() == "roth":
        isRoth = True
    elif rothMonth.lower() == "fixed":
        monDe = isDollars(monthOrYear)
    else:
        print("Please enter roth or fixed.")
        continue
    contLoop = 1

 # 11. prints value at end of duration for:
    # 12. low, high, start of period, end of period (DCA only)
# 11/12
# buy at high/low/start of monthly stock price
# 0 = high, 1 = low, 2 = start, 3 = end
if monthOrYear == "year":
    if monDe == 0:
        print('Value: ${:,.2f}'.format(timeMarketYear(0, strYr, endYr, monDe, isRoth, startStock)))
    else:
        # def timeMarketYear(vary, startYear, endYear, deposit, isRoth):
        print('High: ${:,.2f}'.format(timeMarketYear(0, strYr, endYr, monDe, isRoth, startStock)))
        print('Start: ${:,.2f}'.format(timeMarketYear(2, strYr, endYr, monDe, isRoth, startStock)))
        print('Low: ${:,.2f}'.format(timeMarketYear(1, strYr, endYr, monDe, isRoth, startStock)))
else:
    if monDe == 0:
        print('Value: ${:,.2f}'.format(timeMarket(0, strYr, endYr, monDe, isRoth, startStock)))
    else:
        # def timeMarket(vary, startYear, endYear, deposit, isRoth):
        print('High: ${:,.2f}'.format(timeMarket(0, strYr, endYr, monDe, isRoth, startStock)))
        print('Start: ${:,.2f}'.format(timeMarket(2, strYr, endYr, monDe, isRoth, startStock)))
        print('End: ${:,.2f}'.format(timeMarket(3, strYr, endYr, monDe, isRoth, startStock)))
        print('Low: ${:,.2f}'.format(timeMarket(1, strYr, endYr, monDe, isRoth, startStock)))

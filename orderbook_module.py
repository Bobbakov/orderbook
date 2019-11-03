from datetime import datetime
import itertools
from random import choice, randint
import operator
import time   
from matplotlib import pyplot as plt
import pandas as pd    
import seaborn as sns
sns.set(rc={'figure.figsize':(10, 5)})

###############################################################################
# FUNCTIONS FOR ORDER
###############################################################################
# Remove offer from order book
def removeOffer(offer, market):
    a = order.activeSellOrders[market.id]
    for c, o in enumerate(a):
        if o.id == offer.id:
            del a[c]
            break

# Remove offer from order book
def reduceOffer(offer, transactionQuantity, market):
    a = order.activeSellOrders[market.id]
    for c, o in enumerate(a):
        if o.id == offer.id:
            if a[c].quantity == transactionQuantity:
                removeOffer(offer, market)
            else:
                a[c].quantity -= transactionQuantity
            break

# Remove bid from order book
def removeBid(bid, market):
    a = order.activeBuyOrders[market.id]
    for c, o in enumerate(a):
        if o.id == bid.id:
            del a[c]
            break  
        
# Remove offer from order book
def reduceBid(bid, transactionQuantity, market):
    a = order.activeBuyOrders[market.id]
    for c, o in enumerate(a):
        if o.id == bid.id:
            if a[c].quantity == transactionQuantity:
                removeBid(bid, market)
            else:
               a[c].quantity -= transactionQuantity
            break

###############################################################################
# ORDER
###############################################################################
        
class order():
    counter = itertools.count()
    history = {}
    activeOrders = {}
    activeBuyOrders = {}
    activeSellOrders = {}
    
    # Initialize order
    def __init__(self, market, trader, side, price, quantity, mute = False):
        self.id = next(order.counter)
        self.datetime = datetime.now()
        self.market = market
        self.trader = trader
        self.side = side
        self.price = price
        self.quantity = quantity
        
        # IF FIRST ORDER IN MARKET --> INITIALIZE ORDERBOOKS
        if not market.id in order.history.keys():
            order.history[market.id] = []
            order.activeOrders[market.id] = []
            order.activeBuyOrders[market.id] = []
            order.activeSellOrders[market.id] = []
        
        # Add order to order history
        order.history[market.id].append(self)
        
        # Check if order results in transaction
        # If order is buy order
        if self.side == "Buy":
        
            # start loop
            remainingQuantity = self.quantity
            while True:
                # print(loopCounter)
                # If there are active sell orders --> continue
                if not not order.activeSellOrders[market.id]:
                    sellOrders = sorted(order.activeSellOrders[market.id], key = operator.attrgetter("price"))
                    bestOffer = sellOrders[0]
                    
                    # If limit price buy order >= price best offer --> transaction
                    if self.price >= bestOffer.price:
                        transactionPrice = bestOffer.price
                        
                        # If quantity order larger than best offer
                        if remainingQuantity > bestOffer.quantity:
                            transactionQuantity = bestOffer.quantity
                            
                            # Register transaction
                            transaction(self, bestOffer, market, transactionPrice, transactionQuantity)
                            
                            if not mute:
                                transactionDescription(self, bestOffer, market, transactionPrice, transactionQuantity)
                            
                            # Remove offer from orderbook
                            removeOffer(bestOffer, market)  
                            
                            # Reduce remaining quantity order
                            remainingQuantity -= transactionQuantity
                        # If quantity order equals quantity best offer    
                        elif remainingQuantity == bestOffer.quantity:
                            transactionQuantity = bestOffer.quantity
                            
                            # Register transaction
                            transaction(self, bestOffer, market, transactionPrice, transactionQuantity)
                            
                            if not mute:
                                transactionDescription(self, bestOffer, market, transactionPrice, transactionQuantity)
                            
                            # Remove offer from orderbook
                            removeOffer(bestOffer, market) 

                            # order is executed --> break loop
                            break       
                        # IF quantity order is small than quantity best offer
                        else:
                            transactionQuantity = remainingQuantity
                            
                            # Register transaction
                            transaction(self, bestOffer, market, transactionPrice, transactionQuantity)
                            
                            if not mute:
                                transactionDescription(self, bestOffer, market, transactionPrice, transactionQuantity)
                            
                            # Reduce offer
                            reduceOffer(bestOffer, transactionQuantity, market)
                            break
                            
                        
                    # If bid price < best offer --> no transaction    
                    else:
                        self.quantity = remainingQuantity
                        order.activeOrders[market.id].append(self)
                        order.activeBuyOrders[market.id].append(self)
                        break
                    
                # If there are NOT active sell orders --> add order to active orders        
                else:
                    self.quantity = remainingQuantity
                    order.activeOrders[market.id].append(self)
                    order.activeBuyOrders[market.id].append(self)
                    break
                
        # If order is sell order                  
        else:
            
            # start loop
            remainingQuantity = self.quantity
            while True:
                # if there are active buy orders --> continue
                if not not order.activeBuyOrders[market.id]:
                    buyOrders = sorted(order.activeBuyOrders[market.id], key = operator.attrgetter("price"), reverse = True)
                    bestBid = buyOrders[0]
                    
                    # If limit price sell order <= price best bid --> transaction
                    if bestBid.price >= self.price:
                        transactionPrice = bestBid.price
                        
                        # If quantity offer larger than quantity best bid
                        if remainingQuantity > bestBid.quantity:
                            transactionQuantity = bestBid.quantity
                            
                            # Register transaction
                            transaction(bestBid, self, market, transactionPrice, transactionQuantity)
                            
                            if not mute:
                                transactionDescription(bestBid, self, market, transactionPrice, transactionQuantity)
                            
                            # Remove bid from orderbook
                            removeBid(bestBid, market)    
                            
                            remainingQuantity -= transactionQuantity
                          # If quantity order equals quantity best offer    
                        elif remainingQuantity == bestBid.quantity:
                            transactionQuantity = bestBid.quantity
                            
                            # Register transaction
                            transaction(bestBid, self, market, transactionPrice, transactionQuantity)
                            
                            if not mute:
                                transactionDescription(bestBid, self, market, transactionPrice, transactionQuantity)
                            
                            # Remove offer from orderbook
                            removeBid(bestBid, market) 

                            # order is executed --> break loop
                            break       
                        
                        # IF quantity order is smaller than quantity best bid
                        else:
                            transactionQuantity = remainingQuantity
                            
                            # Register transaction
                            transaction(bestBid, self, market, transactionPrice, transactionQuantity)
                            
                            if not mute:
                                transactionDescription(bestBid, self, market, transactionPrice, transactionQuantity)
                            
                            # Reduce offer
                            reduceBid(bestBid, transactionQuantity, market)
                            break
                        
                    # No transaction    
                    else:
                        self.quantity = remainingQuantity
                        order.activeOrders[market.id].append(self)
                        order.activeSellOrders[market.id].append(self)
                        break
                    
                # If there are NOT active buy orders --> add order to active orders         
                else: 
                    self.quantity = remainingQuantity
                    order.activeOrders[market.id].append(self)
                    order.activeSellOrders[market.id].append(self)
                    break
                
            
    def __str__(self):
        return "{} \t {} \t {} \t {} \t {} \t {}".format(self.id, self.market, self.trader, self.side, self.price, self.quantity)

###############################################################################
# FUNCTIONS FOR TRANSACTIONS
###############################################################################
def transactionDescription(bid, offer, market, transactionPrice, transactionQuantity):
    return print("At market {} - Best bid: {} ({}) Best offer: {} ({}) --> Transaction at: {} ({})".format(market.id, bid.price, bid.quantity, 
                 offer.price, offer.quantity, transactionPrice, transactionQuantity))

###############################################################################
# TRANSACTIONS
###############################################################################

class transaction():
    counter = itertools.count()
    history = {}
    historyList = {}
    
    def __init__(self, buyOrder, sellOrder, market, price, quantity):
        self.id = next(transaction.counter)
        self.datetime = datetime.now()
        self.buyOrder = buyOrder
        self.sellOrder = sellOrder
        self.market = market
        self.price = price
        self.quantity = quantity
        
        if not market.id in transaction.history.keys():
            transaction.history[market.id] = []
            transaction.historyList[market.id] = []
        
        transaction.history[market.id].append(self)
        transaction.historyList[market.id].append([self.datetime.time(), self.price])
        
    def __str__(self):
        return "{} \t {} \t {} \t {} \t {} \t {} \t {}".format(self.id, self.datetime.time(), self.market, self.buyOrder.trader, self.sellOrder.trader, self.price, self.quantity)        

def showOrderbookPlt2():
    buyOrders = [(bo.price, -1 * bo.quantity) for bo in order.activeBuyOrders]
    sellOrders = [(so.price, so.quantity) for so in order.activeSellOrders]
    
    def sumKeys(orders):
        result = {}
        for k, v in orders:
            result[k] = result.get(k, 0) + v
        return result

    buyOrdersAgg = sumKeys(buyOrders)
    sellOrdersAgg = sumKeys(sellOrders)

    fig = plt.figure(figsize=(15, 7.5)) 
    
    ax = fig.add_subplot(1, 1, 1)
    ax.spines["left"].set_position('center')
    ax.spines["right"].set_color("none")
    ax.spines["top"].set_color("none")
    ax.spines["bottom"].set_color("none")
    
    plt.xlim(-15, 15)
    
    yMax = 101
    plt.ylim(0, yMax)
    plt.yticks(list(range(0, yMax)), list(range(0, yMax)))
    # ax.set_yticklabels(x, minor=False)
    #plt.axvline(0, color='grey', alpha=0.25)
    
    plt.barh(list(buyOrdersAgg.keys()), list(buyOrdersAgg.values()), align = "center", color = "green")
    plt.barh(list(sellOrdersAgg.keys()), list(sellOrdersAgg.values()), align = "center", color = "red")
        
    plt.show()

###############################################################################
# MARKET
############################################################################### 
# Generate n random Orders    
class market():
    counter = itertools.count()
    # INITIALIZE THE MARKET
    def __init__(self):
        self.id = next(market.counter)
       
    def __str__(self):
        return "{}".format(self.id)    
    
    # IF WE GENERATE ORDERS --> WE START THE MARKET  
    def orderGenerator(self, n, sleeptime = 0, mute = True, mute2 = True, display = "raw", 
                   dime_algo = False, pf_algo = False):
        c = 1
        for o in range(int(n)):
            if not mute:
                print("Iteration: {}".format(c))
            
            c+= 1
            # ACTION AGENT 1
            side = choice(["Buy", "Sell"])
            price = randint(0, 100)
            quantity = randint(1, 10)
            market = self
            order(market, "Bert", side, price, quantity, mute = mute2)
            
            # ACTION AGENT 2                    
            if dime_algo:
                alwaysBestBid("bestBidder")  
                alwaysBestOffer("bestOffer")
        
            
            # ACTION AGENT 3
            if pf_algo:
                priceFollowing("Follow")
                   
            time.sleep(float(sleeptime))       
    
    # Show orderbook            
    def showOrderbook(self):
        widthOrderbook = len("93       0       Bert    Buy     33      5")
        print(widthOrderbook * 2 * "*")
        for sellOrder in sorted(order.activeSellOrders[self.id], key = operator.attrgetter("price"), reverse = True):
                print(widthOrderbook * "." + " " + str(sellOrder))
        for buyOrder in sorted(order.activeBuyOrders[self.id], key = operator.attrgetter("price"), reverse = True):
                print(str(buyOrder) + " " + widthOrderbook * ".")
        print(widthOrderbook * 2 * "*")        
        print(" ")
    
    def plot(self):
        df = pd.DataFrame(transaction.historyList[self.id], columns = ["time", "price"])
        return df.plot() 
    
    # Show transaction history
    def transactionHistory(self):
        for t in transaction.history[self.id]:
            print(t)

###############################################################################
# ALGORITHMIC TRADING STRATEGIES
###############################################################################        
# FROM HERE FOLLOW ALGORITHMIC STRATEGIES
def alwaysBestBid(name):
    quantity = randint(1, 10)
    # If there are active buy orders --> improve best bid
    if not not order.activeBuyOrders:
        buyOrders = sorted(order.activeBuyOrders, key = operator.attrgetter("price"), reverse = True)
        bestBid = buyOrders[0]
        
        # If trader is not best bid --> improve best bid
        if not bestBid.trader == name:
            order(name, "Buy", bestBid.price + 1, quantity)    
        else:
            pass
    # Else --> create best bid    
    else:
        order(name, "Buy", 1, quantity)
        
def alwaysBestOffer(name):    
    quantity = randint(1, 10)
    # If there are active sell orders --> improve best offer
    if not not order.activeSellOrders:
        sellOrders = sorted(order.activeSellOrders, key = operator.attrgetter("price"))
        bestOffer = sellOrders[0]
        
        # If trader is not best bid --> improve best bid
        if not bestOffer.trader == name:
            order(name, "Sell", bestOffer.price - 1, quantity)    
        else:
            pass
    # Else --> create best bid    
    else:
        order(name, "Sell", 100, quantity)        
        
def priceFollowing(name):
    # If transaction --> check for trend
    if len(transaction.history) >= 2:
        lastPrice = transaction.history[-1].price
        secondLastPrice = transaction.history[-2].price
        quantity = randint(1, 10)
        
        # If price up --> buy best offer
        if lastPrice > secondLastPrice:
            if not not order.activeSellOrders:
                #sellOrders = sorted(order.activeSellOrders, key = operator.attrgetter("price"))
                #bestOffer = sellOrders[0]
                order(name, "Buy", 100, quantity)
        
    # If price down --> hit best bid    
        if lastPrice < secondLastPrice:
            if not not order.activeBuyOrders:
                #buyOrders = sorted(order.activeBuyOrders, key = operator.attrgetter("price"), reverse = True)
                #bestBid = buyOrders[0]
                order(name, "Sell", 1, quantity)        
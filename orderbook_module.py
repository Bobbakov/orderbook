from datetime import datetime
import itertools
from random import choice, randint
import operator
import time   
from matplotlib import pyplot as plt

class transaction():
    counter = itertools.count()
    history = []
    historyList = []
    def __init__(self, buyOrder, sellOrder, price, quantity):
        self.id = next(transaction.counter)
        self.datetime = datetime.now()
        self.buyOrder = buyOrder
        self.sellOrder = sellOrder
        self.price = price
        self.quantity = quantity
        
        transaction.history.append(self)
        transaction.historyList.append([self.datetime.time(), self.price])
        
    def __str__(self):
        return "{} \t {} \t {} \t {} \t {} \t {}".format(self.id, self.datetime.time(), self.buyOrder.agent, self.sellOrder.agent, self.price, self.quantity)
        
class order():
    counter = itertools.count()
    history = []
    activeOrders = []
    activeBuyOrders = []
    activeSellOrders = []
    
    # Initialize order
    def __init__(self, trader, side, price, quantity):
        self.id = next(order.counter)
        self.datetime = datetime.now()
        self.trader = trader
        self.side = side
        self.price = price
        self.quantity = quantity
        
        # Add order to order history
        order.history.append(self)
        
        # Check if order results in transaction
        # If order is buy order
        if self.side == "Buy":
        
            # start loop
            remainingQuantity = self.quantity
            while True:
                # print(loopCounter)
                # If there are active sell orders --> continue
                if not not order.activeSellOrders:
                    sellOrders = sorted(order.activeSellOrders, key = operator.attrgetter("price"))
                    bestOffer = sellOrders[0]
                    
                    # If limit price buy order >= price best offer --> transaction
                    if self.price >= bestOffer.price:
                        transactionPrice = bestOffer.price
                        
                        # If quantity order larger than best offer
                        if remainingQuantity > bestOffer.quantity:
                            transactionQuantity = bestOffer.quantity
                            
                            # Register transaction
                            transaction(self, bestOffer, transactionPrice, transactionQuantity)
                            transactionDescription(self, bestOffer, transactionPrice, transactionQuantity)
                            
                            # Remove offer from orderbook
                            removeOffer(bestOffer)  
                            
                            # Reduce remaining quantity order
                            remainingQuantity -= transactionQuantity
                        # If quantity order equals quantity best offer    
                        elif remainingQuantity == bestOffer.quantity:
                            transactionQuantity = bestOffer.quantity
                            
                            # Register transaction
                            transaction(self, bestOffer, transactionPrice, transactionQuantity)
                            transactionDescription(self, bestOffer, transactionPrice, transactionQuantity)
                            
                            # Remove offer from orderbook
                            removeOffer(bestOffer) 

                            # order is executed --> break loop
                            break       
                        # IF quantity order is small than quantity best offer
                        else:
                            transactionQuantity = remainingQuantity
                            
                            # Register transaction
                            transaction(self, bestOffer, transactionPrice, transactionQuantity)
                            transactionDescription(self, bestOffer, transactionPrice, transactionQuantity)
                            
                            # Reduce offer
                            reduceOffer(bestOffer, transactionQuantity)
                            break
                            
                        
                    # If bid price < best offer --> no transaction    
                    else:
                        self.quantity = remainingQuantity
                        order.activeOrders.append(self)
                        order.activeBuyOrders.append(self)
                        break
                    
                # If there are NOT active sell orders --> add order to active orders        
                else:
                    self.quantity = remainingQuantity
                    order.activeOrders.append(self)
                    order.activeBuyOrders.append(self)
                    break
                
        # If order is sell order                  
        else:
            
            # start loop
            remainingQuantity = self.quantity
            while True:
                # if there are active buy orders --> continue
                if not not order.activeBuyOrders:
                    buyOrders = sorted(order.activeBuyOrders, key = operator.attrgetter("price"), reverse = True)
                    bestBid = buyOrders[0]
                    
                    # If limit price sell order <= price best bid --> transaction
                    if bestBid.price >= self.price:
                        transactionPrice = bestBid.price
                        
                        # If quantity offer larger than quantity best bid
                        if remainingQuantity > bestBid.quantity:
                            transactionQuantity = bestBid.quantity
                            
                            # Register transaction
                            transaction(bestBid, self, transactionPrice, transactionQuantity)
                            transactionDescription(bestBid, self, transactionPrice, transactionQuantity)
                            
                            # Remove bid from orderbook
                            removeBid(bestBid)    
                            
                            remainingQuantity -= transactionQuantity
                          # If quantity order equals quantity best offer    
                        elif remainingQuantity == bestBid.quantity:
                            transactionQuantity = bestBid.quantity
                            
                            # Register transaction
                            transaction(bestBid, self, transactionPrice, transactionQuantity)
                            transactionDescription(bestBid, self, transactionPrice, transactionQuantity)
                            
                            # Remove offer from orderbook
                            removeBid(bestBid) 

                            # order is executed --> break loop
                            break       
                        
                        # IF quantity order is smaller than quantity best bid
                        else:
                            transactionQuantity = remainingQuantity
                            
                            # Register transaction
                            transaction(bestBid, self, transactionPrice, transactionQuantity)
                            transactionDescription(bestBid, self, transactionPrice, transactionQuantity)
                            
                            # Reduce offer
                            reduceBid(bestBid, transactionQuantity)
                            break
                        
                    # No transaction    
                    else:
                        self.quantity = remainingQuantity
                        order.activeOrders.append(self)
                        order.activeSellOrders.append(self)
                        break
                    
                # If there are NOT active buy orders --> add order to active orders         
                else: 
                    self.quantity = remainingQuantity
                    order.activeOrders.append(self)
                    order.activeSellOrders.append(self)
                    break
                
            
    def __str__(self):
        return "{} \t {} \t {} \t {} \t {}".format(self.id, self.trader, self.side, self.price, self.quantity)

# Remove offer from order book
def removeOffer(offer):
    for c, o in enumerate(order.activeSellOrders):
        if o.id == offer.id:
            del order.activeSellOrders[c]
            break

# Remove offer from order book
def reduceOffer(offer, transactionQuantity):
    for c, o in enumerate(order.activeSellOrders):
        if o.id == offer.id:
            if order.activeSellOrders[c].quantity == transactionQuantity:
                removeOffer(offer)
            else:
                order.activeSellOrders[c].quantity -= transactionQuantity
            break

# Remove bid from order book
def removeBid(bid):
    for c, o in enumerate(order.activeBuyOrders):
        if o.id == bid.id:
            del order.activeBuyOrders[c]
            break  
        
# Remove offer from order book
def reduceBid(bid, transactionQuantity):
    for c, o in enumerate(order.activeBuyOrders):
        if o.id == bid.id:
            if order.activeBuyOrders[c].quantity == transactionQuantity:
                removeBid(bid)
            else:
                order.activeBuyOrders[c].quantity -= transactionQuantity
            break

def transactionDescription(bid, offer, transactionPrice, transactionQuantity):
    return print("Best bid: {} ({}) Best offer: {} ({}) --> Transaction at: {} ({})".format(bid.price, bid.quantity, 
                 offer.price, offer.quantity, transactionPrice, transactionQuantity))        
    
# Show orderbook            
def showOrderbook():
    widthOrderbook = len("0        Bert    Buy     8       3")
    print(widthOrderbook * 2 * "*")
    for sellOrder in sorted(order.activeSellOrders, key = operator.attrgetter("price"), reverse = True):
            print(widthOrderbook * "." + " " + str(sellOrder))
    for buyOrder in sorted(order.activeBuyOrders, key = operator.attrgetter("price"), reverse = True):
            print(str(buyOrder) + " " + widthOrderbook * ".")
    print(widthOrderbook * 2 * "*")        
    print(" ")
    
# Show transaction history
def transactionHistory():
    for t in transaction.history:
        print(t)

def plotPriceHistory():
    import pandas as pd   
    df = pd.DataFrame(transaction.historyList, columns = ["time", "price"])
    return df.plot()        

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

"""
if __name__ == "__main__":
    n = input("Input number of orders you want to create: ")
    sleeptime = input("Insert number of seconds between orders entered: ")
    orderGenerator(n, sleeptime)
"""
# FROM HERE FOLLOW ALGORITHMIC STRATEGIES
def alwaysBestBid(name):
    quantity = randint(1, 100)
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
    quantity = randint(1, 100)
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
    if not not transaction.history:
        lastPrice = transaction.history[0].price
        secondLastPrice = transaction.history[1].price
        
        # If price up --> buy best offer
        if lastPrice > secondLastPrice:
            if not not order.activeSellOrders:
                sellOrders = sorted(order.activeSellOrders, key = operator.attrgetter("price"))
                bestOffer = sellOrders[0]
                order(name, "Buy", bestOffer.price, bestOffer.quantity)
        
    # If price down --> hit best bid    
        if lastPrice < secondLastPrice:
            if not not order.activeBuyOrders:
                buyOrders = sorted(order.activeBuyOrders, key = operator.attrgetter("price"), reverse = True)
                bestBid = buyOrders[0]
                order(name, "Sell", bestBid.price, bestBid.quantity)
        
# Generate n random Orders    
def orderGenerator(n, sleeptime = 0, mute = True, display = "raw", 
                   algorithm_dime = False, algorithm_pricefollowing = False):
    counter = 1
    for o in range(int(n)):
        if not mute:
            print("Iteration: {}".format(counter))
        
        # Action agent 1
        side = choice(["Buy", "Sell"])
        price = randint(0, 100)
        quantity = randint(1, 10)
        order("Bert", side, price, quantity)
        
        if not mute:
            print("Action random:")
            if display == "raw":
                showOrderbook()
            if display == "plt":
                showOrderbookPlt2()
                
        if algorithm_dime:
            alwaysBestBid("bestBidder")  
            
            # Action agent 2
            if not mute:
                print("Action best bid algorithm:")
                if display == "raw":
                    showOrderbook()
                if display == "plt":
                    showOrderbookPlt2()
            
            alwaysBestOffer("bestOffer")
    
            # Action agent 3
            if not mute:
                print("Action best offer algorithm:")
                if display == "raw":
                    showOrderbook()
                if display == "plt":
                    showOrderbookPlt2()
        
        if algorithm_pricefollowing:
            priceFollowing("priceFollowing")
            
            # Action agent 2
            if not mute:
                print("Action price following algorithm:")
                if display == "raw":
                    showOrderbook()
                if display == "plt":
                    showOrderbookPlt2()
               
        time.sleep(float(sleeptime))
        counter += 1        
    
        


        
        
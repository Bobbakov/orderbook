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
    def __init__(self, market, agent, side, price, quantity, mute_transactions = True):
        self.id = next(order.counter)
        self.datetime = datetime.now()
        self.market = market
        self.agent = agent
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
                            
                            if not mute_transactions:
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
                            
                            if not mute_transactions:
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
                            
                            if not mute_transactions:
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
                                
                                
                                if not mute_transactions:
                                    transactionDescription(bestBid, self, market, transactionPrice, transactionQuantity)
                                
                                # Remove bid from orderbook
                                removeBid(bestBid, market)    
                                
                                remainingQuantity -= transactionQuantity
                              # If quantity order equals quantity best offer    
                            elif remainingQuantity == bestBid.quantity:
                                transactionQuantity = bestBid.quantity
                                
                                # Register transaction
                                transaction(bestBid, self, market, transactionPrice, transactionQuantity)
                                
                                if not mute_transactions:
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
                                
                                if not mute_transactions:
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
        return "{} \t {} \t {} \t {} \t {}".format(self.market, self.agent.name, self.side, self.price, self.quantity)

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
    # CHECK IF RUNNING POSITION IS CORRECT
    historyPosition = {}
    
    def __init__(self, buyOrder, sellOrder, market, price, quantity):
        self.id = next(transaction.counter)
        self.datetime = datetime.now()
        self.buyOrder = buyOrder
        self.sellOrder = sellOrder
        self.market = market
        self.price = price
        self.quantity = quantity
        
        buyOrder.agent.position += quantity
        sellOrder.agent.position -= quantity
        
        if not market.id in transaction.history.keys():
            transaction.history[market.id] = []
            transaction.historyList[market.id] = []
            
        if not (market.id, buyOrder.agent.name) in transaction.historyPosition.keys():
            transaction.historyPosition[market.id, buyOrder.agent.name] = []
            
        if not (market.id, sellOrder.agent.name) in transaction.historyPosition.keys():
            transaction.historyPosition[market.id, sellOrder.agent.name] = []        
        
        transaction.history[market.id].append(self)
        transaction.historyList[market.id].append([self.id, self.datetime.time(), self.price])
        transaction.historyPosition[market.id, buyOrder.agent.name].append([self.id, buyOrder.agent.position])
        transaction.historyPosition[market.id, sellOrder.agent.name].append([self.id, sellOrder.agent.position])
        
    def __str__(self):
        return "{} \t {} \t {} \t {} \t {} \t {} \t {}".format(self.id, self.datetime.time(), self.market, self.buyOrder.agent.name, self.sellOrder.agent.name, self.price, self.quantity)        

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
    
def getLastPriceElse(market, p0):
    if market.id in transaction.history.keys():
        p = transaction.history[market.id][-1].price 
    else:
        p = p0             
    return p

###############################################################################
# AGENTS
###############################################################################        
# INITIALIZE AGENT
class agent():
    def __init__(self, name): 
        self.name = name
        self.position = 0
        self.runningProfit = 0
    
    # PICK ALGORITHMIC TRADING STRATEGY AGENT    
    def uniformRandom(self, market, mute_transactions = True):
        side = choice(["Buy", "Sell"])
        price = randint(market.minprice, market.maxprice)
        quantity = randint(market.minquantity, market.maxquantity)
        
        order(market, self, side, price, quantity, mute_transactions = mute_transactions)
    
    def bestBidOffer(self, market, mute_transactions = True):
        quantity = randint(market.minquantity, market.maxquantity)
        
        # If there are active buy orders --> improve best bid
        if not not order.activeBuyOrders[market.id]:
            buyOrders = sorted(order.activeBuyOrders[market.id], key = operator.attrgetter("price"), reverse = True)
            bestBid = buyOrders[0]
            
            # If trader is not best bid --> improve best bid
            if not bestBid.agent.name == self.name:
                order(market, self, "Buy", bestBid.price + 1, quantity, mute_transactions)    
            else:
                pass
        # Else --> create best bid    
        else:
            order(market, self, "Buy", market.minprice, quantity, mute_transactions)
         
        quantity = randint(market.minquantity, market.maxquantity)
        # If there are active sell orders --> improve best offer
        if not not order.activeSellOrders[market.id]:
            sellOrders = sorted(order.activeSellOrders[market.id], key = operator.attrgetter("price"))
            bestOffer = sellOrders[0]
            
            # If trader is not best bid --> improve best bid
            if not bestOffer.agent.name == self.name:
                order(market, self, "Sell", bestOffer.price - 1, quantity, mute_transactions)    
            else:
                pass
        # Else --> create best bid    
        else:
            order(market, self, "Sell", market.maxprice, quantity, mute_transactions)        
    
    def bestBidOfferStop(self, market, mute_transactions = True):
        quantity = randint(market.minquantity, market.maxquantity)
        
        if self.position > 250:
            order(market, self, "Sell", market.minprice, 250, mute_transactions = False)  
        elif self.position < - 250:
            order(market, self, "Buy", market.maxprice, 250, mute_transactions = False)  
        else:
            # If there are active buy orders --> improve best bid
            if not not order.activeBuyOrders[market.id]:
                buyOrders = sorted(order.activeBuyOrders[market.id], key = operator.attrgetter("price"), reverse = True)
                bestBid = buyOrders[0]
                
                # If trader is not best bid --> improve best bid
                if not bestBid.agent.name == self.name:
                    order(market, self, "Buy", bestBid.price + 1, quantity, mute_transactions)    
                else:
                    pass
            # Else --> create best bid    
            else:
                order(market, self, "Buy", market.minprice, quantity, mute_transactions)
             
            quantity = randint(market.minquantity, market.maxquantity)
            # If there are active sell orders --> improve best offer
            if not not order.activeSellOrders[market.id]:
                sellOrders = sorted(order.activeSellOrders[market.id], key = operator.attrgetter("price"))
                bestOffer = sellOrders[0]
                
                # If trader is not best bid --> improve best bid
                if not bestOffer.agent.name == self.name:
                    order(market, self, "Sell", bestOffer.price - 1, quantity, mute_transactions)    
                else:
                    pass
            # Else --> create best bid    
            else:
                order(market, self, "Sell", market.maxprice, quantity, mute_transactions) 
        
###############################################################################
# MARKET
############################################################################### 
# from numpy.random import normal

agent1 = agent("random")
agent2 = agent("marketMaker")
agent3 = agent("makerMakerStop")

agents = [(agent1, "r"),
          (agent2, "mm"),
          (agent3, "mm_stop")]

# Generate n random Orders    
class market():
    counter = itertools.count()
    # INITIALIZE THE MARKET
    def __init__(self, minprice = 1, maxprice = 100, minquantity = 1, maxquantity = 10):
        self.id = next(market.counter)
        self.minprice = minprice
        self.maxprice = maxprice
        self.minquantity = minquantity
        self.maxquantity = maxquantity
        self.agents = []
    
    # ADD AGENTS --> STRATEGIES    
    def addAgents(self, agents):
        for a, s in agents:
            self.agents.append((a, s))
       
    def __str__(self):
        return "{}".format(self.id)    
    
    # IF WE GENERATE ORDERS --> WE START THE MARKET  
    def orderGenerator(self, n, sleeptime = 0):
        c = 1
        
        for o in range(int(n)):      
            # ACTION RANDOM AGENT
            for a, s in self.agents:
                if s == "r":
                    a.uniformRandom(self) 
                if s == "mm":
                    a.bestBidOffer(self)
                if s == "mm_stop":
                    a.bestBidOfferStop(self)            
            
            c+= 1
            time.sleep(float(sleeptime))       
            
    def clear(self):
        order.activeBuyOrders[self.id] = []
        order.activeSellOrders[self.id] = []
        
    # Show orderbook            
    def showOrderbook(self):
        widthOrderbook = len("0       Bert    Buy     33      5")
        print(widthOrderbook * 2 * "*")
        
        for sellOrder in sorted(order.activeSellOrders[self.id], key = operator.attrgetter("price"), reverse = True):
                print(widthOrderbook * "." + " " + str(sellOrder))
        for buyOrder in sorted(order.activeBuyOrders[self.id], key = operator.attrgetter("price"), reverse = True):
                print(str(buyOrder) + " " + widthOrderbook * ".")
        print(widthOrderbook * 2 * "*")        
        print(" ")
    
    def plot(self):
        df = pd.DataFrame(transaction.historyList[self.id], columns = ["id", "time", "price"])
        df["volatility"] = df["price"].rolling(7).std()
        df["volatilityTrend"] = df["volatility"].rolling(14).mean()
        df = df[["id", "price", "volatility", "volatilityTrend"]]
        df = df.set_index("id")
        return df.plot() 
    
    def plotPositions(self):
        # PLOT RANDOM AGENT
        for a, s in self.agents:
            right = pd.DataFrame(transaction.historyPosition[self.id, a.name], columns = ["id", a.name])
            right = right.set_index("id")
            plt.plot(right, label = str(a.name))
            
        return plt.show()
    
    def plotPricePosition(self):
        df = pd.DataFrame(transaction.historyList[self.id], columns = ["id", "time", "price"])
        df["volatility"] = df["price"].rolling(7).std()
        df["volatilityTrend"] = df["volatility"].rolling(14).mean()
        df = df[["id", "price", "volatility", "volatilityTrend"]]
        df = df.set_index("id")
        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        ax1.plot(df["price"], label = ["price"])
        ax1.plot(df["volatility"], label = "volatility")
        ax1.plot(df["volatilityTrend"], label = "volatilityTrend")
        ax1.set_ylabel('price')
        
        # PLOT RANDOM AGENT
        Bert = pd.DataFrame(transaction.historyPosition[self.id, "Bert"], columns = ["id", "Bert"])
        Bert = Bert.set_index("id")
        #plt.plot(Bert)
        
        ax2 = ax1.twinx()
        ax2.plot(Bert)
        
        # PLOT MARKET MAKER
        BBO = pd.DataFrame(transaction.historyPosition[self.id, "BBO"], columns = ["id", "position"])
        BBO = BBO.set_index("id")
        
        ax2.plot(BBO)
        ax2.set_ylabel('position')
        fig.legend()
        
        return plt.show()    
    
    # Show transaction history
    def transactionHistory(self):
        for t in transaction.history[self.id]:
            print(t)
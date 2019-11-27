# orderbook
This library consists of a market simulator, in which you can create markets, add agents, send in orders and get transactions.

The library consists of four classes:
(1) market
(2) agent
(3) order
(4) transactions.


Step 1:

Import the libary:

import orderbook.*

Step 2:
Instantiate a market:

a = market()

b = market()

c = market()
...

Step 3: 

Add agents to your market

The library comes with (as of now) three pre-set type of agents:

(1) A 'random' agent, sending in buy/sell orders at random, picking both prices and quanties from a uniform distribution

(2) A market maker, always being best bid and best offer

(3) A market maker with position limit. Same as (2) except that it will close its entire position once its position limit is exceeded.

You can add agents via:

a.addAgents()

Note: you will add agent (1), (2) and (3) by default. 

You can add as many agents as you want.

You can add an agent by:

newAgent = (agent('nameAgent'), strategyAgent)

With strategyAgent being either 'r' (for random), 'mm' (for market maker) or 'mm_stop' for market maker with position limit.

Then type:

a.addAgents([newAgent])

Step 4: 
Start the market.

You can do so by typing:

a.orderGenerator(n) (with n being the number of iterations)

Once finished, you can see the final orderbook by typing:
a.showOrderbook()

You can the transactions done by typing:
a.showTransactionHistory()

You can check the price development by typing:
a.plot()

And positions of your agents by typing:
a.plotPositions().



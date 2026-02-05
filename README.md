# Graph-Based Anti-Money Laundering (AML) Engine


## The Business Problem
Traditional AML systems rely on static rules (e.g., "Flag any transaction > $10,000"). Sophisticated criminals evade this by "structuring" (breaking large sums into small, micro-transactions) or "layering" (moving money through mule accounts). These patterns are invisible in Excel rows but obvious in a network graph.

## The Solution
I developed a forensic detection engine using Graph Theory and Statistical Thresholding to identify money laundering topologies in high-volume transaction data.

## Key Features

Network Construction: Modeled 50,000+ transactions as a Directed Graph using NetworkX.

Star Topology Detection: Applied In-Degree Centrality algorithms to identify "Kingpin" accounts aggregating funds from multiple disconnected sources.

Structuring Filters: Implemented statistical heuristics to flag "High-Frequency / Low-Volume" patterns indicative of structuring (smurfing).

## Results

Detection: Successfully isolated 8 distinct laundering rings from 50,000 transactions.

Impact: Identified $1.6 Million in illicit flow volume that would have bypassed standard threshold filters.

False Positive Reduction: Visualized the network to differentiate between "Whales" (single large senders) and "Smurfs" (organized structuring).

## Tech Stack

Python: Core Logic

NetworkX: Graph Algorithms

Pandas: Data Engineering

Matplotlib: Forensic Visualization

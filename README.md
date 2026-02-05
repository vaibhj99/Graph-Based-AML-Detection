#  Graph-Based Anti-Money Laundering (AML) Engine

###  The Business Problem
Traditional banking compliance relies on static rules (e.g., *"Flag transaction > $10,000"*). Sophisticated criminals evade this by **Structuring** (splitting funds) and **Layering** (moving funds through mule accounts). These patterns are invisible in spreadsheets but obvious in a network graph.

###  The Solution
I built a **Forensic Graph Detection Engine** using Python (`NetworkX`) to identify "Star Topologies" (Many-to-One flows) typical of money laundering rings.

###  Key Results

**1. Network Topology Detection**
*Isolated 8 distinct "Laundering Rings" from 50,000 transactions using In-Degree Centrality.*
![Topology View](1_network_topology.png)


**2. Forensic Drill-Down**
*Analyzed transaction distributions to distinguish between legitimate high-value senders and suspicious layering behavior.*
![Forensic View](2_forensic_analysis.png)


**3. Risk Impact Analysis**
*Quantified the financial exposure. Identified top 8 Kingpins moving over **$1.6 Million** in aggregate illicit volume.*
![Risk Profile](3_executive_risk_profile.png)

---

### Tech Stack
* **Python:** Core Logic & Data Processing
* **NetworkX:** Graph Algorithms (Centrality, Ego Graphs)
* **Pandas:** Data Engineering
* **Matplotlib:** Forensic Visualization

import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

# --- CONFIGURATION ---
FILE_PATH = 'paysim.csv'  # Make sure this matches your file name
SAMPLE_SIZE = 50000       # We take a sample to save RAM (adjust if you have 16GB+ RAM)

print("Loading data... this might take a minute.")

# --- STEP 1: SMART LOADING ---
# We only load relevant columns to save memory
df = pd.read_csv(FILE_PATH, usecols=['step', 'type', 'amount', 'nameOrig', 'nameDest', 'isFraud'])

# Filter: Money Laundering usually involves TRANSFER (sending) and CASH_OUT (withdrawing)
df_filtered = df[df['type'].isin(['TRANSFER', 'CASH_OUT'])]

# Sampling: Take the first N rows for the prototype
df_sample = df_filtered.head(SAMPLE_SIZE)

print(f"Data Loaded. Processing {len(df_sample)} transactions.")

# --- STEP 2: BUILD THE NETWORK ---
print("Building the Graph...")
G = nx.DiGraph()

# Add edges (Transaction: Origin -> Destination)
# We include 'amount' as a weight so we can analyze it later
for index, row in df_sample.iterrows():
    G.add_edge(row['nameOrig'], row['nameDest'], weight=row['amount'], type=row['type'])

# --- STEP 3: THE SMURF HUNTING LOGIC ---
# We look for "Fan-In" patterns: Many accounts sending to ONE account.
# Heuristic: In-Degree > 5 (received from 5+ people) AND Mean Amount < 50,000 (Structuring)

suspicious_accounts = []

# Iterate through all nodes (accounts)
for node in G.nodes():
    # Get all incoming transactions
    in_edges = G.in_edges(node, data=True)
    in_degree = len(in_edges)
    
    if in_degree >= 5: # Threshold: Receiving from 5+ sources
        amounts = [data['weight'] for u, v, data in in_edges]
        avg_amount = sum(amounts) / len(amounts)
        
        # Check for structuring (e.g., amounts that aren't huge individually but add up)
        if avg_amount < 50000: 
            suspicious_accounts.append(node)

print(f"\n FOUND {len(suspicious_accounts)} SUSPICIOUS 'LAUNDERING' HUBS.")
print(f"Sample IDs: {suspicious_accounts[:5]}")







# --- STEP 4: VISUALIZATION  ---
if suspicious_accounts:
    target = suspicious_accounts[0]
    
    # FIX: We convert to 'Undirected' just for the visual so we can see 
    # who sent the money (Predecessors) not just where it went (Successors)
    G_visual = G.to_undirected()
    
    # Create the subgraph of the Kingpin + The Ants
    subgraph = nx.ego_graph(G_visual, target, radius=1)
    
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(subgraph, seed=42, k=0.5) # k regulates the distance between nodes
    
    # Draw the Ants (Blue)
    nx.draw(subgraph, pos, with_labels=False, node_color='skyblue', 
            edge_color='gray', node_size=200, alpha=0.7)
    
    # Draw the Kingpin (Red and Bigger)
    nx.draw_networkx_nodes(subgraph, pos, nodelist=[target], node_color='red', node_size=1500)
    
    # Add a label just for the Kingpin
    nx.draw_networkx_labels(subgraph, pos, labels={target: "Laundering Hub"}, font_color='white')
    
    plt.title(f"Visual Proof of Structuring: Hub & Spoke Network\nSuspect ID: {target}", fontsize=14)
    plt.show()

else:
    print("No smurfing patterns found in this sample size. Try increasing SAMPLE_SIZE.")








'''


# --- STEP 4: VISUALIZATION (THE COMBINED VIEW) ---
if suspicious_accounts:
    print(f"\nGeneratin Unified Forensic Chart for {len(suspicious_accounts)} Suspects...")
    
    # 1. Prepare Data
    plot_data = []
    
    for kingpin in suspicious_accounts:
        in_edges = G.in_edges(kingpin, data=True)
        count = len(in_edges)
        
        # Create a label that includes the ID AND the Count
        # e.g., "User_123 (6 Txns)"
        label = f"{kingpin}\n({count} senders)"
        
        for u, v, data in in_edges:
            plot_data.append({
                'Label': label,
                'Amount': data['weight'],
                'Kingpin': kingpin # Keep raw ID for sorting
            })
    
    df_plot = pd.DataFrame(plot_data)
    
    # Sort by "Max Amount" so the biggest criminals are at the top
    # (This makes the chart readable)
    sort_order = df_plot.groupby('Kingpin')['Amount'].max().sort_values(ascending=True).index
    
    # Create a mapping to sort the labels correctly
    # We want the labels (with counts), but sorted by the logic above
    label_map = {row['Kingpin']: row['Label'] for index, row in df_plot.iterrows()}
    sorted_labels = [label_map[k] for k in sort_order]
    
    # --- PLOTTING ---
    plt.figure(figsize=(12, 8))
    
    # Plot the dots (The Transactions)
    # We use the 'Label' column for Y-axis so the count is shown automatically
    plt.scatter(df_plot['Amount'], df_plot['Label'], 
                alpha=0.7, s=100, color='teal', edgecolors='black', zorder=3)
    
    # Add the "Evidence Line" ($10k Threshold)
    plt.axvline(x=10000, color='red', linestyle='--', linewidth=2, alpha=0.8, zorder=2)
    plt.text(12000, 0, 'Reporting Limit ($10k)', color='red', fontweight='bold', va='bottom')
    
    # Styling
    plt.title(f'Forensic Analysis: Transaction Structuring Detected\n(Sample of {len(suspicious_accounts)} Suspicious Accounts)', fontsize=15, fontweight='bold')
    plt.xlabel('Transaction Amount ($)', fontsize=12, fontweight='bold')
    plt.ylabel('Suspicious Account ( & Transaction Count)', fontsize=12, fontweight='bold')
    plt.grid(axis='x', linestyle='--', alpha=0.5, zorder=1)
    
    # Formatting X-axis to show $ signs (e.g., $50,000)
    current_values = plt.gca().get_xticks()
    plt.gca().set_xticklabels([f'${int(x):,}' for x in current_values])
    
    plt.tight_layout()
    plt.show()

else:
    print("No patterns found.")


# --- STEP 4: VISUALIZATION (ALL KINGPINS) ---
if suspicious_accounts:
    print(f"\n Generating Galaxy View for {len(suspicious_accounts)} Suspects...")
    
    # 1. Switch to Undirected so we can find neighbors easily
    G_visual = G.to_undirected()
    
    # 2. Collect ALL nodes we want to draw (Kingpins + Their Smurfs)
    nodes_to_draw = set(suspicious_accounts) # Start with the 8 Kingpins
    
    for kingpin in suspicious_accounts:
        # Get neighbors (Smurfs) for each Kingpin and add to set
        neighbors = list(G_visual.neighbors(kingpin))
        nodes_to_draw.update(neighbors)
    
    # 3. Create the Subgraph containing ONLY these clusters
    subgraph = G_visual.subgraph(nodes_to_draw)
    
    # 4. Setup the Plot
    plt.figure(figsize=(14, 10))
    
    # Use 'spring_layout' with k=0.15 (controls distance between islands)
    # iterations=50 helps untangle the separate stars
    pos = nx.spring_layout(subgraph, k=0.15, iterations=50, seed=42)
    
    # 5. Draw the Nodes
    # Draw Smurfs (Blue) - All nodes in subgraph NOT in suspicious_accounts
    smurfs = [n for n in subgraph.nodes() if n not in suspicious_accounts]
    nx.draw_networkx_nodes(subgraph, pos, nodelist=smurfs, node_color='skyblue', node_size=100, alpha=0.6)
    
    # Draw Kingpins (Red)
    nx.draw_networkx_nodes(subgraph, pos, nodelist=suspicious_accounts, node_color='red', node_size=500)
    
    # 6. Draw Edges
    nx.draw_networkx_edges(subgraph, pos, edge_color='gray', alpha=0.3)
    
    # 7. Add Labels (Only for Kingpins to keep it clean)
    labels = {n: n if n in suspicious_accounts else '' for n in subgraph.nodes()}
    # We shorten the label to just the first 4 chars to prevent clutter (e.g. "C660...")
    short_labels = {n: n[:4]+"..." if n in suspicious_accounts else '' for n in subgraph.nodes()}
    
    nx.draw_networkx_labels(subgraph, pos, labels=short_labels, font_size=8, font_color='black', font_weight='bold')

    plt.title(f"The Fraud Constellation: {len(suspicious_accounts)} Laundering Rings Detected", fontsize=16)
    plt.axis('off') # Hide the X/Y axis for a cleaner look
    plt.show()

else:
    print("No smurfing patterns found.")




# --- STEP 4: VISUALIZATION (DUAL-AXIS COMBO CHART) ---
if suspicious_accounts:
    print(f"\n Generating Dual-Axis Analysis for {len(suspicious_accounts)} Suspects...")
    
    # 1. Prepare Data
    plot_data = []
    for kingpin in suspicious_accounts:
        in_edges = G.in_edges(kingpin, data=True)
        count = len(in_edges)
        total_vol = sum([data['weight'] for u, v, data in in_edges])
        
        plot_data.append({
            'Kingpin': kingpin,
            'Total_Amount': total_vol,
            'Tx_Count': count
        })
    
    df_plot = pd.DataFrame(plot_data)
    # Sort by Amount so the chart looks organized
    df_plot = df_plot.sort_values(by='Total_Amount', ascending=False)
    
    # --- PLOTTING ---
    fig, ax1 = plt.subplots(figsize=(12, 7))
    
    # BAR CHART (Total Amount) - Left Axis
    bars = ax1.bar(df_plot['Kingpin'], df_plot['Total_Amount'], color='firebrick', label='Total Money Laundered ($)', alpha=0.8)
    ax1.set_xlabel('Suspicious Account ID', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Total Amount Received ($)', fontsize=12, fontweight='bold', color='firebrick')
    ax1.tick_params(axis='y', labelcolor='firebrick')
    
    # Format Y-axis with commas (e.g. 1,000,000)
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
    plt.xticks(rotation=45, ha='right')

    # LINE CHART (Transaction Count) - Right Axis
    ax2 = ax1.twinx()  # Create a second Y-axis sharing the same X-axis
    line = ax2.plot(df_plot['Kingpin'], df_plot['Tx_Count'], color='navy', marker='o', linewidth=3, markersize=10, label='Transaction Count')
    ax2.set_ylabel('Number of Transactions', fontsize=12, fontweight='bold', color='navy')
    ax2.tick_params(axis='y', labelcolor='navy')
    ax2.set_ylim(0, max(df_plot['Tx_Count']) + 2) # Add some headroom

    # ADD LABELS
    # 1. Amount Labels on Bars
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                 f'${int(height):,}',
                 ha='center', va='bottom', fontsize=10, color='black', fontweight='bold')

    # 2. Count Labels on Line Dots
    for i, txt in enumerate(df_plot['Tx_Count']):
        ax2.annotate(str(txt), (i, df_plot['Tx_Count'].iloc[i]), 
                     textcoords="offset points", xytext=(0,10), ha='center', 
                     fontsize=11, fontweight='bold', color='navy', 
                     bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="navy", alpha=0.9))

    plt.title('Money Laundering Risk Profile: Volume vs. Frequency', fontsize=16, fontweight='bold')
    plt.grid(axis='x', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()

else:
    print("No patterns found.")'''

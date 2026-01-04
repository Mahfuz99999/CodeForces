import sys
import math
from collections import defaultdict, deque
import random
from typing import List, Tuple

def solve():
    input_data = sys.stdin.read().strip().split()
    if not input_data:
        return
    
    it = iter(input_data)
    
    # Read initial parameters
    N = int(next(it))  # Number of Groups
    S = int(next(it))  # Spines per Group
    L = int(next(it))  # Leaves per Group
    
    M = int(next(it))  # Number of OXCs
    K = int(next(it))  # Links per OXC-Spine pair
    P = int(next(it))  # Number of planes
    
    # Calculate derived parameters
    S_per_plane = S // P
    R = N * S_per_plane * K  # Ports per OXC
    
    # Initialize OXC connections (all idle initially)
    oxc_connections = [[-1] * R for _ in range(M)]
    
    # Process 5 queries
    results = []
    for query_idx in range(5):
        Q = int(next(it))  # Number of flows in this query
        
        flows = []
        for _ in range(Q):
            gA = int(next(it))
            leafA = int(next(it))
            gB = int(next(it))
            leafB = int(next(it))
            flows.append((gA, leafA, gB, leafB))
        
        # For tracking flow counts on links
        link_flow_count = defaultdict(int)
        spine_usage = [[0] * S for _ in range(N)]
        oxc_usage = [0] * M
        
        # Store routing paths
        routing_paths = []
        
        # Process each flow
        for flow_idx, (gA, leafA, gB, leafB) in enumerate(flows):
            # Choose spine in source group (round-robin for load balancing)
            spineA = (leafA + flow_idx) % S
            
            # Choose spine in destination group
            spineB = (leafB + flow_idx) % S
            
            # Determine planes
            planeA = spineA % P
            planeB = spineB % P
            
            # Choose OXC: prefer one in the same plane as both spines if possible
            # If not, choose any OXC that minimizes conflicts
            best_oxc = -1
            min_conflict = float('inf')
            
            for oxc in range(M):
                oxc_plane = oxc % P
                # Check if OXC is in a compatible plane
                if oxc_plane == planeA or oxc_plane == planeB:
                    # Estimate conflict for this OXC
                    conflict = oxc_usage[oxc]
                    if conflict < min_conflict:
                        min_conflict = conflict
                        best_oxc = oxc
            
            if best_oxc == -1:
                # Fallback: choose OXC with minimum usage
                best_oxc = min(range(M), key=lambda x: oxc_usage[x])
            
            # Choose link numbers
            kA = flow_idx % K
            kB = (flow_idx + 1) % K
            
            # Update usage counts
            spine_usage[gA][spineA] += 1
            spine_usage[gB][spineB] += 1
            oxc_usage[best_oxc] += 1
            
            # Store routing path
            routing_paths.append((spineA, kA, best_oxc, spineB, kB))
            
            # Update OXC connections
            # Calculate port numbers
            portA = gA * (S_per_plane * K) + (spineA % S_per_plane) * K + kA
            portB = gB * (S_per_plane * K) + (spineB % S_per_plane) * K + kB
            
            # Connect ports in the OXC
            oxc_connections[best_oxc][portA] = portB
            oxc_connections[best_oxc][portB] = portA
        
        # Prepare output for this query
        query_result = []
        
        # Output OXC connections
        for oxc_idx in range(M):
            conn_str = ' '.join(str(x) for x in oxc_connections[oxc_idx])
            query_result.append(conn_str)
        
        # Output routing paths
        for path in routing_paths:
            path_str = ' '.join(str(x) for x in path)
            query_result.append(path_str)
        
        results.append('\n'.join(query_result))
    
    # Output all results
    print('\n'.join(results))

if __name__ == "__main__":
    solve()

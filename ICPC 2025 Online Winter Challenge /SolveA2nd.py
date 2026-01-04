import sys
from collections import defaultdict

def solve():
    data = list(map(int, sys.stdin.read().split()))
    it = iter(data)
    
    # Read network parameters
    N = next(it)  # Number of groups
    S = next(it)  # Spines per group
    L = next(it)  # Leaves per group
    
    M = next(it)  # Number of OXCs
    K = next(it)  # Links per OXC-Spine pair
    P = next(it)  # Number of planes
    
    # Calculate derived parameters
    S_per_plane = S // P
    M_per_plane = M // P
    Up = M_per_plane * K  # Capacity per spine
    R = N * S_per_plane * K  # Ports per OXC
    
    # Store previous OXC configuration (all idle initially)
    prev_oxc_config = [[-1] * R for _ in range(M)]
    
    # Process 5 queries
    output_lines = []
    
    for query_idx in range(5):
        Q = next(it)  # Number of flows in this query
        
        # Read flows
        flows = []
        for _ in range(Q):
            gA = next(it)
            leafA = next(it)
            gB = next(it)
            leafB = next(it)
            flows.append((gA, leafA, gB, leafB))
        
        # Data structures for this query
        leaf_plane_counter = defaultdict(int)  # (g, leaf, plane) -> count
        leaf_spine_counter = defaultdict(int)  # (g, leaf, plane) -> spine index
        
        # For each OXC: track used links per spine
        oxc_used_links = [defaultdict(int) for _ in range(M)]
        
        # Required connections for each OXC
        required_connections = [set() for _ in range(M)]
        
        # Routing paths for each flow
        routing_paths = []
        
        # Process each flow
        for flow_idx, (gA, leafA, gB, leafB) in enumerate(flows):
            # Choose plane for this flow
            p0 = (gA + gB) % P
            chosen_plane = p0
            for offset in range(P):
                p = (p0 + offset) % P
                if (leaf_plane_counter[(gA, leafA, p)] < S_per_plane and 
                    leaf_plane_counter[(gB, leafB, p)] < S_per_plane):
                    chosen_plane = p
                    break
            
            # Update counters
            leaf_plane_counter[(gA, leafA, chosen_plane)] += 1
            leaf_plane_counter[(gB, leafB, chosen_plane)] += 1
            
            # Choose spines
            rel_spineA = leaf_spine_counter[(gA, leafA, chosen_plane)] % S_per_plane
            spineA = chosen_plane * S_per_plane + rel_spineA
            leaf_spine_counter[(gA, leafA, chosen_plane)] += 1
            
            rel_spineB = leaf_spine_counter[(gB, leafB, chosen_plane)] % S_per_plane
            spineB = chosen_plane * S_per_plane + rel_spineB
            leaf_spine_counter[(gB, leafB, chosen_plane)] += 1
            
            # Choose OXC and links
            oxc_list = [m for m in range(M) if m % P == chosen_plane]
            best_oxc = -1
            best_kA = -1
            best_kB = -1
            
            # Try to find OXC with available links
            for oxc in oxc_list:
                usedA = oxc_used_links[oxc].get((gA, spineA), 0)
                usedB = oxc_used_links[oxc].get((gB, spineB), 0)
                
                # Find available link for A
                freeA = -1
                for k in range(K):
                    if not (usedA & (1 << k)):
                        freeA = k
                        break
                
                # Find available link for B
                freeB = -1
                for k in range(K):
                    if not (usedB & (1 << k)):
                        freeB = k
                        break
                
                if freeA != -1 and freeB != -1:
                    best_oxc = oxc
                    best_kA = freeA
                    best_kB = freeB
                    break
            
            # If no OXC has both links free, use first available
            if best_oxc == -1:
                best_oxc = oxc_list[0]
                usedA = oxc_used_links[best_oxc].get((gA, spineA), 0)
                usedB = oxc_used_links[best_oxc].get((gB, spineB), 0)
                
                # Find any available link
                for k in range(K):
                    if not (usedA & (1 << k)):
                        best_kA = k
                        break
                else:
                    best_kA = 0
                    
                for k in range(K):
                    if not (usedB & (1 << k)):
                        best_kB = k
                        break
                else:
                    best_kB = 0
            
            # Mark links as used
            oxc_used_links[best_oxc][(gA, spineA)] = oxc_used_links[best_oxc].get((gA, spineA), 0) | (1 << best_kA)
            oxc_used_links[best_oxc][(gB, spineB)] = oxc_used_links[best_oxc].get((gB, spineB), 0) | (1 << best_kB)
            
            # Calculate port numbers
            portA = gA * (S_per_plane * K) + (spineA % S_per_plane) * K + best_kA
            portB = gB * (S_per_plane * K) + (spineB % S_per_plane) * K + best_kB
            
            # Store required connection
            required_connections[best_oxc].add((portA, portB))
            
            # Store routing path
            routing_paths.append((spineA, best_kA, best_oxc, spineB, best_kB))
        
        # Build new OXC configuration
        new_oxc_config = [[-1] * R for _ in range(M)]
        
        for oxc in range(M):
            # First, establish required connections
            for portA, portB in required_connections[oxc]:
                new_oxc_config[oxc][portA] = portB
                new_oxc_config[oxc][portB] = portA
            
            # Then, reuse old connections if possible
            for port in range(R):
                connected_port = prev_oxc_config[oxc][port]
                if connected_port != -1 and port < connected_port:  # Process each pair once
                    if (new_oxc_config[oxc][port] == -1 and 
                        new_oxc_config[oxc][connected_port] == -1):
                        new_oxc_config[oxc][port] = connected_port
                        new_oxc_config[oxc][connected_port] = port
        
        # Output for this query
        for oxc in range(M):
            output_lines.append(' '.join(str(x) for x in new_oxc_config[oxc]))
        
        for path in routing_paths:
            output_lines.append(' '.join(str(x) for x in path))
        
        # Update previous configuration for next query
        prev_oxc_config = new_oxc_config
    
    # Write all output
    sys.stdout.write('\n'.join(output_lines))

if __name__ == '__main__':
    solve()

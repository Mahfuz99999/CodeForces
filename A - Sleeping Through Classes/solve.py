t = int(input())
for _ in range(t):
    n, k = map(int, input().split())
    s = input().strip()
    awake_until = -1
    sleep_count = 0
    for i in range(n):
        if s[i] == '1':
            awake_until = max(awake_until, i + k)
        if s[i] == '0' and i > awake_until:
            sleep_count += 1
        else:
            # awake: if s[i]=='1' or i <= awake_until
            pass
    print(sleep_count)

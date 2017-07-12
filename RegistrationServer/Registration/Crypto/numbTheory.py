def factor(n):
    if n in [1,-1,0]: return []
    if n<0: n=-n
    F = []
    while n!=1:
        p = trial_division(n)
        e = 1
        n /= p
        while n%p == 0:
            e += 1; n/=p
        F.append(int(p))
    F.sort()
    return F

def trial_division(n):
    if n==1: return 1
    for p in [2,3,5]:
        if n%p == 0: return p
    bound = n
    dif = [6,4,2,4,2,4,6,2]
    m = 7; i = 1
    while m <= bound and m*m <= n:
        if n%m == 0:
            return m
        m += dif[i%8]
        i +=1
    return n

def primitive_root(p,start=2):
    if p==2:return 1
    F = factor(p-1)
    a = start
    while a<p:
        generates = True
        for q in F:
            if pow(a,(p-1)//q,p) == 1:
                generates = False
                break
        if generates: return a
        a +=1
    assert False, "p must be prime"
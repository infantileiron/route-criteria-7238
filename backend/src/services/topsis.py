import math
def topsis(values,directions,weights):
 if len(values)<2 or not weights or any(len(row)!=len(weights) for row in values) or len(directions)!=len(weights):raise ValueError("方案/方向/权重维度不一致，至少两个方案")
 if any(d not in ("cost","benefit") for d in directions):raise ValueError("指标方向须为cost或benefit")
 if any(not math.isfinite(w) or w<=0 for w in weights) or not math.isclose(sum(weights),1,rel_tol=1e-9,abs_tol=1e-9):raise ValueError("权重须为和为1的有限正数")
 if any(not math.isfinite(x) for row in values for x in row):raise ValueError("方案指标须有限")
 k=len(weights);norms=[math.sqrt(math.fsum(row[j]**2 for row in values)) for j in range(k)];issues=[]
 for j in range(k):
  column=[r[j] for r in values]
  if norms[j]==0:issues.append({"criterion_index":j,"reason":"零范数指标"})
  elif math.isclose(max(column),min(column),rel_tol=1e-12,abs_tol=1e-12):issues.append({"criterion_index":j,"reason":"常量或数值上近常量指标"})
 empty={"available":False,"reason":"指标无辨识力，未排除后硬排名，请复核输入并新建指标口径","issues":issues,"norms":norms,"scores":[None]*len(values),"ranks":[None]*len(values),"d_plus":[None]*len(values),"d_minus":[None]*len(values),"ideal_best":[],"ideal_worst":[]}
 if issues:return empty
 weighted=[[row[j]/norms[j]*weights[j] for j in range(k)] for row in values]
 best=[(max if directions[j]=="benefit" else min)(r[j] for r in weighted) for j in range(k)]
 worst=[(min if directions[j]=="benefit" else max)(r[j] for r in weighted) for j in range(k)]
 dplus=[math.sqrt(math.fsum((r[j]-best[j])**2 for j in range(k))) for r in weighted]
 dminus=[math.sqrt(math.fsum((r[j]-worst[j])**2 for j in range(k))) for r in weighted]
 if any(a+b<=0 for a,b in zip(dplus,dminus)):return {**empty,"reason":"理想点距离和为0，不可排名"}
 scores=[b/(a+b) for a,b in zip(dplus,dminus)];order=sorted(range(len(scores)),key=lambda i:-scores[i]);ranks=[0]*len(scores);last=None;rank=0
 for index,i in enumerate(order):
  if last is None or not math.isclose(scores[i],last,rel_tol=1e-12,abs_tol=1e-12):rank=index+1;last=scores[i]
  ranks[i]=rank
 return {"available":True,"reason":"按成本/收益方向向量归一的TOPSIS","issues":[],"norms":norms,"scores":scores,"ranks":ranks,"d_plus":dplus,"d_minus":dminus,"ideal_best":best,"ideal_worst":worst}

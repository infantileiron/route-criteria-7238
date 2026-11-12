from src.services.topsis import topsis
def perturb(values,directions,weights,delta):
 scenarios=[]
 for j in range(len(weights)):
  for sign in (-1,1):
   changed=list(weights);changed[j]*=1+sign*delta;total=sum(changed);changed=[w/total for w in changed]
   result=topsis(values,directions,changed)
   scenarios.append({"criterion_index":j,"multiplier":1+sign*delta,"weights":changed,"scores":result["scores"],"ranks":result["ranks"]})
 return scenarios

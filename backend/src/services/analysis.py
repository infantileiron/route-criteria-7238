import hashlib,json
from src.services.ahp import ahp
from src.services.topsis import topsis
from src.services.sensitivity import perturb
def analyze(dataset,criteria,judgment):
 columns={c["code"]:c for c in dataset.columns};codes=[c["code"] for c in criteria.criteria];directions=[c["direction"] for c in criteria.criteria]
 values=[[a["values"][code] for code in codes] for a in dataset.alternatives]
 weights=ahp(judgment.matrix,judgment.cr_threshold);rank=topsis(values,directions,weights["weights"])
 scenarios=perturb(values,directions,weights["weights"],judgment.perturbation) if rank["available"] else []
 rows=[]
 for i,a in enumerate(dataset.alternatives):
  ranks=[s["ranks"][i] for s in scenarios if s["ranks"][i] is not None]
  rows.append({"alternative_id":a["alternative_id"],"name":a["name"],"values":a["values"],"score":rank["scores"][i],"rank":rank["ranks"][i],"d_plus":rank["d_plus"][i],"d_minus":rank["d_minus"][i],"min_rank":min(ranks) if ranks else None,"max_rank":max(ranks) if ranks else None})
 rows.sort(key=lambda r:r["rank"] if r["rank"] is not None else 10**9)
 return {"ahp":weights,"matrix_original":judgment.matrix,"criteria":[{**columns[c["code"]],"direction":c["direction"]} for c in criteria.criteria],"topsis":rank,"alternatives":rows,"perturbation":judgment.perturbation,"sensitivity":scenarios,"checksum":hashlib.sha256(json.dumps({"alternatives":dataset.alternatives,"criteria":criteria.criteria,"matrix":judgment.matrix},sort_keys=True).encode()).hexdigest(),"assumptions":["全部航段均为模拟备选方案，不提供实际导航、航行安全或调度指令。","AHP采用正互反判断矩阵的主特征向量，RI表为3阶0.58、4阶0.90、5阶1.12、6阶1.24；默认CR阈值0.10仅为声明的判断规则。","原矩阵完整保存；高CR只发出警告，不自动修改判断值或悄悄改权重。","TOPSIS按欧氏列范数归一，成本越小越优、收益越大越优。任何常量/零范数指标或距离退化都明确不可排名，不强行给先后次序。","敏感性为一次只扰动一个权重的正负比例情景，并重新归一化；名次范围不是概率，也不是联合扰动下的稳健保证。"]}

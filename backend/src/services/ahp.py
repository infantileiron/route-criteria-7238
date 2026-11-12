import math
RI={3:.58,4:.90,5:1.12,6:1.24}
def validate_matrix(matrix,n=None):
 n=len(matrix) if n is None else n
 if n not in RI or len(matrix)!=n or any(len(row)!=n for row in matrix):raise ValueError("判断矩阵须为与指标数一致的3至6阶方阵")
 if any(not math.isfinite(v) or v<=0 for row in matrix for v in row):raise ValueError("判断矩阵所有元素须为有限正值")
 for i in range(n):
  for j in range(n):
   v=matrix[i][j]
   if not math.isfinite(v) or v<=0:raise ValueError("判断矩阵所有元素须为有限正值")
   if i==j and not math.isclose(v,1,rel_tol=0,abs_tol=1e-10):raise ValueError("矩阵对角须为1，系统不自动修正原矩阵")
   if not math.isclose(v,1/matrix[j][i],rel_tol=1e-8,abs_tol=1e-10):raise ValueError("判断矩阵须正互反，请手动核查aij与aji，系统不自动改写")
 return n
def ahp(matrix,threshold=.1):
 n=validate_matrix(matrix);largest=max(max(row) for row in matrix);scaled=[[v/largest for v in row] for row in matrix];w=[1/n]*n
 for iteration in range(1,20001):
  product=[math.fsum(scaled[i][j]*w[j] for j in range(n)) for i in range(n)];total=math.fsum(product)
  if total<=0 or not math.isfinite(total):raise ValueError("矩阵数值范围无法稳定计算")
  new=[x/total for x in product]
  if max(abs(a-b) for a,b in zip(new,w))<1e-13:w=new;break
  w=new
 else:raise ValueError("主特征向量迭代未收敛，请检查矩阵极端值")
 product=[math.fsum(matrix[i][j]*w[j] for j in range(n)) for i in range(n)]
 if any(x<=0 for x in w):raise ValueError("主特征向量出现零权重，数值范围过大")
 eigenvalue=math.fsum(product[i]/w[i] for i in range(n))/n
 if not math.isfinite(eigenvalue) or eigenvalue<n-1e-7:raise ValueError("特征值数值异常，未输出权重")
 ci=max(0,(eigenvalue-n)/(n-1));cr=ci/RI[n]
 return {"weights":w,"lambda_max":eigenvalue,"ci":ci,"ri":RI[n],"cr":cr,"threshold":threshold,"cr_warning":cr>threshold,"iterations":iteration,"eigen_residual":max(abs(product[i]-eigenvalue*w[i]) for i in range(n)),"ri_table":RI,"rule":"CR高于所设阈值仅为声明的讨论警告，不是业务安全判定；原矩阵保持不变"}

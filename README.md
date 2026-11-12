# 岩舟航运 · 备选航段多指标权衡

给岩舟11人航运分析组使用的模拟航段比较航册。显式锁定成本/收益方向，保存原始AHP正互反判断矩阵，计算主特征向量、CI/CR和TOPSIS贴近度，再用单权重扰动复核名次范围。仅为多准则讨论，不提供实际导航、航行安全或调度指令。

## 场景与工作日

团队原先用Excel直接加权备选航段，存在权重判断循环矛盾、成本/收益方向混用、名次对权重变化敏感但无记录三项痛点。上游为匿名模拟方案指标；本项目替代口径锁定、权重一致性核查、排序与人工复核；下游为比较报告与CSV归档，不连接真实航道或坐标服务。

09:00分析员登录；09:03核对 yanzhou_alternatives_202611.json 的12方案×4指标；09:08明确费用/时长为成本、准班率/舱位为收益；09:12输入正互反判断矩阵和声明CR阈值0.10；09:15提交Redis后台计算；09:18检查原矩阵、主特征值、CI/CR；09:22比较TOPSIS贴近度和优/劣理想点距离；09:27核查逐指标±10%权重扰动的名次范围；09:32记录方向、警告和模拟场景边界；09:36管理员确认最新复核接受后归档；09:40只读账号下载12行实际计算结果CSV。

|角色|页面|权限和典型动作|
|---|---|---|
|admin|全部|读写、计算、复核、批准归档|
|analyst|备选航段/指标方向/成对判断/排序/权衡复核|创建并排队运行，提交意见；批准归档后端403|
|viewer|全部只读和归档下载|查看原矩阵与排名；写操作后端403|

## 启动与账号

```sh
cp .env.example .env
docker compose up -d --build --wait
docker compose exec -T backend python -m scripts.seed_demo
```

前端 http://localhost:18223 ，后端文档 http://localhost:19223/docs ，MySQL映射17723。账号：admin@yanzhou.demo、analyst@yanzhou.demo、viewer@yanzhou.demo；密码均为 `Route2026!`。开发JWT密钥应在部署前替换。

恰好frontend/backend/worker/db/redis五服务，全部healthcheck；backend等待MySQL/Redis健康，worker再等待backend种子完成，frontend等待backend。数据库、Redis AOF和worker心跳各用命名卷。结束演示执行 `docker compose down -v --remove-orphans`，会清除本项目演示数据。

SEED_DEMO=true自动建表并填充，固定ID/自然键幂等，不重复插入、不覆盖用户修改。seed2304生成12条模拟备选航段和4指标：模拟费用（万元）、时长（小时）、准班率（%）、可用舱位（TEU）。一致性基线权重为.35/.25/.25/.15，另保留循环矛盾矩阵供真实警告演示；一致基线含完成运行、人工复核和归档。不存在真实航行数据。

## 六实体与页面

AlternativeDataset保存方案/指标定义/数值；CriteriaSet固定指标顺序与cost/benefit方向；JudgmentMatrix保存原始矩阵、CR阈值和扰动比例，参数列为MySQL DOUBLE；DecisionRun由Redis独立worker计算并持久化状态与结果；ChoiceReview保存判断依据及高CR警告确认；Report在最新人工复核accepted后由admin批准，run唯一。

六业务页：航册总览、备选航段、指标方向、成对判断、排序与敏感性、权衡复核（含操作留痕）。展示真实权重条、原矩阵、排名表、优/劣理想点距离散点与扰动名次线段。矩阵表显示3位小数，悬停可见完整原值，数据库与运行结果保存完整JSON；没有静默修复矩阵的路径。手机布局保留退出和只读账号功能。

## 两类算法与判断规则

### AHP

输入为3—6阶有限正互反方阵，对角须为1，aij与aji互反（浮点校验容差明确为1e-8相对/1e-10绝对）。错误返回422，不自动补互反值，也不自动修正不一致。幂迭代计算主右特征向量，L1归一到权重和1；用各 `(Aw)_i/w_i` 的均值求lambda_max，输出特征残差和迭代次数。内部缩放仅用于数值运算，原始输入不改写。

`CI=(lambda_max−n)/(n−1)`，仅对浮点负零附近CI取0；`CR=CI/RI`。本项目明确采用RI表：3=.58，4=.90，5=1.12，6=1.24；默认CR阈值.10，允许用户声明.01—.50。高CR是讨论警告，不是安全判定。高CR仍保留结果和原矩阵；若分析员提交接受意见，必须明确勾选已阅读警告，否则后端422。幂迭代不收敛或数值范围异常会保留failed状态，不输出伪权重。

AHP背景见 [Saaty的原始方法论文](https://doi.org/10.1504/IJSSCI.2008.017590)；本项目所声明RI数列亦可对照[公开研究方法表1](https://www.mdpi.com/2073-4441/7/12/6670)。这里的阈值是本应用声明规则，不作为实际业务合规或安全标准。

### TOPSIS与单权重扰动

按欧氏列范数 `sqrt(sum x_ij²)` 归一，乘AHP权重。收益型优点取列最大、劣点最小；成本型相反。到优/劣点分别为欧氏距离D+、D−，贴近度 `C=D−/(D++D−)`，按C降序，数值相同或1e-12近等时保留并列竞争名次。

任一指标为零范数、常量或1e-12数值容差内近常量，就返回available=false，所有分数/名次为null并列出原因；不删除该列后硬排名。全同方案以及理想点距离和0同样不排名。原始数据和方向保留供复核。应用支持3—6指标，独立算法oracle也覆盖两指标手算向量。

敏感性：每一指标权重单独乘(1−delta)和(1+delta)，再把全部权重归一。delta默认.10，可选0—.50；n指标共2n个确定性情景。报告各方案在这些情景下的最小—最大名次与基准名次，不解释为概率或联合扰动下的稳健保证。向量归一与理想点方法可对照[TOPSIS公开研究的经典算法说明](https://informatica.vu.lt/journal/INFORMATICA/article/455/file/pdf)。

### 复现与失败态

固定方案JSON、指标方向/顺序、原矩阵校验码及参数，计算为确定性，无随机评分。输入2—1000方案、3—6指标，所有方案指标集合必须一致，数值须有限且绝对值≤1e12。矩阵正值/对角/互反/维度、参数边界、外键、重名均后端校验。队列和计算失败保留error，可新建运行重试。不可排名是已完成的分析结果，不等于运行失败；CSV明确包含ranking_available与reason，不用0代替null名次。

## 技术、目录和开发

|部分|技术|
|---|---|
|前端|Vue3.5、TypeScript5.7、Vite6、Nginx1.28|
|后端|Python3.11、FastAPI、SQLAlchemy、PyJWT|
|持久化|MySQL8.4，JSON原矩阵和结果，DOUBLE参数|
|队列|Redis7.4 AOF、独立Python worker与心跳|

frontend/src含api/stores/types/components/common/hooks/pages/router/utils/constants；backend/src含routes/controllers/services/models/schemas/middlewares/utils/constants/config；backend/scripts含seed，backend/migrations说明初次模型建表。测试、日志、截图、TESTING/verification在批次test-artifacts/gb-2304，不混入源码。

后端本地安装requirements.txt，配置DATABASE_URL/REDIS_URL/JWT_SECRET，在backend执行`uvicorn src.main:app --reload`，另开`python -m src.worker`。前端`npm ci && npm run dev`，Vite已将/api代理到19223并去前缀；Docker由Nginx同样处理。Vue锁文件复用已验证版本，只JSON修改根包名与根package名，不替换依赖节点；构建使用npm ci。

环境：COMPOSE_PROJECT_NAME=route-criteria；FRONTEND_PORT=18223；BACKEND_PORT=19223；DB_PORT=17723；JWT_SECRET；SEED_DEMO。DATABASE_URL/REDIS_URL在Compose注入；`.env`忽略，`.env.example`供复制。

共享枚举Role、RunStatus、Direction在backend/src/constants/enums.py与frontend/src/constants/enums.ts；controllers/auth.py执行角色规则，worker.py和services/runs.py更新状态，Status组件消费；direction由schemas/criteria.py验证，Criteria.vue输入，WeightBars/Results消费。复核decision在schemas/review.py和前端constants，Reviews页消费。

## 已知边界

CR阈值与RI表明确声明，不能据此判断实际航行安全。TOPSIS允许指标间补偿，排序依赖当前方案集合、归一和权重，不能当作客观最优路线。单权重扰动不是全局敏感性或概率分析；未做联合扰动和随机模拟。JSON表单导入，无CSV解析器。单worker启动恢复queued/running，无分布式租约；初次由SQLAlchemy建表，无生产迁移回滚。Google Fonts使用Noto Sans SC/ZCOOL XiaoWei，不可访问时字体回退。开发密钥和演示账号只供本地模拟。

MIT License。

<script setup lang="ts">
import {ref,computed,watch} from 'vue';
import type {DatasetVersion,MetricSupplement} from '../types/domain';
import type {Workspace} from '../stores/workspace';
import PageHeading from '../components/common/PageHeading.vue';
import Notice from '../components/common/Notice.vue';
import {create} from '../api/datasets';
import {listVersions,listSupplements,submitSupplement} from '../api/supplements';
import {useAsync} from '../hooks/useAsync';
import {number} from '../utils/format';
const props=defineProps<{data:Workspace;canWrite:boolean;refresh:()=>Promise<void>}>();
const selected=ref(''),name=ref(''),source=ref('alternatives.json'),columns=ref('[{"code":"cost","label":"费用","unit":"万元"},{"code":"hours","label":"时长","unit":"小时"},{"code":"capacity","label":"舱位","TEU"}]'),text=ref('');
const versions=ref<DatasetVersion[]>([]),supplements=ref<MetricSupplement[]>([]),viewVersionNo=ref<number|null>(null);
const baseVersion=ref<number>(1),idemKey=ref(''),supplementText=ref(''),replayNotice=ref('');
const ds=computed(()=>props.data.datasets.find(d=>d.id===selected.value)||props.data.datasets[0]);
const viewed=computed(()=>versions.value.find(v=>v.version_no===viewVersionNo.value)||null);
const shownAlternatives=computed(()=>viewed.value?viewed.value.alternatives:(ds.value?.alternatives||[]));
const shownColumns=computed(()=>viewed.value?viewed.value.columns:(ds.value?.columns||[]));
const importForm=useAsync(),batchForm=useAsync();
async function loadVersionData(){
 versions.value=[];supplements.value=[];viewVersionNo.value=null;replayNotice.value='';
 if(!ds.value)return;
 [versions.value,supplements.value]=await Promise.all([listVersions(ds.value.id),listSupplements(ds.value.id)]);
 baseVersion.value=ds.value.current_version;
}
function pickVersion(no:number){viewVersionNo.value=viewVersionNo.value===no?null:no}
async function submit(){await importForm.execute(async()=>{await create({name:name.value,source:source.value,columns:JSON.parse(columns.value),alternatives:JSON.parse(text.value)});name.value='';text.value='';await props.refresh()})}
watch(ds,(d)=>{if(d)loadVersionData()},{immediate:true});
async function submitBatch(){
 replayNotice.value='';
 await batchForm.execute(async()=>{
  const items=JSON.parse(supplementText.value);
  const out=await submitSupplement({dataset_id:ds.value.id,base_version:baseVersion.value,idempotency_key:idemKey.value,items});
  replayNotice.value=out.replayed?'重复投递：未新增版本，返回已受理批次的原始结果。':`已受理并生成 v${out.dataset_version.version_no}，整批原子生效。`;
  supplementText.value='';idemKey.value='';
  await props.refresh();await loadVersionData();
 });
}
</script>
<template><PageHeading code="02 / ALTERNATIVE SEGMENTS" title="方案可比较，先要指标同口径。" description="每个方案保留同一组3—6项有限数值指标。费用补报按航段编号批量受理，产生不可变版本；重复投递不新增版本，基于过期版本拒绝受理。真实航道、坐标与导航指令不在本项目中。"/>
<section class="paper"><div class="section-heading"><h2>模拟备选航段</h2><select aria-label="选择方案集" :value="ds?.id" @change="selected=($event.target as HTMLSelectElement).value;loadVersionData()"><option v-for="d in data.datasets" :key="d.id" :value="d.id">{{d.name}}</option></select></div>
<template v-if="ds"><div class="data-caption"><b>{{shownAlternatives.length}}个方案</b><span>{{shownColumns.length}}项指标</span><span>{{ds.source}}</span><span>当前版本 v{{ds.current_version}}</span><span v-if="viewed" class="version-tag">查看中：v{{viewed.version_no}}（历史快照）</span></div>
<div class="version-chips" v-if="versions.length"><span>版本：</span><button v-for="v in versions" :key="v.id" type="button" class="chip" :class="{active:viewVersionNo===v.version_no}" @click="pickVersion(v.version_no)">v{{v.version_no}}<small>{{v.created_at.slice(11,19)}}</small></button></div>
<div class="table-scroll"><table><thead><tr><th>方案</th><th v-for="c in shownColumns" :key="c.code">{{c.label}}<small>{{c.unit}}</small></th></tr></thead><tbody><tr v-for="a in shownAlternatives" :key="a.alternative_id"><td><b>{{a.name}}</b><small>{{a.alternative_id}}</small></td><td v-for="c in shownColumns" :key="c.code">{{number(a.values[c.code],2)}}</td></tr></tbody></table></div>
<p class="caption" v-if="viewed">{{viewed.change_note}} · {{viewed.created_by}} · {{viewed.created_at}}</p>
<div class="supplement-log" v-if="supplements.length"><h3>补报批次留痕</h3><table><thead><tr><th>批次</th><th>基于版本</th><th>产生版本</th><th>航段数</th><th>提交人</th><th>时间</th></tr></thead><tbody><tr v-for="s in supplements" :key="s.id"><td><small>{{s.idempotency_key}}</small></td><td>v{{s.base_version}}</td><td>v{{s.new_version}}</td><td>{{s.items.length}}</td><td>{{s.author}}</td><td>{{s.created_at.slice(11,19)}}</td></tr></tbody></table></div>
</template>
<Notice v-else>请导入至少两个方案和3—6项指标，再明确成本或收益方向。</Notice></section>
<section class="paper" v-if="canWrite&&ds"><h2>按航段编号批量补报指标</h2><p class="caption">整批规则：任一航段未知、指标缺失或存在未定义指标、数值非有限值，整批不生效。base_version 须等于当前最新版本，否则拒绝受理；相同幂等键或相同内容重复投递只回放结果，不新增版本。</p>
<form class="grid-form" @submit.prevent="submitBatch"><label>基于版本 base_version<input required type="number" min="1" v-model.number="baseVersion"/></label><label class="wide">幂等键 idempotency_key（8—120字符，重复投递用）<input required minlength="8" maxlength="120" v-model="idemKey" placeholder="例如 cost-reattach-20261112-01"/></label><label class="wide">补报JSON数组（每航段须给全部指标）<textarea rows="5" required v-model="supplementText" placeholder='[{"alternative_id":"YZ-01","values":{"cost":30.5,"hours":24,"punctuality":90,"capacity":150}}, …]'/></label><Notice v-if="batchForm.error.value" error>{{batchForm.error.value}}</Notice><Notice v-else-if="replayNotice">{{replayNotice}}</Notice><button :disabled="batchForm.busy.value">核查并整批受理</button></form></section>
<section class="paper" v-if="canWrite"><h2>导入模拟方案</h2><form class="grid-form" @submit.prevent="submit"><label>方案集名称<input required minlength="2" v-model="name"/></label><label>来源文件名<input v-model="source"/></label><label class="wide">指标定义JSON<textarea rows="3" required v-model="columns"/></label><label class="wide">方案JSON数组<textarea rows="4" required v-model="text" placeholder='[{"alternative_id":"YZ-X1","name":"模拟方案X1","values":{"cost":20,"hours":24,"capacity":150}}, …]'/></label><Notice v-if="importForm.error.value" error>{{importForm.error.value}}</Notice><button :disabled="importForm.busy.value">核查并导入</button></form></section></template>

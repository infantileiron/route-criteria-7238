export const number=(v:number|null|undefined,d=3)=>v==null?'不可排名':v.toFixed(d);
export const percent=(v:number|null|undefined)=>v==null?'—':(v*100).toFixed(1)+'%';
export const date=(v:string)=>new Date(v).toLocaleString('zh-CN',{hour12:false});

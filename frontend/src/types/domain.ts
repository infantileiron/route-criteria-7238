export interface User{email:string;role:string}
export interface Column{code:string;label:string;unit:string}
export interface Alternative{alternative_id:string;name:string;values:Record<string,number>}
export interface Dataset{id:string;name:string;source:string;columns:Column[];alternatives:Alternative[];current_version:number;created_at:string}
export interface DatasetVersion{id:string;dataset_id:string;version_no:number;alternatives:Alternative[];columns:Column[];change_note:string;supplement_id:string;created_by:string;created_at:string}
export interface MetricSupplement{id:string;idempotency_key:string;dataset_id:string;base_version:number;items:{alternative_id:string;values:Record<string,number>}[];content_fingerprint:string;status:string;dataset_version_id:string;new_version:number;author:string;created_at:string}
export interface Criterion{code:string;direction:'cost'|'benefit'}
export interface Criteria{id:string;name:string;dataset_id:string;criteria:Criterion[];created_at:string}
export interface Judgment{id:string;name:string;criteria_set_id:string;matrix:number[][];cr_threshold:number;perturbation:number;created_at:string}
export interface Ranking extends Alternative{score:number|null;rank:number|null;d_plus:number|null;d_minus:number|null;min_rank:number|null;max_rank:number|null}
export interface CriterionMeta extends Column{direction:'cost'|'benefit'}
export interface Result{ahp:{weights:number[];lambda_max:number;ci:number;ri:number;cr:number;threshold:number;cr_warning:boolean;iterations:number;eigen_residual:number;ri_table:Record<string,number>;rule:string};matrix_original:number[][];criteria:CriterionMeta[];topsis:{available:boolean;reason:string;issues:{criterion_index:number;reason:string}[];norms:number[];scores:(number|null)[];ranks:(number|null)[];d_plus:(number|null)[];d_minus:(number|null)[];ideal_best:number[];ideal_worst:number[]};alternatives:Ranking[];perturbation:number;sensitivity:{criterion_index:number;multiplier:number;weights:number[];scores:(number|null)[];ranks:(number|null)[]}[];version:{dataset_version_id:string;version_no:number|null;dataset_id:string;frozen_at:string};checksum:string;assumptions:string[]}
export interface Run{id:string;judgment_id:string;dataset_version_id:string;status:string;result:Result;error:string;created_at:string}
export interface Review{id:string;run_id:string;note:string;decision:string;accept_warning:boolean;author:string;created_at:string}
export interface Report{id:string;run_id:string;title:string;published_by:string;created_at:string}
export interface Audit{id:string;actor:string;action:string;status:number;created_at:string}

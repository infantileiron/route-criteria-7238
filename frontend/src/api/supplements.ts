import {request,post} from './client';
import type {DatasetVersion,MetricSupplement} from '../types/domain';
export const listVersions=(datasetId:string)=>request<DatasetVersion[]>(`/datasets/${datasetId}/versions`);
export const getVersion=(datasetId:string,versionNo:number)=>request<DatasetVersion>(`/datasets/${datasetId}/versions/${versionNo}`);
export const listSupplements=(datasetId:string)=>request<MetricSupplement[]>(`/datasets/${datasetId}/supplements`);
export const submitSupplement=(data:unknown)=>post<{replayed:boolean;supplement:MetricSupplement;dataset_version:DatasetVersion}>('/datasets/supplements',data);

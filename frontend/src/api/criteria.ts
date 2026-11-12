import {request,post} from './client';import type {Criteria} from '../types/domain';
export const list=()=>request<Criteria[]>('/criteria');
export const create=(data:unknown)=>post<Criteria>('/criteria',data);

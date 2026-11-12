import {request,post} from './client';import type {Judgment} from '../types/domain';
export const list=()=>request<Judgment[]>('/judgments');
export const create=(data:unknown)=>post<Judgment>('/judgments',data);

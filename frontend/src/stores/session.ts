import type {User} from '../types/domain';
export function readUser():User|null{try{return JSON.parse(localStorage.getItem('route-user')||'null')}catch{return null}}
export function save(token:string,user:User){localStorage.setItem('route-token',token);localStorage.setItem('route-user',JSON.stringify(user))}
export function clear(){localStorage.removeItem('route-token');localStorage.removeItem('route-user')}

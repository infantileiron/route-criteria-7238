import * as datasets from '../api/datasets';import * as criteria from '../api/criteria';import * as judgments from '../api/judgments';import * as runs from '../api/runs';import * as reviews from '../api/reviews';import * as reports from '../api/reports';import * as audit from '../api/audit';
export async function load(){const [d,c,j,r,v,p,a]=await Promise.all([datasets.list(),criteria.list(),judgments.list(),runs.list(),reviews.list(),reports.list(),audit.list()]);return {datasets:d,criteria:c,judgments:j,runs:r,reviews:v,reports:p,audit:a}}
export type Workspace=Awaited<ReturnType<typeof load>>;
export const emptyWorkspace=():Workspace=>({datasets:[],criteria:[],judgments:[],runs:[],reviews:[],reports:[],audit:[]});

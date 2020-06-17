import { Moment } from './moment';

export interface Timeline {
    Moments: Moment[],
    PagingToken: string
}
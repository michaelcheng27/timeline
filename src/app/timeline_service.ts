import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

import { Observable, of } from 'rxjs';

import { Timeline } from './timeline';


@Injectable({ providedIn: 'root' })
export class TimelineService {

  private timelineUrl = "https://m224e6853e.execute-api.us-west-2.amazonaws.com/dev/timeline";  // URL to web api
  httpOptions = {
    headers: new HttpHeaders({
      'Content-Type': 'application/json'
    })
  };

  constructor(
    private http: HttpClient) {
  }

  getTimeline(pagingToken: string): Observable<Timeline> {
    return this.http.post<Timeline>(this.timelineUrl, { "PagingToken": pagingToken }, this.httpOptions);
  }
}

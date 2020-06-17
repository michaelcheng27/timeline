import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

import { Observable, of } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';

import { Moment } from './moment';
import { MessageService } from './message.service';


@Injectable({ providedIn: 'root' })
export class TimelineService {

  private momentsUrl = 'https://6ff5sp51ha.execute-api.us-west-2.amazonaws.com/dev/timeline';  // URL to web api
  private paingToken = null;
  httpOptions = {
    headers: new HttpHeaders({
      'Content-Type': 'application/json', "Access-Control-Allow-Headers": "Content-Type",
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
    })
  };

  constructor(
    private http: HttpClient) {
  }

  getMoments(): Observable<Moment[]> {
    return this.http.post<Moment[]>(this.momentsUrl, {}, this.httpOptions);
  }
}

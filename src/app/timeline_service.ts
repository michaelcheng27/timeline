import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

import { Observable, of } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';

import { Moment } from './moment';
import { MessageService } from './message.service';


@Injectable({ providedIn: 'root' })
export class TimelineService {

  private momentsUrl = "https://m224e6853e.execute-api.us-west-2.amazonaws.com/dev/timeline";  // URL to web api
  private paingToken = null;
  httpOptions = {
    headers: new HttpHeaders({
      'Content-Type': 'application/json'
    })
  };

  constructor(
    private http: HttpClient) {
  }

  getMoments(): Observable<Moment[]> {
    console.log(`this.httpOptions = ${this.httpOptions}`);
    return this.http.post<Moment[]>(this.momentsUrl, {}, this.httpOptions);
  }
}

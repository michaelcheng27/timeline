import { Component, OnInit } from '@angular/core';
import { Moment } from '../moment';
import { TimelineService } from '../timeline_service';

@Component({
  selector: 'app-grid',
  templateUrl: './grid.component.html',
  styleUrls: ['./grid.component.scss']
})
export class GridComponent implements OnInit {
  moments: Moment[] = [];
  throttle = 300;
  scrollDistance = 4;
  scrollUpDistance = 2;
  nextPagingToken = null;

  constructor(private timelineService: TimelineService) { }

  ngOnInit() {
    console.log(`grid init`);
    this.getTimeline();
  }

  getTimeline(): void {
    this.timelineService.getTimeline(this.nextPagingToken)
      .subscribe(timeline => {
        console.log(`timeline = ${JSON.stringify(timeline)}`);
        this.nextPagingToken = timeline.PagingToken;
        this.moments = this.moments.concat(timeline.Moments);
        console.log(`moment = ${JSON.stringify(this.moments)}`);
      }
      );
  }


  onScrollDown(ev) {
    console.log('scrolled down!!', ev);
    this.getTimeline();
  }
}

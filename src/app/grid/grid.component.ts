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
  initial = true;

  constructor(private timelineService: TimelineService) { }

  ngOnInit() {
    this.getTimeline();
  }

  getTimeline(): void {
    this.timelineService.getTimeline(this.nextPagingToken)
      .subscribe(timeline => {
        this.nextPagingToken = timeline.PagingToken;
        this.moments = this.moments.concat(timeline.Moments);
      }
      );
  }


  onScrollDown(ev) {
    console.log('scrolled down!!', ev);
    if (this.nextPagingToken) {
      this.getTimeline();
    }
  }
}

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

  constructor(private timelineService: TimelineService) { }

  ngOnInit() {
    console.log(`grid init`);
    this.getMoments();
  }

  getMoments(): void {
    this.timelineService.getMoments()
      .subscribe(moments => {
        this.moments = this.moments.concat(moments);
        console.log(`moment = ${JSON.stringify(this.moments)}`);
      }
      );
  }


  onScrollDown(ev) {
    console.log('scrolled down!!', ev);
    this.getMoments();
  }
}

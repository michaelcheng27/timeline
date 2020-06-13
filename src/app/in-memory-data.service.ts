import { Injectable } from '@angular/core';
import { InMemoryDbService } from 'angular-in-memory-web-api';
import { Hero } from './hero';

@Injectable({
  providedIn: 'root',
})
export class InMemoryDataService implements InMemoryDbService {
  createDb() {
    const heroes = [
      { id: 11, name: 'Dr Nice', s3Handle: "https://timeline-photo-test.s3-us-west-2.amazonaws.com/20180403_101554.jpg" },
      { id: 12, name: 'Narco', s3Handle: "https://timeline-photo-test.s3-us-west-2.amazonaws.com/20180403_101607.jpg" },
      { id: 13, name: 'Bombasto', s3Handle: "https://timeline-photo-test.s3-us-west-2.amazonaws.com/20180403_123312.jpg" },
      { id: 14, name: 'Celeritas', s3Handle: "https://timeline-photo-test.s3-us-west-2.amazonaws.com/20180403_130829.jpg" },
      { id: 15, name: 'Magneta', s3Handle: "https://timeline-photo-test.s3-us-west-2.amazonaws.com/20180403_130833.jpg" },
      { id: 16, name: 'RubberMan', s3Handle: "https://timeline-photo-test.s3-us-west-2.amazonaws.com/20180403_130840.jpg" },
      { id: 17, name: 'Dynama', s3Handle: "https://timeline-photo-test.s3-us-west-2.amazonaws.com/20180403_131504.jpg" },
      { id: 18, name: 'Dr IQ', s3Handle: "https://timeline-photo-test.s3-us-west-2.amazonaws.com/20180403_132200.jpg" },
      { id: 19, name: 'Magma', s3Handle: "https://timeline-photo-test.s3-us-west-2.amazonaws.com/20180403_132541.jpg" },
      { id: 20, name: 'Tornado', s3Handle: "https://timeline-photo-test.s3-us-west-2.amazonaws.com/20180403_133305.jpg" }
    ];
    return { heroes };
  }

  // Overrides the genId method to ensure that a hero always has an id.
  // If the heroes array is empty,
  // the method below returns the initial number (11).
  // if the heroes array is not empty, the method below returns the highest
  // hero id + 1.
  genId(heroes: Hero[]): number {
    return heroes.length > 0 ? Math.max(...heroes.map(hero => hero.id)) + 1 : 11;
  }
}

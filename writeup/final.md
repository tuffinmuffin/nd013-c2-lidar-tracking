# Final Writeup

## Step 1 - filter.py (kalman filter )
###
This section was to write an kalaman filter for use with the lidar data. This extended the excerises from 2d to 3d. The larges issue was determining the Q value. A post in the mentor help provided the correct matrix. However the matrix was supposed to be provided in the Hints sections of the project. There is a "TODO" there.

The final RMSE was 0.32 which was within the project reqs.

<img title="Figure 1" alt="Alt text" src="images/F_S1_RMSE_Plot.png"> Figure 1 Final RMSE for part 1.

## Step 2 - trackmanagment.py (track managment)
###
This section was to manage track states from initial creation to death. The first step was to initilize the track detected location and set unknown velocities.

After that the track would be delete if not detected again, moved to tentative state if detected again, or moved to confirmed if detected over a treshold value.
At each step the track can die and get removed if it is no longer tracked. FOr the case of confirmed tracks if its esitamted location grew too large it is removed.

A final RMSE was 0.78.
<img title="Figure 2" alt="Alt text" src="images/F_S2_RMSE_Plot.png"> Figure 2 Final RMSE for part 2.

## Step 3 - association.py (track /meas association)
###
This section was to associate measurements to tracks. This worked very well.

<img title="Figure 3" alt="Alt text" src="images/F_S3_RMSE_Plot.png"> Figure 3 Final RMSE for part 3.

<img title="Figure 4" alt="Alt text" src="images/F_S3_Track0_Plot.png"> Figure 4 Early tracks before passing confirmed threshold

<img title="Figure 5" alt="Alt text" src="images/F_S3_Track1_Plot.png"> Figure 5 Tracks of 3 confirmed positions after one moved in from rear

<img title="Figure 6" alt="Alt text" src="images/F_S3_Track2_Plot.png"> Figure 6 Track showing false detection of bush. Has not been moved to tentative

<img title="Figure 7" alt="Alt text" src="images/F_S3_Track2_Plot.png"> Figure 7 Track showing false detection of bush. Has been moved to tentative after several detections but never enough to move it to a false confirmed track
<img title="Figure 8" alt="Alt text" src="images/F_S3_Track3_Plot.png"> Figure 8 New track has been detected outside camera FOV. It has not been confirmed but is tentative. See Figure 5 for later confirmation

## Step 4 - measurements.py (Adding Camera fusion)

###
This section was to add camera support to augment the lidar. This allows finer tracking and quicker confirmation and removal of tracks.


<img title="Figure 9" alt="Alt text" src="images/F_S4_RMSE_Plot.png"> Figure 9 Final RMSE for part 4. Note that track 3 was in view but out of range most of the data set for lidar but there was a period it was close enough in the lidar to get picked up and kept being tracked by camera. This was not in the example pictures at end of part 4. THis may be due to different track deletion decisions.


Final project Video

<iframe width="560" height="315" src="https://www.youtube.com/embed/kFlF-6-usT0" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>


Final video embedded below

[![Final Tracking with Sensor Fusion](http://img.youtube.com/vi/kFlF-6-usT0/0.jpg)](https://youtu.be/kFlF-6-usT0 "Final Tracking with Sensor Fusion")



## Write up Questions

1. Write a short recap of the four tracking steps and what you implemented there (filter, track management, association, camera fusion). Which results did you achieve? Which part of the project was most difficult for you to complete, and why?

Details of each step are above.

Data flow
* New detections are captured by a sensor.
* The detections are associated by the association.py file to tracks in trackmanagment.py
* detections without an assosication are then added as a new track.
* exsisting tracks are location is updated via predict in the filter.py and then updated based on assicated data with update.
* If tracks are not in the new detections the track managment will note this and the kalman filter uncertainy will increase.
* If the tracks are detected the managment will note this and the kalman filter will increase their rating.
* Finally tracks that fall outside of certain metrics will be culled.

The hardest part turned out to be the association step. This was due to a bug in the track management checking if the track uncertainty was too great and this took me a long time to track down. FOllowing that until the provided covience matrics for 3d was found on the project board this was giving me math difficulties to make sure it was updated correctly.

2. Do you see any benefits in camera-lidar fusion compared to lidar-only tracking (in theory and in your concrete results)?
Yes. The results with camera augmentation improved the tracks and a few ghosts tracks that never were confirmed were culled much sooner. This followed the theory of how sensor fusion should work.

3. Which challenges will a sensor fusion system face in real-life scenarios? Did you see any of these challenges in the project?
AI detecting false positives due to various factors. In the project this was caused often by bushes. Then also detecting objets that are not part of the road (cars were found by AI behind fences).

Weather and dirt would be another factor. However this did not come into play for this.

According to some "cyber security" someone spoffing a car with a cardboard cut out or throwing dirt at the windsheild. They can be silly by bad actors should be considered. Sensor fusion could help with this. Radar on a paper cutout or one sensor being occulded or fooled may not affect other sensors.


4. Can you think of ways to improve your tracking results in the future?

The first one that comes to mind would be adding more sensors from the car to the fusion. We have multiple cameras with diffrent FOVs and we have other lidars and a radar that can be used to add extra data to the system.

THe AI detection could be improved. THe provided one seemed fairly solid for this type of class but the state of the art is better.



# recognize-Music-note-from-sheet
This is a project that read Sheet music and mark place where potential a music Note.

The main approach is simple
First i find every single bar in the music sheet, by changing the image to black and white then using openCV morphologyEx to find horizontal line.
  i gave it 5 interation for more precision

Then cut it out into one single image with the hieght is 9 time the music length

from then, i make it into two categories:
  + those note in middle two line
  + those note lay on the line

So we will work with note in middle of two line first:
  we have two type of note, a note is black blob, this is kinda easy to handle, we just make sure we go through a long line of black pixel, and find center of it
  About the white note, i will save the black pixel that i went through when finding the black note, but not the a black note, i may be a note tail, or the white note.
  After saving all of it, i find two consecutively elements in the list, and find distance between them, if they are smaller than threshold, it will be a white note.
  
And about the those note lay on one line:
  This is kinda tricky , instead of finding using one line to check, i choose 3, because if we use 1, it will be full of black pixel because of the line.
  And follow the idea above, first find the black if we go through a long line of black pixel (here is 3)
  Then find the White note in the list we have save

After finding, we will return the location of every note, but here i just draw a small circle on each note to present the location


Some footage of the result:
![Screenshot 2022-07-27 154830](https://user-images.githubusercontent.com/102981020/181204499-b3f359f8-3eb0-49c6-8ba4-eb818c7810f1.png)

And beside, i also code to find the location of bass clef and trebel clef, in order to skip it when reading the bar

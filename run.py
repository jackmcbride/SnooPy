import cv2, time, pandas
from datetime import datetime

#First frame of the video e.g. the frame that every subsequent frame is compared against
first_frame=None
#List of status updates from the video feed
status_list=[None, None]
#Pandas data frame for collecting activity timestamps
df=pandas.DataFrame(columns=["Start", "End"])
#Setup camera
video=cv2.VideoCapture(0)
#Pause briefly to allow for a clear image to be taken
time.sleep(0.5)
#List for timestamps
times = []
#Set current time 
current_time = datetime.now()

while True:
    #Measure time delta
    time_delta=datetime.now() - current_time
    #Read frames from the video feed
    check, frame=video.read()
    #Initial status is 0, for no activity
    status=0
    #Convert colour frame to gray scale
    gray=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #Smooth frame using gaussian blur
    gray=cv2.GaussianBlur(gray, (21, 21), 0)

    #Check if first frame has been set, or if the time delta of 15 seconds has been exceeded.
    if first_frame is None or (time_delta.total_seconds() >= 15):
        #Update current time
        current_time = datetime.now()
        #Update first frame
        first_frame=gray
        continue

    #Calculate any differences between the first frame, and the current frame of the feed
    delta_frame=cv2.absdiff(first_frame, gray)
    #Thresholding. If a given pixel has a threshold value of 30, turn it white to highlight the change in the video feed. Assign the second output (which is the thresholded image) to thresh_frame
    thresh_frame=cv2.threshold(delta_frame, 25, 255, cv2.THRESH_BINARY)[1]
    #Dilate the threshold frame - highlight the deltas between the frames
    thresh_frame=cv2.dilate(thresh_frame, None, iterations=2)

    #In OpenCV, finding contours is like finding white object from black background
    #Find the contours of the highlighted delta between the frames
    (_,contours,_)=cv2.findContours(thresh_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        #Adjust this value for detecting objects of differing sizes
        if cv2.contourArea(contour) < 1000:
            continue
        #Significant activity detected. Change status to 1
        status=1
        #Get the coordinates of the bounding rectangle around the contour
        (x, y, w, h)=cv2.boundingRect(contour)
        #Draw the rectangle. (x,y) is the top left corner, and (x+w, y+h) is the bottom right
        cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 3)
    
    #Add the status to the list
    status_list.append(status)
    #Remove all previous statuses beside the most recent two
    #We do this because we're only interested in detecting sudden changes, so we check the most recent two statuses
    status_list=status_list[-2:]

    #If the status changes, append the timestamp, Take a screenshot
    if status_list[0] != status_list[1]:
        #Take timestamp
        timestamp=datetime.now()
        #Take screenshot if something appears
        if status_list[1] == 1:
            time.sleep(2)
            check, image=video.read()
            #Save image to images folder
            cv2.imwrite('Images/' + str(timestamp) + ".jpg", image)
        #Append the current timestamp to the list of times
        times.append(timestamp)
    
    #Create a colour window with SnooPy title
    cv2.imshow("SnooPy", frame)
    cv2.moveWindow("SnooPy", 10, 10)

    #Listen to key presses
    key=cv2.waitKey(1)

    #If the listener detects q, quit the program and append latest datetime if status has changed
    if key == ord('q'):
        if status==1:
            times.append(datetime.now())
        break

for i in range(0, len(times), 2):
    df=df.append({"Start" : times[i], "End" : times[i+1]}, ignore_index=True)

#Convert dataframe to csv file
df.to_csv("Times.csv")

video.release()
cv2.destroyAllWindows()
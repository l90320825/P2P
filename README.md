# P2P Decentralized Network with BitTorrent Protocol

Please use this README file to provide the following documentation for this project:

| Student Name  | Student ID | Github Usernames |
| :-----------  | :--------: | :--------------- |
| Chun Tat Chan | 916770782  | chuntatchan      |
| John To       | 917507752  | l90320825        |

### General description of the project (a few sentences)
<p>
	In this programming project, we, Chun Tat Chan and John To, implemented a decentralized peer-to-peer network architecture (P2P), including the basic implementation of the BitTorrent protocol (BTP). The purpose of this programming project was the gain an in depth understanding of the process behind the archiecture of a decentralized peer-to-peer network as the cumulation of all the material we learned in class.
</p>

##### If you used external Python modules/libraries. Provide a requirements.txt file
* No external python modules/libraries used.

##### Python version and compatibility issues (if any)
* Shouldn't have compatibility issues, but just in case we used Python version: 3.8.2 (John) and 3.8.3 (Chun Tat).

##### Clear and specific instructions about how to run your project. If your project does not run or contains errors, you'll get a 0 in the project no matter how much work you put on it. So, test your code properly and make sure that it runs without errors.
<ol>
	<li> Clone the repo using this command: `git clone https://github.com/l90320825/P2P.git` </li>
	<li> After cloning the repo, run: `pip install requirements.txt` to install all the missing modules/libraries. </li>
	<li> Please run peer.py using this command: `python peer.py`. First run two seeders in different command prompts using different SERVER_IP. You can adjust SERVER_IP in peer.py on line 36 and change role=SEEDER on line 53. Lastly run a peer in a different command prompt using a different SERVER_IP on line 36 and change role=PEER on line 53.
	</li>
	<li> With this, you should now see the peer's tracker finding seeders and starting the download process. </li>
</ol>

##### A few sentences about all the challenges you found during the implementation of this project and how you overcame them. Please be honest here.
* In the beginning, we felt fairly confident about this project as we felt like we conceptually understood the project. However, when it came to coding it using python; many implementation details went over our heads. Some of the challenges we faced during this project were figuring out how to implement multiple clients to download pieces from multiple servers. Despite receiving lots of help on Slack and in Class, the implementation details were still fairly difficult to grasp and took a lot of time. Threading clients that preform the file write and read were quite challenging as well. Communication between uploader and downloader took lots of time as well. The tracker from the lab was not preforming its function, thus we had to spend some time fixing it and having it properly update the DHT routing tables. Overall, it was just a lot of debugging through writing proper print statements everywhere and finding out which lines of code are causing the code to fail and fixing them. After implementing everything, we have now gained an in depth understanding of how a decentralized peer-to-peer network functions.

## Note that failure to provide the above docs will result in a 30% deduction in your final grade for this project. 

# Project Guidelines 

A document with detailed guidelines (P2P.pdf) to implement this project can be found in the 'help' folder and posted on iLearn

# The Tit-For-Tat Transfer Protocol

Your P2P program must implement the Tit-For-Tat transfer protocol. This protocol only allows a peer to be downloading/uploading
data from/to a maximum of four other peers or seeders; the top three with maximum upload rate, and a a random chosen peer. 
The goal of connecting to a random peer/seeder is to increment the participation of rarest peers in the network. This situation
must be reevaluated every 30 seconds because peers disconnect and connect all the time during the sharing process. 

See P2P.pdf for more info about how to compute temporal upload and downloads rates. 

# HTPBS for Showing Pieces Downloading/Uploading Progresses 

In order to show the progress of the pieces your peer is uploading or downloading to/from the P2P network, you can use the htpbs (horizontal threaded progress bars) library. This library tracks the progress of threaded jobs and is customizable to for your project. Exactly what you need for this project!. For more info about this library: https://pypi.org/project/htpbs/

### Install with PIP

```python 
pip3 install htpbs
```

# Grading Rubric: 

1. This project is worth 25% of your final grade, and will be graded using a point scale where the 
maximum possible grade is 100 points. For example, a grade of 80/100 in this project will be converted to 
0.80 * 25% = 20% of 25%

2. The project has one extra-credit part: scaling the capability of the project to support sharing files in 
more than two swarms (5%). 

3. If the peer runs without errors, it connects to at least 2 peers that are already connected to the 
network, and you provided all the docs requested at the beginning of this README page then (+50)

4. If any of the requirements from step 3 is missing, I will apply a grade (at my discretion) depending on how much 
work the student has done in the project. However, this grade will be way below the 50 points threshold. 
Please make sure to test your project properly before submission to avoid this situation. 

5. For each part of the program that is correctly implemented (after step 3 is successfully executed), then (+10) points
Note that I will give also partial credit if there are parts that are not fully implemented but have some work done. 
Parts of the program are: (1) the torrent file is scanned correctly, (2) the tracker works as expected, (3) the 
Tit-for-Tac protocol implemented correctly (4) the blocks
and pieces are downloaded/uploaded/saved as expected and messages are correctly sent between peers, and
(5) real time progress of your program while downloading and uploading pieces is shown on screen. 

7. Late submissions won't be accepted since the due date for this project is set to the last day of class.

# Submission Guidelines 

This project is due the last day of the semester. After you complete and test your project, go to the assignments table, 
located in the main README file of this repository, and set this project to "done" or "completed". 
Failure to do that will result in your project not being graded because I will assume that the project 
hasn't been submitted. No exceptions here!!!. 

Good luck!!!

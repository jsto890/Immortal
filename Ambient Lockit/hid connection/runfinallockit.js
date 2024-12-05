var ACNLockitLib = require('./ambient');

var ACNLockit = new ACNLockitLib();             //Create new ACNLockit Object

ACNLockit.setFrameFormat(3);            //Set Frame Rate to 59.94

/*
Frame Formats:
0: "23.976",
1: "24",
2: "25",
3: "29.97",
4: "30",
5: "29.97 drop",
6: "30 drop",
7: "47.96",
8: "48",
9: "50",
10: "59.94",
11: "60"
*/

//ACNLockit.getFrameFormat();              //Get Frame Rate and Return in Console.log
//ACNLockit.getSync();                             //Get Sync and Return in Console.log

//ACNLockit.getMisc();

//ACNLockit.setSyncFormat(1,4,6);
//ACNLockit.reset();
//ACNLockit.getACNChannel();
//ACNLockit.setACNChannel(12);
ACNLockit.LTCCallback(1);
ACNLockit.closedevice()
//ACNLockit.resetTime();                          //Reset TC

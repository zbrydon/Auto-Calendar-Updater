const { google } = require('googleapis');
const newShifts = require('./newShifts.json');
const { spawnSync } = require('child_process');
const { OAuth2 } = google.auth;
require('dotenv').config()




const clientId = process.env.CLIENT_ID;
const clientSecret = process.env.CLIENT_SECRET;
const refreshToken = process.env.REFRESH_TOKEN;
const calendarId = process.env.CALENDAR_ID;

const oAuth2Client = new OAuth2(clientId, clientSecret)

oAuth2Client.setCredentials({ refresh_token: refreshToken })

const calendar = google.calendar({ version: 'v3', auth: oAuth2Client })

const eventStartTime = new Date();
eventStartTime.setDate(eventStartTime.getDay() + 2)

const eventEndTime = new Date();
eventEndTime.setDate(eventEndTime.getDay() + 2);
eventEndTime.setMinutes(eventEndTime.getMinutes() + 45);

function runScript() {
    let py = spawnSync('py', ['./app.py']);
    return py;
}

function convertDateTime(date, time) {
    let offset = new Date().getTimezoneOffset() / -60;
    let dateTime = date + 'T' + time + ':00+' + offset + ':00';
    return dateTime;
}

function getTime() {
    let today = new Date();
    let date = today.getFullYear() + '-' + (today.getMonth() + 1) + '-' + today.getDate();
    let time = today.getHours() + ":" + today.getMinutes() + ":" + today.getSeconds();
    let offset = new Date().getTimezoneOffset() / -60;
    let dateTime = date + 'T' + time + '+' + offset + ':00';
    return dateTime;
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function getShifts() {
    let dateTime = getTime();
    console.log(calendarId);
    result = calendar.events.list({
        calendarId: calendarId,
        timeMin: dateTime
    });
    console.log(result);
    return result;
}

async function deleteAndAddShifts() {
    let shifts = await getShifts().catch(e => { console.log(e) });
    for (let i = 0; i < shifts.data.items.length; i++) {
        await calendar.events.delete({
            calendarId: calendarId,
            eventId: shifts.data.items[i].id
        }).catch(e => { console.log(e) });
        sleep(10000);
        console.log(i + "  :  deleted");
    }
    console.log(newShifts.length);
    for (let j = 0; j < newShifts.length; j++) {
        let newStart = convertDateTime(newShifts[j].date, newShifts[j].startTime);
        let newEnd = convertDateTime(newShifts[j].date, newShifts[j].endTime);
        let event = {
            summary: 'Work - Break: ' + newShifts[j].break,
            location: '127 Boronia Rd, Boronia VIC 3155',
            description: 'Another Day, Another Dollar...',
            start: {
                dateTime: newStart,
                timeZone: 'Australia/Melbourne'
            },
            end: {
                dateTime: newEnd,
                timeZone: 'Australia/Melbourne'
            },
            colorId: 11
        };
        await calendar.events.insert({
            calendarId: calendarId,
            resource: event
        }).catch(e => { console.log(e) });
        sleep(10000);
        console.log(j + "   :   created");
    }
}

runScript();
deleteAndAddShifts();

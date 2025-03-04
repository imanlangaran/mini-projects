# Persian Calendat Events

## Exporting events and save them into a json file
using [this](https://gist.github.com/hosseinmasoomi/0d5f873ec54e5538d3f46264c82d4126) stript and [time.ir](time.ir) website you can export all events in console panel in your browser 

```js
Array.from(document.querySelectorAll("li[class='eventHoliday ']"), (node => ({
    date:document.querySelector("input[type='text']").value +'/' + (Array.from(document.querySelectorAll("div[class='col-md-12']>div>div>span>span>span"), node => node.innerText).findIndex(x => x === node.innerText.split(" ")[1]) + 1).toString() + "/" + node.innerText.split(" ")[0].replace(/[۰-۹]/g, d => '۰۱۲۳۴۵۶۷۸۹'.indexOf(d)),
    description: node.innerText.split(" ").slice(2).join(" ")
})))
```

actually the query abow just provide the days that are holidays.
i wanted all the events.
so i changed the query and this is what i used:

```js
Array.from(document.querySelectorAll("ul.list-unstyled li"), (node => ({
    date:document.querySelector("input[type='text']").value +'/' + (Array.from(document.querySelectorAll("div[class='col-md-12']>div>div>span>span>span"), node => node.innerText).findIndex(x => x === node.innerText.split(" ")[1]) + 1).toString() + "/" + node.innerText.split(" ")[0].replace(/[۰-۹]/g, d => '۰۱۲۳۴۵۶۷۸۹'.indexOf(d)),
    description: node.innerText.split(" ").slice(2).join(" ")
})))
```

and its result is stored in (json file)[./PersianEvents.json]

## new Website of time.ir
in their newer version of [time.ir](new.time.ir) they used APIs.
so you can easily call them and store or use raw data.

here is the bash request 

```bash
curl 'https://api.time.ir/v1/event/fa/events/yearlycalendar?year=1404' \
  -H 'x-api-key: ZAVdqwuySASubByCed5KYuYMzb9uB2f7'
```
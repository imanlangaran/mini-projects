//+------------------------------------------------------------------+
//| AIChartBridge.mq5                                                |
//|                                                                  |
//| Polls the FastAPI chart bridge and draws AI annotations on the   |
//| chart. Wire format: one trendline per line, pipe-separated:      |
//|                                                                  |
//|   id|direction|time1|price1|time2|price2|extend_right            |
//|                                                                  |
//| id          : becomes the chart object "AI_<id>"                 |
//| direction   : "up" (green) or "down" (red)                       |
//| times       : epoch seconds (UTC) — MQL5 datetime is epoch-based |
//| prices      : market price                                       |
//| extend_right: 1 = ray right (OBJPROP_RAY_RIGHT), 0 = segment     |
//|                                                                  |
//| Receiving the same id again UPDATES the existing object in place |
//| (ObjectMove) instead of piling up duplicates.                    |
//|                                                                  |
//| MT5 requirement: Tools -> Options -> Expert Advisors ->          |
//| "Allow WebRequest for listed URL" -> add http://127.0.0.1:8000   |
//+------------------------------------------------------------------+
#property strict
#property copyright "TradeAgent"
#property version   "1.00"

input string BridgeURL          = "http://127.0.0.1:8000";
input int    PollIntervalSeconds = 2;
input color  UpColor            = clrLimeGreen;
input color  DownColor          = clrTomato;
input int    LineWidth           = 2;

string ChartSymbol;
string TimeframeName;

//+------------------------------------------------------------------+
int OnInit()
  {
   ChartSymbol = _Symbol;
   TimeframeName = EnumToString(_Period);
   StringReplace(TimeframeName, "PERIOD_", "");

   EventSetTimer(PollIntervalSeconds);

   Print("AI Chart Bridge started: ", ChartSymbol, " ", TimeframeName,
         " -> ", BridgeURL);

   return(INIT_SUCCEEDED);
  }
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
   EventKillTimer();
  }
//+------------------------------------------------------------------+
void OnTimer()
  {
   FetchAnnotations();
  }
//+------------------------------------------------------------------+
void FetchAnnotations()
  {
   string url = BridgeURL +
                "/annotations?symbol=" + ChartSymbol +
                "&timeframe=" + TimeframeName;

   char   data[];
   char   result[];
   string result_headers;

   ResetLastError();

   int status = WebRequest(
      "GET",
      url,
      "",            // cookie
      "",            // referer
      5000,          // timeout ms
      data,          // request body (empty for GET)
      0,             // data size
      result,
      result_headers
   );

   if(status == -1)
     {
      int err = GetLastError();

      if(err == 4014 || err == 4060)
         Print("WebRequest blocked: add ", BridgeURL,
               " to Tools -> Options -> Expert Advisors -> Allow WebRequest. Error: ", err);
      else
         Print("WebRequest failed. Error: ", err);

      return;
     }

   if(status != 200)
     {
      Print("Bridge returned HTTP ", status);
      return;
     }

   string response = CharArrayToString(result);

   if(StringLen(response) == 0)
      return;                      // nothing to draw yet

   ParseAnnotations(response);
  }
//+------------------------------------------------------------------+
//| Parse the pipe format and draw/update each trendline.            |
//+------------------------------------------------------------------+
void ParseAnnotations(string response)
  {
   string lines[];
   int n = StringSplit(response, '\n', lines);

   for(int i = 0; i < n; i++)
     {
      string line = lines[i];

      StringTrimLeft(line);
      StringTrimRight(line);

      if(StringLen(line) == 0)
         continue;

      string parts[];
      if(StringSplit(line, '|', parts) != 7)
        {
         Print("Malformed annotation line: ", line);
         continue;
        }

      string id          = parts[0];
      string direction   = parts[1];
      long   time1       = StringToInteger(parts[2]);
      double price1      = StringToDouble(parts[3]);
      long   time2       = StringToInteger(parts[4]);
      double price2      = StringToDouble(parts[5]);
      bool   extend_right = (StringToInteger(parts[6]) != 0);

      if(StringLen(id) == 0 || time1 == 0 || time2 == 0)
        {
         Print("Invalid annotation: ", line);
         continue;
        }

      DrawTrendline(id, direction, (datetime)time1, price1,
                    (datetime)time2, price2, extend_right);
     }
  }
//+------------------------------------------------------------------+
//| Create or update one OBJ_TREND line named "AI_<id>".             |
//+------------------------------------------------------------------+
void DrawTrendline(string id, string direction,
                   datetime time1, double price1,
                   datetime time2, double price2,
                   bool extend_right)
  {
   string name = "AI_" + id;
   color  line_color = (direction == "up") ? UpColor : DownColor;

   if(ObjectFind(0, name) < 0)
     {
      if(!ObjectCreate(0, name, OBJ_TREND, 0, time1, price1, time2, price2))
        {
         Print("ObjectCreate failed for ", name, ". Error: ", GetLastError());
         return;
        }

      ObjectSetInteger(0, name, OBJPROP_COLOR,     line_color);
      ObjectSetInteger(0, name, OBJPROP_WIDTH,     LineWidth);
      ObjectSetInteger(0, name, OBJPROP_STYLE,     STYLE_SOLID);
      ObjectSetInteger(0, name, OBJPROP_BACK,      false);
      ObjectSetInteger(0, name, OBJPROP_SELECTABLE, true);

      Print("Created AI trendline: ", name);
     }
   else
     {
      // Same id posted again: move the anchors in place, no duplicates
      ObjectMove(0, name, 0, time1, price1);
      ObjectMove(0, name, 1, time2, price2);
     }

   ObjectSetInteger(0, name, OBJPROP_RAY_RIGHT, extend_right);
   ObjectSetInteger(0, name, OBJPROP_COLOR,     line_color);

   ChartRedraw(0);
  }
//+------------------------------------------------------------------+

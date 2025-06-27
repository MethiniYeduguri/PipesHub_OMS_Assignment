from datetime import datetime,time,timedelta
from collections import deque
import os
from time import sleep

class RequestType:
    UNKNOWN = 0
    NEW = 1
    MODIFY = 2
    CANCEL = 3

class ResponseType:
    UNKNOWN = 0
    ACCEPT = 1
    REJECT = 2

class OrderRequest:
    #stockid--id of the stock
    #stockprize-price of the stock
    #stocksize-how many units of stock
    #stockdo-to buy or sell the stock
    #ordid-the id of the order
    #ordreqtype-new,modify,cancel type
    #ordtime-time of the order placed
    def __init__(self,stockid,stockprice,stocksize,stockdo,ordid,ordreqtype,ordtime):
        self.stockid=stockid
        self.stockprice=stockprice
        self.stocksize=stocksize
        self.stockdo=stockdo
        self.ordid=ordid
        self.ordreqtype=ordreqtype
        self.ordtime=ordtime

class OrderResponse:
    def __init__(self, order_id, response_type):
        self.order_id = order_id
        self.response_type = response_type
        self.timestamp = datetime.now()

class OrderManagement:
    def __init__(self,maxord_persec=2):
        self.queue=deque()
        self.max_orders=maxord_persec
        self.sent_now_second=0
        self.current_now_second=datetime.now().second
        self.logon=time(22,0)
        self.logout=time(23,0)
        self.flag_logon=False
        self.flag_logout=False
        self.noof_order_times_sent={}
    def on_data_order(self,request:OrderRequest):
        now=datetime.now().time()
        second=datetime.now().second

        if(now>=self.logon and not(self.flag_logon)):
            self.send_logon()
            self.flag_logon=True

        if(now>self.logout and not(self.flag_logout)):
            self.send_logout()
            self.flag_logout=True
            
        if not self.logon<=request.ordtime<=self.logout :
            print(f"Order {now} is rejected.Time is over")
            return

        #modifies the order which is in queue
        if(request.ordreqtype==RequestType.MODIFY):
            for order in self.queue:
                if(order.ordid==request.ordid):
                    order.stockprice=request.stockprice
                    order.stocksize=request.stocksize
                    print(f"Order {order.ordid} is modified in queue")
                    return
            print(f"Order {request.ordid} is not found in queue-Modify failed")
            return

        #cancels the order which is in queue
        if(request.ordreqtype==RequestType.CANCEL):
            before_len=len(self.queue)
            self.queue=deque(i for i in self.queue if i.ordid!=request.ordid)
            if(len(self.queue)<before_len):
                print(f"Order {request.ordid} is canceled in queue")
            else:
                print(f"Order {request.ordid} is not found in queue-Cancel failed")
            return
        
        #resetting and send from queue
        if(second!=self.current_now_second):
            self.current_now_second=second
            self.sent_now_second=0
            #send queued requests first and adds to the present second requests
            while(self.queue and (self.sent_now_second<self.max_orders)):
                queued_order = self.queue.popleft()
                self.send(queued_order)
                self.sent_now_second += 1

        #considers the new orders which can take care now not by queue
        if(self.sent_now_second<self.max_orders):
            self.send(request)
            self.sent_now_second += 1
        #new orders taken care by queue
        else:
            print(f"Order {request.ordid} is queued-Limit hit")
            self.queue.append(request)

    def on_data_response(self,response:OrderResponse):

        if not os.path.exists("order_responses.csv"):
            with open("order_responses.csv", "w") as f:
                f.write("OrderID,ResponseType,Latency\n")

        if(response.order_id in self.noof_order_times_sent):
            sent_time=self.noof_order_times_sent.pop(response.order_id)
            latency=(response.timestamp-sent_time).total_seconds()
            print(f"Response for order {response.order_id}: {response.response_type},Latency:{latency:.3f}s")

            if(response.response_type==ResponseType.ACCEPT):
                status="ACCEPTED"
            elif(response.response_type==ResponseType.REJECT):
                status="REJECTED"
            else:
                status="UNKNOWN"
            
            with open("order_responses.csv", "a")as f:
                f.write(f"{response.order_id},{response.response_type},{latency:.3f}\n")
        else:
            print(f"Response received for unknown order ID:{response.order_id}")

    def send(self,request:OrderRequest):
        print(f"Sending order {request.ordid} to exchange")
        self.noof_order_times_sent[request.ordid]=datetime.now()

    def send_logon(self):
        #sending msg of timings of window
        print("Window is in Logon")

    def send_logout(self):
        #sending msg of timings of window
        print("Window is in Logout")

now = datetime.now()
valid_time = now.time()
invalid_time = (now + timedelta(hours=2)).time()

if __name__ == "__main__":

    orders = [
    OrderRequest(5001, 100, 20, 'B', 1111, RequestType.NEW, ordtime=valid_time),
    OrderRequest(5002, 200, 30, 'S', 1112, RequestType.NEW, ordtime=valid_time),
    OrderRequest(5002, 0, 0, 'S', 1112, RequestType.CANCEL, ordtime=valid_time),     # CANCEL 1112 early
    OrderRequest(5003, 300, 40, 'B', 1113, RequestType.NEW, ordtime=valid_time),
    OrderRequest(5003, 350, 99, 'B', 1113, RequestType.MODIFY, ordtime=valid_time),  # MODIFY 1113 early
    OrderRequest(5004, 400, 50, 'S', 1114, RequestType.NEW, ordtime=invalid_time),
    OrderRequest(5005, 500, 60, 'B', 1115, RequestType.NEW, ordtime=valid_time),
    ]
    om = OrderManagement()
    for order in orders:
        om.on_data_order(order)
        sleep(0.5)

    # Simulate a response
    response = OrderResponse(1112,ResponseType.ACCEPT)
    om.on_data_response(response)

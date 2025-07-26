import os
import razorpay


def razorpay_client():
        RAZORPAY_API_KEY=os.getenv("RAZORPAY_API_KEY")
        RAZORPAY_API_SECRET_KEY=os.getenv("RAZORPAY_API_SECRET_KEY")
        RAZORPAY_VERSION=os.getenv("RAZORPAY_VERSION")
        razorpay_client = razorpay.Client(auth=(RAZORPAY_API_KEY,RAZORPAY_API_SECRET_KEY ))
        razorpay_client.set_app_details({"title" : "bifrost flow", "version" : RAZORPAY_VERSION})
        return razorpay_client
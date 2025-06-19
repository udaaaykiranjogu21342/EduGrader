import pymongo

try:
    client = pymongo.MongoClient("mongodb+srv://udaykiranjogu2005:udaykiran@2005@edugrader.dog6lyc.mongodb.net/?retryWrites=true&w=majority&appName=EduGrader")
    client.server_info()  # Forces connection on a request as the connect=True parameter of MongoClient seems not to work here
    print("Connected to MongoDB successfully!")
except Exception as e:
    print("Failed to connect:", e)

#Face Detect API
This is a simple face detection api that takes as input, an image and gives as output, detected faces on the image. This API can be used as an alternative to the paid face detection APIs currently available as it gives quite good accuracy levels.
the technologies used include: 
- Django
- Docker
- TensorFlow with MTCNN model
- Minio
- PostgreSQL
- RabbitMQ
- Redis
- Celery

##Architecture

The architecture used is a micro-service architecture with asynchronous processing of requests.
The diagram below highlights the architecture used;

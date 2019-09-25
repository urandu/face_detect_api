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

![alt text](./docs/face detect api.png "Architectural diagram")

##Local Deployment

To deploy the API locally, run the following commands
- clone this repo `git clone https://github.com/urandu/face_detect_api.git`
- `cd fac_detect_api`
- run `docker-compose up `
- wait for the necessary docker images to be pulled and started
- on a different terminal, run ``
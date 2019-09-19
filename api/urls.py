from django.conf.urls import url
from .views import DetectFaces, CreateFaceArray, CreateFaceEmbedding, CreateFaceEncoding, \
    ClusterFaces, ClassifyFace, ClassifyFaces, FaceClassification, Clusters, NewImage

urlpatterns = [
    url(r'^new_image/$', NewImage.as_view(), name='file-upload'),
    url(r'^detect_faces/$', DetectFaces.as_view(), name='detect_faces'),
    url(r'^create_face_array/$', CreateFaceArray.as_view(), name='create_face_array'),
    url(r'^create_face_embedding/$', CreateFaceEmbedding.as_view(), name='create_face_embedding'),
    url(r'^create_face_encoding/$', CreateFaceEncoding.as_view(), name='create_face_encoding'),
    url(r'^cluster_faces/$', ClusterFaces.as_view(), name='cluster_faces'),
    url(r'^classify_face/$', ClassifyFace.as_view(), name='classify_face'),
    url(r'^classify_faces/$', ClassifyFaces.as_view(), name='classify_faces'),
    url(r'^get_classification/$', FaceClassification.as_view(), name='get_classification'),
    url(r'^clusters/$', Clusters.as_view(), name='get_clusters'),
]
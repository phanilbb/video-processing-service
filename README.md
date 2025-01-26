# Video Processing Service

This is a Flask-based API designed for video uploading, trimming, merging, and sharing functionality. It allows users to upload videos, trim them, merge multiple videos, and share them through a token-based system.

## Project Structure

```commandline
video-processing-service/
│── app/
│   │── config/
│   │   └── __init__.py
│   │── exceptions/
│   │   ├── __init__.py
│   │   └── video_exceptions.py
│   │── logging/
│   │   └── __init__.py
│   │── routes/
│   │   ├── __init__.py
│   │   └── video_routes.py
│   │── service/
│   │   ├── processor/
│   │   │   ├── __init__.py
│   │   │   └── video_processor.py
│   │   ├── validator/
│   │   │   ├── __init__.py
│   │   │   └── video_validator.py
│   │   ├── __init__.py
│   │   └── video_service.py
│   │── utils/
│   │   ├── __init__.py
│   │   └── file_utils.py
│   │── videos/
│   │   ├── __init__.py
│   │   └── models.py
│── app.log
│── app.py
│── authentication.py
│── constants.py
│── extension.py
│── tests/
│   ├── __init__.py
│   └── test_routes.py
│── migrations/
│── README.md
```
# Project Setup

### 1. Ensure Python 3.x is installed on your system.
### 2. Set Up Virtual Environment
```
python -m venv venv
source venv/bin/activate
```
### 3. Install Dependencies
```
pip install -r requirements.txt
```
### 4. Run Database Migrations (Optional)
```
flask db upgrade
```
### 5. Run Tests (Optional)
```
pytest
```
### 5. Run the service
```
flask run --port 8000
```

### 6. Access the API By default, the API will run at
```
http://127.0.0.1:8000
```

### 6. Check for Bearer token in the config file

-----------------------

# API Reference
## 1. Upload Video


```http
  POST /video
```

Headers

| Parameter       | Type     | Description                |
|:----------------| :------- |:---------------------------|
| `Authorization` | `string` | **Required**. Bearer Token |

Request Body

| Parameter     | Type   | Description             |
|:--------------|:-------|:------------------------|
| `form-data`   | `file` | **Required video file** |


### Response:

#### 201 Created: 
```
{
    "message": "Video uploaded successfully", 
    "video_id": <video_id>
}
```

#### 400 Bad Request
```
{
    "error": "Invalid file"
}
```

#### 500 Internal Server Error
```
{
    "error": "<error message>"
}
```

## 2. Get Video


```http
  GET /video/${id}
```

Headers

| Parameter       | Type     | Description                |
|:----------------| :------- |:---------------------------|
| `Authorization` | `string` | **Required**. Bearer Token |

### Response:

#### 200 Response: 
```
{
    "duration": <duration>,
    "file_path": "<file_path>"
    "filename": "<file_name>"
    "id": <video_id>,
    "size": <size>
}
```

#### 404 Video Not found
```
{
    "error": "Video not found with ID <Id>"
}
```

#### 500 Internal Server Error
```
{
    "error": "<error message>"
}
```

## 3. Trim a video


```http
  POST /video/${id}/trim
```

Headers

| Parameter       | Type     | Description                |
|:----------------| :------- |:---------------------------|
| `Authorization` | `string` | **Required**. Bearer Token |

Request Body

| Parameter | Type  | Description              |
|:----------|:------|:-------------------------|
| `start`   | `int` | **Required** video start |
| `end`     | `int` | **Required** video end   |


### Response:

#### 200 Response: 
```
{
    "message": "Video trimmed successfully", 
    "video_id": <video_id>
}
```

#### 404 Video Not found
```
{
    "error": "Video not found with ID <Id>"
}
```

#### 500 Internal Server Error
```
{
    "error": "<error message>"
}
```


## 4. Merge videos


```http
  POST /videos
```

Headers

| Parameter       | Type     | Description                |
|:----------------| :------- |:---------------------------|
| `Authorization` | `string` | **Required**. Bearer Token |

Request Body

| Parameter   | Type        | Description            |
|:------------|:------------|:-----------------------|
| `video_ids` | `List<int>` | **Required** video ids |


### Response:

#### 200 Response: 
```
{
    "message": "Video merged successfully", 
    "video_id": <video_id>
}
```

#### 404 Video Not found
```
{
    "error": "Video not found with ID <Id>"
}
```

#### 500 Internal Server Error
```
{
    "error": "<error message>"
}
```

## 5. Share a video


```http
  POST /video/${id}/share
```

Headers

| Parameter       | Type     | Description                |
|:----------------| :------- |:---------------------------|
| `Authorization` | `string` | **Required**. Bearer Token |

### Response:

#### 200 Response: 
```
{
    "expiry_time": "<expiry time>"
    "share_url": "<share_url>"
}
```

#### 404 Video Not found
```
{
    "error": "Video not found with ID <Id>"
}
```

#### 500 Internal Server Error
```
{
    "error": "<error message>"
}
```



# Coco-Tasks Annotation Tool

This repository contains the code for the web application used to annotated the [COCO-Tasks dataset](https://github.com/coco-tasks/dataset).

This is a Django web application that we used to run on a server. The interface looks like the screenshot below.

![Screenshot](/screenshot.png)

## What Is This?

* This is a Django web application
* We ran this on a server
* Users would remotely log into their account and annotate images for the COCO-Tasks dataset.

## Running The Server

The Django application has *models* (as in Django models) for:

* Category: a COCO category
* Image: a COCO image
* Annot: a COCO annotation for an object
* Task: a task in our dataset
* Job: a Users job to annotate an Image for a Task
* PreferredAnnot: a preferred Annot for a Job.

Plus the User model which we reused the Django's User.



There are various Django commands that will populate the database with full categories, images and annotation of COCO. There are also commands to assign jobs to users. And Finally commands to extract the data into a JSON file format that is later used to create the dataset.



## Requirements

We used Python 3.6 and the other requirements are specified in the `requirements.txt` file.

You also need to use the COCO's Python API which is included in this repository. You just have to compile it using the following commands.

```bash
cd src/external/coco/PythonAPI
make
```

If you want to run this on a head-less server you will probably run into Matplotlib issues. Just run the following to fix them.

```bash
mkdir -p ~/.config/matplotlib
echo "backend: template" >> ~/.config/matplotlib/matplotlibrc
```

## Preparing The Database

To setup the database (we use SQLite) just run the following.

```bash
./manage.py migrate
./manage.py createsuperuser
```

### Downloading COCO

You need the images and annotations of the COCO dataset to make the annotation server really work.

You need to download 2014 Train and Val images and their annotations from [here](http://cocodataset.org/#download) and extracting the images.

You need COCO root directory with this structure inside:

```
.
+-- annotations
|   +-- instances_train2014.json
|   +-- instances_val2014.json
+-- train2014
|   +-- COCO_train2014_000000000009.jpg
|   +-- COCO_train2014_000000000025.jpg
|   +-- ...
+-- val2014
    +-- COCO_val2014_000000000042.jpg
    +-- COCO_val2014_000000000073.jpg
    +-- ...
```

I assume that this root directory is located at `~/mscoco`.

## Populating the Database

### Annotation Policy

We had an annotation policy. Basically a set of guidelines for the annotators.

You can load our annotation policy using the following command.

```bash
./manage.py loaddata annotpreferred/fixtures/annotationpolicy.json
```

### Tasks

The definition of the tasks that we used for annotating our dataset along with the images are also provided as a Django "fixture". Do the following to load the tasks.

```bash
./manage.py loaddata annotpreferred/fixtures/tasks.json
```

### Categories

```bash
./manage.py createcategories ~/mscoco/annotations/instances_train2014.json
```

### Images

You also need a list of images that are going to be annotated. The list that we used for our dataset can be found [here](https://github.com/coco-tasks/dataset/tree/cvpr2019/image_lists).

I assume that you have the list of images at `~/mscoco/coco-tasks/image_lists`.

Then you should run the following command.

```bash
./manage.py createimages ~/mscoco/coco-tasks/image_lists ~/mscoco
```

### Annotations

For the images in the dataset, you also need to put the annotations of objects inside them into the database.

```bash
./manage.py createannots ~/mscoco
```

This takes a bit of time.

## Running the Server and Annotating

You can run the server like any other Django app.

```bash
./manage.py runserver
```

### Adding Users

By going to the admin of the Django app you can add users that will annotate the dataset. Just visit <http://localhost:8000/admin/auth/user/> and add a new user.

Let's say you have added a user with `johann` as the username.

### Adding Jobs for Users

Now by running the following command you can add Jobs for `johann` for annotated.

```bash
# ./manage.py addjobs USER_NAME TASK_NUMBER
./manage.py addjobs johann 1
```

This adds jobs for `johann` to annotate task 1.

Now you tell `johann` to login to the go to <http://localhost:8000/> and login using his username and password and start annotating.



## Dumping Annotation Results

After annotation is done, you can use the following command to extract the annotation information into a raw JSON format.

```bash
./manage.py createrawfiles johann user2 user3
```

As you can see, you can pass a list of user names to this command to generate raw files for a bunch of users.

This will create JSON files with the following format.

```js
{  
    "1":{  //task number
        "531568":{  //image number
            "johann":{  //user name
                "424155":0, //annotationid: 0 means this object in this image is not preferred for the task.
                "1159538":0,
                "1605215":1, // 1 means it is preferred.
                "1967102":0,
                "2122630":0
            }
        },
        "283617":{  
            "johann":{  
                "47494":0,
                "108100":1,
                "1096425":0
            }
        }
        // ...
    }
    // ...
}
```

We used these JSON files and created the [COCO-Tasks dataset](https://github.com/coco-tasks/dataset).

## More Information

If you want more information please refer to our [paper](https://arxiv.org/abs/1904.03000) and [supplementary material](https://yassersouri.github.io/papers/coco-tasks-cvpr2019-supmat.pdf).


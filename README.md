
# CSE 30124: Introduction to Artificial Intelligence Final Project

This project seeks to create a simulator to mimic the process of an online rideshare system and develop and evaluate strategies related to the distribution of rides to drivers in a robust and scalable method. 


## Authors

- [@zbrown31](https://github.com/zbrown31)



## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

`GMAPS_API_KEY`

If this value is not added, then the GMapsClient will throw an error of invalid credentials. The author's credentials have been removed to avoid unwanted billing. If it is necessary for testing, the author can provide a temporary key.


## Run Locally

Clone the project

```bash
  git clone https://github.com/zbrown31/cse-30124-project
```

Go to the project directory

```bash
  cd cse-30124-project
```

Install dependencies

```bash
  pip3 install requirements.txt
```

Edit the main.py file by tweaking the appropriate parameters to configure the program to your specifications

Run the experiments

```bash
  python3 main.py
```

